"""Tests for backfill tier ordering and inference chain logic."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from resources.lib.data.backfill import (
    _try_native_scraper,
    _try_inference_chain,
    _map_native_rating,
)


class TestTryNativeScraper:
    @patch("resources.lib.data.backfill.time")
    def test_calls_matching_scraper(self, mock_time):
        with patch("resources.lib.data.backfill._SCRAPER_BY_COUNTRY") as by_country:
            module = MagicMock()
            module.lookup.return_value = ("12", "fsk")
            by_country.get = lambda c: ("fsk", module) if c == "DE" else None

            rating, source = _try_native_scraper(
                "Test Movie", 0.25, "tt123", "movie", 2024, "DE", {"fsk"},
            )
            assert rating == "12"
            assert source == "fsk"

    @patch("resources.lib.data.backfill.time")
    def test_no_scraper_for_country(self, mock_time):
        rating, source = _try_native_scraper(
            "Test Movie", 0.25, None, "movie", 2024, "US", {"fsk"},
        )
        assert rating is None
        assert source is None

    @patch("resources.lib.data.backfill.time")
    def test_scraper_not_enabled(self, mock_time):
        rating, source = _try_native_scraper(
            "Test Movie", 0.25, "tt123", "movie", 2024, "DE", set(),
        )
        assert rating is None
        assert source is None

    @patch("resources.lib.data.backfill.time")
    def test_be_tries_nl_scraper(self, mock_time):
        with patch("resources.lib.data.backfill._SCRAPER_BY_COUNTRY") as by_country:
            module = MagicMock()
            module.lookup.return_value = ("12", "kijkwijzer")
            by_country.get = lambda c: ("kijkwijzer", module) if c == "NL" else None

            rating, source = _try_native_scraper(
                "Test Movie", 0.25, None, "movie", 2024, "BE", {"kijkwijzer"},
            )
            assert rating == "12"
            assert source == "kijkwijzer"


class TestTryInferenceChain:
    @patch("resources.lib.data.backfill.time")
    def test_tmdb_cert_mapped_successfully(self, mock_time):
        tmdb_certs = {"DE": "12", "GB": "15"}
        mappings = {"DE": {"12": "12"}, "GB": {"15": "16"}}

        rating, source = _try_inference_chain(
            ["DE", "GB"], tmdb_certs,
            "Test Movie", 0.25, None, "movie", 2024, "NL", mappings, set(),
        )
        assert rating == "12"
        assert source == "tmdb-inferred-DE"

    @patch("resources.lib.data.backfill.time")
    def test_tmdb_cert_unmappable_skips_scraper(self, mock_time):
        tmdb_certs = {"DE": "99"}
        mappings = {"DE": {}}

        with patch("resources.lib.data.backfill._SCRAPER_BY_COUNTRY") as by_country:
            fsk_module = MagicMock()
            by_country.get = lambda c: ("fsk", fsk_module) if c == "DE" else None

            rating, source = _try_inference_chain(
                ["DE"], tmdb_certs,
                "Test Movie", 0.25, "tt123", "movie", 2024, "NL", mappings, {"fsk"},
            )
            assert rating is None
            fsk_module.lookup.assert_not_called()

    @patch("resources.lib.data.backfill.time")
    def test_no_tmdb_cert_tries_scraper(self, mock_time):
        tmdb_certs = {"GB": "15"}
        mappings = {"DE": {"12": "12"}, "GB": {"15": "16"}}

        with patch("resources.lib.data.backfill._SCRAPER_BY_COUNTRY") as by_country:
            fsk_module = MagicMock()
            fsk_module.lookup.return_value = ("12", "fsk")
            by_country.get = lambda c: ("fsk", fsk_module) if c == "DE" else None

            rating, source = _try_inference_chain(
                ["DE", "GB"], tmdb_certs,
                "Test Movie", 0.25, "tt123", "movie", 2024, "NL", mappings, {"fsk"},
            )
            assert rating == "12"
            assert source == "fsk"

    @patch("resources.lib.data.backfill.time")
    def test_scraper_disabled_falls_through_to_tmdb(self, mock_time):
        tmdb_certs = {"GB": "15"}
        mappings = {"DE": {"12": "12"}, "GB": {"15": "16"}}

        rating, source = _try_inference_chain(
            ["DE", "GB"], tmdb_certs,
            "Test Movie", 0.25, "tt123", "movie", 2024, "NL", mappings, set(),
        )
        assert rating == "16"
        assert source == "tmdb-inferred-GB"

    @patch("resources.lib.data.backfill.time")
    def test_no_tmdb_certs_at_all(self, mock_time):
        mappings = {"DE": {"12": "12"}}

        with patch("resources.lib.data.backfill._SCRAPER_BY_COUNTRY") as by_country:
            fsk_module = MagicMock()
            fsk_module.lookup.return_value = ("12", "fsk")
            by_country.get = lambda c: ("fsk", fsk_module) if c == "DE" else None

            rating, source = _try_inference_chain(
                ["DE"], None,
                "Test Movie", 0.25, "tt123", "movie", 2024, "NL", mappings, {"fsk"},
            )
            assert rating == "12"
            assert source == "fsk"

    @patch("resources.lib.data.backfill.time")
    def test_empty_inference_chain(self, mock_time):
        rating, source = _try_inference_chain(
            [], {"DE": "12"},
            "Test Movie", 0.25, None, "movie", 2024, "NL", {}, set(),
        )
        assert rating is None
        assert source is None

    @patch("resources.lib.data.backfill.time")
    def test_fsk_receives_imdb_id(self, mock_time):
        with patch("resources.lib.data.backfill._SCRAPER_BY_COUNTRY") as by_country:
            fsk_module = MagicMock()
            fsk_module.lookup.return_value = (None, None)
            by_country.get = lambda c: ("fsk", fsk_module) if c == "DE" else None

            _try_inference_chain(
                ["DE"], None,
                "Test Movie", 0.25, "tt123", "movie", 2024, "NL",
                {"DE": {"12": "12"}}, {"fsk"},
            )
            call_kwargs = fsk_module.lookup.call_args
            assert call_kwargs[1]["imdb_id"] == "tt123"


class TestMapNativeRating:
    def test_same_country_returns_unchanged(self):
        assert _map_native_rating("12", "DE", "DE", {}) == "12"

    def test_be_accepts_nl_unchanged(self):
        assert _map_native_rating("AL", "NL", "BE", {}) == "AL"

    def test_foreign_rating_mapped(self):
        mappings = {"DE": {"12": "12", "16": "16"}}
        assert _map_native_rating("12", "DE", "NL", mappings) == "12"

    def test_unmappable_returns_none(self):
        mappings = {"DE": {"12": "12"}}
        assert _map_native_rating("99", "DE", "NL", mappings) is None
