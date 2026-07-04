# Theme guide — music discovery (Part 1)

One **primary** `theme_id` per feedback row. Max **8** themes (see `config/product.json`).

| Theme ID | Label | Includes | Excludes |
|----------|-------|----------|----------|
| `discovery_friction` | Hard to find new music | Search fails, can't find genres, don't know what to play | Pure audio quality bugs |
| `bad_recommendations` | Recommendation products miss | Discover Weekly, Radio, Daily Mix irrelevant | Generic "bad app" |
| `repeat_listening` | Same content on loop | Repeat playlists, same artists, comfort listening | Intentional favorites praise |
| `library_clutter` | Library too large to explore | Saved/liked overload, can't navigate collection | Upload/sync bugs |
| `ui_complexity` | UI blocks exploration | Cluttered home, hard to browse | Login/account only |
| `social_discovery` | Wants shared discovery | Friend activity, Blend, social playlists | Unrelated social features |
| `podcast_vs_music` | Podcasts crowd out music | Home feed mix, podcast recommendations | Podcast content quality |
| `pricing_ads` | Free tier limits exploration | Ads, skip limits, paywall frustration | Unrelated billing |

## Tie-break rules

1. If repeat + bad reco: pick **`repeat_listening`** when user describes habit; **`bad_recommendations`** when product named (DW, Radio).  
2. If UI + discovery: pick **`ui_complexity`** only when navigation is the blocker.  
3. Reddit posts without rating: classify on text intent only.  

## Part 1 research mapping

Each theme should help answer at least one question in [architecture.md §4.1](../architecture.md#41-research-questions--theme-mapping).
