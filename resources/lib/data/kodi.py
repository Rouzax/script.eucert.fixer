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

from typing import Any, Dict, List

from resources.lib.data.media_types import MediaType
from resources.lib.utils import get_logger, json_query

log = get_logger('data')


def get_missing_ratings(media_type: MediaType) -> List[Dict[str, Any]]:
    """
    Query Kodi library for items with empty mpaa field.

    Returns a list of dicts with keys: id, title, tmdb_id, imdb_id.
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

    missing = []
    for item in all_items:
        if not item.get("mpaa"):
            missing.append({
                "id": item[media_type.kodi_id_field],
                "title": item.get("title", ""),
                "tmdb_id": item.get("uniqueid", {}).get("tmdb"),
                "imdb_id": item.get("uniqueid", {}).get("imdb"),
            })

    log.debug("Items with missing ratings",
              media_type=media_type.name, count=len(missing))

    return missing


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
