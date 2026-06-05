"""Tests for OMDB 401 handling."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from resources.lib.providers.omdb import lookup
from resources.lib.utils import ApiKeyError


class TestOmdb401:
    @patch("resources.lib.providers.omdb.requests")
    def test_lookup_401_raises_api_key_error(self, mock_requests):
        resp = MagicMock()
        resp.status_code = 401
        mock_requests.get.return_value = resp

        with pytest.raises(ApiKeyError) as exc_info:
            lookup("tt0137523", "bad_key", {"US": {}})
        assert exc_info.value.provider == "omdb"

    @patch("resources.lib.providers.omdb.requests")
    def test_lookup_200_with_valid_mapping(self, mock_requests):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"Response": "True", "Rated": "R"}
        mock_requests.get.return_value = resp

        rating, source = lookup("tt123", "key", {"US": {"R": "16"}})
        assert rating == "16"
        assert source == "omdb"
