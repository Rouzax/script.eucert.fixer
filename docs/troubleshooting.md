# Troubleshooting

## No ratings are being set

1. **Check your API keys.** Open the addon settings and verify both the TMDB and OMDB keys are entered correctly. Look for `[EUCert.tmdb]` or `[EUCert.omdb]` error messages in the Kodi log.

2. **Check the rating prefix.** The prefix must match what your scraper writes. Find an already-rated item in your library and compare its format to the addon's "Rating prefix" setting (under advanced settings).

3. **Enable debug logging.** In the addon settings under Debugging, turn on debug logging. Reproduce the issue, then check `addon_data/script.eucert.fixer/logs/eucert.log` for details on what each provider returned.

4. **Wait for the first scan.** The addon scans on startup, then every N hours (default: 24). If you just installed it, the first scan may take a few minutes depending on library size.

## Ratings appear but don't match expectations

The addon maps foreign ratings to the target scale using conservative rounding (always rounds to the stricter bracket). If you see a rating that seems too strict, this is by design.

Check the debug log for `tmdb-inferred-{country}` entries to see which country's rating was used and how it was mapped.

## OMDB rate limit errors

The free OMDB tier allows 1,000 requests per day. If you have a large library with many unrated items, you may hit this limit. Solutions:

- Increase the "API rate limit" setting
- Run scans less frequently
- Upgrade to a paid OMDB plan

## FSK lookups returning wrong results

The FSK provider searches by title and cross-references IMDB IDs from the response. For films with common titles (e.g., "Bambi"), multiple results may exist. The provider uses year filtering (when available from Kodi metadata) to narrow results, but older films may not match because FSK rating dates differ from release dates.

## BBFC lookups not working

The BBFC provider scrapes the bbfc.co.uk website. If the website changes its structure, lookups may stop returning results. Check the debug log for `[EUCert.bbfc]` entries. If the site structure changed, file an issue on GitHub.

## Medieraadet lookups not working

The Medieraadet provider uses a JSON API with an embedded key. If the key changes after a site redeployment, lookups will return no results. Check the debug log for `[EUCert.medieraadet]` entries. File an issue on GitHub if the API stops working.

## Kijkwijzer.nl lookups not working

The Kijkwijzer provider uses an AJAX search endpoint with specific headers and a cookie. If the site is redesigned or the endpoint changes, lookups will stop working. Check the debug log for `[EUCert.kijkwijzer_provider]` entries. If you see "Challenge Validation" in the logged response, the bot protection is blocking requests.

## Scraper canary warnings

Each scan cycle tests the enabled scrapers with a known title to verify they are working. If a test fails, a warning is logged:

- `scraper.canary_fail` means the scraper returned no result
- `scraper.canary_mismatch` means it returned an unexpected rating

These warnings indicate the scraper's website may have changed. Check for addon updates or file an issue on GitHub.

## Log file location

The debug log is at:

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\Kodi\userdata\addon_data\script.eucert.fixer\logs\eucert.log` |
| Linux | `~/.kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |
| macOS | `~/Library/Application Support/Kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |
| LibreELEC | `/storage/.kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |

Log files rotate automatically at 500KB. Rotated files: `eucert.1.log`, `eucert.2.log`, `eucert.3.log`.
