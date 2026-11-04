"""Writes every HTML page of the BattleTown website.

The pages are plain HTML, so GitHub Pages serves them as they are. This
script is their source: change the words here, run it, and commit both.

    python3 tools/generate-pages.py

The Rules, Terms and Privacy text is read straight from the plugin's
RulesDocuments.java, so the website always says what /rules says in game.
Run this again whenever that file changes.
"""
import html
import os
import re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_JAVA = os.path.expanduser(
    "~/Documents/BattleTown-Plugin/src/main/java/me/camerontheoret/battletown/hub/rules/RulesDocuments.java")

NAV = [("/", "Home"), ("/classes/", "Classes"), ("/modes/", "Game modes"),
       ("/maps/", "Maps"), ("/store/", "Store"), ("/rules/", "Rules")]

DISCORD = "https://discord.gg/TJ5wBJYCc"
ADDRESS = "play.battletown.store"

# Public alpha opens at midnight Ottawa time.
ALPHA_START = "2026-12-01T00:00:00-05:00"


def page(path, title, description, body, scripts=(), image="https://battletown.store/assets/img/logo-512.png"):
    nav = "\n".join(f'        <a href="{href}">{label}</a>' for href, label in NAV)
    extra_scripts = "".join(f'  <script src="{src}"></script>\n' for src in scripts)
    full_title = "BattleTown" if title is None else f"{title} · BattleTown"
    out = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{full_title}</title>
  <meta name="description" content="{html.escape(description)}">
  <meta name="theme-color" content="#07070a">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{full_title}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:image" content="{image}">
  <meta property="og:url" content="https://battletown.store{path}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/assets/img/icon-32.png" sizes="32x32">
  <link rel="apple-touch-icon" href="/assets/img/icon-180.png">
  <link rel="preload" href="/assets/fonts/lilita-one-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/css/site.css">
  <script>document.documentElement.classList.add("js");</script>
