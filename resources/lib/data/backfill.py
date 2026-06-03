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
    INFERENCE_COUNTRIES,
    RATING_MAPPINGS,
)
from resources.lib.data.kodi import get_missing_ratings, update_rating
from resources.lib.data.media_types import MediaType
from resources.lib.data.tracker import load_tracker, save_tracker, should_apply_fallback
from resources.lib.providers import tmdb, omdb, kijkwijzer
from resources.lib.utils import get_logger, get_setting, get_bool_setting, get_int_setting, get_float_setting

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
    fallback_rating = get_setting('fallback_rating') or DEFAULT_FALLBACK_RATING
    retry_days = get_int_setting('retry_days', DEFAULT_RETRY_DAYS)
    rate_limit = get_float_setting('rate_limit', DEFAULT_RATE_LIMIT_SEC)
    use_kijkwijzer = get_bool_setting('enable_kijkwijzer')

    # Load tracker for this media type
    unresolved = load_tracker(media_type.tracker_filename)

    # Query Kodi for items with missing ratings
    items = get_missing_ratings(media_type)
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

    for item in items:
        item_id = item["id"]
        title = item["title"]
        tmdb_id = item["tmdb_id"]
        imdb_id = item["imdb_id"]

        rating: Optional[str] = None
        source: Optional[str] = None

        try:
            # Tier 1+2: TMDB direct + inference
            if not rating and tmdb_id and tmdb_key:
                rating, source = tmdb.lookup(
                    tmdb_id, tmdb_key, target,
                    INFERENCE_COUNTRIES, RATING_MAPPINGS, media_type,
                )
                time.sleep(rate_limit)

            # Tier 3: OMDB
            if not rating and imdb_id and omdb_key:
                rating, source = omdb.lookup(imdb_id, omdb_key, RATING_MAPPINGS)
                time.sleep(rate_limit)

            # Tier 4: Kijkwijzer.nl
            if not rating and use_kijkwijzer:
                rating, source = kijkwijzer.lookup(title, rate_limit)

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
