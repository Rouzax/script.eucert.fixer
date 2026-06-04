"""
TVmaze provider for external ID resolution.

Uses the free TVmaze API (no key required) to resolve TVmaze IDs
to IMDB/TVDB IDs, which can then be used for TMDB lookups.

Logging:
    Logger: 'tvmaze'
    Key events:
        - tvmaze.resolved (DEBUG): External IDs found
        - tvmaze.no_externals (DEBUG): No useful external IDs
        - tvmaze.error (WARNING): Request failed
"""
from __future__ import annotations

from typing import Optional, Tuple

import requests

from resources.lib.utils import get_logger

log = get_logger('tvmaze')

_BASE_URL = "https://api.tvmaze.com"


def resolve_externals(
    tvmaze_id: str,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch external IDs (IMDB, TVDB) for a TVmaze show.

    Returns (imdb_id, tvdb_id) with None for unavailable IDs.
    """
    url = "{}/shows/{}".format(_BASE_URL, tvmaze_id)

    try:
        resp = requests.get(url, timeout=10)
    except requests.RequestException as e:
        log.warning("Request failed", event="tvmaze.error",
                    tvmaze_id=tvmaze_id, error=str(e))
        return None, None

    if resp.status_code != 200:
        log.debug("Unexpected status", tvmaze_id=tvmaze_id,
                  status=resp.status_code)
        return None, None

    try:
        externals = resp.json().get("externals", {})
    except ValueError:
        return None, None

    imdb_id = externals.get("imdb")
    tvdb_id = externals.get("thetvdb")
    tvdb_str = str(tvdb_id) if tvdb_id else None

    if imdb_id or tvdb_str:
        log.debug("External IDs resolved", event="tvmaze.resolved",
                  tvmaze_id=tvmaze_id, imdb_id=imdb_id, tvdb_id=tvdb_str)
    else:
        log.debug("No useful external IDs", event="tvmaze.no_externals",
                  tvmaze_id=tvmaze_id)

    return imdb_id, tvdb_str
