# Installation

## What you need before you start

- **Kodi 21 (Omega) or later.** Earlier versions are not supported.
- **A TMDB API key.** This is required. TMDB (The Movie Database) is the primary source for ratings. Get a free key at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api).
- **An OMDB API key** (optional). OMDB is used as a secondary source. The free tier allows 1,000 requests per day. Get one at [omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx). The addon works without this key, but fewer ratings will be found for titles that are not in TMDB.

## Install from zip

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

The addon starts its background service automatically when Kodi boots. After you close the settings dialog, a scan will begin within a few minutes.

## What happens next

The addon scans your entire library looking for movies and TV shows that have no age rating. For each one it finds, it searches TMDB, rating authority websites, and OMDB in turn. When it finds a rating, it writes it back to your library immediately.

After the first scan finishes, open any previously unrated movie or TV show and check its info screen. If the addon found a rating, it will now appear in the rating field. Items for which no source had a rating are retried on every scan and will be filled in once the information becomes available.

If you have a large library with many unrated items, the first scan may take several minutes because the addon pauses briefly between each external request to avoid overloading the rating websites.

## If nothing seems to happen

- Check that your TMDB API key is entered correctly in the addon settings. An incorrect key prevents the addon from doing anything.
- The first scan runs on startup. If Kodi was already running when you installed the addon, restart Kodi to start the service.
- See [Troubleshooting](troubleshooting.md) for more help.
