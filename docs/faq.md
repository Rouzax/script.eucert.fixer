# FAQ

## Why is my rating too strict?

The addon uses conservative rounding when mapping between rating systems. When a foreign rating falls between two brackets in your system, the stricter bracket is chosen. This is by design to avoid under-rating content.

## Which scrapers work for my country?

All enabled scrapers work for all countries. Each scraper returns its native rating, which is automatically mapped to your selected country's scale. FSK returns German ratings, BBFC returns UK ratings, Medieraadet returns Danish ratings, and Kijkwijzer returns Dutch ratings.

## Can I customize the rating mappings?

Yes. The addon stores its active configuration in `addon_data/script.eucert.fixer/config/inference.json`. You can edit the inference countries list and the mapping tables. The valid ratings list always comes from the country preset and cannot be overridden. Changing your country in settings resets this file to the preset defaults.

## Why didn't the addon find a rating for a specific title?

Enable debug logging in settings and check `eucert.log`. The log shows which tiers were tried and what each returned. Common reasons: the title is too new for TMDB, the OMDB free tier limit was hit, or the scrapers could not match the title (often due to different naming between your library and the rating agency's database).

## Can I run this on multiple Kodi instances sharing a database?

Yes, but only enable the addon on one instance. Multiple instances scanning the same library will make duplicate API calls and may interfere with each other's tracker files.

## How do I check what the addon is doing?

Enable debug logging in the addon settings under **Debugging**. The log file is at `addon_data/script.eucert.fixer/logs/eucert.log`. Look for `[EUCert.backfill]` entries to see which items were processed and what rating source was used.

## A scraper canary warning appeared in my log. What does it mean?

Each scan cycle tests the enabled scrapers with a known title to verify they still work. `scraper.canary_fail` means the scraper returned no result. `scraper.canary_mismatch` means it returned an unexpected rating. These usually indicate the scraper's website has changed. Check for addon updates or file an issue on GitHub.
