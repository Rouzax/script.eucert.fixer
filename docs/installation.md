# Installation

## Prerequisites

- Kodi 21 (Omega) or later
- A [TMDB API key](https://www.themoviedb.org/settings/api) (free)
- An [OMDB API key](https://www.omdbapi.com/apikey.aspx) (free tier: 1,000 requests/day)

## Install from zip

1. Download the latest release zip from the [GitHub releases page](https://github.com/Rouzax/script.kijkwijzer.ratings/releases)
2. In Kodi, go to **Add-ons** > **Install from zip file**
3. Navigate to the downloaded zip and select it
4. After installation, go to the addon settings and enter your API keys

The background service starts automatically when Kodi boots.

## First run

After entering your API keys:

- The addon scans your library on startup and then on a configurable interval (default: every 24 hours)
- Check the Kodi log for `[Kijkwijzer.service]` and `[Kijkwijzer.backfill]` entries to confirm it is running
- Enable debug logging in the addon's Advanced settings for detailed output in `kijkwijzer.log`
