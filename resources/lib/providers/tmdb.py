"""
TMDB provider for certification lookups.

Checks the target country first (direct match), then tries inference
countries with mapping to the target rating scale.

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


def lookup(
    tmdb_id: str,
    api_key: str,
    target_country: str,
    inference_countries: List[str],
    mappings: Dict[str, Dict[str, str]],
    media_type: MediaType,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Query TMDB for certifications.

    Returns (rating, source) or (None, None).
    """
    endpoint = media_type.tmdb_endpoint.format(id=tmdb_id)
    url = "{}{}".format(TMDB_BASE_URL, endpoint)

    try:
        resp = requests.get(url, params={"api_key": api_key}, timeout=10)
    except requests.RequestException as e:
        log.warning("Request failed", event="tmdb.error",
                    tmdb_id=tmdb_id, error=str(e))
        return None, None

    if resp.status_code == 401:
        raise ApiKeyError("tmdb")

    if resp.status_code != 200:
        log.warning("Unexpected status", event="tmdb.error",
                    tmdb_id=tmdb_id, status=resp.status_code)
        return None, None

    try:
        results = resp.json().get("results", [])
    except ValueError:
        log.warning("Invalid JSON response", event="tmdb.error",
                    tmdb_id=tmdb_id)
        return None, None

    certs = _normalize_certs(media_type.tmdb_parse_certs(results))
    target = target_country.upper()

    # Direct match
    if target in certs:
        log.debug("Direct match", country=target,
                  rating=certs[target], tmdb_id=tmdb_id)
        return certs[target], "tmdb-{}".format(target)

    # Inference from similar countries
    for country in inference_countries:
        country_upper = country.upper()
        if country_upper in certs and country_upper in mappings:
            foreign_rating = certs[country_upper]
            mapped = mappings[country_upper].get(foreign_rating)
            if mapped:
                log.debug("Inferred rating", country=country_upper,
                          foreign_rating=foreign_rating, mapped=mapped,
                          tmdb_id=tmdb_id)
                return mapped, "tmdb-inferred-{}".format(country_upper)
            else:
                log.debug("No mapping for rating", country=country_upper,
                          rating=foreign_rating, tmdb_id=tmdb_id)

    log.debug("No certification found", tmdb_id=tmdb_id)
    return None, None
