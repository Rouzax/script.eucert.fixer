"""
FSK (Germany) provider for rating lookups.

Queries the FSK web API by title, cross-references IMDB IDs from the
response to confirm matches.

Logging:
    Logger: 'fsk'
    Key events:
        - fsk.match (DEBUG): Rating found with IMDB confirmation
        - fsk.title_match (DEBUG): Rating found by title only
        - fsk.no_results (DEBUG): Search returned no results
        - fsk.error (WARNING): Request failed
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import requests

from resources.lib.constants import FSK_API_URL
from resources.lib.utils import get_logger

log = get_logger('fsk')

_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    """Get a reusable requests session."""
    global _session
    if _session is None:
        _session = requests.Session()
    return _session


def _extract_imdb_ids(doc: Dict[str, Any]) -> List[str]:
    """Extract all IMDB IDs from a doc's subproducts."""
    ids = []
    for sub in doc.get("subproducts", []):
        imdb_id = sub.get("imdbId")
        if imdb_id:
            ids.append(str(imdb_id))
    return ids


def _title_matches(doc: Dict[str, Any], title: str) -> bool:
    """Check if a doc's title matches the search title (case-insensitive).

    For TV series, FSK lists individual episodes with titles like
    "BREAKING BAD SEASON 1 - AND THE BAG'S IN THE RIVER". A prefix
    match handles this.
    """
    title_lower = title.lower()
    for field in ("mainTitle", "mainOriginalTitle"):
        val = doc.get(field, "").lower()
        if not val:
            continue
        if val == title_lower or val.startswith(title_lower + " "):
            return True
    return False


def lookup(
    title: str,
    rate_limit: float = 0.25,
    imdb_id: Optional[str] = None,
    media_type_name: str = "movie",
    year: int = 0,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Search the FSK API by title.

    Matches by IMDB ID when available, falls back to title comparison.
    When year is provided, limits results to a 1-year window around
    the release year.
    Returns (rating, "fsk") or (None, None).
    Rating values: '0', '6', '12', '16', '18'.
    """
    session = _get_session()

    if media_type_name == "tvshow":
        super_type = "serial"
        type_options = {"serialOptions[]": "TVSR"}
    else:
        super_type = "single"
        type_options = {"singleOptions[]": "SP"}

    params = {
        "searchLayout": "full",
        "searchTitle": title,
        "superType": super_type,
        "sort": "__ratingReleaseDateTc",
    }
    params.update(type_options)

    if year > 0:
        params["ratingReleaseDateFrom"] = "{}-01-01".format(year - 1)
        params["ratingReleaseDateTo"] = "{}-12-31".format(year + 1)

    try:
        resp = session.get(FSK_API_URL, params=params, timeout=10)
    except requests.RequestException as e:
        log.warning("Request failed", event="fsk.error", title=title, error=str(e))
        return None, None

    if resp.status_code != 200:
        log.warning("Unexpected status", event="fsk.error",
                    title=title, status=resp.status_code)
        return None, None

    try:
        data = resp.json()
    except ValueError:
        log.warning("Invalid JSON response", event="fsk.error", title=title)
        return None, None

    if not data.get("success"):
        log.debug("API returned success=false", title=title)
        return None, None

    docs = data.get("data", {}).get("docs", [])
    if not docs:
        log.debug("No results", title=title)
        return None, None

    # Try IMDB ID match first
    if imdb_id:
        for doc in docs:
            if imdb_id in _extract_imdb_ids(doc):
                rating = str(doc.get("__rating", ""))
                if rating in ("0", "6", "12", "16", "18"):
                    log.debug("IMDB match", title=title,
                              imdb_id=imdb_id, rating=rating)
                    return rating, "fsk"

    # Fall back to title match
    for doc in docs:
        if _title_matches(doc, title):
            rating = str(doc.get("__rating", ""))
            if rating in ("0", "6", "12", "16", "18"):
                log.debug("Title match", title=title, rating=rating)
                return rating, "fsk"

    log.debug("No matching doc", title=title, result_count=len(docs))
    return None, None
