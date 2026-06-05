# EU Certification Fixer

**Set it and forget it. Your Kodi library fills itself.**

EU Certification Fixer is a Kodi background service that automatically fills in missing age certifications for movies and TV shows. It searches TMDB, OMDB, and national rating authority websites, converts the result to your country's scale, and writes it back to your library.

Built for Kodi 21+ (Omega and newer).

---

## What does it do?

When Kodi scrapes metadata, it looks up the age certification for one country. If that country's certification is missing from TMDB, the item gets no certification at all. EU Certification Fixer finds those blank items and fills them in.

The addon runs quietly in the background. It scans your library on startup and on a configurable schedule. You configure it once and it handles everything from there.

### How it finds certifications

| Step | Source | What it checks |
|------|--------|----------------|
| 1 | TMDB | Your country's certification directly |
| 2 | National scraper | Your country's rating authority (e.g. FSK for DE, BBFC for GB) |
| 3 | Inference chain | Similar countries in order of cultural relevance; checks TMDB first, then the scraper for each country |
| 4 | OMDB | US MPAA certification, converted to your scale |
| 5 | Retry / fallback | Retries for 30 days, then applies a configurable fallback |

When converting between rating systems, the addon always picks the stricter option for borderline cases.

---

## Supported Countries

| Country | System | Certifications |
|---------|--------|----------------|
| Netherlands (NL) | Kijkwijzer | AL, 6, 9, 12, 14, 16, 18 |
| Belgium (BE) | Kijkwijzer | AL, 6, 9, 12, 14, 16, 18 |
| Germany (DE) | FSK | 0, 6, 12, 16, 18 |
| Austria (AT) | JMK | AA, 6, 8, 10, 12, 14, 16 |
| United Kingdom (GB) | BBFC | U, PG, 12, 12A, 15, 18, R18 |
| United States (US) | MPAA | G, PG, PG-13, R, NC-17 |
| France (FR) | CNC | TP, U, 10, 12, 16, 18 |
| Denmark (DK) | Medieraadet | A, 7, 11, 15, F |
| Sweden (SE) | Mediemyndigheten | Btl, 7, 11, 15 |

---

## Key Features

- **9 country presets** with inference chains and cross-cultural rating mappings
- **4 national scrapers** that search rating authority websites directly (FSK, BBFC, Medieraadet, Kijkwijzer)
- **Smart conversion** between rating systems, always choosing the stricter option
- **Background operation** with configurable scan intervals and rate limiting
- **Retry tracking** for items not yet in any database, with configurable timeout
- **Replace mode** to fix existing incorrect certifications from mismatched scraper settings

---

## Requirements

- **Kodi 21 (Omega)** or later
- **A TMDB API key** (free, required)
- **An OMDB API key** (optional, recommended for US MPAA fallback)

---

## Installation

- **[Rouzax Repository](https://github.com/Rouzax/repository.rouzax/releases)** *(recommended)*: install the repository zip once; Kodi auto-updates the addon on every stable release.
- **[GitHub Releases](https://github.com/Rouzax/script.eucert.fixer/releases)** (manual): download the zip, then Settings > Add-ons > Install from zip file. Use this for pre-releases.

After install, open the addon settings, enter your TMDB API key, select your country, and close the dialog. The addon begins scanning your library in the background.

See the [Installation page](https://rouzax.github.io/script.eucert.fixer/docs/installation/) for detailed setup instructions.

---

## Documentation

Full documentation is available on the [docs site](https://rouzax.github.io/script.eucert.fixer/docs/):

| Page | Description |
|------|-------------|
| [Installation](https://rouzax.github.io/script.eucert.fixer/docs/installation/) | Setup and first run |
| [Configuration](https://rouzax.github.io/script.eucert.fixer/docs/configuration/) | All settings explained |
| [How It Works](https://rouzax.github.io/script.eucert.fixer/docs/how-it-works/) | The certification lookup pipeline |
| [Rating Systems](https://rouzax.github.io/script.eucert.fixer/docs/rating-systems/) | All 9 systems compared |
| [FAQ](https://rouzax.github.io/script.eucert.fixer/docs/faq/) | Common questions |
| [Troubleshooting](https://rouzax.github.io/script.eucert.fixer/docs/troubleshooting/) | Diagnostics and fixes |

---

## Quick Links

- [Report a Bug](https://github.com/Rouzax/script.eucert.fixer/issues/new?template=bug_report.yml)
- [Request a Feature](https://github.com/Rouzax/script.eucert.fixer/issues/new?template=feature_request.yml)
- [Changelog](changelog.txt)

---

## Credits and License

Licensed under the **MIT License**. See [LICENSE.txt](LICENSE.txt).

<img src="docs/assets/tmdb-logo.svg" alt="TMDB" width="120">

This product uses the TMDB API but is not endorsed or certified by [TMDB](https://www.themoviedb.org/).

Rating system logos are trademarks of their respective organizations and are used here for identification purposes only.
