"""Tests for scraper canary checks and TLS adapter."""
from __future__ import annotations

import ssl
from unittest.mock import MagicMock, patch

from resources.lib.data.backfill import run_canaries


def _make_module(return_value=("12", "fsk"), side_effect=None):
    """Create a mock scraper module with a lookup method."""
    module = MagicMock()
    if side_effect:
        module.lookup.side_effect = side_effect
    else:
        module.lookup.return_value = return_value
    return module


# ---------------------------------------------------------------------------
# run_canaries: return value (which scrapers survive)
# ---------------------------------------------------------------------------


class TestCanaryPass:
    @patch("resources.lib.data.backfill.time")
    @patch("resources.lib.data.backfill.SCRAPER_CANARIES", {
        "fsk": {"title": "The Matrix", "expected": "16", "year": 1999},
    })
    def test_passed_scraper_stays_enabled(self, mock_time):
        module = _make_module(("16", "fsk"))
        with patch("resources.lib.data.backfill._SCRAPER_MODULES", {"fsk": module}):
            result = run_canaries({"fsk"}, 0.25)
        assert result == {"fsk"}

    @patch("resources.lib.data.backfill.time")
    @patch("resources.lib.data.backfill.SCRAPER_CANARIES", {
        "fsk": {"title": "The Matrix", "expected": "16", "year": 1999},
        "bbfc": {"title": "Interstellar", "expected": "12", "year": 2014},
    })
    def test_all_pass_all_survive(self, mock_time):
        fsk_mod = _make_module(("16", "fsk"))
        bbfc_mod = _make_module(("12", "bbfc"))
        modules = {"fsk": fsk_mod, "bbfc": bbfc_mod}
        with patch("resources.lib.data.backfill._SCRAPER_MODULES", modules):
            result = run_canaries({"fsk", "bbfc"}, 0.25)
        assert result == {"fsk", "bbfc"}


class TestCanaryMismatch:
    @patch("resources.lib.data.backfill.time")
    @patch("resources.lib.data.backfill.SCRAPER_CANARIES", {
        "bbfc": {"title": "Interstellar", "expected": "12", "year": 2014},
    })
    def test_wrong_rating_disables_scraper(self, mock_time):
        module = _make_module(("15", "bbfc"))
        with patch("resources.lib.data.backfill._SCRAPER_MODULES", {"bbfc": module}):
            result = run_canaries({"bbfc"}, 0.25)
        assert result == set()

    @patch("resources.lib.data.backfill.time")
    @patch("resources.lib.data.backfill.SCRAPER_CANARIES", {
        "fsk": {"title": "The Matrix", "expected": "16", "year": 1999},
        "bbfc": {"title": "Interstellar", "expected": "12", "year": 2014},
    })
    def test_one_mismatch_only_disables_that_scraper(self, mock_time):
        fsk_mod = _make_module(("16", "fsk"))
        bbfc_mod = _make_module(("15", "bbfc"))
        modules = {"fsk": fsk_mod, "bbfc": bbfc_mod}
        with patch("resources.lib.data.backfill._SCRAPER_MODULES", modules):
            result = run_canaries({"fsk", "bbfc"}, 0.25)
        assert result == {"fsk"}


class TestCanaryNoResult:
    @patch("resources.lib.data.backfill.time")
    @patch("resources.lib.data.backfill.SCRAPER_CANARIES", {
        "kijkwijzer": {"title": "Interstellar", "expected": "12", "year": 2014},
    })
    def test_none_result_disables_scraper(self, mock_time):
        module = _make_module((None, None))
        with patch("resources.lib.data.backfill._SCRAPER_MODULES", {"kijkwijzer": module}):
            result = run_canaries({"kijkwijzer"}, 0.25)
        assert result == set()


class TestCanaryError:
    @patch("resources.lib.data.backfill.time")
    @patch("resources.lib.data.backfill.SCRAPER_CANARIES", {
        "fsk": {"title": "The Matrix", "expected": "16", "year": 1999},
    })
    def test_exception_disables_scraper(self, mock_time):
        module = _make_module(side_effect=ConnectionError("timeout"))
        with patch("resources.lib.data.backfill._SCRAPER_MODULES", {"fsk": module}):
            result = run_canaries({"fsk"}, 0.25)
        assert result == set()


class TestCanarySkipsDisabledScrapers:
    @patch("resources.lib.data.backfill.time")
    @patch("resources.lib.data.backfill.SCRAPER_CANARIES", {
        "fsk": {"title": "The Matrix", "expected": "16", "year": 1999},
        "bbfc": {"title": "Interstellar", "expected": "12", "year": 2014},
    })
    def test_disabled_scraper_not_tested(self, mock_time):
        fsk_mod = _make_module(("16", "fsk"))
        bbfc_mod = _make_module(("15", "bbfc"))
        modules = {"fsk": fsk_mod, "bbfc": bbfc_mod}
        with patch("resources.lib.data.backfill._SCRAPER_MODULES", modules):
            result = run_canaries({"fsk"}, 0.25)
        assert result == {"fsk"}
        bbfc_mod.lookup.assert_not_called()


class TestCanaryPassesThrough:
    @patch("resources.lib.data.backfill.time")
    @patch("resources.lib.data.backfill.SCRAPER_CANARIES", {
        "fsk": {"title": "The Matrix", "expected": "16", "year": 1999},
    })
    def test_scraper_without_canary_passes_through(self, mock_time):
        fsk_mod = _make_module(("16", "fsk"))
        with patch("resources.lib.data.backfill._SCRAPER_MODULES", {"fsk": fsk_mod}):
            result = run_canaries({"fsk", "bbfc"}, 0.25)
        assert "bbfc" in result


