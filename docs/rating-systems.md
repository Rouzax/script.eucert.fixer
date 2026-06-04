# Rating Systems

The addon supports 8 age rating systems across 9 countries. Each system has its own scale, age thresholds, and classification philosophy. When the addon converts a certification from one system to another, the result depends on how the two systems compare.

This page explains what the certifications in each system mean, how systems differ from one another, and why converting between them sometimes produces stricter results than you might expect.

If a converted certification already seems too high, see [FAQ: Why is my certification stricter than I expected?](faq.md#why-is-my-certification-stricter-than-i-expected).

Use the table of contents on the right to jump directly to your country's system.

---

## Kijkwijzer (Netherlands, Belgium)

<span class="logo-badge"><img src="/script.eucert.fixer/docs/assets/kijkwijzer-logo-dark.svg" alt="Kijkwijzer" class="rating-logo"></span>

Operated by NICAM (Netherlands Institute for the Classification of Audiovisual Media).

| Rating | Age | Meaning |
|--------|-----|---------|
| AL | All ages | Suitable for all audiences |
| 6 | 6+ | May be confusing or frightening for young children |
| 9 | 9+ | May contain mild violence or fear |
| 12 | 12+ | Moderate violence, mild sexual content, or substance use |
| 14 | 14+ | Stronger violence, sexual themes, or discrimination |
| 16 | 16+ | Serious violence, explicit sexual content, or hard drug use |
| 18 | 18+ | Extreme violence, very explicit content |

??? info "How this system differs"
    - Uses content descriptor pictograms (violence, fear, sex, language, drugs, discrimination, dangerous behaviour) alongside the age certification. These pictograms explain why a certification was given, not just what the certification is.
    - The 16 certification is legally enforced under the Dutch Criminal Code; lower certifications are advisory.
    - Belgium uses the same Kijkwijzer system, so no conversion is needed between the two countries.
    - The 14 category was added in 2020 to fill the gap between 12 and 16.

---

## FSK (Germany)

<span class="logo-badge"><img src="/script.eucert.fixer/docs/assets/fsk-logo.svg" alt="FSK" class="rating-logo"></span>

Operated by the Freiwillige Selbstkontrolle der Filmwirtschaft (Voluntary Self-Regulation of the Film Industry).

| Rating | Age | Meaning |
|--------|-----|---------|
| 0 | All ages | No age restriction |
| 6 | 6+ | Suitable for ages 6 and above |
| 12 | 12+ | Suitable for ages 12 and above |
| 16 | 16+ | Suitable for ages 16 and above |
| 18 | 18+ | No youth admission (adults only) |

??? info "How this system differs"
    - Certifications are legally binding in Germany, not just advisory.
    - Action films tend to be classified more strictly than in other countries. Sexual content is treated more leniently than in the US.
    - A "Parental Guidance" rule allows children aged 6 and older to see FSK 12 films in cinemas when accompanied by a parent.
    - Some content can be refused classification entirely and banned from public distribution, even beyond FSK 18.

---

## JMK (Austria)

<span class="logo-badge"><img src="/script.eucert.fixer/docs/assets/jmk-logo.svg" alt="JMK" class="rating-logo"></span>

Operated by the Jugendmedienkommission (Youth Media Commission).

| Rating | Age | Meaning |
|--------|-----|---------|
| AA | All ages | Suitable for all audiences |
| 6 | 6+ | May contain brief moments of tension |
| 8 | 8+ | May contain mild violence or conflict |
| 10 | 10+ | May contain moderate themes or tension |
| 12 | 12+ | May contain violence, mild sexual references |
| 14 | 14+ | Stronger violence or sexual content |
| 16 | 16+ | Not suitable for children under 16 |

??? info "How this system differs"
    - Primarily advisory; the 9 federal states can adopt or modify the JMK certifications. Only the 16 certification is legally restricted.
    - Includes an 8 tier that most other systems lack, providing more granularity for younger audiences.
    - There is no 18 certification. The highest tier is 16. Content that would receive 18 in Germany receives 16 in Austria.
    - Despite sharing a language with Germany, Austria's system produces noticeably different certifications for many films.

---

## BBFC (United Kingdom)

<span class="logo-badge"><img src="/script.eucert.fixer/docs/assets/bbfc-logo.svg" alt="BBFC" class="rating-logo"></span>

Operated by the British Board of Film Classification.

| Rating | Age | Meaning |
|--------|-----|---------|
| U | All ages | Universal, suitable for all |
| PG | General | Parental guidance recommended |
| 12 / 12A | 12+ | Suitable for 12 and over (12A allows under-12s in cinema with an adult) |
| 15 | 15+ | Suitable only for 15 and over |
| 18 | 18+ | Suitable only for adults |
| R18 | 18+ (restricted) | Restricted distribution; licensed premises only |

??? info "How this system differs"
    - Legally enforced; cinemas and retailers must comply with the classification.
    - Stricter on violence (especially horror) than the US, but more lenient on sexual content and language.
    - Eroticised sexual violence is prohibited even at the 18 level.
    - The 12A category only applies to cinema screenings. For home video, the equivalent is 12 (no parental accompaniment option).

---

## MPA (United States)

<span class="logo-badge"><img src="/script.eucert.fixer/docs/assets/mpa-logo.svg" alt="MPA" class="rating-logo"></span>

Operated by the Motion Picture Association (formerly MPAA).

| Rating | Age | Meaning |
|--------|-----|---------|
| G | All ages | General audiences |
| PG | General | Parental guidance suggested |
| PG-13 | 13+ | Parents strongly cautioned |
| R | 17+ | Restricted; under 17 requires accompanying parent |
| NC-17 | 18+ | No one 17 and under admitted |

!!! note "TV ratings"
    US television uses a separate scale: TV-Y, TV-Y7, TV-G, TV-PG, TV-14, and TV-MA. When the addon encounters a US TV certification for a TV show, it converts it to your country's scale using the same mapping tables as film certifications.

??? info "How this system differs"
    - Voluntary and industry-run; not legally enforced. However, most theaters and retailers follow the certifications by convention.
    - Language is a major classification driver. A single use of certain profanity can push a film from PG-13 to R.
    - The violence threshold is much higher than the sexual content threshold: graphic violence may receive PG-13, while brief nudity often triggers R.
    - NC-17 is commercially avoided by studios because many theaters and retailers refuse to carry it. Most filmmakers cut content to qualify for R instead.

---

## CNC (France)

<span class="logo-badge"><img src="/script.eucert.fixer/docs/assets/cnc-logo.svg" alt="CNC" class="rating-logo"></span>

Operated by the Centre national du cinema et de l'image animee (National Centre for Cinema and the Moving Image).

| Rating | Age | Meaning |
|--------|-----|---------|
| TP | All ages | Tous publics (all audiences) |
| U | All ages | Equivalent to TP for imported content |
| 10 | 10+ | Unsuitable for children under 10 |
| 12 | 12+ | Unsuitable for children under 12 |
| 16 | 16+ | Unsuitable for children under 16 |
| 18 | 18+ | Restricted to adults |

??? info "How this system differs"
    - Profanity has no effect on the certification. Language alone never raises a classification.
    - Decisions are discretionary; there are no published guidelines or fixed rules.
    - More permissive overall than most Western systems. No film has been refused a certificate since 1979.
    - An "avertissement" (warning) system flags films that sit at the upper edge of a category, giving parents additional context without raising the official age certification.

---

## Medieraadet (Denmark)

<span class="logo-badge"><img src="/script.eucert.fixer/docs/assets/medieraadet-logo.svg" alt="Medieraadet" class="rating-logo"></span>

Operated by the Danish Media Council for Children and Young People.

| Rating | Age | Meaning |
|--------|-----|---------|
| A | All ages | Approved for all audiences |
| 7 | 7+ | May be distressing for young children |
| 11 | 11+ | Contains themes that may disturb children under 11 |
| 15 | 15+ | Contains themes unsuitable for children under 15 |
| F | Exempt | Exempt from classification |

??? info "How this system differs"
    - Only 5 categories, making it one of the simplest systems in Europe. The F (exempt) category is rarely used and applies to content that bypasses the normal classification process.
    - Focused solely on potential harm to children's wellbeing. Moral or artistic judgment is not considered.
    - Does not use content descriptors. The age threshold alone carries the classification.

---

## Mediemyndigheten (Sweden)

<span class="logo-badge"><img src="/script.eucert.fixer/docs/assets/mediemyndigheten-logo.svg" alt="Mediemyndigheten" class="rating-logo"></span>

Operated by the Swedish Agency for the Media, formed in January 2024 from a merger of Statens medierad and MPRT.

| Rating | Age | Meaning |
|--------|-----|---------|
| Btl | All ages | Barntillaten (approved for children) |
| 7 | 7+ | May be distressing for children under 7 |
| 11 | 11+ | Contains themes unsuitable for children under 11 |
| 15 | 15+ | Contains themes unsuitable for children under 15 |

??? info "How this system differs"
    - No 18+ certification exists. Even films with very explicit content receive 15 at most.
    - Profanity, nudity, and depictions of substance use are not considered harmful in themselves; only content that may frighten or disturb children drives the certification upward.
    - A "companion rule" allows children to watch films with a higher certification when accompanied by an adult.
    - The Swedish and Danish scales are nearly identical in structure (both use 7, 11, 15), which makes conversions between them straightforward.

---

## How ratings are converted

Because no single database has certifications for every country and every title, the addon often needs to take a certification from one system and convert it to another. Understanding how this works helps explain the certifications you see in your library.

When the addon cannot find a certification from your country on TMDB, it checks culturally similar countries in a specific order. Each country preset defines this order. For example:

- **Germany** checks Austria first (same language, similar classification culture), then the Netherlands, Belgium, France, the UK, Denmark, Sweden, and the US.
- **Netherlands** checks Belgium first (same Kijkwijzer system), then Germany, Austria, France, the UK, Denmark, Sweden, and the US.

The order matters because countries checked earlier tend to have more similar classification philosophies. A certification from Austria is more likely to match Germany's standards closely than a certification from the US.

### Conservative rounding

When a foreign certification falls between two thresholds on your country's scale, the addon always picks the stricter option. It will never under-certify content.

This means a converted certification may be one step higher than you expect. For example, a foreign "15" might land between your country's "14" and "16" thresholds. The addon writes "16" in that case, not "14".

The reasoning is straightforward: if content was restricted to ages 15 and above in the source country, allowing access to 14-year-olds in the target country would lower the protection level. The addon avoids this.

### A practical example

To see how this works end to end, consider this scenario.

Suppose you selected Netherlands. A film has no Dutch certification on TMDB, but it does have a BBFC 15 from the UK. Here is what happens:

1. The addon finds no Kijkwijzer certification on TMDB for this film.
2. It checks Belgium (same system), but no certification exists there either.
3. It checks Germany, Austria, France, and then the UK.
4. The UK has a BBFC 15. The addon looks up the UK-to-Netherlands mapping table.
5. BBFC 15 maps to Kijkwijzer 16. The stricter option (16 rather than 14) is chosen because the BBFC 15 threshold sits above the Dutch 14 line.
6. The addon writes "16" to your Kodi library.

This same approach applies to all sources: TMDB inference, OMDB (US certifications), and the national scrapers (FSK, BBFC, Kijkwijzer). Every foreign certification passes through the mapping table for your selected country before it is written.

You can customize these mapping tables if you disagree with specific conversions. See [FAQ: Can I customize the certification mappings?](faq.md#can-i-customize-the-certification-mappings) for details.

For more on why conversions can seem strict, see [FAQ: Why is my certification stricter than I expected?](faq.md#why-is-my-certification-stricter-than-i-expected)

---

## How systems compare

No two countries classify content the same way. Different countries weigh content factors differently, and these tendencies explain why a film may receive a lower certification in one country and a higher one in another.

| Aspect | Stricter | More lenient |
|--------|----------|--------------|
| Violence | Germany (action films), UK (horror), Netherlands | US, France |
| Language | US (can drive a certification on its own) | France (not a factor), continental Europe generally |
| Sexual content | US | Netherlands, Scandinavia, France |

These differences are exactly why cross-system conversions can never be a perfect match. A film that is PG-13 in the US might be certified 12 in the UK but 16 in Germany if it contains stylized action violence. No single mapping can account for every film's content mix, which is why the addon uses conservative rounding: when there is uncertainty, it picks the stricter bracket.

In practice, the biggest surprises tend to come from US-to-European conversions (where violence is treated more strictly in Europe) and from European-to-US conversions (where sexual content and language are treated more strictly in the US). The addon's mapping tables are designed to handle these differences as accurately as possible, but some edge cases are unavoidable.

If a specific conversion consistently produces results you disagree with, you can adjust the mapping tables. See [FAQ: Can I customize the certification mappings?](faq.md#can-i-customize-the-certification-mappings) for instructions.
