"""Tests for CertMonitor debounce logic."""
from __future__ import annotations

import time


class TestCertMonitor:
    def _make_monitor(self):
        from resources.lib.service.daemon import CertMonitor
        return CertMonitor()

    def test_no_pending_scan_initially(self):
        monitor = self._make_monitor()
        assert monitor.has_pending_scan(60) is False

    def test_scan_requested_after_video_scan_finished(self):
        monitor = self._make_monitor()
        monitor.onScanFinished("video")
        assert monitor._scan_requested is True

    def test_ignores_music_scan(self):
        monitor = self._make_monitor()
        monitor.onScanFinished("music")
        assert monitor._scan_requested is False

    def test_debounce_blocks_immediate_trigger(self):
        monitor = self._make_monitor()
        monitor.onScanFinished("video")
        assert monitor.has_pending_scan(60) is False

    def test_debounce_allows_after_delay(self):
        monitor = self._make_monitor()
        monitor.onScanFinished("video")
        monitor._last_scan_event = time.time() - 61
        assert monitor.has_pending_scan(60) is True

    def test_clear_resets_flag(self):
        monitor = self._make_monitor()
        monitor.onScanFinished("video")
        monitor._last_scan_event = time.time() - 61
        assert monitor.has_pending_scan(60) is True
        monitor.clear_scan_request()
        assert monitor.has_pending_scan(60) is False

    def test_clean_finished_also_triggers(self):
        monitor = self._make_monitor()
        monitor.onCleanFinished("video")
        assert monitor._scan_requested is True

    def test_rapid_events_reset_debounce(self):
        monitor = self._make_monitor()
        monitor.onScanFinished("video")
        first_event = monitor._last_scan_event
        monitor.onScanFinished("video")
        assert monitor._last_scan_event >= first_event
