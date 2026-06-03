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
from resources.lib.utils import get_logger

log = get_logger('tmdb')


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

    certs = media_type.tmdb_parse_certs(results)
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
