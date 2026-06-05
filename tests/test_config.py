"""Tests for inference config loading with country presets."""
from __future__ import annotations

import json
import os

from resources.lib.config import load_inference_config, load_preset


def test_loads_nl_preset():
    """NL preset loads valid data from shipped JSON file."""
    preset = load_preset("NL")
    assert preset["country_code"] == "NL"
    assert "AL" in preset["valid_ratings"]
    assert "US" in preset["mappings"]
    assert preset["mappings"]["US"]["R"] == "16"


def test_loads_de_preset():
    """DE preset has FSK ratings."""
    preset = load_preset("DE")
    assert preset["country_code"] == "DE"
    assert preset["valid_ratings"] == ["0", "6", "12", "16", "18"]
    assert preset["inference_countries"][0] == "AT"


def test_missing_preset_falls_back_to_nl():
    """Unknown country code falls back to NL preset."""
    preset = load_preset("XX")
    assert preset["country_code"] == "NL"


def test_creates_config_on_first_run(kodi_stubs, tmp_path):
    """First call seeds inference.json from preset and returns config."""
    config = load_inference_config("NL")
    assert config["country_code"] == "NL"
    assert config["valid_ratings"] == ["AL", "6", "9", "12", "14", "16", "18"]
    assert "US" in config["mappings"]
    assert config["mappings"]["US"]["R"] == "16"


def test_valid_ratings_from_preset_not_user_file(kodi_stubs, tmp_path):
    """valid_ratings always comes from the preset, not the user file."""
    load_inference_config("NL")

    config_dir = os.path.join(str(tmp_path), "script.eucert.fixer", "config")
    config_path = os.path.join(config_dir, "inference.json")
    with open(config_path) as f:
        data = json.load(f)

    data["valid_ratings"] = ["FAKE"]
    with open(config_path, "w") as f:
        json.dump(data, f)

    config = load_inference_config("NL")
    assert config["valid_ratings"] == ["AL", "6", "9", "12", "14", "16", "18"]


def test_custom_inference_countries_preserved(kodi_stubs, tmp_path):
    """User edits to inference_countries are respected."""
    load_inference_config("NL")

    config_dir = os.path.join(str(tmp_path), "script.eucert.fixer", "config")
    config_path = os.path.join(config_dir, "inference.json")
    with open(config_path) as f:
        data = json.load(f)

    data["inference_countries"] = ["DE", "US"]
    with open(config_path, "w") as f:
        json.dump(data, f)

    config = load_inference_config("NL")
    assert config["inference_countries"] == ["DE", "US"]


def test_corrupt_file_returns_preset_defaults(kodi_stubs, tmp_path):
    """Corrupt JSON falls back to preset defaults."""
    load_inference_config("NL")

    config_dir = os.path.join(str(tmp_path), "script.eucert.fixer", "config")
    config_path = os.path.join(config_dir, "inference.json")
    with open(config_path, "w") as f:
        f.write("not json{{{")

    config = load_inference_config("NL")
    assert config["country_code"] == "NL"
    assert len(config["inference_countries"]) == 8


def test_mapping_keys_normalized_to_strings(kodi_stubs, tmp_path):
    """Integer keys in JSON are normalized to strings."""
    load_inference_config("NL")

    config_dir = os.path.join(str(tmp_path), "script.eucert.fixer", "config")
    config_path = os.path.join(config_dir, "inference.json")
    with open(config_path) as f:
        data = json.load(f)

    data["mappings"]["TEST"] = {6: "6", 12: "12"}
    with open(config_path, "w") as f:
        json.dump(data, f)

    config = load_inference_config("NL")
    assert config["mappings"]["TEST"]["6"] == "6"
    assert config["mappings"]["TEST"]["12"] == "12"


def test_de_config_has_correct_prefix(kodi_stubs, tmp_path):
    """DE config returns DE prefix from preset."""
    config = load_inference_config("DE")
    assert config["default_prefix"] == "DE:"
    assert config["country_code"] == "DE"
    assert config["valid_ratings"] == ["0", "6", "12", "16", "18"]
