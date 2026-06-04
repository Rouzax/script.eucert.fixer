# Configuration

Open the addon settings at **Add-ons** > **My Add-ons** > **EU Certification Fixer** > **Configure**.

The settings are organized across three tabs: **Providers**, **Ratings**, and **General**.

---

## Providers tab

### API keys

**TMDB API key** (required)

The addon needs a TMDB key to look up ratings. Without it, no scanning happens. Get a free key at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api).

**OMDB API key** (optional)

OMDB is a secondary source used when TMDB has no rating for a title. Without this key, the addon skips the OMDB step and goes straight to applying the fallback after the retry window expires. The free OMDB tier allows 1,000 requests per day. Most libraries will not exceed this. Get a key at [omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx).

### Rating authority scrapers

These settings control whether the addon searches national rating authority websites. Each scraper looks up ratings from a specific country's classification board and converts the result to your country's scale.

| Setting | Default | What it covers |
|---------|---------|----------------|
| **Enable FSK lookup** | On | German film ratings (fsk.de). Free, no key required. |
| **Enable BBFC lookup** | On | British Board of Film Classification (bbfc.co.uk). |
| **Enable Medieraadet lookup** | On | Danish Media Council (medieraadet.dk). Free, no key required. Cinema releases only; TV series are not covered. |
| **Enable Kijkwijzer lookup** | On | Dutch rating authority (kijkwijzer.nl). May stop working if the website changes. |

You do not need to enable all scrapers. If you only care about your own country's ratings and TMDB has good coverage for your library, you can disable scrapers you do not need.

Note that these scrapers depend on the structure of each website. If a site changes, the corresponding scraper may stop working until an addon update is released. See [Troubleshooting](troubleshooting.md) if a scraper produces unexpected results.

### Correction

**Replace incorrect ratings** (default: off)

When this is off, the addon only processes items that have no rating at all. When you turn this on, the addon also replaces existing ratings that are not valid for your selected country, for example if your library was scraped with a different country setting in the past.

---

## Ratings tab

**Country** (default: NL - Kijkwijzer)

Select your country's age rating system. This controls which ratings are considered valid, how ratings from other countries are converted to your scale, and what format is written to your library.

**Rating prefix** (default: set by the country preset)

The prefix is a short text string prepended to the rating value before it is written to Kodi. For example, a prefix of `Rated ` combined with a rating of `12` produces `Rated 12` in your library.

The default for each country matches what the official Kodi TMDB scraper writes. Change this only if your library was previously scraped with a custom format. To check the format your library uses, find an item that already has a rating and look at its info screen.

**Enable fallback rating** (default: on)

When on, the addon applies a configurable default rating to any item that has not been resolved after the retry window (see below). When off, items remain unrated indefinitely if no source has a result.

**Fallback rating** (default: `NR`)

The rating to apply when the retry window expires and no source has returned a result. `NR` means "not rated." You can set this to any valid rating for your country.

**Retry days** (default: `30`)

How many days the addon keeps trying before applying the fallback. New releases often do not have ratings on TMDB immediately. Keeping a longer retry window gives more time for ratings to be added.

---

## General tab

**Scan interval (hours)** (default: `24`)

How often the addon scans your library for unrated items. A scan also runs automatically when Kodi finishes a library update. The minimum is 1 hour; the maximum is 168 hours (7 days).

**API rate limit (seconds)** (default: `0.25`)

How long the addon waits between calls to external services. Increasing this reduces the risk of hitting rate limits on busy rating websites, but makes scans take longer.

**Show notifications** (default: on)

When on, Kodi displays a notification after a scan that found new ratings. The notification shows how many items were updated.

**Enable debug logging** (default: off)

When on, the addon writes detailed information about every step to a separate log file. This is useful when something is not working as expected. The log file is at:

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\Kodi\userdata\addon_data\script.eucert.fixer\logs\eucert.log` |
| Linux | `~/.kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |
| macOS | `~/Library/Application Support/Kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |
| LibreELEC | `/storage/.kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |

See [Troubleshooting](troubleshooting.md) for guidance on reading the log.
