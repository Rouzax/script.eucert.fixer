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

## Kijkwijzer.nl lookups not working

The Kijkwijzer.nl provider is disabled by default because the website uses bot protection (Akamai) that blocks automated requests. If you have a working connection to kijkwijzer.nl, you can enable it in the addon settings under Country scrapers.

## Log file location

The debug log is at:

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\Kodi\userdata\addon_data\script.eucert.fixer\logs\eucert.log` |
| Linux | `~/.kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |
| macOS | `~/Library/Application Support/Kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |
| LibreELEC | `/storage/.kodi/userdata/addon_data/script.eucert.fixer/logs/eucert.log` |

Log files rotate automatically at 500KB. Rotated files: `eucert.1.log`, `eucert.2.log`, `eucert.3.log`.