</head>
<body>
  <div class="progress" aria-hidden="true"></div>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="/"><img src="/assets/img/icon-192.png" alt="" width="38" height="38">BattleTown</a>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="main-nav" aria-label="Menu"><span></span><span></span><span></span></button>
      <nav class="nav" id="main-nav" aria-label="Main">
{nav}
        <a class="nav-play" href="/#join">Play now</a>
      </nav>
    </div>
  </header>

  <main>
{body}
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-brand">
        <img src="/assets/img/icon-192.png" alt="" width="52" height="52">
        <p><strong>BattleTown</strong><br><code>{ADDRESS}</code> · Minecraft Java 26.3</p>
      </div>
      <nav aria-label="Footer">
        <a href="{DISCORD}">Discord</a>
        <a href="/store/">Store</a>
        <a href="/rules/">Server Rules</a>
        <a href="/rules/#terms">Terms</a>
        <a href="/rules/#privacy">Privacy</a>
      </nav>
      <p>Not an official Minecraft product. Not approved by or associated with Mojang or Microsoft.</p>
    </div>
  </footer>

  <script src="/assets/js/config.js"></script>
  <script src="/assets/js/site.js"></script>
{extra_scripts}</body>
</html>
"""
    dest = os.path.join(SITE, path.strip("/"), "index.html") if path != "/404" else os.path.join(SITE, "404.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as f:
        f.write(out)


def ip_box():
    return f"""<div class="ip-box">
          <code>{ADDRESS}</code>
          <button class="copy-btn" type="button" data-copy="{ADDRESS}" aria-label="Copy the server address">Copy</button>
        </div>"""


# ---------------------------------------------------------------- Classes
# (id, name, accent, motto, line, hall, hearts). Words from classes.yml via the vault class pages.
CLASSES = [
    ("acrobat", "Acrobat", "#E0499E", "Own the air", "Sky Dancer. Live upstairs. Vault up, then smash down from the sky.", 1, 9),
    ("alchemist", "Alchemist", "#9ACD32", "Brew chaos", "Potion Master. Throw flasks. Clouds and weaker melee hits win fights.", 1, 10),
    ("assassin", "Assassin", "#C77DFF", "Strike from the shadows", "Sneak & Strike. Vanish, relocate, hit from behind.", 2, 10),
    ("berserker", "Berserker", "#FF3B3B", "Give in to fury", "All-Out Attacker. Hit harder while you fight. You also take more damage.", 2, 10),
    ("duelist", "Duelist", "#FFFFFF", "Timing is everything", "Counter-Puncher. Wait for their swing, then make them regret it.", 2, 10),
    ("frostborn", "Frostborn", "#7FD4F5", "Freeze the field", "Field Freezer. Chill them first. Then freeze them solid.", 1, 10),
    ("geomancer", "Geomancer", "#A855F7", "Shape the land", "Ground Shaper. Raise walls. Split the ground. Own the map.", 1, 10),
    ("guardian", "Guardian", "#B87333", "Hold the line", "Human Shield. Tank the hit, then throw them off you.", 2, 10),
    ("knight", "Knight", "#55FFFF", "Lead the charge", "Frontline Leader. Walk in, take hits, knock them down.", 2, 10),
    ("lancer", "Lancer", "#D3D47B", "Control the distance", "Reach Fighter. Your spear hits from farther than they expect.", 2, 10),
    ("necromancer", "Necromancer", "#9AE69A", "Rise again", "Soul Collector. Harvest Souls. Permanent night vision. Save two for a second life.", 1, 9),
    ("poseidon", "Poseidon", "#39C6A3", "Command the tide", "Water Commander. Pull enemies in, then dash through them faster.", 2, 10),
    ("pyromancer", "Pyromancer", "#FF8C42", "Let it burn", "Fire Starter. Set the field alight and keep them burning.", 1, 10),
    ("ranger", "Ranger", "#366B35", "Own the distance", "Long-Range Shooter. Stay far. Mark a target. Hit harder with bow and crossbow.", 2, 10),
    ("stormcaller", "Stormcaller", "#5C7CFA", "Call the storm", "Lightning Bringer. Zap several enemies, then finish with your trident.", 1, 10),
    ("warden", "Warden", "#C9812E", "Set the rules", "Ability Breaker. Stop their special moves. You pick who gets shut down.", 1, 10),
]


def accent(cid, colour):
    # Ranger's dark green needs a lighter tint to read on black.
    return "#5FAE5D" if cid == "ranger" else colour


def class_tiles():
    tiles = []
    for cid, name, colour, motto, line, hall, hearts in CLASSES:
        tiles.append(f"""          <a class="class-tile" href="/classes/#{cid}" style="--accent: {accent(cid, colour)}">
            <img src="/assets/img/classes/{cid}-thumb.webp" alt="" loading="lazy" width="480" height="270">
            <span class="tile-text"><span class="tile-name">{name}</span><span class="tile-motto">{html.escape(motto)}</span></span>
          </a>""")
    return "\n".join(tiles)


def class_slides():
    slides = []
    for i, (cid, name, colour, motto, line, hall, hearts) in enumerate(CLASSES):
        loading = "eager" if i == 0 else "lazy"
        slides.append(f"""          <article class="class-slide{' is-active' if i == 0 else ''}" id="{cid}" data-id="{cid}" style="--accent: {accent(cid, colour)}">
            <img src="/assets/img/classes/{cid}.webp" alt="The {name} shrine in a BattleTown Class Hall" loading="{loading}" width="1600" height="900">
            <div class="slide-text">
              <p class="slide-hall">Class Hall {hall}</p>
              <h2 class="slide-name">{name}</h2>
              <p class="slide-motto">{html.escape(motto)}</p>
              <p class="slide-line">{html.escape(line)}</p>
              <ul class="chips"><li>{hearts} hearts</li><li>Own weapons &amp; abilities</li></ul>
            </div>
          </article>""")
    return "\n".join(slides)


def class_picker():
    picks = []
    for i, (cid, name, colour, *_rest) in enumerate(CLASSES):
        picks.append(f"""          <a href="#{cid}" style="--pick: {accent(cid, colour)}" aria-current="{'true' if i == 0 else 'false'}">
            <img src="/assets/img/classes/{cid}-thumb.webp" alt="" loading="lazy" width="480" height="270"><span>{name}</span>
          </a>""")
    return "\n".join(picks)


# ---------------------------------------------------------------- Icons (inline SVG, drawn for this site)

ICON_DUEL = """<svg class="icon" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 10l28 28M10 10h8v8M54 10L26 38M54 10h-8v8M34 42l-6 6 6 6M30 42l6 6-6 6M20 44l-8 8M44 44l8 8"/></svg>"""
ICON_FFA = """<svg class="icon" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M32 6l5 15 15-5-8 13 14 6-15 4 5 15-14-8-2 12-2-12-14 8 5-15-15-4 14-6-8-13 15 5z"/></svg>"""
ICON_TDM = """<svg class="icon" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round" aria-hidden="true"><path d="M8 14l14-6 14 6v14c0 12-8 20-14 24C16 48 8 40 8 28z"/><path d="M28 18l14-6 14 6v14c0 12-8 20-14 24-3-2-6-4-8-7"/></svg>"""
ICON_LAST = """<svg class="icon" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round" aria-hidden="true"><path d="M8 48l4-30 12 12 8-18 8 18 12-12 4 30z"/><path d="M8 56h48"/><circle cx="32" cy="38" r="3" fill="currentColor"/></svg>"""

