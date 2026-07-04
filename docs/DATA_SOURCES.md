# Data sources — Part 1 collection plan

Locked for **Spotify** (`config/product.json`).

| Source | Tool | Target | Output path |
|--------|------|--------|-------------|
| Google Play | `google-play-scraper` | 800 reviews | `data/raw/spotify/play/` |
| App Store | `app-store-scraper` (country `in`) | 400 reviews | `data/raw/spotify/ios/` |
| Reddit | PRAW or manual CSV | 50 threads | `data/raw/spotify/reddit/` |
| Forums | Manual paste | 30 threads | `data/raw/spotify/forum/forums_raw.csv` |
| Social | Manual sample | 20 posts | `data/raw/spotify/social/social_raw.csv` |

## Package / app IDs

| Store | ID |
|-------|-----|
| Android | `com.spotify.music` |
| iOS | `324684580` (country `in`) |

## Rules

- **Public data only** — no login bypass ([edge-cases COL10](../edge-cases.md))  
- Prefer **newest** store reviews (`sort=NEWEST` on Play)  
- Manual sources: columns `source`, `date`, `title`, `text`, `url`, `upvotes`  

## Normalized output

All sources merge to: `data/feedback_normalized.csv` (Part 1B).
