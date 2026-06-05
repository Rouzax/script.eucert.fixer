"""Tests for BBFC provider."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from resources.lib.providers.bbfc import lookup, _parse_next_data


def _make_html(results):
    """Build a minimal HTML page with __NEXT_DATA__ containing search results."""
    next_data = {
        "props": {
            "pageProps": {
                "searchResults": {
                    "results": results,
                },
            },
        },
    }
    return '<html><script id="__NEXT_DATA__" type="application/json">{}</script></html>'.format(
        json.dumps(next_data)
    )


def _make_result(title, classification, result_type="Film"):
    return {
        "title": title,
        "classification": classification,
        "type": result_type,
    }


class TestParseNextData:
    def test_valid_html(self):
        html = _make_html([_make_result("Test", "15")])
        results = _parse_next_data(html)
        assert len(results) == 1
        assert results[0]["title"] == "Test"

    def test_no_script_tag(self):
        assert _parse_next_data("<html></html>") == []

    def test_invalid_json(self):
        html = '<html><script id="__NEXT_DATA__">not json{</script></html>'
        assert _parse_next_data(html) == []

    def test_missing_keys(self):
        html = '<html><script id="__NEXT_DATA__">{"props": {}}</script></html>'
        assert _parse_next_data(html) == []


class TestBbfcLookup:
    @patch("resources.lib.providers.bbfc._get_session")
    def test_exact_title_match(self, mock_session):
        html = _make_html([_make_result("The Matrix", "15")])
        resp = MagicMock()
        resp.status_code = 200
        resp.text = html
        mock_session.return_value.get.return_value = resp

        rating, source = lookup("The Matrix")
        assert rating == "15"
        assert source == "bbfc"

    @patch("resources.lib.providers.bbfc._get_session")
    def test_case_insensitive_match(self, mock_session):
        html = _make_html([_make_result("The Matrix", "15")])
        resp = MagicMock()
        resp.status_code = 200
        resp.text = html
        mock_session.return_value.get.return_value = resp

        rating, source = lookup("the matrix")
        assert rating == "15"

    @patch("resources.lib.providers.bbfc._get_session")
    def test_title_with_year_suffix(self, mock_session):
        html = _make_html([_make_result("The Matrix Reloaded (2003)", "15")])
        resp = MagicMock()
        resp.status_code = 200
        resp.text = html
        mock_session.return_value.get.return_value = resp

        rating, source = lookup("The Matrix Reloaded")
        assert rating == "15"
        assert source == "bbfc"

    @patch("resources.lib.providers.bbfc._get_session")
    def test_no_title_match(self, mock_session):
        html = _make_html([_make_result("Something Else", "12")])
        resp = MagicMock()
        resp.status_code = 200
        resp.text = html
        mock_session.return_value.get.return_value = resp

        rating, source = lookup("The Matrix")
        assert rating is None
        assert source is None

    @patch("resources.lib.providers.bbfc._get_session")
    def test_no_results(self, mock_session):
        html = _make_html([])
        resp = MagicMock()
        resp.status_code = 200
        resp.text = html
        mock_session.return_value.get.return_value = resp

        rating, source = lookup("Nonexistent")
        assert rating is None

    @patch("resources.lib.providers.bbfc._get_session")
    def test_film_type_filter(self, mock_session):
        html = _make_html([
            _make_result("Breaking Bad", "18", "TV Show"),
            _make_result("Breaking Bad", "15", "Film"),
        ])
        resp = MagicMock()
        resp.status_code = 200
        resp.text = html
        mock_session.return_value.get.return_value = resp

        rating, source = lookup("Breaking Bad", media_type_name="movie")
        assert rating == "15"

    @patch("resources.lib.providers.bbfc._get_session")
    def test_tv_type_filter(self, mock_session):
        html = _make_html([
            _make_result("Breaking Bad", "15", "Film"),
            _make_result("Breaking Bad", "18", "TV Show"),
        ])
        resp = MagicMock()
        resp.status_code = 200
        resp.text = html
        mock_session.return_value.get.return_value = resp

        rating, source = lookup("Breaking Bad", media_type_name="tvshow")
        assert rating == "18"

    @patch("resources.lib.providers.bbfc._get_session")
    def test_request_error(self, mock_session):
        import requests
        mock_session.return_value.get.side_effect = requests.RequestException("timeout")

        rating, source = lookup("Test")
        assert rating is None
        assert source is None

    @patch("resources.lib.providers.bbfc._get_session")
    def test_http_error(self, mock_session):
        resp = MagicMock()
        resp.status_code = 500
        mock_session.return_value.get.return_value = resp

        rating, source = lookup("Test")
        assert rating is None

    @patch("resources.lib.providers.bbfc._get_session")
    def test_invalid_classification_skipped(self, mock_session):
        html = _make_html([_make_result("Test", "X")])
        resp = MagicMock()
        resp.status_code = 200
        resp.text = html
        mock_session.return_value.get.return_value = resp

        rating, source = lookup("Test")
        assert rating is None

    @patch("resources.lib.providers.bbfc._get_session")
    def test_all_valid_classifications(self, mock_session):
        for cls in ("U", "PG", "12", "12A", "15", "18", "R18"):
            html = _make_html([_make_result("Test", cls)])
            resp = MagicMock()
            resp.status_code = 200
            resp.text = html
            mock_session.return_value.get.return_value = resp

            rating, source = lookup("Test")
            assert rating == cls, "Failed for classification {}".format(cls)
            assert source == "bbfc"
