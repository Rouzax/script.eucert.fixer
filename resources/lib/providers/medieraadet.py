"""
Medieradet (Denmark) provider for rating lookups.

Queries the Danish Media Council's film rating API by title, then
fetches the detail page for the assessment code.

Logging:
    Logger: 'medieraadet'
    Key events:
        - medieraadet.match (DEBUG): Rating found
        - medieraadet.no_results (DEBUG): Search returned no results
        - medieraadet.no_title_match (DEBUG): No matching title in results
        - medieraadet.error (WARNING): Request failed
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

import requests

from resources.lib.utils import get_logger, title_matches

log = get_logger('medieraadet')

_API_BASE = (
    "https://appfilmvurderinger.silver.extension.gopublic.dk"
    "/api/93c1d303-ae9e-44b1-b939-fb91ba32200a"
)

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:151.0) "
    "Gecko/20100101 Firefox/151.0"
)

_CODE_TO_RATING = {
    "tfa": "A",
    "fr.u7": "7",
    "to7": "7",
    "to11": "11",
    "to15": "15",
}

_ARTICLE_RE = re.compile(r'^(?:the|a|an|der|die|das|den|det|de|le|la|les|el|los|las)\s+', re.IGNORECASE)

_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    """Get a reusable requests session."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers["User-Agent"] = _BROWSER_UA
        _session.headers["Accept"] = "application/json"
    return _session


def _strip_article(title: str) -> str:
    """Strip leading articles for search (the API uses prefix matching)."""
    return _ARTICLE_RE.sub("", title)


def _title_matches(film_detail: Dict[str, Any], title: str) -> bool:
    """Check if a film's title matches (accent-aware, ignoring articles)."""
    stripped = _strip_article(title)
    for key in ("Title", "OriginalTitle", "DanishTitle"):
        val = film_detail.get(key, "")
        if not val:
            continue
        if title_matches(val, title) or title_matches(val, stripped):
            return True
        val_stripped = _strip_article(val)
        if title_matches(val_stripped, title) or title_matches(val_stripped, stripped):
            return True
    return False


def _search(session: requests.Session, title: str) -> List[Dict[str, Any]]:
    """Search for films by title, trying with and without leading articles."""
    queries = [title]
    stripped = _strip_article(title)
    if stripped != title:
        queries.append(stripped)

    for query in queries:
        try:
            resp = session.get(
                "{}/film".format(_API_BASE),
                params={
                    "Title": query,
                    "Sortby": "assessmentreleasedate",
                    "Take": "10",
                    "Skip": "0",
                },
                timeout=10,
            )
        except requests.RequestException as e:
            log.warning("Search failed", event="medieraadet.error",
                        title=title, error=str(e))
            return []

        if resp.status_code != 200:
            log.warning("Unexpected status", event="medieraadet.error",
                        title=title, status=resp.status_code)
            return []

        try:
            data = resp.json()
        except ValueError:
            log.warning("Invalid JSON", event="medieraadet.error", title=title)
            return []

        films = data.get("FilmList") or []
        if films:
            return films

    return []


def _get_detail(session: requests.Session, film_id: int) -> Optional[Dict[str, Any]]:
    """Fetch full detail for a film by ID."""
    try:
        resp = session.get(
            "{}/film/{}".format(_API_BASE, film_id),
            timeout=10,
        )
    except requests.RequestException:
        return None

    if resp.status_code != 200:
        return None

    try:
        return resp.json()
    except ValueError:
        return None


def lookup(
    title: str,
    rate_limit: float = 0.25,
    media_type_name: str = "movie",
    year: int = 0,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Search the Danish Media Council API by title.

    Returns (rating, "medieraadet") or (None, None).
    Rating values: 'A', '7', '11', '15'.
    """
    session = _get_session()

    films = _search(session, title)
    if not films:
        log.debug("No results", title=title)
        return None, None

    for film in films:
        film_id = film.get("Id")
        if not film_id:
            continue

        if year > 0 and abs(film.get("ReleaseYear", 0) - year) > 1:
            continue

        detail = _get_detail(session, film_id)
        if not detail:
            continue

        if not _title_matches(detail, title):
            continue

        code = detail.get("AssesmentCode")
        if not code:
            continue

        rating = _CODE_TO_RATING.get(code)
        if rating:
            log.debug("Match found", title=title,
                       film_title=detail.get("Title", ""),
                       code=code, rating=rating,
                       result_count=len(films))
            return rating, "medieraadet"

    log.debug("No title match", title=title, result_count=len(films))
    return None, None
