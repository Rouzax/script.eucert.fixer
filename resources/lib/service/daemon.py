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
    LIBRARY_SCAN_DEBOUNCE_SEC,
    SERVICE_SLEEP_INTERVAL_SEC,
)
from resources.lib.utils import (
    StructuredLogger, get_bool_setting, get_logger, get_int_setting,
    log_timing, notify,
)
from resources.lib.data.backfill import backfill
from resources.lib.data.media_types import MOVIE, TVSHOW


log = get_logger('service')


class KijkwijzerMonitor(xbmc.Monitor):
    """Monitor subclass that tracks library scan/clean events."""

    def __init__(self) -> None:
        super().__init__()
        self._scan_requested: bool = False
        self._last_scan_event: float = 0.0

    def onScanFinished(self, library: str) -> None:
        if library == "video":
            self._scan_requested = True
            self._last_scan_event = time.time()
            log.info("Library scan finished, rating scan queued",
                     event="service.library_scan_finished")

    def onCleanFinished(self, library: str) -> None:
        if library == "video":
            self._scan_requested = True
            self._last_scan_event = time.time()
            log.info("Library clean finished, rating scan queued",
                     event="service.library_clean_finished")

    def has_pending_scan(self, debounce_sec: float) -> bool:
        """Check if a library-triggered scan is pending and debounce has elapsed."""
        if not self._scan_requested:
            return False
        return (time.time() - self._last_scan_event) >= debounce_sec

    def clear_scan_request(self) -> None:
        """Clear the pending scan flag after a scan runs."""
        self._scan_requested = False


def run() -> None:
    """Main service entry point. Blocks until Kodi requests abort."""
    monitor = KijkwijzerMonitor()

    log.info("Service started", event="service.start")

    last_scan: float = 0.0

    try:
        while not monitor.abortRequested():
            should_scan = False
            now = time.time()

            # Periodic / startup trigger
            interval_hours = get_int_setting('scan_interval', DEFAULT_SCAN_INTERVAL_HOURS)
            interval_sec = interval_hours * 3600
            if now - last_scan >= interval_sec:
                should_scan = True

            # Library event trigger (with debounce)
            if monitor.has_pending_scan(LIBRARY_SCAN_DEBOUNCE_SEC):
                should_scan = True

            # Guard: don't scan while library is updating
            if should_scan and not xbmc.getCondVisibility('Library.IsScanningVideo'):
                total = _run_scan()
                last_scan = time.time()
                monitor.clear_scan_request()
                if total > 0 and get_bool_setting('show_notifications'):
                    notify("Set {} rating{}".format(
                        total, "s" if total != 1 else ""))

            if monitor.waitForAbort(SERVICE_SLEEP_INTERVAL_SEC):
                break
    finally:
        log.info("Service stopping", event="service.stop")
        StructuredLogger.shutdown()


def _run_scan() -> int:
    """Execute a single scan cycle across all media types. Returns total ratings set."""
    log.info("Scan cycle starting", event="service.scan_trigger")

    total_set = 0
    try:
        with log_timing(log, "scan_cycle") as timer:
            media_types = [MOVIE, TVSHOW]

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

    return total_set
