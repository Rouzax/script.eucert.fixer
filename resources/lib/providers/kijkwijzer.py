"""
Kijkwijzer.nl provider for rating lookups.

Uses the Umbraco AJAX search endpoint to find ratings directly from
search results (no detail page scraping needed). The rating is
embedded in CSS class names on the search result marks.

Logging:
    Logger: 'kijkwijzer_provider'
    Key events:
        - kijkwijzer.match (DEBUG): Rating found in search results
        - kijkwijzer.no_results (DEBUG): Search returned no results
        - kijkwijzer.no_title_match (DEBUG): No matching title in results
        - kijkwijzer.error (WARNING): Request failed
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

import requests

from resources.lib.constants import KIJKWIJZER_USER_AGENT
from resources.lib.utils import get_logger

log = get_logger('kijkwijzer_provider')

_SEARCH_URL = "https://www.kijkwijzer.nl/umbraco/surface/searchresults/search"

_SEARCH_HEADERS = {
    "X-UMB-CULTURE": "nl",
    "X-UMB-KEY": "a77f11d2-0e15-4f0f-9d06-eb7adaa48b4d",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.kijkwijzer.nl/",
}

_VALID_RATINGS = frozenset({"6", "9", "12", "14", "16", "18"})

_INVERTED_ARTICLE_RE = re.compile(r'^(.+),\s+(The|A|An|De|Het|Een)$', re.IGNORECASE)

_RESULT_RE = re.compile(
    r'<div\s+class="c-search__result">(.*?)(?=<div\s+class="c-search__result"|</div>\s*</div>\s*</div>)',
    re.DOTALL,
)
_TITLE_RE = re.compile(r'c-search__title[^>]*>(.*?)</h3>', re.DOTALL)
_META_RE = re.compile(r'c-search__text">\s*(.*?)\s*</p>', re.DOTALL)
_RATING_RE = re.compile(r'leeftijd-(\d+)')

_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    """Get a reusable requests session."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers["User-Agent"] = KIJKWIJZER_USER_AGENT
        _session.headers.update(_SEARCH_HEADERS)
        _session.cookies.set("PerplexCookieApproval", "2",
                             domain="www.kijkwijzer.nl")
    return _session


def _parse_results(html: str) -> List[Dict[str, Any]]:
    """Extract search results with title, type, year, and rating from HTML."""
    results = []
    for block in _RESULT_RE.findall(html):
        title_m = _TITLE_RE.search(block)
        if not title_m:
            continue
        title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()

        meta_m = _META_RE.search(block)
        meta_text = ""
        year = 0
        if meta_m:
            meta_text = re.sub(r'\s+', ' ', meta_m.group(1)).strip()
            year_m = re.search(r'\((\d{4})\)', meta_text)
            if year_m:
                year = int(year_m.group(1))

        rating_m = _RATING_RE.search(block)
        if rating_m:
            rating = rating_m.group(1)
        elif 'alle-leeftijden' in block:
            rating = "AL"
        else:
            rating = None

        results.append({
            "title": title,
            "year": year,
            "meta": meta_text,
            "rating": rating,
        })

    return results


def lookup(
    title: str,
    rate_limit: float = 0.25,
    media_type_name: str = "movie",
    year: int = 0,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Search kijkwijzer.nl by title using the AJAX search endpoint.

    Returns (rating, "kijkwijzer") or (None, None).
    Rating values: 'AL', '6', '9', '12', '14', '16', '18'.
    """
    session = _get_session()

    producties = "2" if media_type_name == "tvshow" else "1"

    try:
        resp = session.get(
            _SEARCH_URL,
            params={"query": title, "producties": producties, "amount": "10"},
            timeout=10,
        )
        if resp.status_code != 200:
            log.warning("Search returned unexpected status",
                        event="kijkwijzer.error", title=title,
                        status=resp.status_code)
            return None, None
    except requests.RequestException as e:
        log.warning("Search failed", event="kijkwijzer.error",
                    title=title, error=str(e))
        return None, None

    results = _parse_results(resp.text)
    if not results:
        log.debug("No results", title=title)
        return None, None

    title_lower = title.lower()

    for result in results:
        result_title = result["title"]
        inverted = _INVERTED_ARTICLE_RE.match(result_title)
        if inverted:
            result_title = "{} {}".format(inverted.group(2), inverted.group(1))
        result_lower = result_title.lower()
        if result_lower != title_lower and not result_lower.startswith(title_lower + " "):
            continue

        if year > 0 and result["year"] > 0 and abs(result["year"] - year) > 1:
            continue

        rating = result["rating"]
        if rating and (rating == "AL" or rating in _VALID_RATINGS):
            log.debug("Match found", title=title,
                      result_title=result["title"], rating=rating,
                      result_count=len(results))
            return rating, "kijkwijzer"

    log.debug("No title match", title=title, result_count=len(results))
    return None, None
