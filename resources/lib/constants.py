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

# Seconds to wait after library scan/clean finishes before triggering a rating scan
LIBRARY_SCAN_DEBOUNCE_SEC = 60

# =============================================================================
# Rating Defaults
# =============================================================================

DEFAULT_TARGET_COUNTRY = "NL"
DEFAULT_RATING_PREFIX = "NL:"
DEFAULT_FALLBACK_RATING = "NR"

# Valid Kijkwijzer age ratings
VALID_RATINGS = ("AL", "6", "9", "12", "14", "16", "18")
KNOWN_RATING_PREFIXES = ("Rated ",)

# =============================================================================
# Tracker
# =============================================================================

TRACKER_DIR = "trackers"
TRACKER_MOVIES_FILENAME = "unresolved_movies.json"
TRACKER_TVSHOWS_FILENAME = "unresolved_tvshows.json"

# =============================================================================
# Inference Config
# =============================================================================

CONFIG_DIR = "config"
CONFIG_FILENAME = "inference.json"

# =============================================================================
# External APIs
# =============================================================================

TMDB_BASE_URL = "https://api.themoviedb.org/3"
OMDB_BASE_URL = "https://www.omdbapi.com/"
KIJKWIJZER_SEARCH_URL = "https://www.kijkwijzer.nl/zoeken/"
KIJKWIJZER_USER_AGENT = "Kodi-Kijkwijzer/1.0 (Kodi addon; https://github.com/Rouzax/script.kijkwijzer.ratings)"
