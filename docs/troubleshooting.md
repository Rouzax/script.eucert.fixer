# Troubleshooting

## No ratings are being set

1. **Check your API keys.** Open the addon settings and verify both the TMDB and OMDB keys are entered correctly. Look for `[Kijkwijzer.tmdb]` or `[Kijkwijzer.omdb]` error messages in the Kodi log.

2. **Check the rating prefix.** The prefix must match what your scraper writes. Find an already-rated item in your library and compare its format to the addon's "Rating prefix" setting.

3. **Enable debug logging.** In the addon settings under Advanced, turn on debug logging. Reproduce the issue, then check `addon_data/script.kijkwijzer.ratings/logs/kijkwijzer.log` for details on what each provider returned.

4. **Wait for the first scan.** The addon scans on startup, then every N hours (default: 24). If you just installed it, the first scan may take a few minutes depending on library size.

## Ratings appear but don't match expectations

The addon maps foreign ratings to the target scale using conservative rounding (always rounds to the stricter bracket). If you see a rating that seems too strict, this is by design.

Check the debug log for `tmdb-inferred-{country}` entries to see which country's rating was used and how it was mapped.

## OMDB rate limit errors

The free OMDB tier allows 1,000 requests per day. If you have a large library with many unrated items, you may hit this limit. Solutions:

- Increase the "API rate limit" setting
- Run scans less frequently
- Upgrade to a paid OMDB plan

## Log file location

The debug log is at:

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\Kodi\userdata\addon_data\script.kijkwijzer.ratings\logs\kijkwijzer.log` |
| Linux | `~/.kodi/userdata/addon_data/script.kijkwijzer.ratings/logs/kijkwijzer.log` |
| macOS | `~/Library/Application Support/Kodi/userdata/addon_data/script.kijkwijzer.ratings/logs/kijkwijzer.log` |
| LibreELEC | `/storage/.kodi/userdata/addon_data/script.kijkwijzer.ratings/logs/kijkwijzer.log` |

Log files rotate automatically at 500KB. Rotated files: `kijkwijzer.1.log`, `kijkwijzer.2.log`, `kijkwijzer.3.log`.

## Kijkwijzer.nl lookups not working

The kijkwijzer.nl scraper depends on the site's HTML structure, which may change without notice. If lookups stop working:

1. Check that "Enable kijkwijzer.nl lookup" is on in settings
2. Check the debug log for `[Kijkwijzer.kijkwijzer_provider]` entries
3. If the site structure changed, the scraper may need an update; file an issue on GitHub
