"""
Kijkwijzer.nl scraping provider.

Searches the Dutch rating authority's website by title, then scrapes
the detail page for the age rating.

Logging:
    Logger: 'kijkwijzer_provider'
    Key events:
        - kijkwijzer.match (DEBUG): Rating found on detail page
        - kijkwijzer.no_results (DEBUG): Search returned no results
        - kijkwijzer.no_title_match (DEBUG): No matching title in results
        - kijkwijzer.error (WARNING): Request failed
"""
from __future__ import annotations

import re
import time
from typing import Optional, Tuple

import requests

from resources.lib.constants import KIJKWIJZER_SEARCH_URL, KIJKWIJZER_USER_AGENT
from resources.lib.utils import get_logger

log = get_logger('kijkwijzer_provider')

_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    """Get a reusable requests session."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers["User-Agent"] = KIJKWIJZER_USER_AGENT
    return _session


def lookup(title: str, rate_limit: float = 0.25) -> Tuple[Optional[str], Optional[str]]:
    """
    Search kijkwijzer.nl by title, scrape the detail page for age rating.

    Returns (rating, "kijkwijzer") or (None, None).
    Rating values: 'AL', '6', '9', '12', '14', '16', '18'.
    """
    session = _get_session()

    try:
        resp = session.get(
            KIJKWIJZER_SEARCH_URL,
            params={"query": title, "producties": "0"},
            timeout=10,
        )
        if resp.status_code != 200:
            log.warning("Search returned unexpected status",
                        event="kijkwijzer.error", status=resp.status_code)
            return None, None
    except requests.RequestException as e:
        log.warning("Search failed", event="kijkwijzer.error", error=str(e))
        return None, None

    # Extract film/series links from search results
    links = re.findall(
        r'href="(https://www\.kijkwijzer\.nl/(?:films|series|overige)/[^"]+/)"',
        resp.text,
    )
    if not links:
        log.debug("No search results", title=title)
        return None, None

    # Find best title match from links
    title_lower = title.lower().strip()
    title_slug = re.sub(r"[^a-z0-9]+", "-", title_lower).strip("-")

    best_link = None
    for link in links:
        slug_match = re.search(r"/([^/]+)/$", link)
        if not slug_match:
            continue
        slug = slug_match.group(1)
        slug_base = re.sub(r"-\d+$", "", slug)
        if slug == title_slug or slug_base == title_slug:
            best_link = link
            break
        if slug.startswith(title_slug):
            best_link = link
            break
        if title_slug.startswith(slug_base) and len(slug_base) >= len(title_slug) * 0.6:
            best_link = link
            break

    if not best_link:
        log.debug("No title match", title=title, slug=title_slug)
        return None, None

    log.debug("Title matched", title=title, url=best_link)
    time.sleep(rate_limit)

    # Fetch detail page
    try:
        detail_resp = session.get(best_link, timeout=10)
        if detail_resp.status_code != 200:
            return None, None
    except requests.RequestException:
        return None, None

    detail_text = detail_resp.text

    # Parse rating from detail page
    age_match = re.search(r"schadelijk tot (\d+) jaar", detail_text)
    if age_match:
        age = age_match.group(1)
        if age in ("6", "9", "12", "14", "16", "18"):
            return age, "kijkwijzer"

    # "Alle leeftijden" in heading context
    if re.search(r"<h[12][^>]*>.*?Alle leeftijden", detail_text, re.DOTALL):
        return "AL", "kijkwijzer"
    if detail_text.count("Alle leeftijden") >= 2:
        return "AL", "kijkwijzer"

    log.debug("Could not parse rating from detail page", url=best_link)
    return None, None
