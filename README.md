# BattleTown website

The public website at **https://battletown.store**, served by GitHub Pages from the `main` branch of this repo. It is a plain static site: no build step, no cookies, no trackers, no secrets.

## Pages

| URL | File | What it shows |
|---|---|---|
| `/` | `index.html` | Logo, `play.battletown.store` with a copy button, Java 26.3, alpha date, Discord |
| `/classes/` | `classes/index.html` | The 16 classes |
| `/modes/` | `modes/index.html` | Duel, Free For All, Team Deathmatch, Last Alive |
| `/maps/` | `maps/index.html` | Official Maps, building your own Map, Map sizes |
| `/store/` | `store/index.html` + `assets/js/store.js` | Live Tebex Headless store: packages, basket, checkout on Tebex |
| `/store/thanks/` | `store/thanks/index.html` | Where Tebex sends buyers after paying |
| `/rules/` | `rules/index.html` | Server Rules (`#rules`), Terms (`#terms`), Privacy (`#privacy`) |
| 404 | `404.html` | Page not found |

## Look and feel (4 Nov redesign)

- **Type and colour:** gold block headings in Lilita One (self-hosted in `assets/fonts/`, OFL licence) with a stepped brown extrusion that echoes the logo, on near-black with ruby accents.
- **Art:** `assets/img/classes/` are graded crops of Cameron's in-game class shrine shots from the Warriors Hall and Mages Hall (`~/Documents/BattleTown Art/IG POSTS/<Class>/`), and `assets/img/art/cat-bundles.webp` is a Battle Bundles banner built from his Deals and Winterfest art. Both come from `tools/grade-art.py` (contrast, saturation, split tone, bloom, a light leak in the class colour, vignette, sharpening); re-run it after changing a pick. `assets/img/art/` holds his store banners and category art (`STORE BACKGROUNDS`, `DEALS`, `COLLECTIONS`, `XP BOOSTS`). The `CONCEPT ART` folder is screenshots of another server and must not be used.
- **Motion (`assets/js/site.js`):** rising ember particles, a crossfading class-hall slideshow behind the hero, scroll reveals, pointer tilt on cards, a scroll progress bar, page-to-page view transitions, and a coin burst on Copy. Everything turns off for visitors who ask their system for reduced motion.
- **Live bits:** a server status pill (public `api.mcsrvstat.us`) and a countdown to the public alpha (1 Dec 2026, midnight Ottawa).
- **Music:** four BattleTown Hub tracks in `assets/audio/`. They play only after the visitor taps the player, and keep playing across pages within the same visit.
- **Classes page (`assets/js/classes.js`):** a showcase that shows one class at a time, recolours to its accent, and supports arrows, keys, swipe and `#class` links. Without JavaScript the classes stack.
- **Store:** category banners, a coin that flies into the basket, and a basket button on phones.
- **Phones:** the nav becomes a full-screen menu.

## Changing a page

Every HTML page is written by `tools/generate-pages.py`. Edit the words there, then run:

```bash
python3 tools/generate-pages.py
```

Commit the script and the HTML together. Do not hand-edit the HTML files, or the next run will overwrite your change.

Game words are read from the game itself: the class cards (motto, role, weapons, abilities, Warriors Hall / Mages Hall) from `ClassCards.java`, hearts from the live `classes.yml`, and the Rules, Terms and Privacy text from the plugin's `RulesDocuments.java` (`~/Documents/BattleTown-Plugin/src/main/java/me/camerontheoret/battletown/hub/rules/`). When any of those change in game, run the script again so the website matches. It also writes `sitemap.xml` and `robots.txt` and adds a content hash to every CSS/JS link. `tools/grade-art.py` builds the graded images, the Battle Bundles banner, the link-preview card (`assets/img/social-card.jpg`) and `favicon.ico`.

**Words to use (from the game):** Warriors Hall (Warriors & Hunters) and Mages Hall (Mages & Specialists), never "Class Hall 1/2"; Map, never plot; Community Map for an approved player Map; BattleBucks (currency) and Money (everyday word); `/store` opens the store in game; Battle Plaza, Cosmetic Shop, Creative Shop, Leaderboards, Sky Spirals, Hub Guide.

Styles are in `assets/css/site.css`. The shared script (effects, copy button, menu, status, countdown, music) is `assets/js/site.js`.

## Logo

`assets/img/logo-*` are straight resizes of `BattleTown-Plugin/assets/battletown-logo-4k-transparent.png`. That art has a black background, so the page shows it with `mix-blend-mode: lighten` on a black hero. Never redraw or recolour the logo.

## Later phases

`assets/js/config.js` holds the settings the next phases need. Everything in it is public.

- **Phase 2, store (Tebex Headless): live.** `tebexWebstoreToken` holds the store's *public* token. `assets/js/store.js` reads packages from `https://headless.tebex.io/api/accounts/{token}/categories?includePackages=1`, creates a basket for the buyer's Minecraft name (Tebex checks the name and attaches the UUID), adds packages (quantity 1 each), and sends the buyer to the basket's `links.checkout` on `pay.tebex.io`. Tebex stays merchant of record and runs the same package commands as an in-game purchase. Products, prices, images and descriptions all come from the Tebex panel, so editing a package there changes the site. The basket is remembered in the browser's localStorage (`bt-store-basket`). The Tebex private key never goes in this repo. If the token is emptied, the page falls back to "buy in game with /store".
- **Phase 3, live stats.** The plugin serves a read-only JSON feed on an HTTPS address (for example `https://api.battletown.store/stats.json` behind Bloom's reverse proxy). Put it in `statsFeedUrl`, add a `stats/` page and `assets/js/stats.js` that read it. GitHub Pages is HTTPS, so the feed must be HTTPS too.

## Domain

DNS is at Namecheap (Advanced DNS) for `battletown.store`:

| Type | Host | Value |
|---|---|---|
| A | `@` | 185.199.108.153 |
| A | `@` | 185.199.109.153 |
| A | `@` | 185.199.110.153 |
| A | `@` | 185.199.111.153 |
| AAAA | `@` | 2606:50c0:8000::153 |
| AAAA | `@` | 2606:50c0:8001::153 |
| AAAA | `@` | 2606:50c0:8002::153 |
| AAAA | `@` | 2606:50c0:8003::153 |
| CNAME | `www` | `camerontheoretchrome-bit.github.io.` |
| A | `play` | 204.77.5.104 (the Minecraft server on Bloom; not part of the website) |

The `CNAME` file in this repo tells GitHub Pages the site's domain.

## Preview on the Mac

```bash
python3 -m http.server 8765
```

Then open http://127.0.0.1:8765/. The store works from the preview too, but Tebex sends you back to 127.0.0.1 after checkout.
