"""Tests for Medieraadet (Denmark) provider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from resources.lib.providers.medieraadet import _strip_article, lookup


class TestStripArticle:
    def test_english_the(self):
        assert _strip_article("The Matrix") == "Matrix"

    def test_english_a(self):
        assert _strip_article("A Beautiful Mind") == "Beautiful Mind"

    def test_german_der(self):
        assert _strip_article("Der Untergang") == "Untergang"

    def test_danish_den(self):
        assert _strip_article("Den Store Dag") == "Store Dag"

    def test_no_article(self):
        assert _strip_article("Interstellar") == "Interstellar"

    def test_case_insensitive(self):
        assert _strip_article("the matrix") == "matrix"


def _mock_search_response(films):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "ResultCount": len(films),
        "TotalResultCount": len(films),
        "FilmList": films,
    }
    return resp


def _mock_detail_response(detail):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = detail
    return resp


def _make_film(film_id, title, year=2024):
    return {"Id": film_id, "Title": title, "ReleaseYear": year}


def _make_detail(title, code, year=2024, original_title=None, danish_title=None):
    return {
        "Id": 1,
        "Title": title,
        "OriginalTitle": original_title or title,
        "DanishTitle": danish_title or title,
        "ReleaseYear": year,
        "AssesmentCode": code,
        "Classification": "test",
    }


class TestMedieraadetLookup:
    @patch("resources.lib.providers.medieraadet._get_session")
    def test_basic_match(self, mock_session):
        session = mock_session.return_value
        session.get.side_effect = [
            _mock_search_response([_make_film(1, "Interstellar", 2014)]),
            _mock_detail_response(_make_detail("Interstellar", "to11", 2014)),
        ]

        rating, source = lookup("Interstellar")
        assert rating == "11"
        assert source == "medieraadet"

    @patch("resources.lib.providers.medieraadet._get_session")
    def test_all_rating_codes(self, mock_session):
        codes = {"tfa": "A", "fr.u7": "7", "to7": "7", "to11": "11", "to15": "15"}
        for code, expected in codes.items():
            session = mock_session.return_value
            session.get.side_effect = [
                _mock_search_response([_make_film(1, "Test")]),
                _mock_detail_response(_make_detail("Test", code)),
            ]
            rating, source = lookup("Test")
            assert rating == expected, "code {} should map to {}".format(code, expected)

    @patch("resources.lib.providers.medieraadet._get_session")
    def test_article_stripping_retry(self, mock_session):
        session = mock_session.return_value
        empty = _mock_search_response([])
        found = _mock_search_response([_make_film(1, "Matrix", 1999)])
        detail = _mock_detail_response(
            _make_detail("Matrix", "to15", 1999, original_title="The Matrix")
        )
        session.get.side_effect = [empty, found, detail]

        rating, source = lookup("The Matrix")
        assert rating == "15"
        assert session.get.call_count == 3

    @patch("resources.lib.providers.medieraadet._get_session")
    def test_year_filtering(self, mock_session):
        session = mock_session.return_value
        session.get.side_effect = [
            _mock_search_response([
                _make_film(1, "Bambi", 1942),
                _make_film(2, "Bambi", 2024),
            ]),
            _mock_detail_response(_make_detail("Bambi", "tfa", 2024)),
        ]

        rating, source = lookup("Bambi", year=2024)
        assert rating == "A"

    @patch("resources.lib.providers.medieraadet._get_session")
    def test_no_results(self, mock_session):
        session = mock_session.return_value
        session.get.side_effect = [
            _mock_search_response([]),
            _mock_search_response([]),
        ]

        rating, source = lookup("Nonexistent Film That Does Not Exist")
        assert rating is None
        assert source is None

    @patch("resources.lib.providers.medieraadet._get_session")
    def test_no_title_match(self, mock_session):
        session = mock_session.return_value
        session.get.side_effect = [
            _mock_search_response([_make_film(1, "Something Else")]),
            _mock_detail_response(_make_detail("Something Else", "to11")),
        ]

        rating, source = lookup("Totally Different")
        assert rating is None

    @patch("resources.lib.providers.medieraadet._get_session")
    def test_unknown_code_skipped(self, mock_session):
        session = mock_session.return_value
        session.get.side_effect = [
            _mock_search_response([_make_film(1, "Test")]),
            _mock_detail_response(_make_detail("Test", "unknown_code")),
        ]

        rating, source = lookup("Test")
        assert rating is None

    @patch("resources.lib.providers.medieraadet._get_session")
    def test_request_error(self, mock_session):
        import requests
        session = mock_session.return_value
        session.get.side_effect = requests.RequestException("timeout")

        rating, source = lookup("Test")
        assert rating is None
        assert source is None

    @patch("resources.lib.providers.medieraadet._get_session")
    def test_original_title_match(self, mock_session):
        session = mock_session.return_value
        session.get.side_effect = [
            _mock_search_response([_make_film(1, "Stjaernekrigen")]),
            _mock_detail_response(
                _make_detail("Stjaernekrigen", "to11",
                             original_title="Star Wars",
                             danish_title="Stjaernekrigen")
            ),
        ]

        rating, source = lookup("Star Wars")
        assert rating == "11"
