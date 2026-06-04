<p align="center">
  <img src="assets/kijkwijzer-logo-dark.svg" alt="Kijkwijzer" width="400" class="only-light">
  <img src="assets/kijkwijzer-logo.svg" alt="Kijkwijzer" width="400" class="only-dark">
</p>

# EU Certification Fixer

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

EU Certification Fixer runs in the background and periodically scans your library for items without ratings. It checks multiple sources in order:

1. **TMDB direct** -- target country certification
2. **TMDB inferred** -- mapped from culturally similar countries
3. **OMDB** -- US MPAA rating mapped to your target scale
4. **Country scrapers** -- FSK (Germany), BBFC (UK), Kijkwijzer.nl (Netherlands)
5. **Fallback** -- a configurable default after a retry window expires

Items that no source can resolve are tracked and retried on every scan. Only after the retry window expires (default: 30 days) is the fallback rating applied, giving time for new releases to get certifications added to TMDB.

## Supported countries

| Country | System | Ratings |
|---------|--------|---------|
| Netherlands (NL) | Kijkwijzer | AL, 6, 9, 12, 14, 16, 18 |
| Belgium (BE) | Kijkwijzer | AL, 6, 9, 12, 14, 16, 18 |
| Germany (DE) | FSK | 0, 6, 12, 16, 18 |
| Austria (AT) | JMK | 0, 6, 10, 12, 14, 16, 18 |
| United Kingdom (GB) | BBFC | U, PG, 12, 12A, 15, 18, R18 |
| United States (US) | MPAA | G, PG, PG-13, R, NC-17 |
| France (FR) | CNC | U, 10, 12, 16, 18 |
| Denmark (DK) | Medieradet | A, 7, 11, 15 |
| Sweden (SE) | Mediemyndigheten | Btl, 7, 11, 15 |

## Quick start

1. [Install the addon](installation.md)
2. Open the addon settings and enter your [TMDB](https://www.themoviedb.org/settings/api) and [OMDB](https://www.omdbapi.com/apikey.aspx) API keys
3. Select your country from the dropdown
4. The addon starts scanning automatically in the background