MODES = [
    ("Duel", ICON_DUEL, "1v1", ["Best of 3 rounds. Win 2 rounds to win the Duel.", "Each round lasts up to 90 seconds.", "If time runs out, the player with more health left wins the round."]),
    ("Free For All", ICON_FFA, "3–8", ["Everyone for themselves. You respawn after 5 seconds.", "First to 10 kills wins, or most kills after 6 minutes.", "No teaming."]),
    ("Team Deathmatch", ICON_TDM, "2v2 · 4v4", ["Blue team against Red team. You respawn after 5 seconds.", "First team to 10 kills (2v2) or 20 kills (4v4) wins.", "Bring your friends: party up and queue together."]),
    ("Last Alive", ICON_LAST, "4 · 8", ["One life each. The last fighter standing wins.", "Out of the fight? Watch the rest of the match as a spectator.", "No teaming."]),
]


def mode_tiles(full):
    tiles = []
    for i, (name, icon, players, rules) in enumerate(MODES):
        items = "".join(f"<li>{html.escape(r)}</li>" for r in (rules if full else rules[:1]))
        tiles.append(f"""          <article class="card mode-tile tilt reveal" style="--delay: {i * 0.08:.2f}s">
            {icon}
            <p class="big">{players}</p>
            <h3>{name}</h3>
            <ul>{items}</ul>
          </article>""")
    return "\n".join(tiles)


# ---------------------------------------------------------------- Home

HERO_SLIDES = ["knight", "stormcaller", "alchemist", "pyromancer", "geomancer", "acrobat"]
hero_imgs = "\n".join(
    '          <img src="/assets/img/classes/%s.webp" alt="" %s width="1600" height="900">'
    % (c, 'fetchpriority="high"' if i == 0 else 'loading="lazy"')
    for i, c in enumerate(HERO_SLIDES))

TICKER_WORDS = ["16 classes", "4 game modes", "14 official Maps", "Build your own Map", "Earn royalties", "Rank 1 to 100",
                "Duel", "Free For All", "Team Deathmatch", "Last Alive", "Java 26.3", "Public alpha 1 December"]
ticker = "".join(f"<span>{w}</span>" for w in TICKER_WORDS * 2)

