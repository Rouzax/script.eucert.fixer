"""
Background service daemon for Kijkwijzer Ratings.

Runs a periodic scan loop that checks for missing ratings and fills them.
Respects Kodi abort requests for clean shutdown.

Logging:
    Logger: 'service'
    Key events:
        - service.start (INFO): Daemon started
        - service.stop (INFO): Daemon shutting down
        - service.scan_trigger (INFO): Scan cycle starting
        - service.scan_complete (INFO): Scan cycle finished
        - service.scan_error (ERROR): Scan cycle failed
"""
from __future__ import annotations

import time

import xbmc

from resources.lib.constants import (
    DEFAULT_SCAN_INTERVAL_HOURS,
    SERVICE_SLEEP_INTERVAL_SEC,
)
from resources.lib.utils import StructuredLogger, get_logger, get_int_setting, log_timing
from resources.lib.data.backfill import backfill
from resources.lib.data.media_types import MOVIE, TVSHOW


log = get_logger('service')


def run() -> None:
    """Main service entry point. Blocks until Kodi requests abort."""
    monitor = xbmc.Monitor()

    log.info("Service started", event="service.start")

    last_scan: float = 0.0

    try:
        while not monitor.abortRequested():
            interval_hours = get_int_setting('scan_interval', DEFAULT_SCAN_INTERVAL_HOURS)
            interval_sec = interval_hours * 3600

            now = time.time()
            if now - last_scan >= interval_sec:
                _run_scan()
                last_scan = time.time()

            if monitor.waitForAbort(SERVICE_SLEEP_INTERVAL_SEC):
                break
    finally:
        log.info("Service stopping", event="service.stop")
        StructuredLogger.shutdown()


def _run_scan() -> None:
    """Execute a single scan cycle across all media types."""
    log.info("Scan cycle starting", event="service.scan_trigger")

    try:
        with log_timing(log, "scan_cycle") as timer:
            media_types = [MOVIE, TVSHOW]
            total_set = 0

            for media_type in media_types:
                stats = backfill(media_type)
                count = (
                    stats.get("tmdb_direct", 0) +
                    stats.get("tmdb_inferred", 0) +
                    stats.get("omdb", 0) +
                    stats.get("kijkwijzer", 0) +
                    stats.get("fallback", 0)
                )
                total_set += count
                timer.mark(media_type.name)

        log.info("Scan cycle complete", event="service.scan_complete",
                 ratings_set=total_set)
    except Exception:
        log.exception("Scan cycle failed", event="service.scan_error")
