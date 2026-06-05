"""Tests for FSK provider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from resources.lib.providers.fsk import lookup


def _make_response(docs, success=True, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = {
        "success": success,
        "data": {"totalRecords": len(docs), "docs": docs},
    }
    return resp


def _make_doc(title, rating, imdb_ids=None, original_title=""):
    doc = {
        "mainTitle": title,
        "mainOriginalTitle": original_title,
        "__rating": rating,
        "subproducts": [],
    }
    for imdb_id in (imdb_ids or []):
        doc["subproducts"].append({"imdbId": imdb_id})
    return doc


class TestFskLookup:
    @patch("resources.lib.providers.fsk._get_session")
    def test_imdb_match(self, mock_session):
        doc = _make_doc("Der Film", 12, imdb_ids=["tt1234567"])
        mock_session.return_value.get.return_value = _make_response([doc])

        rating, source = lookup("Der Film", imdb_id="tt1234567")
        assert rating == "12"
        assert source == "fsk"

    @patch("resources.lib.providers.fsk._get_session")
    def test_title_match_no_imdb(self, mock_session):
        doc = _make_doc("Bambi", 0)
        mock_session.return_value.get.return_value = _make_response([doc])

        rating, source = lookup("Bambi")
        assert rating == "0"
        assert source == "fsk"

    @patch("resources.lib.providers.fsk._get_session")
    def test_original_title_match(self, mock_session):
        doc = _make_doc("Der Pate", 16, original_title="The Godfather")
        mock_session.return_value.get.return_value = _make_response([doc])

        rating, source = lookup("The Godfather")
        assert rating == "16"
        assert source == "fsk"

    @patch("resources.lib.providers.fsk._get_session")
    def test_imdb_preferred_over_title(self, mock_session):
        wrong = _make_doc("Bambi", 0)
        right = _make_doc("Bambi 2", 6, imdb_ids=["tt9999"])
        mock_session.return_value.get.return_value = _make_response([wrong, right])

        rating, source = lookup("Bambi", imdb_id="tt9999")
        assert rating == "6"

    @patch("resources.lib.providers.fsk._get_session")
    def test_no_results(self, mock_session):
        mock_session.return_value.get.return_value = _make_response([])

        rating, source = lookup("Nonexistent Film")
        assert rating is None
        assert source is None

    @patch("resources.lib.providers.fsk._get_session")
    def test_no_title_match(self, mock_session):
        doc = _make_doc("Something Else", 12)
        mock_session.return_value.get.return_value = _make_response([doc])

        rating, source = lookup("Totally Different")
        assert rating is None

    @patch("resources.lib.providers.fsk._get_session")
    def test_request_error(self, mock_session):
        import requests
        mock_session.return_value.get.side_effect = requests.RequestException("timeout")

        rating, source = lookup("Test")
        assert rating is None
        assert source is None

    @patch("resources.lib.providers.fsk._get_session")
    def test_http_error(self, mock_session):
        resp = MagicMock()
        resp.status_code = 500
        mock_session.return_value.get.return_value = resp

        rating, source = lookup("Test")
        assert rating is None

    @patch("resources.lib.providers.fsk._get_session")
    def test_tvshow_super_type(self, mock_session):
        doc = _make_doc("Breaking Bad", 16)
        mock_session.return_value.get.return_value = _make_response([doc])

        lookup("Breaking Bad", media_type_name="tvshow")

        call_kwargs = mock_session.return_value.get.call_args
        params = call_kwargs.kwargs.get("params", call_kwargs[1].get("params", {}))
        assert params["superType"] == "serial"
        assert params.get("serialOptions[]") == "TVSR"

    @patch("resources.lib.providers.fsk._get_session")
    def test_movie_super_type(self, mock_session):
        doc = _make_doc("Bambi", 0)
        mock_session.return_value.get.return_value = _make_response([doc])

        lookup("Bambi", media_type_name="movie")

        call_kwargs = mock_session.return_value.get.call_args
        params = call_kwargs.kwargs.get("params", call_kwargs[1].get("params", {}))
        assert params["superType"] == "single"
        assert params.get("singleOptions[]") == "SP"

    @patch("resources.lib.providers.fsk._get_session")
    def test_invalid_rating_skipped(self, mock_session):
        doc = _make_doc("Test", 99)
        mock_session.return_value.get.return_value = _make_response([doc])

        rating, source = lookup("Test")
        assert rating is None

    @patch("resources.lib.providers.fsk._get_session")
    def test_year_filtering_adds_date_params(self, mock_session):
        doc = _make_doc("The Matrix", 16)
        mock_session.return_value.get.return_value = _make_response([doc])

        lookup("The Matrix", year=1999)

        call_kwargs = mock_session.return_value.get.call_args
        params = call_kwargs.kwargs.get("params", call_kwargs[1].get("params", {}))
        assert params["ratingReleaseDateFrom"] == "1998-01-01"
        assert params["ratingReleaseDateTo"] == "2000-12-31"
        assert params["sort"] == "__ratingReleaseDateTc"

    @patch("resources.lib.providers.fsk._get_session")
    def test_no_year_omits_date_params(self, mock_session):
        doc = _make_doc("Bambi", 0)
        mock_session.return_value.get.return_value = _make_response([doc])

        lookup("Bambi", year=0)

        call_kwargs = mock_session.return_value.get.call_args
        params = call_kwargs.kwargs.get("params", call_kwargs[1].get("params", {}))
        assert "ratingReleaseDateFrom" not in params
        assert "ratingReleaseDateTo" not in params

    @patch("resources.lib.providers.fsk._get_session")
    def test_tvshow_skips_year_filter(self, mock_session):
        doc = _make_doc("Pokémon - Staffel 22", 6)
        mock_session.return_value.get.return_value = _make_response([doc])

        lookup("Pokémon", year=1997, media_type_name="tvshow")

        call_kwargs = mock_session.return_value.get.call_args
        params = call_kwargs.kwargs.get("params", call_kwargs[1].get("params", {}))
        assert "ratingReleaseDateFrom" not in params
        assert "ratingReleaseDateTo" not in params

    @patch("resources.lib.providers.fsk._get_session")
    def test_success_false(self, mock_session):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"success": False}
        mock_session.return_value.get.return_value = resp

        rating, source = lookup("Test")
        assert rating is None
