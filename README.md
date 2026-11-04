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

## Changing a page

Every HTML page is written by `tools/generate-pages.py`. Edit the words there, then run:

```bash
python3 tools/generate-pages.py
```

Commit the script and the HTML together. Do not hand-edit the HTML files, or the next run will overwrite your change.

The Rules, Terms and Privacy text is read from the plugin's `RulesDocuments.java` (`~/Documents/BattleTown-Plugin/src/main/java/me/camerontheoret/battletown/hub/rules/`). When `/rules` changes in game, run the script again so the website matches.

Styles are in `assets/css/site.css` and the shared script (copy button, current-page highlight) is in `assets/js/site.js`.

## Logo

`assets/img/logo-*` are straight resizes of `BattleTown-Plugin/assets/battletown-logo-4k-transparent.png`. That art has a black background, so the page shows it with `mix-blend-mode: lighten` on a black hero. Never redraw or recolour the logo.

## Later phases

`assets/js/config.js` holds the settings the next phases need. Everything in it is public.

- **Phase 2, store (Tebex Headless): live.** `tebexWebstoreToken` holds the store's *public* token. `assets/js/store.js` reads packages from `https://headless.tebex.io/api/accounts/{token}/categories?includePackages=1`, creates a basket for the buyer's Minecraft name (Tebex checks the name and attaches the UUID), adds packages (quantity 1 each), and sends the buyer to the basket's `links.checkout` on `pay.tebex.io`. Tebex stays merchant of record and runs the same package commands as an in-game purchase. Products, prices, images and descriptions all come from the Tebex panel, so editing a package there changes the site. The basket is remembered in the browser's localStorage (`bt-store-basket`). The Tebex private key never goes in this repo. If the token is emptied, the page falls back to "buy in game with /buy".
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
