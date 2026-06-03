"""
Backfill orchestration.

Coordinates the multi-tier rating lookup for a single media type:
overrides -> TMDB direct -> TMDB inferred -> OMDB -> kijkwijzer.nl -> fallback.

Logging:
    Logger: 'backfill'
    Key events:
        - backfill.start (INFO): Scan starting for media type
        - backfill.complete (INFO): Scan finished for media type
        - backfill.rated (INFO): Rating applied to an item
        - backfill.pending (DEBUG): Item still waiting for rating
"""
from __future__ import annotations

import time
from typing import Dict, Optional

from resources.lib.constants import (
    DEFAULT_FALLBACK_RATING,
    DEFAULT_RATE_LIMIT_SEC,
    DEFAULT_RETRY_DAYS,
    DEFAULT_TARGET_COUNTRY,
    DEFAULT_RATING_PREFIX,
)
from resources.lib.config import load_inference_config
from resources.lib.data.kodi import get_items_needing_ratings, update_rating
from resources.lib.data.media_types import MediaType
from resources.lib.data.tracker import load_tracker, save_tracker, should_apply_fallback
from resources.lib.providers import tmdb, omdb, kijkwijzer
from resources.lib.utils import (
    ApiKeyError, get_logger, get_setting, get_bool_setting,
    get_int_setting, get_float_setting, notify,
)

log = get_logger('backfill')


def backfill(media_type: MediaType) -> Dict[str, int]:
    """
    Run the full rating backfill for a single media type.

    Returns a stats dict with counts per source.
    """
    # Read settings
    tmdb_key = get_setting('tmdb_api_key')
    omdb_key = get_setting('omdb_api_key')
    target = get_setting('target_country') or DEFAULT_TARGET_COUNTRY
    prefix = get_setting('rating_prefix') or DEFAULT_RATING_PREFIX
    enable_fallback = get_bool_setting('enable_fallback')
    fallback_rating = ""
    retry_days = DEFAULT_RETRY_DAYS
    if enable_fallback:
        raw_fallback = get_setting('fallback_rating')
        fallback_rating = raw_fallback if raw_fallback else DEFAULT_FALLBACK_RATING
        retry_days = get_int_setting('retry_days', DEFAULT_RETRY_DAYS)
    rate_limit = get_float_setting('rate_limit', DEFAULT_RATE_LIMIT_SEC)
    use_kijkwijzer = get_bool_setting('enable_kijkwijzer')
    replace_incorrect = get_bool_setting('replace_incorrect')
    inference_cfg = load_inference_config()
    inference_countries = inference_cfg["inference_countries"]
    mappings = inference_cfg["mappings"]

    # Load tracker for this media type
    unresolved = load_tracker(media_type.tracker_filename)

    # Query Kodi for items needing ratings
    items = get_items_needing_ratings(media_type, replace_incorrect, fallback_rating)
    log.info("Scan starting", event="backfill.start",
             media_type=media_type.label, missing_count=len(items))

    stats: Dict[str, int] = {
        "tmdb_direct": 0,
        "tmdb_inferred": 0,
        "omdb": 0,
        "kijkwijzer": 0,
        "fallback": 0,
        "pending": 0,
        "error": 0,
    }

    tmdb_valid = True
    omdb_valid = True
    api_key_notified = False

    for item in items:
        item_id = item["id"]
        title = item["title"]
        tmdb_id = item["tmdb_id"]
        imdb_id = item["imdb_id"]
        tvdb_id = item["tvdb_id"]

        if tmdb_key and not tmdb_valid:
            log.debug("Skipping TMDB (auth failed)", title=title)
        if omdb_key and not omdb_valid:
            log.debug("Skipping OMDB (auth failed)", title=title)

        rating: Optional[str] = None
        source: Optional[str] = None

        try:
            # Resolve TMDB ID from TVDB/IMDB when missing
            if not tmdb_id and tmdb_key and tmdb_valid:
                tmdb_id = tmdb.resolve_id(tmdb_key, tvdb_id=tvdb_id, imdb_id=imdb_id)
                if tmdb_id:
                    time.sleep(rate_limit)

            # Tier 1+2: TMDB direct + inference
            if not rating and tmdb_id and tmdb_key and tmdb_valid:
                rating, source = tmdb.lookup(
                    tmdb_id, tmdb_key, target,
                    inference_countries, mappings, media_type,
                )
                time.sleep(rate_limit)

            # Tier 3: OMDB
            if not rating and imdb_id and omdb_key and omdb_valid:
                rating, source = omdb.lookup(imdb_id, omdb_key, mappings)
                time.sleep(rate_limit)

            # Tier 4: Kijkwijzer.nl
            if not rating and use_kijkwijzer:
                rating, source = kijkwijzer.lookup(title, rate_limit)

        except ApiKeyError as e:
            if e.provider == "tmdb":
                tmdb_valid = False
            elif e.provider == "omdb":
                omdb_valid = False
            log.error("Invalid API key", event="backfill.auth_error",
                      provider=e.provider)
            if not api_key_notified:
                notify("{} API key is invalid".format(e.provider.upper()))
                api_key_notified = True
            continue

        except Exception:
            log.exception("Provider error", event="backfill.provider_error",
                          media_type=media_type.label, title=title)
            stats["error"] += 1
            continue

        if rating:
            unresolved.pop(title, None)
            full_rating = "{}{}".format(prefix, rating)
            update_rating(item_id, full_rating, media_type)
            log.info("Rating applied", event="backfill.rated",
                     media_type=media_type.label, title=title,
                     rating=full_rating, source=source)
            stats[_stat_key(source)] += 1

        elif fallback_rating and should_apply_fallback(title, unresolved, retry_days):
            full_rating = "{}{}".format(prefix, fallback_rating)
            update_rating(item_id, full_rating, media_type)
            log.info("Fallback rating applied", event="backfill.rated",
                     media_type=media_type.label, title=title,
                     rating=full_rating, source="fallback")
            unresolved.pop(title, None)
            stats["fallback"] += 1

        else:
            first_seen = unresolved.get(title, {}).get("first_seen", "today")
            log.debug("Item pending", title=title, first_seen=first_seen)
            stats["pending"] += 1

    save_tracker(media_type.tracker_filename, unresolved)

    log.info("Scan complete", event="backfill.complete",
             media_type=media_type.label, **stats)

    return stats


def _stat_key(source: Optional[str]) -> str:
    """Map a source label to a stats dict key."""
    if not source:
        return "error"
    if source == "kijkwijzer":
        return "kijkwijzer"
    if "inferred" in source:
        return "tmdb_inferred"
    if source.startswith("tmdb"):
        return "tmdb_direct"
    return "omdb"
