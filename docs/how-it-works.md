# How It Works

## When does the addon scan?

The addon runs as a background service that starts automatically when Kodi boots. It scans your library on startup, after every library update, and on a repeating schedule (default: every 24 hours).

## What happens during a scan?

The addon fetches your full movie and TV show lists from Kodi and identifies items that have no age rating. For each unrated item, it searches several sources in order until one returns a result. As soon as a rating is found, it is written to your library. The item then shows a rating in its info screen.

Items that no source can resolve are remembered and retried on the next scan.

## How the addon finds a rating

When the addon processes an unrated item, it works through the following steps:

**Step 1: Check TMDB for your country's rating directly.**
TMDB carries age certifications submitted by distributors in many countries. If your chosen country's rating is already there, the addon uses it.

**Step 2: Check TMDB for a rating from a similar country and convert it.**
If TMDB has no rating for your country, the addon checks whether TMDB has a rating from a list of culturally similar countries. If it finds one, it converts that rating to your country's scale. When a foreign rating falls between two values on your country's scale, the stricter of the two is used.

**Step 3: Search national rating authority websites.**
The addon can search the German (FSK), British (BBFC), Danish (Medieraadet), and Dutch (Kijkwijzer) rating authority websites directly. Each enabled scraper searches for the title and returns a rating from that authority's own database. The result is then converted to your country's scale using the same conservative approach described above.

You can enable or disable each scraper in the addon settings. The scraper for your own country runs first, since its rating needs no conversion.

**Step 4: Check OMDB.**
OMDB is an independent database that carries US MPAA ratings. The addon looks up the title by its IMDB ID and converts the US rating to your country's scale.

**Step 5: Apply a fallback after 30 days.**
If none of the above steps found a result, the item is tracked internally. On every subsequent scan, the addon tries all the steps above again. After 30 days (configurable) without a result, the addon applies the fallback rating you have configured (default: `NR`). This delay gives time for new releases to receive certifications in TMDB before the addon gives up.

## What "converting" a rating means

Each country uses its own age rating scale with its own age thresholds. When the addon converts a German FSK rating to a Dutch Kijkwijzer rating, for example, it compares the age thresholds and picks the nearest match. If a rating falls between two thresholds on the target scale, the stricter option is always chosen to avoid under-rating content.

## How the addon tracks unresolved items

When no source returns a result for an item, the addon stores the item's title and the date it was first seen unrated. This information is saved in two files in the addon's data directory:

- `trackers/unresolved_movies.json`
- `trackers/unresolved_tvshows.json`

These files are updated automatically. You do not need to edit them.

## What the addon does not do

The addon only fills in items that are missing a rating. It does not modify items that already have a rating unless you enable "Replace incorrect ratings" in the settings. It does not change any other metadata fields (title, artwork, description, etc.).
