# Configuration

All settings are in the addon's settings dialog: **Add-ons** > **My Add-ons** > **EU Certification Fixer** > **Configure**.

## API Keys

| Setting | Description |
|---------|-------------|
| **TMDB API key** | Required. Get one at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api). Used for direct and inferred rating lookups. |
| **OMDB API key** | Optional but recommended. Get one at [omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx). Used as a fallback when TMDB has no rating. Free tier allows 1,000 requests/day. |

## Country Scrapers

These providers search national rating agency websites directly. Each returns the agency's native rating, which is mapped to your target country's scale automatically.

| Setting | Default | Description |
|---------|---------|-------------|
| **Enable FSK lookup** | On | Search the German rating authority (fsk.de). Free API, no key required. |
| **Enable BBFC lookup** | On | Search the British Board of Film Classification (bbfc.co.uk). Uses web scraping. |
| **Enable Medieraadet lookup** | On | Search the Danish Media Council (medieraadet.dk) for ratings. Free API, no key required. |
| **Enable Kijkwijzer lookup** | On | Search the Dutch rating authority (kijkwijzer.nl). Uses the site's search API, which may break if the website changes. |

## Correction

| Setting | Default | Description |
|---------|---------|-------------|
| **Replace incorrect ratings** | Off | Also replace existing ratings that are not valid for your selected country. When off, only items with no rating are processed. |

## Ratings

| Setting | Default | Description |
|---------|---------|-------------|
| **Country** | NL - Kijkwijzer | Select your country's age rating system. Determines which ratings are valid and how foreign ratings are mapped. |
| **Rating prefix** | *(from preset)* | Text prepended to the rating value. Leave empty to use the default for your country. Must match your scraper's format. |
| **Enable fallback rating** | On | Apply a default rating after the retry window expires. |
| **Fallback rating** | `NR` | Rating to apply when no source can find a result and the retry window has expired. |
| **Retry days** | `30` | Days to keep retrying before applying the fallback. New releases often get certifications added to TMDB after their initial release. |

### Matching the rating prefix

The prefix must match what your Kodi scraper writes. To check:

1. Find an item in your library that already has a rating
2. Look at its Info screen; note the format (e.g., "NL:12" or "Rated PG-13")
3. If it differs from the preset default, set the prefix accordingly in the advanced settings

## Schedule

| Setting | Default | Description |
|---------|---------|-------------|
| **Scan interval (hours)** | `24` | How often the background service checks for items with missing ratings. A scan also runs automatically after each library update. |
| **API rate limit (seconds)** | `0.25` | Delay between external API calls. Increase if you hit rate limits. |

## Notifications

| Setting | Default | Description |
|---------|---------|-------------|
| **Show notifications** | On | Show a Kodi notification after a scan completes with new ratings. |

## Debugging

| Setting | Default | Description |
|---------|---------|-------------|
| **Enable debug logging** | Off | Write detailed diagnostic information to a separate log file at `addon_data/script.eucert.fixer/logs/eucert.log`. |
