# Configuration

Open the addon settings at **Add-ons** > **My Add-ons** > **EU Certification Fixer** > **Configure**.

The settings are organized across three tabs: **Providers**, **Ratings**, and **General**.

---

## Providers tab

### API keys

**TMDB API key** (required)

The addon needs a TMDB key to look up certifications. Without it, no scanning happens. Get a free key at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api).

**OMDB API key** (optional)

OMDB is a last-resort source that carries US MPAA certifications. Without this key, the addon skips the OMDB step. The free tier allows 1,000 requests per day. Most EU libraries will not need this. Get a key at [omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx).

### Rating authority scrapers

These settings control whether the addon searches national rating authority websites. Each scraper looks up certifications from a specific country's classification board and converts the result to your country's scale.

| Setting | Default | What it covers |
|---------|---------|----------------|
| **Enable FSK lookup** | On | [FSK](rating-systems.md#fsk-germany) German film certifications (fsk.de). |
| **Enable BBFC lookup** | On | [BBFC](rating-systems.md#bbfc-united-kingdom) British Board of Film Classification (bbfc.co.uk). |
| **Enable Medieraadet lookup** | On | [Medieraadet](rating-systems.md#medieraadet-denmark) Danish Media Council (medieraadet.dk). Cinema releases only; TV series are not covered. |
| **Enable Kijkwijzer lookup** | On | [Kijkwijzer](rating-systems.md#kijkwijzer-netherlands-belgium) Dutch rating authority (kijkwijzer.nl). |

You do not need to enable all scrapers. If you only care about your own country's certifications and TMDB has good coverage for your library, you can disable scrapers you do not need.

Note that these scrapers depend on the structure of each website. If a site changes, the corresponding scraper may stop working until an addon update is released. See [Troubleshooting](troubleshooting.md) if a scraper produces unexpected results.

### Correction

**Replace incorrect certifications** (default: off)

When this is off, the addon only processes items that have no certification at all. When you turn this on, the addon also checks existing certifications and replaces them if they do not match your selected country. Specifically, the addon replaces a certification when:

- It has the wrong prefix (for example, `Rated PG-13` when your country expects `DE:` prefixed certifications).
- The certification value is not valid for your country's system (for example, an MPAA certification like `R` when your country uses FSK).

Certifications that already have the correct prefix and a valid value for your country are left untouched. The configured not-found certification (default: `NR`) is also preserved.

This setting is useful when your library was previously scraped with a different country or prefix setting, or when your metadata scraper and the addon use different prefix formats. See the [installation guide](installation.md) for advice on matching your scraper settings.

---

## Ratings tab

**Country** (default: NL - Kijkwijzer)

Select your country's age rating system. This controls which certifications are considered valid, how certifications from other countries are converted to your scale, and what format is written to your library.

**Override certification prefix** (default: off, advanced setting)

The certification prefix is a short text string prepended to the certification value before it is written to Kodi. For example, a prefix of `NL:` combined with a certification of `12` produces `NL:12` in your library.

By default, the prefix is set automatically by your selected country preset (for example, `NL:` for Netherlands, `DE:` for Germany, `Rated ` for the US). Switching countries changes the prefix automatically.

If you need a custom prefix, enable **Override certification prefix** in the advanced settings. A text field appears where you can type any prefix you want. Leave it empty to write certifications with no prefix at all.

**Apply certification when not found** (default: on)

When on, the addon applies a configurable default certification to any item that has not been resolved after the retry window (see below). When off, items remain without a certification indefinitely if no source has a result.

**Not-found certification** (default: `NR`)

The certification to apply when the retry window expires and no source has returned a result. `NR` means "not rated." You can set this to any valid certification for your country.

**Retry days** (default: `30`)

How many days the addon keeps trying before applying the not-found certification. New releases often do not have certifications on TMDB immediately. Keeping a longer retry window gives more time for certifications to be added.

---

## General tab

**Scan interval (hours)** (default: `24`)

How often the addon scans your library for uncertified items. A scan also runs automatically when Kodi finishes a library update. The minimum is 1 hour; the maximum is 168 hours (7 days).

**API rate limit (seconds)** (default: `0.25`)

How long the addon waits between calls to external services. Increasing this reduces the risk of hitting rate limits on busy rating authority websites, but makes scans take longer.

**Show notifications** (default: on)

When on, Kodi displays a notification after a scan that found new certifications. The notification shows how many items were updated.

**Enable debug logging** (default: off)

When on, the addon writes detailed information about every step to a separate log file. This is useful when something is not working as expected. The log file is at:

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\Kodi\userdata\addon_data\script.eucert.fixer\logs\eucert.log` |
| Linux | `~/.kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |
| macOS | `~/Library/Application Support/Kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |
| LibreELEC | `/storage/.kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |

See [Troubleshooting](troubleshooting.md) for guidance on reading the log.
