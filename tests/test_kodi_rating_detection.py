"""Tests for rating prefix stripping and needs-rating detection."""
from __future__ import annotations

import pytest

from resources.lib.data.kodi import _strip_rating_prefix, _needs_rating

NL_RATINGS = ("AL", "6", "9", "12", "14", "16", "18")
DE_RATINGS = ("0", "6", "12", "16", "18")


class TestStripRatingPrefix:
    def test_empty_string(self):
        assert _strip_rating_prefix("") == ""

    def test_country_prefix_two_letter(self):
        assert _strip_rating_prefix("NL:12") == "12"
        assert _strip_rating_prefix("NL:R") == "R"
        assert _strip_rating_prefix("NL:AL") == "AL"
        assert _strip_rating_prefix("US:TV-G") == "TV-G"

    def test_country_prefix_three_letter(self):
        assert _strip_rating_prefix("USA:R") == "R"

    def test_rated_prefix(self):
        assert _strip_rating_prefix("Rated TV-MA") == "TV-MA"
        assert _strip_rating_prefix("Rated TV-14") == "TV-14"
        assert _strip_rating_prefix("Rated NR") == "NR"

    def test_bare_rating(self):
        assert _strip_rating_prefix("AL") == "AL"
        assert _strip_rating_prefix("12") == "12"
        assert _strip_rating_prefix("NR") == "NR"
        assert _strip_rating_prefix("TV-Y7") == "TV-Y7"

    def test_lowercase_not_stripped(self):
        assert _strip_rating_prefix("nl:12") == "nl:12"


class TestNeedsRating:
    def test_empty_mpaa_always_needs_rating(self):
        assert _needs_rating("", False, "NR", NL_RATINGS) is True
        assert _needs_rating("", True, "NR", NL_RATINGS) is True

    def test_replace_off_skips_non_empty(self):
        assert _needs_rating("NL:R", False, "NR", NL_RATINGS) is False
        assert _needs_rating("Rated TV-MA", False, "NR", NL_RATINGS) is False

    def test_replace_on_flags_invalid_bare_values(self):
        assert _needs_rating("R", True, "NR", NL_RATINGS) is True
        assert _needs_rating("PG-13", True, "NR", NL_RATINGS) is True
        assert _needs_rating("G", True, "NR", NL_RATINGS) is True

    def test_replace_on_flags_wrong_prefix(self):
        assert _needs_rating("NL:R", True, "NR", NL_RATINGS, "NL:") is True
        assert _needs_rating("NL:PG-13", True, "NR", NL_RATINGS, "NL:") is True
        assert _needs_rating("Rated TV-MA", True, "NR", NL_RATINGS, "NL:") is True
        assert _needs_rating("NL:G", True, "NR", NL_RATINGS, "NL:") is True

    def test_replace_on_preserves_valid_with_prefix(self):
        assert _needs_rating("NL:AL", True, "NR", NL_RATINGS, "NL:") is False
        assert _needs_rating("NL:6", True, "NR", NL_RATINGS, "NL:") is False
        assert _needs_rating("NL:12", True, "NR", NL_RATINGS, "NL:") is False
        assert _needs_rating("NL:16", True, "NR", NL_RATINGS, "NL:") is False

    def test_replace_on_preserves_valid_bare(self):
        assert _needs_rating("AL", True, "NR", NL_RATINGS) is False
        assert _needs_rating("6", True, "NR", NL_RATINGS) is False
        assert _needs_rating("12", True, "NR", NL_RATINGS) is False

    def test_replace_on_preserves_fallback_with_prefix(self):
        assert _needs_rating("NL:NR", True, "NR", NL_RATINGS, "NL:") is False

    def test_replace_on_preserves_fallback_bare(self):
        assert _needs_rating("NR", True, "NR", NL_RATINGS) is False

    def test_replace_on_custom_fallback(self):
        assert _needs_rating("NL:CUSTOM", True, "CUSTOM", NL_RATINGS, "NL:") is False
        assert _needs_rating("NL:CUSTOM", True, "NR", NL_RATINGS, "NL:") is True

    @pytest.mark.parametrize("mpaa", [
        "NL:9", "NL:14", "NL:18",
    ])
    def test_all_valid_nl_ratings_with_prefix(self, mpaa):
        assert _needs_rating(mpaa, True, "NR", NL_RATINGS, "NL:") is False

    @pytest.mark.parametrize("mpaa", [
        "9", "14", "18",
    ])
    def test_all_valid_nl_ratings_bare(self, mpaa):
        assert _needs_rating(mpaa, True, "NR", NL_RATINGS) is False


class TestNeedsRatingBlankPrefix:
    """When override_prefix is on with blank prefix, any prefixed value
    should be flagged even if the bare value is valid."""

    def test_country_prefix_flagged(self):
        assert _needs_rating("NL:12", True, "NR", NL_RATINGS, "") is True
        assert _needs_rating("DE:16", True, "NR", NL_RATINGS, "") is True
        assert _needs_rating("NL:AL", True, "NR", NL_RATINGS, "") is True

    def test_rated_prefix_flagged(self):
        assert _needs_rating("Rated NR", True, "NR", NL_RATINGS, "") is True
        assert _needs_rating("Rated 12", True, "NR", NL_RATINGS, "") is True

    def test_bare_valid_preserved(self):
        assert _needs_rating("12", True, "NR", NL_RATINGS, "") is False
        assert _needs_rating("AL", True, "NR", NL_RATINGS, "") is False

    def test_bare_fallback_preserved(self):
        assert _needs_rating("NR", True, "NR", NL_RATINGS, "") is False


class TestNeedsRatingMissingPrefix:
    """When a prefix is expected, bare values should be flagged."""

    def test_bare_valid_flagged(self):
        assert _needs_rating("12", True, "NR", NL_RATINGS, "NL:") is True
        assert _needs_rating("AL", True, "NR", NL_RATINGS, "NL:") is True

    def test_bare_fallback_flagged(self):
        assert _needs_rating("NR", True, "NR", NL_RATINGS, "NL:") is True

    def test_wrong_country_prefix_flagged(self):
        assert _needs_rating("DE:12", True, "NR", NL_RATINGS, "NL:") is True

    def test_correct_prefix_preserved(self):
        assert _needs_rating("NL:12", True, "NR", NL_RATINGS, "NL:") is False
        assert _needs_rating("NL:NR", True, "NR", NL_RATINGS, "NL:") is False


class TestNeedsRatingDE:
    """Verify dynamic valid_ratings works for DE (FSK) scale."""

    def test_fsk_0_is_valid(self):
        assert _needs_rating("DE:0", True, "NR", DE_RATINGS, "DE:") is False

    def test_fsk_12_is_valid(self):
        assert _needs_rating("DE:12", True, "NR", DE_RATINGS, "DE:") is False

    def test_nl_rating_flagged_for_de(self):
        assert _needs_rating("NL:AL", True, "NR", DE_RATINGS, "DE:") is True
        assert _needs_rating("NL:9", True, "NR", DE_RATINGS, "DE:") is True
        assert _needs_rating("NL:14", True, "NR", DE_RATINGS, "DE:") is True

    def test_fsk_values_with_prefix(self):
        for rating in DE_RATINGS:
            assert _needs_rating("DE:{}".format(rating), True, "NR", DE_RATINGS, "DE:") is False

    def test_bare_fsk_flagged_when_prefix_expected(self):
        assert _needs_rating("12", True, "NR", DE_RATINGS, "DE:") is True