class TestCanaryForwardsYear:
    @patch("resources.lib.data.backfill.time")
    @patch("resources.lib.data.backfill.SCRAPER_CANARIES", {
        "bbfc": {"title": "Interstellar", "expected": "12", "year": 2014},
    })
    def test_year_passed_to_lookup(self, mock_time):
        module = _make_module(("12", "bbfc"))
        with patch("resources.lib.data.backfill._SCRAPER_MODULES", {"bbfc": module}):
            run_canaries({"bbfc"}, 0.25)
        module.lookup.assert_called_once_with(
            "Interstellar", 0.25, media_type_name="movie", year=2014,
        )

    @patch("resources.lib.data.backfill.time")
    @patch("resources.lib.data.backfill.SCRAPER_CANARIES", {
        "test": {"title": "SomeMovie", "expected": "PG"},
    })
    def test_no_year_omits_kwarg(self, mock_time):
        module = _make_module(("PG", "test"))
        with patch("resources.lib.data.backfill._SCRAPER_MODULES", {"test": module}):
            run_canaries({"test"}, 0.5)
        module.lookup.assert_called_once_with(
            "SomeMovie", 0.5, media_type_name="movie",
        )


# ---------------------------------------------------------------------------
# Canary results flow into backfill (integration with daemon)
# ---------------------------------------------------------------------------


class TestCanaryDisablesPreventsRating:
    @patch("resources.lib.data.backfill.time")
    @patch("resources.lib.data.backfill.SCRAPER_CANARIES", {
        "fsk": {"title": "The Matrix", "expected": "16", "year": 1999},
        "bbfc": {"title": "Interstellar", "expected": "12", "year": 2014},
        "kijkwijzer": {"title": "Interstellar", "expected": "12", "year": 2014},
    })
    def test_mixed_canary_results(self, mock_time):
        fsk_mod = _make_module(("16", "fsk"))
        bbfc_mod = _make_module(("15", "bbfc"))
        kw_mod = _make_module(side_effect=ConnectionError("blocked"))
        modules = {"fsk": fsk_mod, "bbfc": bbfc_mod, "kijkwijzer": kw_mod}
        with patch("resources.lib.data.backfill._SCRAPER_MODULES", modules):
            result = run_canaries({"fsk", "bbfc", "kijkwijzer"}, 0.25)
        assert result == {"fsk"}


# ---------------------------------------------------------------------------
# TLS adapter: create_scraper_session
# ---------------------------------------------------------------------------


class TestCreateScraperSession:
    def test_returns_session_with_adapter(self):
        from resources.lib.utils import create_scraper_session

        session = create_scraper_session()
        adapter = session.get_adapter("https://example.com")
        assert adapter is not None
        assert type(adapter).__name__ == "_BrowserTLSAdapter"

    def test_session_works_for_http(self):
        from resources.lib.utils import create_scraper_session

        session = create_scraper_session()
        adapter = session.get_adapter("http://example.com")
        assert type(adapter).__name__ != "_BrowserTLSAdapter"

    def test_seclevel1_produces_more_ciphers(self):
        ctx_default = ssl.create_default_context()
        default_count = len(ctx_default.get_ciphers())

        ctx_relaxed = ssl.create_default_context()
        ctx_relaxed.set_ciphers("DEFAULT:@SECLEVEL=1")
        relaxed_count = len(ctx_relaxed.get_ciphers())

        assert relaxed_count >= default_count

    def test_adapter_fallback_on_bad_cipher_string(self):
        from resources.lib.utils import create_scraper_session

        with patch("resources.lib.utils.ssl") as mock_ssl:
            ctx = MagicMock()
            ctx.set_ciphers.side_effect = ssl.SSLError("bad cipher")
            mock_ssl.create_default_context.return_value = ctx
            mock_ssl.SSLError = ssl.SSLError

            session = create_scraper_session()
            assert session is not None


# ---------------------------------------------------------------------------
# Each scraper uses create_scraper_session
# ---------------------------------------------------------------------------


class TestScrapersUseSharedAdapter:
    @patch("resources.lib.providers.kijkwijzer.create_scraper_session")
    def test_kijkwijzer_uses_shared_session(self, mock_create):
        import resources.lib.providers.kijkwijzer as kw
        kw._session = None
        mock_session = MagicMock()
        mock_create.return_value = mock_session

        session = kw._get_session()
        mock_create.assert_called_once()
        assert session is mock_session
        kw._session = None

    @patch("resources.lib.providers.bbfc.create_scraper_session")
    def test_bbfc_uses_shared_session(self, mock_create):
        import resources.lib.providers.bbfc as bbfc_mod
        bbfc_mod._session = None
        mock_session = MagicMock()
        mock_create.return_value = mock_session

        session = bbfc_mod._get_session()
        mock_create.assert_called_once()
        assert session is mock_session
        bbfc_mod._session = None

    @patch("resources.lib.providers.fsk.create_scraper_session")
    def test_fsk_uses_shared_session(self, mock_create):
        import resources.lib.providers.fsk as fsk_mod
        fsk_mod._session = None
        mock_session = MagicMock()
        mock_create.return_value = mock_session

        session = fsk_mod._get_session()
        mock_create.assert_called_once()
        assert session is mock_session
        fsk_mod._session = None

    @patch("resources.lib.providers.medieraadet.create_scraper_session")
    def test_medieraadet_uses_shared_session(self, mock_create):
        import resources.lib.providers.medieraadet as med_mod
        med_mod._session = None
        mock_session = MagicMock()
        mock_create.return_value = mock_session

        session = med_mod._get_session()
        mock_create.assert_called_once()
        assert session is mock_session
        med_mod._session = None
