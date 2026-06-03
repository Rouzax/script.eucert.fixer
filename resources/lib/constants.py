"""Centralized constants for Kijkwijzer Ratings addon."""
from __future__ import annotations

# =============================================================================
# Addon Identity
# =============================================================================

DEFAULT_ADDON_ID = "script.kijkwijzer.ratings"
ADDON_PREFIX = "Kijkwijzer"

# =============================================================================
# Logging
# =============================================================================

LOG_DIR_NAME = "logs"
LOG_FILENAME = "kijkwijzer.log"
LOG_MAX_SIZE_BYTES = 512 * 1024  # 500KB per file
LOG_MAX_ROTATED_FILES = 3
LOG_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
LOG_TIMESTAMP_TRIM = -3  # Trim microseconds to milliseconds
LOG_MAX_VALUE_LENGTH = 200

# =============================================================================
# Service
# =============================================================================

KODI_HOME_WINDOW_ID = 10000

# Default scan interval in hours
DEFAULT_SCAN_INTERVAL_HOURS = 24

# Sleep granularity: how often the service loop checks for abort (seconds)
SERVICE_SLEEP_INTERVAL_SEC = 1

# Rate limit between external API calls (seconds)
DEFAULT_RATE_LIMIT_SEC = 0.25

# Days to retry unresolved items before applying fallback
DEFAULT_RETRY_DAYS = 30

# =============================================================================
# Rating Defaults
# =============================================================================

DEFAULT_TARGET_COUNTRY = "NL"
DEFAULT_RATING_PREFIX = "Rated "
DEFAULT_FALLBACK_RATING = "NR"

# Valid Kijkwijzer age ratings
VALID_RATINGS = ("AL", "6", "9", "12", "14", "16", "18")

# Inference country chain: ordered by cultural similarity to NL.
# Each country's ratings get mapped to the target scale.
INFERENCE_COUNTRIES = ["BE", "DE", "AT", "FR", "GB", "DK", "SE", "US"]

# Rating mappings: foreign country rating -> NL Kijkwijzer equivalent.
# Conservative rounding: always maps to the stricter bracket.
RATING_MAPPINGS = {
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

# =============================================================================
# Tracker
# =============================================================================

TRACKER_DIR = "trackers"
TRACKER_MOVIES_FILENAME = "unresolved_movies.json"
TRACKER_TVSHOWS_FILENAME = "unresolved_tvshows.json"

# =============================================================================
# External APIs
# =============================================================================

TMDB_BASE_URL = "https://api.themoviedb.org/3"
OMDB_BASE_URL = "https://www.omdbapi.com/"
KIJKWIJZER_SEARCH_URL = "https://www.kijkwijzer.nl/zoeken/"
KIJKWIJZER_USER_AGENT = "Kodi-Kijkwijzer/1.0 (Kodi addon; https://github.com/Rouzax/script.kijkwijzer.ratings)"
