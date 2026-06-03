"""
Media type definitions for movies and TV shows.

Each MediaType captures all the differences between content types:
JSON-RPC methods, TMDB endpoints, and response parsers. All other
code is generic across media types.

Logging:
    No logging in this module (pure data definitions).
"""
from __future__ import annotations

from typing import Callable, Dict, List


class MediaType:
    """Immutable media type definition."""

    def __init__(
        self,
        name: str,
        label: str,
        kodi_list_method: str,
        kodi_set_method: str,
        kodi_id_field: str,
        kodi_result_key: str,
        tmdb_endpoint: str,
        tmdb_parse_certs: Callable[[List[Dict]], Dict[str, str]],
        tracker_filename: str,
    ) -> None:
        self.name = name
        self.label = label
        self.kodi_list_method = kodi_list_method
        self.kodi_set_method = kodi_set_method
        self.kodi_id_field = kodi_id_field
        self.kodi_result_key = kodi_result_key
        self.tmdb_endpoint = tmdb_endpoint
        self.tmdb_parse_certs = tmdb_parse_certs
        self.tracker_filename = tracker_filename


def _parse_movie_certs(results: List[Dict]) -> Dict[str, str]:
    """Parse TMDB /movie/{id}/release_dates response."""
    certs: Dict[str, str] = {}
    for entry in results:
        country = entry.get("iso_3166_1", "")
        for rd in entry.get("release_dates", []):
            if rd.get("certification"):
                certs[country] = rd["certification"]
                break
    return certs


def _parse_tv_certs(results: List[Dict]) -> Dict[str, str]:
    """Parse TMDB /tv/{id}/content_ratings response."""
    return {
        r["iso_3166_1"]: r["rating"]
        for r in results
        if r.get("rating")
    }


MOVIE = MediaType(
    name="movie",
    label="Movie",
    kodi_list_method="VideoLibrary.GetMovies",
    kodi_set_method="VideoLibrary.SetMovieDetails",
    kodi_id_field="movieid",
    kodi_result_key="movies",
    tmdb_endpoint="/movie/{id}/release_dates",
    tmdb_parse_certs=_parse_movie_certs,
    tracker_filename="unresolved_movies.json",
)

TVSHOW = MediaType(
    name="tvshow",
    label="TV Show",
    kodi_list_method="VideoLibrary.GetTVShows",
    kodi_set_method="VideoLibrary.SetTVShowDetails",
    kodi_id_field="tvshowid",
    kodi_result_key="tvshows",
    tmdb_endpoint="/tv/{id}/content_ratings",
    tmdb_parse_certs=_parse_tv_certs,
    tracker_filename="unresolved_tvshows.json",
)
