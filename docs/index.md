<p align="center">
  <img src="assets/kijkwijzer-logo-dark.svg" alt="Kijkwijzer" width="400" class="only-light">
  <img src="assets/kijkwijzer-logo.svg" alt="Kijkwijzer" width="400" class="only-dark">
</p>

# Kijkwijzer Ratings

<p align="center">
  <img src="assets/al.svg" alt="AL" width="40">
  <img src="assets/6.svg" alt="6" width="40">
  <img src="assets/9.svg" alt="9" width="40">
  <img src="assets/12.svg" alt="12" width="40">
  <img src="assets/14.svg" alt="14" width="40">
  <img src="assets/16.svg" alt="16" width="40">
  <img src="assets/18.svg" alt="18" width="40">
</p>

Automatically backfill missing age ratings for movies and TV shows in your Kodi library.

## The problem

Kodi's TMDB scraper only fetches age ratings for one configured country. When that country's certification is missing on TMDB, the movie or TV show gets no rating at all.

## The solution

Kijkwijzer Ratings runs in the background and periodically scans your library for items without ratings. It checks multiple sources in order:

1. **TMDB direct** -- target country certification
2. **TMDB inferred** -- mapped from culturally similar countries
3. **OMDB** -- US MPAA rating mapped to your target scale
4. **Kijkwijzer.nl** -- the Dutch rating authority's website
5. **Fallback** -- a configurable default after a retry window expires

Items that no source can resolve are tracked and retried on every scan. Only after the retry window expires (default: 30 days) is the fallback rating applied, giving time for new releases to get certifications added to TMDB.

## Quick start

1. [Install the addon](installation.md)
2. Open the addon settings and enter your [TMDB](https://www.themoviedb.org/settings/api) and [OMDB](https://www.omdbapi.com/apikey.aspx) API keys
3. The addon starts scanning automatically in the background

No other configuration is needed for most users. The defaults target the Dutch (NL) Kijkwijzer rating system.
