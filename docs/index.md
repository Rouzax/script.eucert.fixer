# EU Certification Fixer

Automatically fill in missing age ratings for movies and TV shows in your Kodi library.

## The problem this solves

When Kodi scrapes metadata for a movie or TV show, it looks up the age rating for one country. If that country's rating is not yet in the TMDB database, the item gets no rating at all. This leaves parts of your library blank, making it harder to filter content by age suitability.

EU Certification Fixer (the addon) runs quietly in the background, finds those unrated items, and fills in the missing ratings automatically.

## What the addon does

When the addon finds an item without a rating, it searches several sources in order until one returns a result:

1. It checks TMDB for your chosen country's rating directly.
2. If that is not available, it checks whether TMDB has a rating from a culturally similar country and converts it to your country's scale.
3. It then searches national rating authority websites (FSK for Germany, BBFC for the UK, Medieraadet for Denmark, Kijkwijzer for the Netherlands) and converts the result to your scale.
4. It checks OMDB, which carries US MPAA ratings, and converts those to your scale.
5. If none of these return a result, the item is retried on every scan. After 30 days without a result, a configurable fallback rating is applied.

Once a rating is found, it is written back to your Kodi library and appears in the item's info screen.

## Supported countries

| Country | Rating system | Ratings |
|---------|--------------|---------|
| Netherlands (NL) | Kijkwijzer | AL, 6, 9, 12, 14, 16, 18 |
| Belgium (BE) | Kijkwijzer | AL, 6, 9, 12, 14, 16, 18 |
| Germany (DE) | FSK | 0, 6, 12, 16, 18 |
| Austria (AT) | JMK | 0, 6, 10, 12, 14, 16, 18 |
| United Kingdom (GB) | BBFC | U, PG, 12, 12A, 15, 18, R18 |
| United States (US) | MPAA | G, PG, PG-13, R, NC-17 |
| France (FR) | CNC | U, 10, 12, 16, 18 |
| Denmark (DK) | Medieraadet | A, 7, 11, 15 |
| Sweden (SE) | Mediemyndigheten | Btl, 7, 11, 15 |

## Getting started

1. [Install the addon](installation.md) and open its settings.
2. Enter your TMDB API key (free, required). Get one at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api).
3. Select your country from the dropdown.
4. Close settings. The addon begins scanning your library in the background.

After the first scan completes, previously unrated items in your library will show a rating in their info screen. How many items are filled in depends on how many sources have data for your titles.

See [Installation](installation.md) for detailed steps and what to expect after setup.

---

<img src="assets/tmdb-logo.svg" alt="TMDB" width="120">

This product uses the TMDB API but is not endorsed or certified by [TMDB](https://www.themoviedb.org/).
