"""Tests for TMDB ID resolution, certification lookup, and 401 handling."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from resources.lib.providers.tmdb import (
    resolve_id, lookup, fetch_certs, match_direct, match_inferred,
)
from resources.lib.utils import ApiKeyError


class TestResolveId:
    @patch("resources.lib.providers.tmdb.requests")
    def test_resolve_from_tvdb_id(self, mock_requests):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "movie_results": [],
            "tv_results": [{"id": 118357, "name": "1883"}],
        }
        mock_requests.get.return_value = resp

        result = resolve_id("fake_key", tvdb_id="396390")
        assert result == "118357"
        mock_requests.get.assert_called_once()
        call_kwargs = mock_requests.get.call_args
        assert call_kwargs[1]["params"]["external_source"] == "tvdb_id"

    @patch("resources.lib.providers.tmdb.requests")
    def test_resolve_from_imdb_id(self, mock_requests):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "movie_results": [{"id": 550, "title": "Fight Club"}],
            "tv_results": [],
        }
        mock_requests.get.return_value = resp

        result = resolve_id("fake_key", imdb_id="tt0137523")
        assert result == "550"

    @patch("resources.lib.providers.tmdb.requests")
    def test_resolve_prefers_tvdb_over_imdb(self, mock_requests):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"tv_results": [{"id": 999}], "movie_results": []}
        mock_requests.get.return_value = resp

        resolve_id("fake_key", tvdb_id="123", imdb_id="tt999")
        call_kwargs = mock_requests.get.call_args
        assert "/find/123" in call_kwargs[0][0]
        assert call_kwargs[1]["params"]["external_source"] == "tvdb_id"

    def test_resolve_no_ids_returns_none(self):
        assert resolve_id("fake_key") is None

    @patch("resources.lib.providers.tmdb.requests")
    def test_resolve_no_results_returns_none(self, mock_requests):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"movie_results": [], "tv_results": []}
        mock_requests.get.return_value = resp

        assert resolve_id("fake_key", tvdb_id="999999") is None

    @patch("resources.lib.providers.tmdb.requests")
    def test_resolve_401_raises_api_key_error(self, mock_requests):
        resp = MagicMock()
        resp.status_code = 401
        mock_requests.get.return_value = resp

        with pytest.raises(ApiKeyError) as exc_info:
            resolve_id("bad_key", tvdb_id="123")
        assert exc_info.value.provider == "tmdb"


class TestFetchCerts:
    @patch("resources.lib.providers.tmdb.requests")
    def test_returns_certs_dict(self, mock_requests):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "results": [
                {"iso_3166_1": "NL", "rating": "12"},
                {"iso_3166_1": "DE", "rating": "12"},
            ]
        }
        mock_requests.get.return_value = resp

        media_type = MagicMock()
        media_type.tmdb_endpoint = "/tv/{id}/content_ratings"
        media_type.tmdb_parse_certs = lambda results: {
            r["iso_3166_1"]: r["rating"] for r in results
        }

        certs = fetch_certs("456", "fake_key", media_type)
        assert certs == {"NL": "12", "DE": "12"}

    @patch("resources.lib.providers.tmdb.requests")
    def test_http_error_returns_none(self, mock_requests):
        resp = MagicMock()
        resp.status_code = 500
        mock_requests.get.return_value = resp

        media_type = MagicMock()
        media_type.tmdb_endpoint = "/movie/{id}/release_dates"

        assert fetch_certs("123", "fake_key", media_type) is None

    @patch("resources.lib.providers.tmdb.requests")
    def test_401_raises_api_key_error(self, mock_requests):
        resp = MagicMock()
        resp.status_code = 401
        mock_requests.get.return_value = resp

        media_type = MagicMock()
        media_type.tmdb_endpoint = "/movie/{id}/release_dates"

        with pytest.raises(ApiKeyError) as exc_info:
            fetch_certs("123", "bad_key", media_type)
        assert exc_info.value.provider == "tmdb"

    @patch("resources.lib.providers.tmdb.requests")
    def test_invalid_json_returns_none(self, mock_requests):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.side_effect = ValueError("bad json")
        mock_requests.get.return_value = resp

        media_type = MagicMock()
        media_type.tmdb_endpoint = "/movie/{id}/release_dates"

        assert fetch_certs("123", "fake_key", media_type) is None

    @patch("resources.lib.providers.tmdb.requests")
    def test_request_exception_returns_none(self, mock_requests):
        import requests
        mock_requests.get.side_effect = requests.RequestException("timeout")
        mock_requests.RequestException = requests.RequestException

        media_type = MagicMock()
        media_type.tmdb_endpoint = "/movie/{id}/release_dates"

        assert fetch_certs("123", "fake_key", media_type) is None


class TestMatchDirect:
    def test_direct_match_found(self):
        certs = {"NL": "12", "DE": "16", "GB": "15"}
        rating, source = match_direct(certs, "NL")
        assert rating == "12"
        assert source == "tmdb-NL"

    def test_no_match_returns_none(self):
        certs = {"DE": "16", "GB": "15"}
        rating, source = match_direct(certs, "NL")
        assert rating is None
        assert source is None

    def test_case_insensitive_target(self):
        certs = {"NL": "12"}
        rating, source = match_direct(certs, "nl")
        assert rating == "12"
        assert source == "tmdb-NL"

    def test_empty_certs(self):
        rating, source = match_direct({}, "NL")
        assert rating is None
        assert source is None


class TestMatchInferred:
    def test_inferred_match_via_mapping(self):
        certs = {"DE": "12"}
        mappings = {"DE": {"12": "12", "16": "16"}}
        rating, source = match_inferred(certs, "NL", ["DE", "GB"], mappings)
        assert rating == "12"
        assert source == "tmdb-inferred-DE"

    def test_unmapped_rating_skips_to_next(self):
        certs = {"DE": "99", "GB": "15"}
        mappings = {"DE": {"12": "12"}, "GB": {"15": "16"}}
        rating, source = match_inferred(certs, "NL", ["DE", "GB"], mappings)
        assert rating == "16"
        assert source == "tmdb-inferred-GB"

    def test_no_inference_countries_returns_none(self):
        certs = {"DE": "12"}
        rating, source = match_inferred(certs, "NL", [], {"DE": {"12": "12"}})
        assert rating is None
        assert source is None

    def test_no_matching_certs_returns_none(self):
        certs = {"FR": "U"}
        mappings = {"DE": {"12": "12"}}
        rating, source = match_inferred(certs, "NL", ["DE"], mappings)
        assert rating is None
        assert source is None

    def test_country_needs_both_cert_and_mapping(self):
        certs = {"DE": "12"}
        mappings = {}
        rating, source = match_inferred(certs, "NL", ["DE"], mappings)
        assert rating is None
        assert source is None


class TestLookup401:
    @patch("resources.lib.providers.tmdb.requests")
    def test_lookup_401_raises_api_key_error(self, mock_requests):
        resp = MagicMock()
        resp.status_code = 401
        mock_requests.get.return_value = resp

        media_type = MagicMock()
        media_type.tmdb_endpoint = "/movie/{id}/release_dates"

        with pytest.raises(ApiKeyError) as exc_info:
            lookup("123", "bad_key", "NL", [], {}, media_type)
        assert exc_info.value.provider == "tmdb"
