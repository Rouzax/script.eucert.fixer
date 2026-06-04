"""
Backfill orchestration.

Coordinates the multi-tier rating lookup for a single media type:
TMDB direct -> TMDB inferred -> OMDB -> country scrapers -> fallback.

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
from typing import Dict, Optional, Tuple

from resources.lib.constants import (
    DEFAULT_FALLBACK_RATING,
    DEFAULT_RATE_LIMIT_SEC,
    DEFAULT_RETRY_DAYS,
    SCRAPER_CANARIES,
)
from resources.lib.config import load_inference_config
from resources.lib.data.kodi import get_items_needing_ratings, update_rating
from resources.lib.data.media_types import MediaType
from resources.lib.data.tracker import load_tracker, save_tracker, should_apply_fallback
from resources.lib.providers import tmdb, omdb, kijkwijzer, fsk, bbfc, medieraadet
from resources.lib.utils import (
    ApiKeyError, get_country_code, get_logger, get_setting, get_bool_setting,
    get_int_setting, get_float_setting, notify,
)

log = get_logger('backfill')


def backfill(media_type: MediaType) -> Dict[str, int]:
    """
    Run the full rating backfill for a single media type.

    Returns a stats dict with counts per source.
    """
    tmdb_key = get_setting('tmdb_api_key')
    if not tmdb_key:
        log.warning("TMDB API key not configured, skipping scan",
                    event="backfill.skip", media_type=media_type.label)
        return {"tmdb_direct": 0, "tmdb_inferred": 0, "omdb": 0,
                "scraper": 0, "fallback": 0, "pending": 0, "error": 0}

    omdb_key = get_setting('omdb_api_key')
    country_code = get_country_code()
    config = load_inference_config(country_code)
    valid_ratings = tuple(config["valid_ratings"])
    inference_countries = config["inference_countries"]
    mappings = config["mappings"]
    target = config["country_code"]
    prefix = get_setting('rating_prefix') or config.get("default_prefix", "")

    enable_fallback = get_bool_setting('enable_fallback')
    fallback_rating = ""
    retry_days = DEFAULT_RETRY_DAYS
    if enable_fallback:
        raw_fallback = get_setting('fallback_rating')
        fallback_rating = raw_fallback if raw_fallback else DEFAULT_FALLBACK_RATING
        retry_days = get_int_setting('retry_days', DEFAULT_RETRY_DAYS)
    rate_limit = get_float_setting('rate_limit', DEFAULT_RATE_LIMIT_SEC)
    use_fsk = get_bool_setting('enable_fsk')
    use_bbfc = get_bool_setting('enable_bbfc')
    use_medieraadet = get_bool_setting('enable_medieraadet')
    use_kijkwijzer = get_bool_setting('enable_kijkwijzer')
    replace_incorrect = get_bool_setting('replace_incorrect')

    unresolved = load_tracker(media_type.tracker_filename)

    items = get_items_needing_ratings(
        media_type, replace_incorrect, fallback_rating, valid_ratings,
    )
    log.info("Scan starting", event="backfill.start",
             media_type=media_type.label, missing_count=len(items))

    stats: Dict[str, int] = {
        "tmdb_direct": 0,
        "tmdb_inferred": 0,
        "omdb": 0,
        "scraper": 0,
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
        item_year = item.get("year", 0)
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

            # Tier 4: Country scrapers
            if not rating:
                rating, source = _try_scrapers(
                    title, rate_limit, imdb_id, media_type.name,
                    item_year, target, mappings,
                    use_fsk, use_bbfc, use_medieraadet, use_kijkwijzer,
                )

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


def _map_native_rating(
    native_rating: str,
    scraper_country: str,
    target: str,
    mappings: Dict[str, Dict[str, str]],
) -> Optional[str]:
    """Map a scraper's native rating to the target country scale."""
    if scraper_country == target:
        return native_rating
    table = mappings.get(scraper_country, {})
    return table.get(native_rating)


