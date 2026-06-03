# Configuration

All settings are in the addon's settings dialog: **Add-ons** > **My Add-ons** > **Kijkwijzer Ratings** > **Configure**.

## API Keys

| Setting | Description |
|---------|-------------|
| **TMDB API key** | Required. Get one at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api). Used for direct and inferred rating lookups. |
| **OMDB API key** | Optional but recommended. Get one at [omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx). Used as a fallback when TMDB has no rating. Free tier allows 1,000 requests/day. |

## Ratings

| Setting | Default | Description |
|---------|---------|-------------|
| **Target country** | `NL` | ISO 3166-1 country code for the rating system you want. |
| **Rating prefix** | `Rated ` | Text prepended to the rating value. Must match your scraper's format. Check an existing rated item in your library to see what format it uses. |
| **Fallback rating** | `NR` | Applied when no source can find a result and the retry window has expired. Leave empty to skip items permanently. |
| **Retry days** | `30` | Days to keep retrying before applying the fallback. New releases often get certifications added to TMDB after their initial release. |

### Matching the rating prefix

The prefix must match what your Kodi scraper writes. To check:

1. Find an item in your library that already has a rating
2. Look at its Info screen; note the format (e.g., "Rated 12" or just "12")
3. Set the prefix accordingly ("Rated " with trailing space, or empty)

## Providers

| Setting | Default | Description |
|---------|---------|-------------|
| **Enable kijkwijzer.nl lookup** | On | Search the Dutch rating authority's website when TMDB and OMDB have no result. Disable if you are not targeting the Dutch rating system. |

## Schedule

| Setting | Default | Description |
|---------|---------|-------------|
| **Scan interval (hours)** | `24` | How often the background service checks for items with missing ratings. |
| **API rate limit (seconds)** | `0.25` | Delay between external API calls. Increase if you hit rate limits. |

## Advanced

| Setting | Default | Description |
|---------|---------|-------------|
| **Enable debug logging** | Off | Write detailed diagnostic information to a separate log file at `addon_data/script.kijkwijzer.ratings/logs/kijkwijzer.log`. |
