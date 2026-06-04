# How It Works

The addon resolves ratings to your selected country's scale. Each country preset defines valid ratings, an inference chain of culturally similar countries, and mapping tables to convert between scales.

## Lookup tiers

When the addon finds an item with an empty rating, it checks sources in order. The first source to return a result wins.

### Tier 1: TMDB direct

Queries TMDB for the target country's certification. For movies this uses the `/movie/{id}/release_dates` endpoint; for TV shows, `/tv/{id}/content_ratings`.

### Tier 2: TMDB inferred

When the target country has no certification on TMDB, the addon checks other countries ordered by cultural similarity and maps their rating to the target scale. Each country preset defines its own inference chain. For example, the NL preset checks:

| Priority | Country | System |
|----------|---------|--------|
| 1 | Belgium (BE) | Kijkwijzer (same system as NL) |
| 2 | Germany (DE) | FSK |
| 3 | Austria (AT) | JMK |
| 4 | France (FR) | CNC |
| 5 | United Kingdom (GB) | BBFC |
| 6 | Denmark (DK) | Medieradet |
| 7 | Sweden (SE) | Mediemyndigheten |
| 8 | United States (US) | MPAA |

All mappings use conservative rounding (when a rating falls between two brackets, the stricter one is used).

### Tier 3: OMDB

Queries the Open Movie Database by IMDB ID. The US MPAA "Rated" field is mapped to the target scale via the US mapping table in the preset.

### Tier 4: Country scrapers

Each enabled scraper searches a national rating agency's website or API and returns the agency's native rating. The rating is then mapped to your target country's scale using the preset's mapping tables.

| Scraper | Country | Method | Notes |
|---------|---------|--------|-------|
| **FSK** | Germany (DE) | REST API | Free, unauthenticated. Searches by title with IMDB ID cross-reference. Supports year filtering for disambiguation. |
| **BBFC** | United Kingdom (GB) | Web scraping | Parses structured JSON from the BBFC website. Filters by Film or TV Show type. |
| **Medieraadet** | Denmark (DK) | JSON API | Free, unauthenticated. Searches by title with article stripping and year filtering. Cinema releases only, no TV series. |
| **Kijkwijzer** | Netherlands (NL) | AJAX search API | Uses the site's AJAX search API. Returns ratings directly from search results. Handles inverted titles (e.g. "Matrix, The"). |

If the scraper's native rating has no mapping to your target country, the result is discarded and the next scraper is tried.

### Tier 5: Fallback

After all sources have been exhausted, the item enters the retry tracker. On each subsequent scan, all sources are tried again. Only after the configured retry window (default: 30 days) has passed without a result is the fallback rating applied.

## Retry tracking

Items that no source can resolve are tracked in JSON files stored in the addon's data directory:

- `trackers/unresolved_movies.json`
- `trackers/unresolved_tvshows.json`

Each entry records the date the item was first seen without a rating. On every scan, all sources are retried. This gives time for new releases to get certifications added to TMDB.

## Cross-cultural mapping

Each country preset ships mapping tables for converting ratings from all other supported countries. Mappings follow these principles:

- "All ages" ratings always map to the target's "all ages" bracket
- "Adult only" ratings always map to the target's maximum bracket
- Intermediate ratings map to the nearest bracket in the target scale
- When equidistant between two brackets, the stricter one is used (conservative rounding)

## Background service

The addon runs as a Kodi service that starts automatically when Kodi boots. It scans the library on startup, after library updates, and on a configurable interval (default: every 24 hours).

The service respects Kodi's shutdown requests and stops cleanly when Kodi exits.