def _try_scrapers(
    title: str,
    rate_limit: float,
    imdb_id: Optional[str],
    media_type_name: str,
    year: int,
    target: str,
    mappings: Dict[str, Dict[str, str]],
    use_fsk: bool,
    use_bbfc: bool,
    use_medieraadet: bool,
    use_kijkwijzer: bool,
) -> Tuple[Optional[str], Optional[str]]:
    """Try enabled country scrapers in order. Returns (mapped_rating, source) or (None, None)."""
    if use_fsk:
        native, src = fsk.lookup(
            title, rate_limit, imdb_id=imdb_id,
            media_type_name=media_type_name, year=year,
        )
        if native and src:
            mapped = _map_native_rating(native, "DE", target, mappings)
            if mapped:
                return mapped, src
            log.debug("No DE mapping for FSK rating",
                      title=title, native=native, target=target)
        time.sleep(rate_limit)

    if use_bbfc:
        native, src = bbfc.lookup(
            title, rate_limit, media_type_name=media_type_name,
        )
        if native and src:
            mapped = _map_native_rating(native, "GB", target, mappings)
            if mapped:
                return mapped, src
            log.debug("No GB mapping for BBFC rating",
                      title=title, native=native, target=target)
        time.sleep(rate_limit)

    if use_medieraadet:
        native, src = medieraadet.lookup(
            title, rate_limit, media_type_name=media_type_name, year=year,
        )
        if native and src:
            mapped = _map_native_rating(native, "DK", target, mappings)
            if mapped:
                return mapped, src
            log.debug("No DK mapping for Medieraadet rating",
                      title=title, native=native, target=target)
        time.sleep(rate_limit)

    if use_kijkwijzer:
        native, src = kijkwijzer.lookup(title, rate_limit)
        if native and src:
            mapped = _map_native_rating(native, "NL", target, mappings)
            if mapped:
                return mapped, src
            log.debug("No NL mapping for Kijkwijzer rating",
                      title=title, native=native, target=target)

    return None, None


_SCRAPER_MODULES = {
    "fsk": fsk,
    "bbfc": bbfc,
    "medieraadet": medieraadet,
    "kijkwijzer": kijkwijzer,
}


def run_canaries(
    use_fsk: bool,
    use_bbfc: bool,
    use_medieraadet: bool,
    use_kijkwijzer: bool,
    rate_limit: float,
) -> None:
    """Test each enabled scraper with a known title to detect breakage."""
    enabled = {
        "fsk": use_fsk,
        "bbfc": use_bbfc,
        "medieraadet": use_medieraadet,
        "kijkwijzer": use_kijkwijzer,
    }

    for name, canary in SCRAPER_CANARIES.items():
        if not enabled.get(name):
            continue

        module = _SCRAPER_MODULES.get(name)
        if not module:
            continue

        title = canary["title"]
        expected = canary["expected"]
        kwargs = {"media_type_name": "movie"}
        if "year" in canary:
            kwargs["year"] = canary["year"]

        try:
            rating, _ = module.lookup(title, rate_limit, **kwargs)
        except Exception:
            log.warning("Canary request failed",
                        event="scraper.canary_error", scraper=name, title=title)
            time.sleep(rate_limit)
            continue

        if rating == expected:
            log.debug("Canary passed", scraper=name, title=title, rating=rating)
        elif rating is None:
            log.warning("Canary returned no result; scraper may be broken",
                        event="scraper.canary_fail",
                        scraper=name, title=title, expected=expected)
        else:
            log.warning("Canary returned unexpected rating; scraper may have changed",
                        event="scraper.canary_mismatch",
                        scraper=name, title=title, expected=expected, got=rating)
        time.sleep(rate_limit)


def _stat_key(source: Optional[str]) -> str:
    """Map a source label to a stats dict key."""
    if not source:
        return "error"
    if source in ("kijkwijzer", "fsk", "bbfc", "medieraadet"):
        return "scraper"
    if "inferred" in source:
        return "tmdb_inferred"
    if source.startswith("tmdb"):
        return "tmdb_direct"
    return "omdb"