HOME = f"""    <section class="hero">
      <div class="hero-bg" aria-hidden="true">
{hero_imgs}
      </div>
      <canvas class="embers" aria-hidden="true"></canvas>
      <div class="wrap">
        <div class="hero-logo-wrap">
          <picture>
            <source srcset="/assets/img/logo-1024.webp" type="image/webp">
            <img class="hero-logo" src="/assets/img/logo-512.png" alt="BattleTown crowned BT logo" width="400" height="400" fetchpriority="high">
          </picture>
        </div>
        <h1>BattleTown</h1>
        <p class="lead">Sixteen classes. Fast, fierce matches. Arenas built by players. Pick your fighter and claim the crown.</p>

        {ip_box()}

        <div class="live-row">
          <span class="pill" data-server-status><span class="dot"></span><span class="status-text">Checking server…</span></span>
          <span class="pill" data-countdown="{ALPHA_START}"><span class="countdown-label">Public alpha in</span> <span class="countdown"></span></span>
          <span class="pill">Minecraft <strong>Java 26.3</strong></span>
        </div>

        <div class="btn-row">
          <a class="btn" href="#join">How to join</a>
          <a class="btn btn-discord" href="{DISCORD}">Join the Discord</a>
        </div>
      </div>
      <a class="scroll-cue" href="#fighters" aria-label="Scroll down"></a>
    </section>

    <div class="ticker" aria-hidden="true"><div class="ticker-track">{ticker}</div></div>

    <section class="section" id="fighters">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="eyebrow">Choose your fighter</span>
          <h2>16 classes. One crown.</h2>
          <p class="lead">Every class has its own weapons, armour and abilities. Walk into a Class Hall, step on a pad, and fight your way.</p>
        </div>
        <div class="rail reveal">
{class_tiles()}
        </div>
        <div class="btn-row" style="justify-content: flex-start; margin-top: 8px">
          <a class="btn btn-ghost" href="/classes/">Meet every class</a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section-head center reveal">
          <span class="eyebrow">Game modes</span>
          <h2>Pick your fight</h2>
          <p class="lead">Matches last 4 to 7 minutes. Vote on the Map, count down, and go.</p>
        </div>
        <div class="grid">
{mode_tiles(False)}
        </div>
        <div class="btn-row" style="margin-top: 28px">
          <a class="btn btn-ghost" href="/modes/">All the rules</a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap split">
        <div class="art-frame tilt reveal">
          <img src="/assets/img/classes/stormcaller.webp" alt="The Stormcaller shrine, built in BattleTown" loading="lazy" width="1600" height="900">
        </div>
        <div class="reveal" style="--delay: 0.1s">
          <span class="eyebrow">Creative Maps</span>
          <h2>Build the arena. Get paid.</h2>
          <p class="lead">Buy a Map, build your own arena in Creative and send it to BattleTown. If it's approved, it joins public matches with your name on it, and you earn $1,000 BattleBucks every time a match on it finishes.</p>
          <div class="btn-row" style="justify-content: flex-start">
            <a class="btn" href="/maps/">How building works</a>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap split">
        <div class="reveal">
          <span class="eyebrow">Store</span>
          <h2>Gear up in style</h2>
          <p class="lead">BattleBucks, XP Boosts, Class Collections and the Winterfest Mythic Bundle. Cosmetics only: nothing you buy changes a fight.</p>
          <div class="btn-row" style="justify-content: flex-start">
            <a class="btn" href="/store/">Open the store</a>
          </div>
        </div>
        <div class="art-frame tilt reveal" style="--delay: 0.1s">
          <img src="/assets/img/art/cat-collections.webp" alt="Class Collections" loading="lazy" width="1400" height="788">
        </div>
      </div>
    </section>

    <section class="cta-band" id="join">
      <div class="wrap">
        <div class="reveal">
          <span class="eyebrow">Ready?</span>
          <h2>Join the battle</h2>
          <p class="lead">Minecraft: Java Edition 26.3 → Multiplayer → Add Server → paste the address. Say yes to the BattleTown resource pack: the game needs it.</p>
          {ip_box()}
          <div class="btn-row" style="margin-top: 28px">
            <a class="btn btn-discord" href="{DISCORD}">Join the Discord</a>
          </div>
        </div>
      </div>
    </section>
"""

