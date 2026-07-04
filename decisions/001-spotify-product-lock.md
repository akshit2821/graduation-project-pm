# ADR-001: Product lock — Spotify

**Status:** accepted  
**Date:** 2026-05-23  
**Part:** 0  

## Context

Graduation brief allows **Spotify** or **Gaana**. Part 1 requires multi-source public feedback at scale.

## Decision

Lock **Spotify** for corpus, deck (`NL Spotify.pdf`), and MVP copy.

- Android: `com.spotify.music`  
- iOS: `324684580` (country `in`)  

## Rationale

| Factor | Spotify |
|--------|---------|
| Play/App review volume | High |
| Reddit / forums | r/spotify, Community boards |
| Free scrapers | Mature |
| Interview recruitment (India) | Broad |

Gaana deferred — would require separate `data/raw/gaana/` if explored later (**edge S2**).

## Consequences

- All artifacts use Spotify branding consistently (**edge S1**).  
- Segment: Indian urban repeat listeners 22–35 (`config/product.json`).  

## Related

- [edge-cases.md §Part 0](../edge-cases.md#part-0--product-lock-and-setup) **S1–S3**  
- [docs/DATA_SOURCES.md](../docs/DATA_SOURCES.md)
