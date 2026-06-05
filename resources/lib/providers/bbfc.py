"""
BBFC (UK) provider for rating lookups.

Searches the BBFC website and parses __NEXT_DATA__ JSON for
classifications.

Logging:
    Logger: 'bbfc'
    Key events:
        - bbfc.match (DEBUG): Classification found
        - bbfc.no_results (DEBUG): Search returned no results
        - bbfc.no_title_match (DEBUG): No matching title in results
        - bbfc.parse_error (WARNING): Failed to parse __NEXT_DATA__
        - bbfc.error (WARNING): Request failed
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

import requests

from resources.lib.constants import BBFC_SEARCH_URL
from resources.lib.utils import get_logger, title_matches

log = get_logger('bbfc')

_session: Optional[requests.Session] = None

_NEXT_DATA_RE = re.compile(
    r'<script\s+id="__NEXT_DATA__"[^>]*>(.*?)</script>',
    re.DOTALL,
)

_VALID_CLASSIFICATIONS = frozenset({"U", "PG", "12", "12A", "15", "18", "R18"})

_YEAR_SUFFIX_RE = re.compile(r'\s*\(\d{4}\)\s*$')

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


def _get_session() -> requests.Session:
    """Get a reusable requests session."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers["User-Agent"] = _BROWSER_UA
    return _session


def _parse_next_data(html: str) -> List[Dict[str, Any]]:
    """Extract search results from __NEXT_DATA__ script tag."""
    match = _NEXT_DATA_RE.search(html)
    if not match:
        return []

    try:
        data = json.loads(match.group(1))
    except (json.JSONDecodeError, ValueError):
        return []

    try:
        return data["props"]["pageProps"]["searchResults"]["results"]
    except (KeyError, TypeError):
        return []


def _media_type_filter(result: Dict[str, Any], media_type_name: str) -> bool:
    """Check if a result matches the desired media type."""
    result_type = result.get("type", "").lower()
    if media_type_name == "tvshow":
        return "tv" in result_type
    return "film" in result_type


def _extract_year(title_with_year: str) -> int:
    """Extract year from a BBFC title like 'The Matrix (1999)'."""
    m = re.search(r'\((\d{4})\)\s*$', title_with_year)
    return int(m.group(1)) if m else 0


def lookup(
    title: str,
    rate_limit: float = 0.25,
    media_type_name: str = "movie",
    year: int = 0,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Search the BBFC website by title.

    When year is provided, prefers results matching that year.
    Returns (classification, "bbfc") or (None, None).
    Classification values: 'U', 'PG', '12', '12A', '15', '18', 'R18'.
    """
    session = _get_session()

    type_filter = "TV Show" if media_type_name == "tvshow" else "Film"

    try:
        resp = session.get(
            BBFC_SEARCH_URL,
            params={"q": title, "t[]": type_filter},
            timeout=10,
        )
    except requests.RequestException as e:
        log.warning("Request failed", event="bbfc.error", title=title, error=str(e))
        return None, None

    if resp.status_code != 200:
        log.warning("Unexpected status", event="bbfc.error",
                    title=title, status=resp.status_code)
        return None, None

    results = _parse_next_data(resp.text)
    if not results:
        log.debug("No results", title=title)
        return None, None

    best_match = None
    for result in results:
        if not _media_type_filter(result, media_type_name):
            continue

        result_title = result.get("title", "")
        result_bare = _YEAR_SUFFIX_RE.sub("", result_title).strip()
        if not title_matches(result_bare, title):
            continue

        classification = result.get("classification", "")
        if classification not in _VALID_CLASSIFICATIONS:
            continue

        result_year = _extract_year(result_title)

        if year > 0 and result_year > 0 and abs(result_year - year) <= 1:
            log.debug("Match found", title=title,
                      classification=classification, year=result_year,
                      result_count=len(results))
            return classification, "bbfc"

        if best_match is None:
            best_match = (classification, result_title)

    if best_match:
        log.debug("Match found", title=title, classification=best_match[0],
                  result_count=len(results))
        return best_match[0], "bbfc"

    log.debug("No title match", title=title, result_count=len(results))
    return None, None