# ---------------------------------------------------------------- Classes page

CLASSES_BODY = f"""    <section class="page-head">
      <div class="wrap reveal">
        <span class="eyebrow">Choose your fighter</span>
        <h1>Classes</h1>
        <p class="lead">Walk into a Class Hall in the Hub and step on a class pad to pick one. Every class has its own weapons, armour and abilities, and you can switch between matches.</p>
      </div>
    </section>

    <section class="section-tight">
      <div class="wrap showcase">
        <div class="stage" aria-roledescription="carousel" aria-label="Classes">
{class_slides()}
          <button class="stage-arrow prev" type="button" aria-label="Previous class">‹</button>
          <button class="stage-arrow next" type="button" aria-label="Next class">›</button>
        </div>
        <nav class="picker" aria-label="Pick a class">
{class_picker()}
        </nav>
      </div>
    </section>
"""

# ---------------------------------------------------------------- Modes page

MODES_BODY = f"""    <section class="page-head">
      <div class="page-head-art" style="background-image: url('/assets/img/classes/knight.webp')"></div>
      <div class="wrap reveal">
        <span class="eyebrow">Game modes</span>
        <h1>Pick your fight</h1>
        <p class="lead">Step onto a Battle Plaza platform in the Hub, or type <code>/play</code>. Quick Play puts you in whichever mode fills first. Players vote on the Map, then the fight starts.</p>
      </div>
    </section>

    <section class="section-tight">
      <div class="wrap">
        <div class="grid grid-2">
{mode_tiles(True)}
        </div>

        <div class="callout reveal">
          <p><strong>Every finished public match pays BattleBucks and rank XP.</strong> Win, get kills and assists, and spend it on cosmetics or your own Map.</p>
        </div>
      </div>
    </section>
"""

# ---------------------------------------------------------------- Maps page

MAPS = ["Castle", "Apocalypse", "BackRooms", "Sky Temple", "Atlantis", "Volcano", "IceBound",
        "Oriental", "Mesa", "Fantasy", "Jungle", "Nether", "Aqua", "End"]

# (name, side in blocks, price)
MAP_SIZES = [("Micro", 64, "$100,000"), ("Mini", 96, "$300,000"), ("Small", 144, "$1,000,000"),
             ("Medium", 216, "$5,000,000"), ("Large", 288, "$10,000,000"), ("Huge", 388, "$20,000,000")]

map_items = "\n".join(f'          <li class="reveal" style="--delay: {i * 0.04:.2f}s">{m}</li>' for i, m in enumerate(MAPS))
size_items = "\n".join(
    f"""          <div class="size">
            <div class="size-block" style="--s: {round(30 + side * 0.42)}; --delay: {i * 0.12:.2f}s"></div>
            <div class="size-name">{name}</div>
            <div class="size-meta">{side} × {side}<br><strong>{price}</strong></div>
          </div>""" for i, (name, side, price) in enumerate(MAP_SIZES))

