"""
Inference configuration loader.

Manages the inference.json config file in addon_data. Loads defaults
from country preset files shipped with the addon. On first run, seeds
the user's config from the selected country preset.

Logging:
    Logger: 'config'
    Key events:
        - config.preset_loaded (DEBUG): Preset loaded from addon resources
        - config.created (INFO): Default config written to addon_data
        - config.loaded (DEBUG): Config loaded from addon_data
        - config.error (WARNING): Failed to load, using preset defaults
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict

from resources.lib.constants import (
    CONFIG_DIR, CONFIG_FILENAME, DEFAULT_ADDON_ID,
    DEFAULT_COUNTRY_CODE, PRESETS_DIR,
)
from resources.lib.utils import get_addon, get_logger

log = get_logger('config')


def _get_presets_dir() -> str:
    """Get the path to the shipped preset files in the addon install dir."""
    try:
        addon_path = get_addon().getAddonInfo('path')
    except RuntimeError:
        addon_path = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        ))
    return os.path.join(addon_path, "resources", PRESETS_DIR)


def load_preset(country_code: str) -> Dict[str, Any]:
    """
    Load a country preset from the shipped preset files.

    Falls back to the default country (NL) if the requested preset
    is missing. Returns the full preset dict.
    """
    presets_dir = _get_presets_dir()
    path = os.path.join(presets_dir, "{}.json".format(country_code))

    if not os.path.isfile(path):
        log.warning("Preset not found, falling back to default",
                    event="config.error",
                    country=country_code, fallback=DEFAULT_COUNTRY_CODE)
        path = os.path.join(presets_dir, "{}.json".format(DEFAULT_COUNTRY_CODE))

    try:
        with open(path, encoding="utf-8") as f:
            preset = json.load(f)
        log.debug("Preset loaded", country=country_code, path=path)
        return preset
    except (json.JSONDecodeError, OSError) as e:
        log.warning("Failed to load preset", event="config.error",
                    country=country_code, error=str(e))
        return _fallback_preset()


def _fallback_preset() -> Dict[str, Any]:
    """Minimal hardcoded fallback if no preset file can be read."""
    return {
        "country_code": DEFAULT_COUNTRY_CODE,
        "country_name": "Netherlands",
        "system_name": "Kijkwijzer",
        "display_name": "NL - Kijkwijzer",
        "valid_ratings": ["AL", "6", "9", "12", "14", "16", "18"],
        "default_prefix": "NL:",
        "inference_countries": ["BE", "DE", "AT", "FR", "GB", "DK", "SE", "US"],
        "mappings": {},
    }


def _get_config_dir() -> str:
    """Get the config directory path, creating it if needed."""
    import xbmcvfs  # noqa: PLC0415 -- late import for testability

    try:
        addon_id = get_addon().getAddonInfo('id')
    except RuntimeError:
        addon_id = DEFAULT_ADDON_ID

    config_dir = xbmcvfs.translatePath(
        "special://profile/addon_data/{}/{}/".format(addon_id, CONFIG_DIR)
    )
    if not xbmcvfs.exists(config_dir):
        xbmcvfs.mkdirs(config_dir)
    return config_dir


def _get_config_path() -> str:
    return os.path.join(_get_config_dir(), CONFIG_FILENAME)


def seed_from_preset(country_code: str) -> None:
    """Write a fresh inference.json from the preset. Overwrites any existing file."""
    preset = load_preset(country_code)
    seed_data = {
        "country_code": country_code,
        "inference_countries": preset["inference_countries"],
        "mappings": preset["mappings"],
    }
    path = _get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(seed_data, f, indent=2, sort_keys=True)
        log.info("Config seeded from preset", event="config.created",
                 country=country_code, path=path)
    except OSError as e:
        log.warning("Failed to write config", event="config.error",
                    error=str(e))


def load_inference_config(country_code: str) -> Dict[str, Any]:
    """
    Load inference config for a country.

    Loads the preset first, then checks for a user-edited inference.json
    in addon_data. If no user file exists, seeds one from the preset.

    Returns a dict with: country_code, valid_ratings, default_prefix,
    inference_countries, mappings. valid_ratings always comes from the
    preset (not user-editable).
    """
    import xbmcvfs  # noqa: PLC0415 -- late import for testability

    preset = load_preset(country_code)
    valid_ratings = list(preset.get("valid_ratings", []))
    default_prefix = str(preset.get("default_prefix", ""))

    path = _get_config_path()

    needs_seed = not xbmcvfs.exists(path)

    if not needs_seed:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            stored_country = data.get("country_code")
            if not stored_country or stored_country != country_code:
                log.info("Country changed, re-seeding config",
                         event="config.reseed",
                         old_country=stored_country, new_country=country_code)
                needs_seed = True
        except (json.JSONDecodeError, OSError):
            needs_seed = True

    if needs_seed:
        seed_from_preset(country_code)
        return {
            "country_code": country_code,
            "valid_ratings": valid_ratings,
            "default_prefix": default_prefix,
            "inference_countries": list(preset.get("inference_countries", [])),
            "mappings": dict(preset.get("mappings", {})),
        }

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        log.debug("Config loaded", path=path)

        countries = data.get("inference_countries")
        mappings = data.get("mappings")
        if not isinstance(countries, list) or not isinstance(mappings, dict):
            log.warning("Invalid config structure, using preset defaults",
                        event="config.error")
            return {
                "country_code": country_code,
                "valid_ratings": valid_ratings,
                "default_prefix": default_prefix,
                "inference_countries": list(preset.get("inference_countries", [])),
                "mappings": dict(preset.get("mappings", {})),
            }

        norm_mappings: Dict[str, Dict[str, str]] = {}
        for country, table in mappings.items():
            if isinstance(table, dict):
                norm_mappings[country] = {str(k): str(v) for k, v in table.items()}

        return {
            "country_code": country_code,
            "valid_ratings": valid_ratings,
            "default_prefix": default_prefix,
            "inference_countries": [str(c) for c in countries],
            "mappings": norm_mappings,
        }
    except (json.JSONDecodeError, OSError) as e:
        log.warning("Failed to load config, using preset defaults",
                    event="config.error", error=str(e))
        return {
            "country_code": country_code,
            "valid_ratings": valid_ratings,
            "default_prefix": default_prefix,
            "inference_countries": list(preset.get("inference_countries", [])),
            "mappings": dict(preset.get("mappings", {})),
        }
