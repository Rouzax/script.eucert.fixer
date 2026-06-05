# Troubleshooting

## No ratings are being set

**Check your TMDB API key.**
Open the addon settings and verify the TMDB API key is entered correctly. Without a valid key, the addon cannot scan at all. If the key is wrong, try deleting and retyping it.

**Wait for the first scan.**
The addon scans on startup and then on a schedule (default: every 24 hours). If you just installed the addon, the first scan may still be running. A large library with many unrated items can take several minutes to process.

**Restart Kodi after installation.**
If Kodi was already running when you installed the addon, the background service may not have started. Restart Kodi so the service starts fresh.

**Check the certification prefix.**
The prefix must match what your Kodi scraper already writes to the library. Find an item that already has a certification and check its format on the info screen (for example, `NL:12` or `Rated PG-13`). By default the addon uses the prefix from your country preset. If your scraper uses a different format, enable **Override certification prefix** in the advanced settings and set it to match.

**Enable debug logging.**
In the addon settings under **General**, turn on debug logging. Then go to **Programs** > **Add-ons** > **EU Certification Fixer** to trigger a scan. Check the log file for details on what the addon found and did not find. See [Log file location](#log-file-location) below.

---

## Ratings appear but seem wrong

The addon always picks the stricter of two options when converting a rating from one country's scale to another. A rating that seems too strict is the addon choosing the safer side of a borderline case. This is by design.

If you see a rating that seems completely incorrect (not just stricter than expected), enable debug logging and check the log to see which source provided the rating and how it was converted. If the mapping looks wrong, [report it on GitHub](https://github.com/Rouzax/script.eucert.fixer/issues/new) with the title, the rating that was applied, and the source shown in the log.

---

## API rate limit errors in the log

The OMDB free tier allows 1,000 requests per day. If you have a large library with many unrated items, you may reach this limit. When this happens, the addon logs the error and skips OMDB for the rest of that scan. OMDB will work again the next day.

To reduce how quickly you reach the limit:

- Increase the "API rate limit" setting so requests are spaced further apart.
- Reduce how often the addon scans by increasing the scan interval.
- Upgrade to a paid OMDB plan if the limit is a recurring problem.

---

## Some titles are not found by scrapers

Each scraper searches for a title by name. The addon handles accented characters (for example, "Pokémon" matches "Pokemon"), common article inversions ("Matrix, The" matches "The Matrix"), and TV series with season suffixes ("Pokémon: XY" matches a search for "Pokémon"). If the name in your Kodi library still differs from the name used by the rating authority, the scraper may not find a match. Common causes:

- **Completely different title.** Some titles are translated or localized. The addon searches using your Kodi library title, which may not match the name the rating authority uses.
- **Year mismatches (movies).** For movies, the addon filters results by release year to avoid false matches on common titles. If the year in your library metadata differs from the year the rating authority used, the result may be skipped. TV shows are not year-filtered because rating authorities often classify seasons years after the original air date.
- **New releases.** Title databases at rating authorities are not always up to date immediately after release.
- **TV series.** The Danish Medieraadet scraper covers cinema releases only; TV series are not in its database.

If a specific title is repeatedly not found, enable debug logging and check the log to see which scrapers were tried, how many results they returned, and why none matched. If you believe the addon should have found the title, [report it on GitHub](https://github.com/Rouzax/script.eucert.fixer/issues/new) and include the relevant lines from the debug log.

---

## A scraper stopped working for all titles

Each scan cycle, the addon checks whether each enabled scraper is working by looking up a known title and verifying the result. If this check fails, the addon logs a warning.

If you see a warning that a scraper's health check failed, this usually means the rating authority's website has changed in a way that broke the addon's ability to search it. This is not something you can fix by changing settings. Check the [GitHub releases page](https://github.com/Rouzax/script.eucert.fixer/releases) for an updated version of the addon that fixes the issue, or file a report at the [GitHub issues page](https://github.com/Rouzax/script.eucert.fixer/issues).

While a scraper is broken, ratings from that authority will not be found, but all other sources continue to work normally.

---

## Log file location

Enable debug logging in the addon settings under **General**, then check the log file at:

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\Kodi\userdata\addon_data\script.eucert.fixer\logs\eucert.log` |
| Linux | `~/.kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |
| macOS | `~/Library/Application Support/Kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |
| LibreELEC | `/storage/.kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |

Log files rotate automatically at 500 KB. When the log file reaches that size, it is renamed to `eucert.1.log` and a new `eucert.log` is started. Up to three rotated files are kept.
