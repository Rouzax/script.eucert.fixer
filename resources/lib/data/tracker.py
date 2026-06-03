"""
Unresolved items tracker.

Tracks items that no provider could resolve, with a retry window
before applying the fallback rating. Tracker files are stored in
addon_data per media type.

Logging:
    Logger: 'tracker'
    Key events:
        - tracker.new (DEBUG): New unresolved item tracked
        - tracker.expired (DEBUG): Retry window expired for item
        - tracker.save (DEBUG): Tracker file saved
        - tracker.save_fail (WARNING): Failed to save tracker file
"""
from __future__ import annotations

import json
import os
from datetime import date
from typing import Any, Dict

import xbmcaddon
import xbmcvfs

from resources.lib.constants import DEFAULT_ADDON_ID, TRACKER_DIR
from resources.lib.utils import get_logger

log = get_logger('tracker')


def _get_tracker_dir() -> str:
    """Get the tracker directory path, creating it if needed."""
    try:
        addon = xbmcaddon.Addon()
        addon_id = addon.getAddonInfo('id')
    except RuntimeError:
        addon_id = DEFAULT_ADDON_ID

    tracker_dir = xbmcvfs.translatePath(
        "special://profile/addon_data/{}/{}/".format(addon_id, TRACKER_DIR)
    )
    if not xbmcvfs.exists(tracker_dir):
        xbmcvfs.mkdirs(tracker_dir)
    return tracker_dir


def load_tracker(filename: str) -> Dict[str, Any]:
    """Load unresolved tracker from JSON. Returns dict of title -> metadata."""
    path = os.path.join(_get_tracker_dir(), filename)
    try:
        if not xbmcvfs.exists(path):
            return {}
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_tracker(filename: str, data: Dict[str, Any]) -> None:
    """Save unresolved tracker to JSON."""
    path = os.path.join(_get_tracker_dir(), filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        log.debug("Tracker saved", filename=filename, count=len(data))
    except OSError as e:
        log.warning("Failed to save tracker", event="tracker.save_fail",
                    filename=filename, error=str(e))


def should_apply_fallback(
    title: str,
    unresolved: Dict[str, Any],
    retry_days: int,
) -> bool:
    """
    Check if an item has been unresolved long enough for fallback.

    Also adds the item to the tracker if not yet tracked.

    Returns True if fallback should be applied.
    """
    today = date.today().isoformat()

    if title not in unresolved:
        unresolved[title] = {"first_seen": today}
        log.debug("Tracking new unresolved item", title=title)
        return False

    try:
        first_seen = date.fromisoformat(unresolved[title]["first_seen"])
    except (KeyError, ValueError):
        unresolved[title] = {"first_seen": today}
        log.warning("Reset corrupt tracker entry", event="tracker.reset",
                    title=title)
        return False

    days_elapsed = (date.today() - first_seen).days

    if days_elapsed >= retry_days:
        log.debug("Retry window expired", title=title,
                  days_elapsed=days_elapsed)
        return True

    log.debug("Still in retry window", title=title,
              days_elapsed=days_elapsed, retry_days=retry_days)
    return False
