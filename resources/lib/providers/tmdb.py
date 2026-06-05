"""
TMDB provider for certification lookups.

Exposes three granular functions for split-tier usage in backfill:
    fetch_certs  -- single API call, returns {country: rating} dict
    match_direct -- pure lookup for the target country
    match_inferred -- walks the inference chain with mapping

The convenience wrapper lookup() calls all three in sequence.

Logging:
    Logger: 'tmdb'
    Key events:
        - tmdb.direct (DEBUG): Direct match found for target country
        - tmdb.inferred (DEBUG): Rating inferred from another country
        - tmdb.no_match (DEBUG): No certification found
        - tmdb.error (WARNING): API request failed
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import requests

from resources.lib.constants import TMDB_BASE_URL
from resources.lib.data.media_types import MediaType
from resources.lib.utils import ApiKeyError, get_logger

log = get_logger('tmdb')

# TMDB uses different certification strings for SE TV vs SE movies.
# Normalize TV format ("Från 7 år") to movie format ("7") so the rest
# of the pipeline only sees one set of values per country.
_CERT_NORMALIZE = {
    "SE": {
        "Från 7 år": "7",
        "Från 11 år": "11",
        "Från 15 år": "15",
    },
}


def _normalize_certs(certs: Dict[str, str]) -> Dict[str, str]:
    """Normalize country-specific certification aliases to canonical values."""
    for country, table in _CERT_NORMALIZE.items():
        if country in certs:
            certs[country] = table.get(certs[country], certs[country])
    return certs


def resolve_id(
    api_key: str,
    tvdb_id: Optional[str] = None,
    imdb_id: Optional[str] = None,
) -> Optional[str]:
    """
    Resolve a TMDB ID from an external ID using the /find endpoint.

    Tries tvdb_id first, then imdb_id. Returns the TMDB ID as a string,
    or None if resolution fails.
    """
    external_id = None
    source = None
    if tvdb_id:
        external_id = tvdb_id
        source = "tvdb_id"
    elif imdb_id:
        external_id = imdb_id
        source = "imdb_id"

    if not external_id:
        return None

    url = "{}/find/{}".format(TMDB_BASE_URL, external_id)

    try:
        resp = requests.get(
            url,
            params={"api_key": api_key, "external_source": source},
            timeout=10,
        )
    except requests.RequestException as e:
        log.warning("Resolve request failed", event="tmdb.error",
                    external_id=external_id, error=str(e))
        return None

    if resp.status_code == 401:
        raise ApiKeyError("tmdb")

    if resp.status_code != 200:
        log.debug("Resolve returned unexpected status",
                  external_id=external_id, status=resp.status_code)
        return None

    try:
        data = resp.json()
    except ValueError:
        return None

    for key in ("movie_results", "tv_results"):
        results = data.get(key, [])
        if results:
            resolved_id = results[0].get("id")
            if resolved_id is not None:
                log.debug("Resolved TMDB ID", external_id=external_id,
                          source=source, tmdb_id=resolved_id)
                return str(resolved_id)

    log.debug("Could not resolve TMDB ID", external_id=external_id,
              source=source)
    return None


def fetch_certs(
    tmdb_id: str,
    api_key: str,
    media_type: MediaType,
) -> Optional[Dict[str, str]]:
    """Fetch certifications from TMDB for all countries.

    Makes a single API call. Returns {country_code: rating} or None on
    failure. Raises ApiKeyError on 401.
    """
    endpoint = media_type.tmdb_endpoint.format(id=tmdb_id)
    url = "{}{}".format(TMDB_BASE_URL, endpoint)

    try:
        resp = requests.get(url, params={"api_key": api_key}, timeout=10)
    except requests.RequestException as e:
        log.warning("Request failed", event="tmdb.error",
                    tmdb_id=tmdb_id, error=str(e))
        return None

    if resp.status_code == 401:
        raise ApiKeyError("tmdb")

    if resp.status_code != 200:
        log.warning("Unexpected status", event="tmdb.error",
                    tmdb_id=tmdb_id, status=resp.status_code)
        return None

    try:
        results = resp.json().get("results", [])
    except ValueError:
        log.warning("Invalid JSON response", event="tmdb.error",
                    tmdb_id=tmdb_id)
        return None

    return _normalize_certs(media_type.tmdb_parse_certs(results))


def match_direct(
    certs: Dict[str, str],
    target_country: str,
) -> Tuple[Optional[str], Optional[str]]:
    """Check for a direct certification match for the target country."""
    target = target_country.upper()
    if target in certs:
        log.debug("Direct match", country=target, rating=certs[target])
        return certs[target], "tmdb-{}".format(target)
    return None, None


def match_inferred(
    certs: Dict[str, str],
    target_country: str,
    inference_countries: List[str],
    mappings: Dict[str, Dict[str, str]],
) -> Tuple[Optional[str], Optional[str]]:
    """Try to infer a rating from similar countries' certifications."""
    for country in inference_countries:
        country_upper = country.upper()
        if country_upper in certs and country_upper in mappings:
            foreign_rating = certs[country_upper]
            mapped = mappings[country_upper].get(foreign_rating)
            if mapped:
                log.debug("Inferred rating", country=country_upper,
                          foreign_rating=foreign_rating, mapped=mapped)
                return mapped, "tmdb-inferred-{}".format(country_upper)
            else:
                log.debug("No mapping for rating", country=country_upper,
                          rating=foreign_rating)

    log.debug("No inferred certification found", target=target_country)
    return None, None


def lookup(
    tmdb_id: str,
    api_key: str,
    target_country: str,
    inference_countries: List[str],
    mappings: Dict[str, Dict[str, str]],
    media_type: MediaType,
) -> Tuple[Optional[str], Optional[str]]:
    """Query TMDB for certifications (convenience wrapper).

    Makes a single API call, checks direct match, then inferred.
    Returns (rating, source) or (None, None).
    """
    certs = fetch_certs(tmdb_id, api_key, media_type)
    if certs is None:
        return None, None

    rating, source = match_direct(certs, target_country)
    if rating:
        return rating, source

    return match_inferred(certs, target_country, inference_countries, mappings)