MAPS_BODY = f"""    <section class="page-head">
      <div class="page-head-art" style="background-image: url('/assets/img/art/header.webp')"></div>
      <div class="wrap reveal">
        <span class="eyebrow">Maps</span>
        <h1>The arenas</h1>
        <p class="lead">Every match is played on a Map. Before a match starts, players vote on which one to fight on. BattleTown has {len(MAPS)} official Maps, and players can build more.</p>
      </div>
    </section>

    <section class="section-tight">
      <div class="wrap">
        <h2 class="reveal">Official Maps</h2>
        <ul class="map-list">
{map_items}
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="wrap split">
        <div class="reveal">
          <span class="eyebrow">Creative</span>
          <h2>Build your own Map</h2>
          <p class="lead">Buy a Map at the Creative Shop in the Hub and build your own arena in Creative. If BattleTown approves it, it joins public matches.</p>
        </div>
        <ol class="steps reveal" style="--delay: 0.1s">
          <li><strong>Buy a Map</strong> with in-game BattleBucks. Pick a size.</li>
          <li><strong>Build</strong> your arena in Creative, with the build tools.</li>
          <li><strong>Set Battle Spawns</strong> so a full match can play on it, then test it.</li>
          <li><strong>Send it to BattleTown.</strong> A curator plays it and decides.</li>
          <li><strong>Get approved</strong> and your Map shows up in public Map votes, with your name on it.</li>
          <li><strong>Earn royalties:</strong> $1,000 BattleBucks every time a public match on your Map finishes.</li>
        </ol>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section-head center reveal">
          <span class="eyebrow">Map sizes</span>
          <h2>Start small. Go huge.</h2>
          <p class="lead">Prices are in-game BattleBucks. You can grow a Map to a bigger size later.</p>
        </div>
        <div class="sizes reveal">
{size_items}
        </div>
      </div>
    </section>
"""

# ---------------------------------------------------------------- Store

STORE_BODY = f"""    <section class="page-head">
      <div class="page-head-art" style="background-image: url('/assets/img/art/header.webp')"></div>
      <div class="wrap reveal">
        <span class="eyebrow">Store</span>
        <h1>The BattleTown Store</h1>
        <p class="lead">BattleBucks, XP Boosts, Class Collections and bundles. Checkout is run by Tebex, our payment partner, so we never see your card details. Everything is delivered to your account on <code>{ADDRESS}</code>.</p>
      </div>
    </section>

    <section class="section-tight">
      <div class="wrap">
        <!-- Filled by assets/js/store.js from Tebex Headless when a webstore token is set in config.js. -->
        <div id="store-app" hidden>
          <form class="store-name" id="store-name-form" autocomplete="on">
            <label for="store-name">Your Minecraft name</label>
            <div class="store-name-row">
              <input id="store-name" name="username" type="text" inputmode="text" autocapitalize="off" autocorrect="off" spellcheck="false" maxlength="16" placeholder="e.g. Steve" required>
              <button class="copy-btn" type="submit">Use this name</button>
            </div>
            <p class="store-name-status" id="store-name-status" aria-live="polite">Purchases go to this Minecraft: Java Edition account.</p>
          </form>

          <p class="store-message" id="store-message" role="alert" hidden></p>

          <div class="store-layout">
            <div class="store-main">
              <nav class="store-cats" id="store-cats" aria-label="Store sections"></nav>
              <div id="store-shelves"><p class="store-loading">Loading the store…</p></div>
            </div>

            <aside class="basket" id="basket" aria-label="Basket">
              <h2>Basket</h2>
              <ul class="basket-items" id="basket-items"></ul>
              <p class="basket-total-row"><span>Total</span> <strong id="basket-total"></strong></p>
              <button class="btn basket-checkout" id="basket-checkout" type="button" disabled>Checkout</button>
              <p class="basket-note" id="basket-note"></p>
              <p class="basket-note">Taxes are added at checkout. Purchases are covered by the <a href="/rules/#terms">Terms of Service</a>.</p>
            </aside>
          </div>

          <a class="btn basket-bar" id="basket-bar" href="#basket">Basket</a>
        </div>

        <div class="callout" id="store-coming-soon">
          <p><strong>Buy in game.</strong> Join <code>{ADDRESS}</code> and type <code>/buy</code>. Checkout is handled by Tebex, and we never see your card details.</p>
        </div>
        <noscript><p>The store needs JavaScript. You can also buy in game with <code>/buy</code>.</p></noscript>
      </div>
    </section>
"""

