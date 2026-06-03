"""
Kodi JSON-RPC communication for rating queries and updates.

Uses xbmc.executeJSONRPC() for internal communication (no HTTP needed).

Logging:
    Logger: 'data'
    Key events:
        - data.query (DEBUG): Library query executed
        - data.update (INFO): Rating written to library
        - data.update_fail (WARNING): Failed to write rating
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

from resources.lib.constants import KNOWN_RATING_PREFIXES, VALID_RATINGS
from resources.lib.data.media_types import MediaType
from resources.lib.utils import get_logger, json_query

log = get_logger('data')

_COUNTRY_PREFIX_RE = re.compile(r'^[A-Z]{2,3}:')


def _strip_rating_prefix(mpaa: str) -> str:
    """Strip known prefixes to extract the bare rating value."""
    if not mpaa:
        return ""
    match = _COUNTRY_PREFIX_RE.match(mpaa)
    if match:
        return mpaa[match.end():]
    for prefix in KNOWN_RATING_PREFIXES:
        if mpaa.startswith(prefix):
            return mpaa[len(prefix):]
    return mpaa


def _needs_rating(mpaa: str, replace_incorrect: bool, fallback_rating: str) -> bool:
    """Check whether an item's mpaa value needs a Kijkwijzer rating."""
    if not mpaa:
        return True
    if not replace_incorrect:
        return False
    bare = _strip_rating_prefix(mpaa)
    if bare in VALID_RATINGS:
        return False
    if fallback_rating and bare == fallback_rating:
        return False
    log.debug("Flagged for replacement", mpaa=mpaa, stripped=bare)
    return True


def get_items_needing_ratings(
    media_type: MediaType,
    replace_incorrect: bool = False,
    fallback_rating: str = "",
) -> List[Dict[str, Any]]:
    """
    Query Kodi library for items needing a Kijkwijzer rating.

    When replace_incorrect is False, only items with empty mpaa are returned.
    When True, items with non-Kijkwijzer ratings (e.g. US ratings like R,
    PG-13, TV-MA) are also included.

    Returns a list of dicts: id, title, tmdb_id, imdb_id, tvdb_id.
    """
    query = {
        "jsonrpc": "2.0",
        "method": media_type.kodi_list_method,
        "params": {
            "properties": ["mpaa", "uniqueid", "title"],
            "sort": {"method": "title"},
        },
        "id": 1,
    }

    result = json_query(query)
    all_items = result.get(media_type.kodi_result_key, [])

    log.debug("Library query returned items",
              media_type=media_type.name, total=len(all_items))

    candidates = []
    for item in all_items:
        mpaa = item.get("mpaa", "")
        if _needs_rating(mpaa, replace_incorrect, fallback_rating):
            uniqueid = item.get("uniqueid", {})
            candidates.append({
                "id": item[media_type.kodi_id_field],
                "title": item.get("title", ""),
                "tmdb_id": uniqueid.get("tmdb"),
                "imdb_id": uniqueid.get("imdb"),
                "tvdb_id": uniqueid.get("tvdb"),
            })

    log.debug("Items needing ratings",
              media_type=media_type.name, count=len(candidates),
              replace_incorrect=replace_incorrect)

    return candidates


def update_rating(
    item_id: int,
    rating_value: str,
    media_type: MediaType,
) -> bool:
    """
    Set the mpaa field for an item via JSON-RPC.

    Returns True on success, False on failure.
    """
    query = {
        "jsonrpc": "2.0",
        "method": media_type.kodi_set_method,
        "params": {
            media_type.kodi_id_field: item_id,
            "mpaa": rating_value,
        },
        "id": 1,
    }

    result = json_query(query, return_result=False)
    success = result.get("result") == "OK"

    if success:
        log.info("Rating set", event="data.update",
                 media_type=media_type.name, item_id=item_id,
                 rating=rating_value)
    else:
        log.warning("Failed to set rating", event="data.update_fail",
                    media_type=media_type.name, item_id=item_id,
                    response=str(result))

    return success
