# Installation

## What you need before you start

- **Kodi 21 (Omega) or later.** Earlier versions are not supported.
- **A TMDB API key.** This is required. TMDB (The Movie Database) is the primary source for certifications. Get a free key at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api).
- **An OMDB API key** (optional, US only). OMDB carries US MPAA certifications as a last resort when all other sources (TMDB, national scrapers) have no result. The addon converts the US certification to your country's scale. The free tier allows 1,000 requests per day. Get one at [omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx). Most EU libraries will rarely need this.

## Install from repository (recommended)

Installing from the Rouzax repository gives you automatic updates when new versions are released.

1. Download the repository zip from [https://github.com/Rouzax/repository.rouzax](https://github.com/Rouzax/repository.rouzax).
2. In Kodi, go to **Add-ons** and select **Install from zip file**.
3. Navigate to the downloaded repository zip and select it. This installs the Rouzax repository.
4. Go to **Add-ons** > **Install from repository** > **Rouzax Repository** > **Services** > **EU Certification Fixer** and select **Install**.

## Install from zip (manual)

If you prefer not to use the repository, you can install the addon directly from a zip file. You will need to repeat this process manually for each update.

1. Download the latest release zip from the [GitHub releases page](https://github.com/Rouzax/script.eucert.fixer/releases).
2. In Kodi, go to **Add-ons** and select **Install from zip file**.
3. Navigate to the downloaded zip file and select it.
4. Kodi will confirm the installation with a notification in the top-right corner.

## Set up the addon

After installation:

1. Go to **Add-ons** > **My Add-ons** > **EU Certification Fixer** > **Configure**.
2. On the **Providers** tab, enter your TMDB API key. If you have an OMDB key, enter that too.
3. On the **Ratings** tab, select your country from the dropdown.
4. Close the settings dialog.

The addon starts its background service automatically when Kodi boots. The first scan runs when Kodi finishes a library update, or after the configured scan interval (default: 24 hours), whichever comes first. To scan immediately, go to **Programs** > **Add-ons** > **EU Certification Fixer**. This triggers a one-time scan outside the normal schedule.

!!! tip "Match your scraper settings"

    Kodi's built-in TMDB scraper has its own certification country and prefix settings, separate from this addon. By default, the scraper uses US certifications with a "Rated " prefix, regardless of which country you actually select. If the scraper and addon use different prefixes, your library will end up with inconsistent certification formats.

    To keep things consistent, open your scraper settings and set the certification country to match the country you selected in the addon. Set the prefix to match as well (for example, "DE:" for Germany or "NL:" for Netherlands).

    If you would rather not change the scraper settings, you can enable **Replace incorrect certifications** in the addon settings instead. The addon will then correct mismatched prefixes automatically during each scan.

    Note: Austria and Belgium are not available in the TMDB scraper's certification country dropdown. For those countries, this addon is the only way to get correct local certifications.

## What happens next

The addon scans your entire library looking for movies and TV shows that have no age certification. For each one it finds, it searches TMDB, rating authority websites, and OMDB in turn. When it finds a certification, it writes it back to your library immediately.

After the first scan finishes, open any previously uncertified movie or TV show and check its info screen. If the addon found a certification, it will now appear in the rating field. Items for which no source had a certification are retried on every scan and will be filled in once the information becomes available.

If you have a large library with many uncertified items, the first scan may take several minutes because the addon pauses briefly between each external request to avoid overloading the rating authority websites.

## If nothing seems to happen

- Check that your TMDB API key is entered correctly in the addon settings. An incorrect key prevents the addon from doing anything.
- The first scan runs on startup. If Kodi was already running when you installed the addon, restart Kodi to start the service.
- See [Troubleshooting](troubleshooting.md) for more help.
