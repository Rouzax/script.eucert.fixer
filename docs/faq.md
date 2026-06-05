# FAQ

## Why is my certification stricter than I expected?

When the addon converts a certification from one country's scale to another, it always picks the stricter option if a certification falls between two values on the target scale. For example, if a German FSK 12 maps to somewhere between a Dutch 12 and 14, the addon writes 14. This is intentional: the addon errs on the side of caution rather than under-certifying content.

Different countries also weigh content factors differently: the US is stricter on language and sexual content, while Germany and the UK are stricter on violence. These differences mean cross-system conversions can never be a perfect match. See [Rating Systems: How systems compare](rating-systems.md#how-systems-compare) for details.

## Which scrapers work for my country?

All enabled scrapers work for all countries. Each scraper looks up a certification from its own national database and the addon converts the result to your selected country's scale. You do not need to be in Germany to benefit from FSK certifications, for example. The scraper for your own country runs first, since that result requires no conversion.

## Can I customize the certification mappings?

Yes. The addon stores its active country configuration in a file called `inference.json`, located in the addon's data folder:

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\Kodi\userdata\addon_data\script.eucert.fixer\config\inference.json` |
| Linux | `~/.kodi/userdata/addon_data/script.eucert.fixer/config/inference.json` |
| macOS | `~/Library/Application Support/Kodi/userdata/addon_data/script.eucert.fixer/config/inference.json` |
| LibreELEC | `/storage/.kodi/userdata/addon_data/script.eucert.fixer/config/inference.json` |

This file contains the list of similar countries to check and the mapping tables that convert foreign certifications to your scale. You can edit it with a text editor. Note that changing your country in the addon settings will overwrite this file with the default values for the new country.

## Why didn't the addon find a certification for a specific title?

Enable debug logging in the addon settings under **General**, then check `eucert.log`. The log shows which sources were tried for each title and what each one returned.

Common reasons a title is not found:

- The title is a new release and certifications have not yet been submitted to TMDB.
- The title name in your Kodi library differs from the name used by a rating authority.
- The OMDB free tier limit (1,000 requests/day) was reached during the scan.
- A scraper is not working due to a website change. See [Troubleshooting](troubleshooting.md).

Items that cannot be resolved are retried on every scan. After 30 days without a result, the not-found certification is applied.

## I have multiple Kodi devices sharing a database. Do I install this on all of them?

No. Install and enable the addon on only one device. All devices read from the same library database, so certifications filled in by one device appear on all of them immediately. Running the addon on multiple devices has no benefit and uses your API quota faster (OMDB's free tier allows only 1,000 requests per day). Pick the device that runs the most, such as a headless server or your primary living room device.

## How do I check what the addon is doing right now?

Enable debug logging in the addon settings under **General**. The log file (see above) records every item the addon processes, which source found the certification, and what certification was written. New entries appear as scans run.

## A health check warning appeared in my log. What does it mean?

Each scan cycle, the addon checks whether each enabled scraper is still working by looking up a known title and checking the result. If the result is missing or wrong, the addon logs a warning.

This warning means the scraper's website has likely changed in a way that prevents the addon from searching it correctly. It is not caused by your settings. Check the [GitHub releases page](https://github.com/Rouzax/script.eucert.fixer/releases) for an updated version, or report the issue at the [GitHub issues page](https://github.com/Rouzax/script.eucert.fixer/issues).

While the health check is failing, that particular scraper will not return certifications, but all other sources continue to work.
