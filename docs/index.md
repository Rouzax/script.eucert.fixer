# EU Certification Fixer

Automatically fill in missing age certifications for movies and TV shows in your Kodi library.

## The problem this solves

When Kodi scrapes metadata for a movie or TV show, it looks up the age certification for one country. If that country's certification is not yet in the TMDB database, the item gets no certification at all. This leaves parts of your library blank, making it harder to filter content by age suitability.

EU Certification Fixer (the addon) runs quietly in the background, finds those items without a certification, and fills in the missing certifications automatically.

## What the addon does

When the addon finds an item without a certification, it searches several sources in order until one returns a result:

1. It checks TMDB for your chosen country's certification directly.
2. If that is not available, it checks whether TMDB has a certification from a culturally similar country and converts it to your country's scale.
3. It then searches national rating authority websites (FSK for Germany, BBFC for the UK, Medieraadet for Denmark, Kijkwijzer for the Netherlands) and converts the result to your scale.
4. It checks OMDB, which carries US MPAA certifications, and converts those to your scale.
5. If none of these return a result, the item is retried on every scan. After 30 days without a result, a configurable not-found certification is applied.

Once a certification is found, it is written back to your Kodi library and appears in the item's info screen.

## Supported countries

| Country | System | Certifications |
|---------|--------|----------------|
| Netherlands (NL) | [Kijkwijzer](rating-systems.md#kijkwijzer-netherlands-belgium) | AL, 6, 9, 12, 14, 16, 18 |
| Belgium (BE) | [Kijkwijzer](rating-systems.md#kijkwijzer-netherlands-belgium) | AL, 6, 9, 12, 14, 16, 18 |
| Germany (DE) | [FSK](rating-systems.md#fsk-germany) | 0, 6, 12, 16, 18 |
| Austria (AT) | [JMK](rating-systems.md#jmk-austria) | AA, 6, 8, 10, 12, 14, 16 |
| United Kingdom (GB) | [BBFC](rating-systems.md#bbfc-united-kingdom) | U, PG, 12, 12A, 15, 18, R18 |
| United States (US) | [MPA](rating-systems.md#mpa-united-states) | G, PG, PG-13, R, NC-17 |
| France (FR) | [CNC](rating-systems.md#cnc-france) | TP, U, 10, 12, 16, 18 |
| Denmark (DK) | [Medieraadet](rating-systems.md#medieraadet-denmark) | A, 7, 11, 15 |
| Sweden (SE) | [Mediemyndigheten](rating-systems.md#mediemyndigheten-sweden) | Btl, 7, 11, 15 |

See [Rating Systems](rating-systems.md) for what each certification means and how systems compare.

## Getting started

1. [Install the addon](installation.md) and open its settings.
2. Enter your TMDB API key (free, required). Get one at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api).
3. Select your country from the dropdown.
4. Close settings. The addon begins scanning your library in the background.

After the first scan completes, previously uncertified items in your library will show a certification in their info screen. How many items are filled in depends on how many sources have data for your titles.

See [Installation](installation.md) for detailed steps and what to expect after setup.

---

<img src="assets/tmdb-logo.svg" alt="TMDB" width="120">

This product uses the TMDB API but is not endorsed or certified by [TMDB](https://www.themoviedb.org/).

Rating system logos are trademarks of their respective organizations and are used here for identification purposes only.
