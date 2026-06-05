"""Tests for shared title matching utilities."""
from __future__ import annotations

from resources.lib.utils import normalize_for_compare, title_matches


class TestNormalizeForCompare:
    def test_strips_accents(self):
        assert normalize_for_compare("Pokémon") == "pokemon"

    def test_strips_umlauts(self):
        assert normalize_for_compare("Über") == "uber"

    def test_lowercases(self):
        assert normalize_for_compare("HELLO") == "hello"

    def test_plain_text_unchanged(self):
        assert normalize_for_compare("hello") == "hello"

    def test_multiple_accents(self):
        assert normalize_for_compare("André Küpers") == "andre kupers"


class TestTitleMatches:
    def test_exact_match(self):
        assert title_matches("Pokémon", "Pokémon") is True

    def test_exact_match_case_insensitive(self):
        assert title_matches("POKÉMON", "pokémon") is True

    def test_accent_fallback(self):
        assert title_matches("Pokemon", "Pokémon") is True

    def test_accent_fallback_reverse(self):
        assert title_matches("Pokémon", "Pokemon") is True

    def test_prefix_with_space(self):
        assert title_matches("Pokémon Staffel 22", "Pokémon") is True

    def test_prefix_with_colon(self):
        assert title_matches("Pokémon: XY", "Pokémon") is True

    def test_prefix_with_dash(self):
        assert title_matches("Pokémon - Staffel 22", "Pokémon") is True

    def test_accent_plus_prefix(self):
        assert title_matches("Pokemon the Series: XY", "Pokémon") is True

    def test_accent_plus_colon_prefix(self):
        assert title_matches("Pokemon: To Be a Pokemon Master", "Pokémon") is True

    def test_no_false_positive_without_separator(self):
        assert title_matches("Pokémonster", "Pokémon") is False

    def test_no_false_positive_substring(self):
        assert title_matches("Theater", "The") is False

    def test_shorter_result_no_match(self):
        assert title_matches("Pok", "Pokémon") is False

    def test_empty_strings(self):
        assert title_matches("", "") is True
        assert title_matches("Pokémon", "") is False

    def test_bbfc_pokemon_real_data(self):
        assert title_matches("Pokemon the Series: XY (2025)", "Pokémon") is True
        assert title_matches("Pokemon the Series: XY", "Pokémon") is True

    def test_fsk_pokemon_real_data(self):
        assert title_matches("Pokémon - Staffel 22", "Pokémon") is True
        assert title_matches("Pokémon: XY - Erkundungen in Kalos (S18)", "Pokémon") is True
        assert title_matches("Pokémon Horizonte - Volume 4", "Pokémon") is True