THANKS_BODY = f"""    <section class="page-head">
      <canvas class="embers" aria-hidden="true"></canvas>
      <div class="wrap reveal">
        <span class="eyebrow">Thank you</span>
        <h1>You're all set!</h1>
        <p class="lead">Your purchase is on its way. Tebex emails your receipt.</p>
      </div>
    </section>

    <section class="section-tight">
      <div class="wrap">
        <ol class="steps reveal">
          <li><strong>Join</strong> <code>{ADDRESS}</code>. Delivery can take a few minutes after payment.</li>
          <li><strong>BattleBucks</strong> go straight to your balance. <strong>XP Boosts</strong>, <strong>Collections</strong> and <strong>bundles</strong> show up in game, ready to use. Cosmetics are in your <code>/wardrobe</code>.</li>
          <li>Something missing after 15 minutes? Email <a href="mailto:battletowntm@gmail.com">battletowntm@gmail.com</a> or open a ticket on the <a href="{DISCORD}">Discord</a>.</li>
        </ol>
        <div class="btn-row" style="justify-content: flex-start; margin-top: 28px">
          <a class="btn" href="/store/">Back to the store</a>
        </div>
      </div>
    </section>
    <script>try {{ localStorage.removeItem("bt-store-basket"); }} catch (e) {{}}</script>
"""

# ---------------------------------------------------------------- Rules


def java_string(s):
    return s.replace('\\"', '"').replace("\\\\", "\\")


def parse_rules():
    src = open(RULES_JAVA).read()
    updated = re.search(r'UPDATED = "([^"]*)" \+ VERSION \+ "([^"]*)"', src)
    version = re.search(r"VERSION = (\d+);", src).group(1)
    updated_text = updated.group(1) + version + updated.group(2)

    def list_of(name):
        block = re.search(name + r" =\s*List\.of\((.*?)\);", src, re.S).group(1)
        return [java_string(m) for m in re.findall(r'"((?:[^"\\]|\\.)*)"', block)]

    short_rules = list_of("SHORT_RULES")
    short_punish = re.search(r'SHORT_PUNISHMENT =\s*"([^"]*)"', src).group(1)
    short_terms = list_of("SHORT_TERMS")

    docs = {}
    for name in ("RULES_PAGES", "TERMS_PAGES", "PRIVACY_PAGES"):
        start = src.index(f"List<Page> {name} =")
        end = src.index("\n            );", start)
        block = src[start:end]
        blocks = []
        for kind, text in re.findall(r'(heading|text|note)\(\s*("(?:[^"\\]|\\.)*"|UPDATED)\s*\)', block):
            text = updated_text if text == "UPDATED" else java_string(text[1:-1])
            blocks.append((kind, text))
        docs[name] = blocks
    return short_rules, short_punish, short_terms, docs


def linkify(text):
    t = html.escape(text)
    t = t.replace("battletowntm@gmail.com", '<a href="mailto:battletowntm@gmail.com">battletowntm@gmail.com</a>')
    t = t.replace("discord.gg/TJ5wBJYCc", f'<a href="{DISCORD}">discord.gg/TJ5wBJYCc</a>')
    t = re.sub(r"(/report)", r"<code>\1</code>", t)
    return t


def render_doc(blocks):
    out = []
    for kind, text in blocks:
        if kind == "heading":
            out.append(f"          <h3>{html.escape(text)}</h3>")
        elif kind == "note":
            out.append(f'          <p class="note">{html.escape(text)}</p>')
        else:
            out.append(f"          <p>{linkify(text)}</p>")
    return "\n".join(out)


short_rules, short_punish, short_terms, docs = parse_rules()
short_rules_html = "\n".join(f"            <li>{linkify(r)}</li>" for r in short_rules)
short_terms_html = "\n".join(f"            <li>{html.escape(t)}</li>" for t in short_terms)

