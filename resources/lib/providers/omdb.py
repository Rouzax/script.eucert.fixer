"""
OMDB provider for rating lookups.

Maps US MPAA ratings to the target scale via the US mapping table.

Logging:
    Logger: 'omdb'
    Key events:
        - omdb.match (DEBUG): Rating found and mapped
        - omdb.no_match (DEBUG): No usable rating from OMDB
        - omdb.error (WARNING): API request failed
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

import requests

from resources.lib.constants import OMDB_BASE_URL
from resources.lib.utils import ApiKeyError, get_logger

log = get_logger('omdb')


def lookup(
    imdb_id: str,
    api_key: str,
    mappings: Dict[str, Dict[str, str]],
) -> Tuple[Optional[str], Optional[str]]:
    """
    Query OMDB by IMDB ID.

    Returns (rating, source) or (None, None).
    """
    try:
        resp = requests.get(
            OMDB_BASE_URL,
            params={"i": imdb_id, "apikey": api_key},
            timeout=10,
        )
    except requests.RequestException as e:
        log.warning("Request failed", event="omdb.error",
                    imdb_id=imdb_id, error=str(e))
        return None, None

    if resp.status_code == 401:
        raise ApiKeyError("omdb")

    if resp.status_code != 200:
        log.warning("Unexpected status", event="omdb.error",
                    imdb_id=imdb_id, status=resp.status_code)
        return None, None

    try:
        data = resp.json()
    except ValueError:
        log.warning("Invalid JSON response", event="omdb.error",
                    imdb_id=imdb_id)
        return None, None

    if data.get("Response") == "False":
        log.debug("No result", imdb_id=imdb_id)
        return None, None

    rated = data.get("Rated", "")
    if not rated or rated == "N/A":
        return None, None

    us_mappings = mappings.get("US", {})
    mapped = us_mappings.get(rated)
    if mapped:
        log.debug("Rating mapped", imdb_id=imdb_id,
                  us_rating=rated, mapped=mapped)
        return mapped, "omdb"

    log.debug("No US mapping for rating", imdb_id=imdb_id, rated=rated)
    return None, None
