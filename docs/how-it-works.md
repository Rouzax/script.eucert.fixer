# How It Works

## When does the addon scan?

The addon runs as a background service that starts automatically when Kodi boots. It scans your library on startup, after every library update, and on a repeating schedule (default: every 24 hours). The addon does not scan while you are watching a video, to avoid interfering with playback.

## What happens during a scan?

The addon fetches your full movie and TV show lists from Kodi and identifies items that have no age certification. For each uncertified item, it searches several sources in order until one returns a result. As soon as a certification is found, it is written to your library. The item then shows a certification in its info screen.

Items that no source can resolve are remembered and retried on the next scan.

## How the addon finds a certification

When the addon processes an uncertified item, it works through the following steps:

**Step 1: Check TMDB for your country's certification directly.**
TMDB carries age certifications submitted by distributors in many countries. If your chosen country's certification is already there, the addon uses it.

**Step 2: Check TMDB for a certification from a similar country and convert it.**
If TMDB has no certification for your country, the addon checks whether TMDB has a certification from a list of culturally similar countries. If it finds one, it converts that certification to your country's scale. When a foreign certification falls between two values on your country's scale, the stricter of the two is used.

**Step 3: Search national rating authority websites.**
The addon can search the German ([FSK](rating-systems.md#fsk-germany)), British ([BBFC](rating-systems.md#bbfc-united-kingdom)), Danish ([Medieraadet](rating-systems.md#medieraadet-denmark)), and Dutch ([Kijkwijzer](rating-systems.md#kijkwijzer-netherlands-belgium)) rating authority websites directly. Each enabled scraper searches for the title and returns a certification from that authority's own database. The result is then converted to your country's scale using the same conservative approach described above.

You can enable or disable each scraper in the addon settings. The scraper for your own country runs first, since its certification needs no conversion.

**Step 4: Check OMDB.**
OMDB is an independent database that carries US MPAA certifications. The addon looks up the title by its IMDB ID and converts the US certification to your country's scale.

**Step 5: Apply a not-found certification after 30 days.**
If none of the above steps found a result, the item is tracked internally. On every subsequent scan, the addon tries all the steps above again. After 30 days (configurable) without a result, the addon applies the not-found certification you have configured (default: `NR`). This delay gives time for new releases to receive certifications in TMDB before the addon gives up.

## What "converting" a certification means

Each country uses its own age rating scale with its own age thresholds. When the addon converts a certification from one country to another, it uses a mapping table that defines the closest equivalent on the target scale. If a certification falls between two thresholds on the target scale, the stricter option is always chosen to avoid under-certifying content.

The addon checks countries in order of cultural similarity. For example, when you select Germany, the addon checks Austria first (same language and similar classification culture) before checking more distant systems like the US. This order improves accuracy because culturally similar countries tend to classify content in similar ways.

For a detailed walkthrough of how this works, including a step-by-step example and a comparison of how different systems weigh violence, language, and sexual content, see [Rating Systems: How certifications are converted](rating-systems.md#how-ratings-are-converted).

## How the addon tracks unresolved items

When no source returns a result for an item, the addon stores the item's title and the date it was first seen without a certification. This information is saved in two files in the addon's data directory:

- `trackers/unresolved_movies.json`
- `trackers/unresolved_tvshows.json`

These files are updated automatically. You do not need to edit them.

## What the addon does not do

The addon only fills in items that are missing a certification. It does not modify items that already have a certification unless you enable "Replace incorrect certifications" in the settings. It does not change any other metadata fields (title, artwork, description, etc.).
