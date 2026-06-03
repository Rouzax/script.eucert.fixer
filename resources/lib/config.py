"""
Inference configuration loader.

Manages the inference.json config file in addon_data. Ships with NL
Kijkwijzer defaults baked in. On first run, writes the defaults to
addon_data so power users can edit them.

Logging:
    Logger: 'config'
    Key events:
        - config.created (INFO): Default config written to addon_data
        - config.loaded (DEBUG): Config loaded from addon_data
        - config.error (WARNING): Failed to load, using defaults
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict

from resources.lib.constants import CONFIG_DIR, CONFIG_FILENAME, DEFAULT_ADDON_ID
from resources.lib.utils import get_addon, get_logger

log = get_logger('config')

DEFAULT_INFERENCE_COUNTRIES = ["BE", "DE", "AT", "FR", "GB", "DK", "SE", "US"]

DEFAULT_RATING_MAPPINGS = {
    "BE": {
        "AL": "AL", "6": "6", "9": "9", "12": "12",
        "14": "14", "16": "16", "18": "18",
    },
    "DE": {
        "0": "AL", "6": "6", "12": "12", "16": "16", "18": "18",
    },
    "AT": {
        "0": "AL", "6": "6", "10": "12", "12": "12",
        "14": "14", "16": "16", "18": "18",
    },
    "FR": {
        "U": "AL", "10": "12", "12": "12", "16": "16", "18": "18",
    },
    "GB": {
        "U": "AL", "PG": "6", "12": "12", "12A": "12",
        "15": "16", "18": "18", "R18": "18",
    },
    "DK": {
        "A": "AL", "7": "6", "11": "12", "15": "16",
    },
    "SE": {
        "Btl": "AL", "7": "6", "11": "12", "15": "16",
    },
    "US": {
        "G": "AL", "PG": "6", "PG-13": "12",
        "R": "16", "NC-17": "18",
        "TV-Y": "AL", "TV-Y7": "6", "TV-G": "AL",
        "TV-PG": "9", "TV-14": "14", "TV-MA": "16",
    },
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


def _build_defaults() -> Dict[str, Any]:
    return {
        "inference_countries": list(DEFAULT_INFERENCE_COUNTRIES),
        "mappings": {k: dict(v) for k, v in DEFAULT_RATING_MAPPINGS.items()},
    }


def load_inference_config() -> Dict[str, Any]:
    """
    Load inference config from addon_data.

    Creates the default file on first run. Returns a dict with
    'inference_countries' (list of str) and 'mappings' (dict).
    """
    import xbmcvfs  # noqa: PLC0415 -- late import for testability

    path = _get_config_path()

    if not xbmcvfs.exists(path):
        defaults = _build_defaults()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(defaults, f, indent=2, sort_keys=True)
            log.info("Default config created", event="config.created", path=path)
        except OSError as e:
            log.warning("Failed to write default config", event="config.error",
                        error=str(e))
        return defaults

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        log.debug("Config loaded", path=path)

        countries = data.get("inference_countries")
        mappings = data.get("mappings")
        if not isinstance(countries, list) or not isinstance(mappings, dict):
            log.warning("Invalid config structure, using defaults",
                        event="config.error")
            return _build_defaults()

        norm_mappings: Dict[str, Dict[str, str]] = {}
        for country, table in mappings.items():
            if isinstance(table, dict):
                norm_mappings[country] = {str(k): str(v) for k, v in table.items()}

        return {
            "inference_countries": [str(c) for c in countries],
            "mappings": norm_mappings,
        }
    except (json.JSONDecodeError, OSError) as e:
        log.warning("Failed to load config, using defaults",
                    event="config.error", error=str(e))
        return _build_defaults()