RULES_BODY = f"""    <section class="page-head">
      <div class="wrap reveal">
        <span class="eyebrow">Fair play</span>
        <h1>Rules &amp; Terms</h1>
        <p class="lead">The same Server Rules, Terms of Service and Privacy Policy you agree to in game with <code>/rules</code>.</p>
        <div class="doc-tabs">
          <a class="btn btn-small" href="#rules">Server Rules</a>
          <a class="btn btn-small" href="#terms">Terms of Service</a>
          <a class="btn btn-small" href="#privacy">Privacy Policy</a>
        </div>
      </div>
    </section>

    <section class="section-tight">
      <div class="wrap doc">
        <div class="card reveal">
          <h2>In short</h2>
          <ol class="short">
{short_rules_html}
          </ol>
          <p>{html.escape(short_punish)}</p>
          <ul>
{short_terms_html}
          </ul>
        </div>
      </div>
    </section>

    <section class="section-tight" id="rules">
      <div class="wrap doc">
        <h2>Server Rules</h2>
{render_doc(docs["RULES_PAGES"])}
      </div>
    </section>

    <section class="section-tight" id="terms">
      <div class="wrap doc">
        <h2>Terms of Service</h2>
{render_doc(docs["TERMS_PAGES"])}
      </div>
    </section>

    <section class="section-tight" id="privacy">
      <div class="wrap doc">
        <h2>Privacy Policy</h2>
{render_doc(docs["PRIVACY_PAGES"])}
        <h3>THIS WEBSITE</h3>
        <p>battletown.store is a plain website hosted on GitHub Pages. It sets no cookies and has no ads or trackers. GitHub may log your IP address when you visit, to run and protect its service.</p>
        <p>The home page asks mcsrvstat.us, a public server-status service, whether the BattleTown server is online, so your browser contacts that service when you visit it.</p>
        <p>The Store page talks to Tebex to show what's for sale and to keep your basket. It sends Tebex the Minecraft name you type there, and your browser remembers that name and your basket on your own device. Payment happens on Tebex's checkout, under Tebex's own terms and privacy policy.</p>
        <p>If you turn on the music, your browser remembers that for the rest of your visit. Music never plays until you tap it.</p>
      </div>
    </section>
"""

NOT_FOUND = """    <section class="hero" style="min-height: 70vh">
      <canvas class="embers" aria-hidden="true"></canvas>
      <div class="wrap">
        <h1>Lost in the arena</h1>
        <p class="lead" style="margin: 0 auto 26px">That page doesn't exist.</p>
        <div class="btn-row"><a class="btn" href="/">Back to the Hub</a></div>
      </div>
    </section>
"""

page("/", None, "BattleTown: class-based PvP arenas for Minecraft Java 26.3. Join at play.battletown.store. Public alpha 1 December 2026.", HOME)
page("/classes/", "Classes", "All 16 BattleTown classes, from Acrobat to Warden.", CLASSES_BODY, scripts=("/assets/js/classes.js",),
     image="https://battletown.store/assets/img/classes/knight.webp")
page("/modes/", "Game modes", "BattleTown game modes: Duel, Free For All, Team Deathmatch and Last Alive.", MODES_BODY)
page("/maps/", "Maps", "BattleTown's official Maps, and how to build your own Map and get it into public matches.", MAPS_BODY)
page("/store/", "Store", "The BattleTown store: BattleBucks, XP Boosts, Class Collections and bundles, with checkout by Tebex.", STORE_BODY, scripts=("/assets/js/store.js",),
     image="https://battletown.store/assets/img/art/cat-collections.webp")
page("/store/thanks/", "Thank you", "Thanks for supporting BattleTown.", THANKS_BODY)
page("/rules/", "Rules & Terms", "BattleTown Server Rules, Terms of Service and Privacy Policy.", RULES_BODY)
page("/404", "Page not found", "Page not found.", NOT_FOUND)
print("ok", sum(len(v) for v in docs.values()), "rule blocks")
