# How It Works

The addon resolves ratings to the Dutch Kijkwijzer scale:

<p>
  <img src="assets/al.svg" alt="AL" width="36">
  <img src="assets/6.svg" alt="6" width="36">
  <img src="assets/9.svg" alt="9" width="36">
  <img src="assets/12.svg" alt="12" width="36">
  <img src="assets/14.svg" alt="14" width="36">
  <img src="assets/16.svg" alt="16" width="36">
  <img src="assets/18.svg" alt="18" width="36">
</p>

## Lookup tiers

When the addon finds an item with an empty rating, it checks sources in order. The first source to return a result wins.

### Tier 1: TMDB direct

Queries TMDB for the target country's certification. For movies this uses the `/movie/{id}/release_dates` endpoint; for TV shows, `/tv/{id}/content_ratings`.

### Tier 2: TMDB inferred

When the target country has no certification on TMDB, the addon checks other countries ordered by cultural similarity and maps their rating to the target scale:

| Priority | Country | System |
|----------|---------|--------|
| 1 | Belgium (BE) | Kijkwijzer (same system as NL) |
| 2 | Germany (DE) | FSK |
| 3 | Austria (AT) | ABMC |
| 4 | France (FR) | CNC |
| 5 | United Kingdom (GB) | BBFC |
| 6 | Denmark (DK) | Medieradet |
| 7 | Sweden (SE) | Swedish Media Council |
| 8 | United States (US) | MPAA |

US is last because its rating philosophy differs from European norms: conservative on nudity but lenient on violence.

All mappings use conservative rounding (always maps to the stricter bracket).

### Tier 3: OMDB

Queries the Open Movie Database by IMDB ID. The US MPAA "Rated" field is mapped to the target scale via the US mapping table.

### Tier 4: Kijkwijzer.nl

Searches the Dutch rating authority's website by title and scrapes the detail page for the age rating. Only used when enabled in settings.

### Tier 5: Fallback

After all sources have been exhausted, the item enters the retry tracker. On each subsequent scan, all sources are tried again. Only after the configured retry window (default: 30 days) has passed without a result is the fallback rating applied.

## Retry tracking

Items that no source can resolve are tracked in JSON files stored in the addon's data directory:

- `trackers/unresolved_movies.json`
- `trackers/unresolved_tvshows.json`

Each entry records the date the item was first seen without a rating. On every scan, all sources are retried. This gives time for new releases to get certifications added to TMDB.

## Background service

The addon runs as a Kodi service that starts automatically when Kodi boots. It scans the library on startup and then on a configurable interval (default: every 24 hours).

The service respects Kodi's shutdown requests and stops cleanly when Kodi exits.
