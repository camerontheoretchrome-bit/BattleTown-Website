"""Writes every HTML page of the BattleTown website.

The pages are plain HTML, so GitHub Pages serves them as they are. This
script is their source: change the words here, run it, and commit both.

    python3 tools/generate-pages.py

Game words are read straight from the game, so the website always says
what the game says. Run this again whenever one of these changes:

  RulesDocuments.java  the Rules, Terms and Privacy text (/rules)
  ClassCards.java      every class card: motto, role, weapons, abilities, hall
  classes.yml          max health (the live server config)

It also writes sitemap.xml and robots.txt, and stamps every CSS/JS link
with a content hash so visitors get changes straight away.
"""
import hashlib
import html
import os
import re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_SRC = os.path.expanduser("~/Documents/BattleTown-Plugin/src/main/java/me/camerontheoret/battletown")
RULES_JAVA = os.path.join(PLUGIN_SRC, "hub/rules/RulesDocuments.java")
CLASS_CARDS_JAVA = os.path.join(PLUGIN_SRC, "classhall/ClassCards.java")
CLASSES_YML = os.path.expanduser("~/Documents/BattleTown-Server/plugins/BattleTown/classes.yml")
SITE_URL = "https://battletown.store"
MAPS_YML = os.path.expanduser("~/Documents/BattleTown-Server/plugins/BattleTown/maps.yml")
PAGES = []

# Visitor stats (GoatCounter: free, no cookies). Paste the site code from
# goatcounter.com here (for https://battletown.goatcounter.com, "battletown")
# and run this script. Empty = no visitor stats at all.
GOATCOUNTER_CODE = ""

NAV = [("/", "Home"), ("/classes/", "Classes"), ("/modes/", "Game modes"),
       ("/maps/", "Maps"), ("/leaderboards/", "Leaderboards"), ("/store/", "Store"), ("/rules/", "Rules")]

DISCORD = "https://discord.gg/TJ5wBJYCc"
ADDRESS = "play.battletown.store"

# Public alpha opens at midnight Ottawa time.
ALPHA_START = "2026-12-01T00:00:00-05:00"


def asset(path):
    """A site path with ?v=<content hash>, so browsers fetch changed files."""
    with open(os.path.join(SITE, path.lstrip("/")), "rb") as f:
        return path + "?v=" + hashlib.sha1(f.read()).hexdigest()[:8]


JSON_LD = """<script type="application/ld+json">{"@context":"https://schema.org","@type":"VideoGame","name":"BattleTown","url":"https://battletown.store/","description":"Class-based PvP arenas for Minecraft: Java Edition 26.3, with 16 classes, four game modes and player-built Maps.","image":"https://battletown.store/assets/img/social-card.jpg","gamePlatform":"Minecraft: Java Edition","genre":["PvP","Arena"],"playMode":"MultiPlayer","sameAs":["https://discord.gg/TJ5wBJYCc"]}</script>"""


GOATCOUNTER_TAG = (f'  <script data-goatcounter="https://{GOATCOUNTER_CODE}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>\n'
                   if GOATCOUNTER_CODE else "")


def page(path, title, description, body, scripts=(), image="https://battletown.store/assets/img/social-card.jpg"):
    if path not in ("/404", "/store/thanks/"):
        PAGES.append(path)
    nav = "\n".join(f'        <a href="{href}">{label}</a>' for href, label in NAV)
    extra_scripts = "".join(f'  <script src="{asset(src)}"></script>\n' for src in scripts)
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
  <meta property="og:site_name" content="BattleTown">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="https://battletown.store{path if path != '/404' else '/'}">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/assets/img/icon-32.png" sizes="32x32">
  <link rel="apple-touch-icon" href="/assets/img/icon-180.png">
  <link rel="preload" href="/assets/fonts/lilita-one-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{asset('/assets/css/site.css')}">
  <script>document.documentElement.classList.add("js");</script>
  {JSON_LD if path == "/" else ""}
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <div class="progress" aria-hidden="true"></div>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="/"><img src="/assets/img/icon-96.webp" alt="" width="38" height="38">BattleTown</a>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="main-nav" aria-label="Menu"><span></span><span></span><span></span></button>
      <nav class="nav" id="main-nav" aria-label="Main">
{nav}
        <a class="nav-play" href="/#join">Play now</a>
      </nav>
    </div>
  </header>

  <main id="main">
{body}
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-brand">
        <img src="/assets/img/icon-96.webp" alt="" width="52" height="52" loading="lazy">
        <p><strong>BattleTown</strong><br><code>{ADDRESS}</code> · Minecraft Java 26.3</p>
      </div>
      <nav aria-label="Footer">
        <a href="{DISCORD}">Discord</a>
        <a href="/leaderboards/">Leaderboards</a>
        <a href="/store/">Store</a>
        <a href="/rules/">Server Rules</a>
        <a href="/rules/#terms">Terms</a>
        <a href="/rules/#privacy">Privacy</a>
      </nav>
      <p>Not an official Minecraft product. Not approved by or associated with Mojang or Microsoft.</p>
    </div>
  </footer>

  <script src="{asset('/assets/js/config.js')}"></script>
  <script src="{asset('/assets/js/site.js')}"></script>
{GOATCOUNTER_TAG}
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
# Read from the game itself: ClassCards.java (the Class Hall card for every
# class) and classes.yml (max health).

HALLS = {"Warriors Hall": "Warriors & Hunters", "Mages Hall": "Mages & Specialists"}


def _balanced(text, i):
    """Index just past the ")" that closes the "(" at text[i], skipping strings."""
    depth, j, in_str = 0, i, False
    while j < len(text):
        c = text[j]
        if in_str:
            if c == "\\":
                j += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    raise ValueError("unbalanced parentheses")


def _strings(text):
    return [java_string(m) for m in re.findall(r'"((?:[^"\\]|\\.)*)"', text)]


def parse_class_cards():
    src = open(CLASS_CARDS_JAVA).read()
    body = src[src.index("private static Map<String, ClassCard> build()"):]
    halls = [(m.start(), m.group(1)) for m in re.finditer(r"//[^\n]*\((Warriors Hall|Mages Hall)\)", body)]
    cards = []
    for m in re.finditer(r"\bput\(\s*cards,", body):
        open_at = body.index("(", m.start())
        block = body[open_at + 1:_balanced(body, open_at) - 1]
        lists = []
        for lm in re.finditer(r"List\.of\(", block):
            if any(a <= lm.start() < b for a, b in lists):
                continue
            o = lm.end() - 1
            lists.append((lm.start(), _balanced(block, o)))
        head = _strings(block[:lists[0][0]])
        weapons = _strings(block[lists[0][0]:lists[0][1]])
        supplies = _strings(block[lists[1][0]:lists[1][1]])
        abilities = re.findall(r'new Ability\(\s*"((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\s*\)', block[lists[2][0]:lists[2][1]])
        colour = "#" + re.search(r"0x([0-9A-Fa-f]{6})", block[lists[2][1]:]).group(1).upper()
        hall = [h for at, h in halls if at < m.start()][-1]
        cid, name, tagline, role, playstyle = head[:5]
        cards.append({
            "id": cid, "name": name, "tagline": tagline, "role": role, "playstyle": playstyle,
            "weapons": weapons, "supplies": supplies,
            "abilities": [(java_string(a), java_string(b)) for a, b in abilities],
            "colour": colour, "hall": hall,
        })
    return cards


def parse_hearts():
    hearts, current = {}, None
    for line in open(CLASSES_YML):
        top = re.match(r"^  ([a-z_]+):\s*$", line)
        if top:
            current = top.group(1)
            continue
        health = re.match(r"^\s+max-health:\s*([0-9.]+)", line)
        if health and current and current not in hearts:
            hearts[current] = float(health.group(1)) / 2
    return hearts


def java_string(s):
    return s.replace('\\"', '"').replace("\\\\", "\\")


CARDS = parse_class_cards()
HEARTS = parse_hearts()
assert len(CARDS) == 16, len(CARDS)


def hearts_text(cid):
    h = HEARTS.get(cid, 10)
    return f"{h:g} hearts"


def weapon_name(w):
    """"Oathkeeper [Iron Sword]" -> ("Oathkeeper", "Iron Sword")."""
    m = re.match(r"(.*?)\s*\[(.*)\]$", w)
    return (m.group(1), m.group(2)) if m else (w, "")


def accent(card):
    # Ranger's dark green needs a lighter tint to read on black.
    return "#5FAE5D" if card["id"] == "ranger" else card["colour"]


def motto(card):
    return card["tagline"].capitalize()


def class_tiles():
    tiles = []
    for c in CARDS:
        tiles.append(f"""          <a class="class-tile" href="/classes/#{c['id']}" style="--accent: {accent(c)}">
            <img src="/assets/img/classes/{c['id']}-thumb.webp" alt="" loading="lazy" width="480" height="270">
            <span class="tile-text"><span class="tile-hall">{c['hall']}</span><span class="tile-name">{c['name']}</span><span class="tile-motto">{html.escape(c['tagline'])}</span></span>
          </a>""")
    return "\n".join(tiles)


def class_slides():
    slides = []
    for i, c in enumerate(CARDS):
        weapons = "".join(
            f"<li><strong>{html.escape(n)}</strong>{(' · ' + html.escape(k)) if k else ''}</li>"
            for n, k in map(weapon_name, c["weapons"]))
        supplies = "".join(f"<li>{html.escape(x)}</li>" for x in c["supplies"])
        abilities = "".join(
            f'<li><strong>{html.escape(n)}</strong><span>{html.escape(e)}</span></li>' for n, e in c["abilities"])
        slides.append(f"""          <article class="class-slide{' is-active' if i == 0 else ''}" id="{c['id']}" data-id="{c['id']}" style="--accent: {accent(c)}">
            <img src="/assets/img/classes/{c['id']}.webp" alt="The {c['name']} shrine in the {c['hall']}" loading="{'eager' if i == 0 else 'lazy'}" width="1600" height="900">
            <div class="slide-text">
              <p class="slide-hall">{c['hall']} · {html.escape(c['role'])}</p>
              <h2 class="slide-name">{c['name']}</h2>
              <p class="slide-motto">{html.escape(c['tagline'])}</p>
              <p class="slide-line">{html.escape(c['playstyle'])}</p>
              <ul class="abilities">{abilities}</ul>
              <ul class="chips"><li>{hearts_text(c['id'])}</li>{weapons}{supplies}</ul>
              <a class="btn btn-small slide-more" href="/classes/{c['id']}/">Full {c['name']} page</a>
            </div>
          </article>""")
    return "\n".join(slides)


def class_picker():
    groups = []
    for hall, subtitle in HALLS.items():
        picks = []
        for c in CARDS:
            if c["hall"] != hall:
                continue
            first = c is CARDS[0]
            picks.append(f"""            <a href="#{c['id']}" style="--pick: {accent(c)}" aria-current="{'true' if first else 'false'}">
              <img src="/assets/img/classes/{c['id']}-thumb.webp" alt="" loading="lazy" width="480" height="270"><span>{c['name']}</span>
            </a>""")
        groups.append(f"""          <div class="picker-group">
            <p class="picker-hall"><strong>{hall}</strong> {subtitle}</p>
            <div class="picker">
{chr(10).join(picks)}
            </div>
          </div>""")
    return "\n".join(groups)


# ---------------------------------------------------------------- Icons (inline SVG, drawn for this site)

ICON_DUEL = """<svg class="icon" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 10l28 28M10 10h8v8M54 10L26 38M54 10h-8v8M34 42l-6 6 6 6M30 42l6 6-6 6M20 44l-8 8M44 44l8 8"/></svg>"""
ICON_FFA = """<svg class="icon" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M32 6l5 15 15-5-8 13 14 6-15 4 5 15-14-8-2 12-2-12-14 8 5-15-15-4 14-6-8-13 15 5z"/></svg>"""
ICON_TDM = """<svg class="icon" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round" aria-hidden="true"><path d="M8 14l14-6 14 6v14c0 12-8 20-14 24C16 48 8 40 8 28z"/><path d="M28 18l14-6 14 6v14c0 12-8 20-14 24-3-2-6-4-8-7"/></svg>"""
ICON_LAST = """<svg class="icon" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round" aria-hidden="true"><path d="M8 48l4-30 12 12 8-18 8 18 12-12 4 30z"/><path d="M8 56h48"/><circle cx="32" cy="38" r="3" fill="currentColor"/></svg>"""

MODES = [
    ("Duel", ICON_DUEL, "1v1", ["Best of 3 rounds. Win 2 rounds to win the Duel.", "Each round lasts up to 90 seconds.", "If time runs out, the player with more health left wins the round."]),
    ("Free For All", ICON_FFA, "3–8", ["Everyone for themselves. You respawn after 5 seconds.", "First to 10 kills wins, or most kills after 6 minutes.", "No teaming."]),
    ("Team Deathmatch", ICON_TDM, "2v2 · 4v4", ["Blue team against Red team. You respawn after 5 seconds.", "First team to 10 kills (2v2) or 20 kills (4v4) wins.", "Bring your friends: party up and queue together."]),
    ("Last Alive", ICON_LAST, "4 · 8", ["One life each. The last fighter standing wins.", "A 5-minute clock: at 4:00 everyone glows, and at time-up the survivor with the most kills wins.", "Out? Watch the rest as a spectator. No teaming."]),
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


# ---------------------------------------------------------------- Hub, features, FAQ

PLACES = [
    ("Battle Plaza", "Step onto a platform to queue for Quick Play, Duel, Free For All, Team Deathmatch or Last Alive."),
    ("Warriors Hall", "Warriors &amp; Hunters: Knight, Guardian, Berserker, Lancer, Duelist, Ranger, Assassin and Poseidon."),
    ("Mages Hall", "Mages &amp; Specialists: Warden, Frostborn, Pyromancer, Alchemist, Stormcaller, Necromancer, Geomancer and Acrobat."),
    ("Cosmetic Shop", "Armour and weapon looks, trails, kill and victory effects, companions, Movement and Medallions."),
    ("Creative Shop", "Buy a Map, then build your own arena in Creative."),
    ("Leaderboards", "See who's on top, from kills and wins to the best builders."),
    ("Sky Spirals", "Four parkour climbs with a timer and medals. Type <code>/sky</code>."),
]

FEATURES = [
    ("1 → 100", "Rank up", "Level up from 1 to 100 by playing. Rewards are earned, never sold."),
    ("16", "Hidden Relics", "Sixteen relics are hidden around the Hub. How many can you find?"),
    ("$1,000", "Map royalties", "Builders earn BattleBucks every time a public match on their Map finishes."),
    ("Weekly", "Map of the Week", "The best Community Map gets the spotlight. Type <code>/mapweek</code>."),
    ("2v2 · 4v4", "Parties", "Team up with friends with <code>/party</code> and queue Team Deathmatch together."),
    ("Voice", "Proximity voice", "Talk to players near you with the Simple Voice Chat mod."),
]

FAQ = [
    ("Is BattleTown free?", "Yes, it's free to play. The store sells cosmetics, BattleBucks and XP Boosts."),
    ("Which Minecraft do I need?", "Minecraft: Java Edition 26.3. Bedrock isn't supported."),
    ("Do I need mods?", "No. The BattleTown resource pack downloads when you join. Performance mods (Sodium, Lithium, Iris), Simple Voice Chat, and the Lunar, Feather and LabyMod clients are allowed. Mods that give an advantage are not."),
    ("Is it pay-to-win?", "No. Nothing in the store changes a fight. XP Boosts only speed up rank XP, and BattleBucks buy cosmetics and Maps."),
    ("When can I play?", "The public alpha opens on 1 December 2026. <a href=\"/alpha.ics\">Add it to your calendar</a> (or <a href=\"https://calendar.google.com/calendar/render?action=TEMPLATE&amp;text=BattleTown%20public%20alpha&amp;dates=20261201T050000Z/20261201T070000Z&amp;details=Join%20at%20play.battletown.store%20(Minecraft%20Java%2026.3)&amp;location=play.battletown.store\">Google Calendar</a>) and join the Discord for news before then."),
    ("Can I play with friends?", "Yes. Add friends with <code>/friends</code>, team up with <code>/party</code>, and queue together."),
    ("How old do I have to be?", "13 or older. Under 18s need a parent or guardian to agree to the <a href=\"/rules/#terms\">Terms</a>."),
]


def places():
    return "\n".join(
        f"""          <article class="card place tilt reveal" style="--delay: {i * 0.05:.2f}s">
            <h3>{name}</h3>
            <p>{text}</p>
          </article>""" for i, (name, text) in enumerate(PLACES))


def features():
    return "\n".join(
        f"""          <article class="card feature tilt reveal" style="--delay: {i * 0.06:.2f}s">
            <p class="big">{big}</p>
            <h3>{name}</h3>
            <p>{text}</p>
          </article>""" for i, (big, name, text) in enumerate(FEATURES))


def faq():
    return "\n".join(
        f"""          <details>
            <summary>{q}</summary>
            <p>{a}</p>
          </details>""" for q, a in FAQ)


# ---------------------------------------------------------------- Home

HERO_SLIDES = ["knight", "stormcaller", "alchemist", "pyromancer", "geomancer", "acrobat"]
# Only the first slide loads with the page; site.js fetches the rest once it has loaded.
hero_imgs = "\n".join(
    '          <img %s="/assets/img/classes/%s.webp" alt="" %s width="1600" height="900">'
    % ("src" if i == 0 else "data-src", c, 'fetchpriority="high"' if i == 0 else "")
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
          <a class="pill pill-link" href="/alpha.ics" data-countdown="{ALPHA_START}" title="Add the launch to your calendar"><span class="countdown-label">Public alpha in</span> <span class="countdown"></span></a>
          <span class="pill">Minecraft <strong>Java 26.3</strong></span>
        </div>
        <div class="live-row live-summary" data-live-summary hidden></div>
        <div class="online-now" data-online-now hidden>
          <span class="online-label"><span class="dot is-online"></span> Online now: <span data-online-count></span></span>
          <ul></ul>
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
          <p class="lead">Eight Warriors &amp; Hunters. Eight Mages &amp; Specialists. Each class has its own weapons, armour and two abilities. Step on a class pad in the Warriors Hall or the Mages Hall and fight your way.</p>
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

    <section class="section" data-home-podium hidden>
      <div class="wrap">
        <div class="section-head center reveal">
          <span class="eyebrow">Live from the Hub</span>
          <h2>Top of the town</h2>
          <p class="lead">The Grand Champion board, live from the Hub's hall of fame.</p>
        </div>
        <div data-podium></div>
        <div class="btn-row" style="margin-top: 28px"><a class="btn btn-ghost" href="/leaderboards/">All leaderboards</a></div>
      </div>
    </section>

    <section class="section" data-recent-matches="6" hidden>
      <div class="wrap faq-wrap">
        <div class="section-head reveal">
          <span class="eyebrow">Live from the arenas</span>
          <h2>Recent matches</h2>
        </div>
        <ol class="recent-matches"></ol>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="eyebrow">The Hub</span>
          <h2>Welcome to BattleTown</h2>
          <p class="lead">Every visit starts in the Hub. Ask a Hub Guide to take you anywhere.</p>
        </div>
        <div class="grid places">
{places()}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section-head center reveal">
          <span class="eyebrow">Always something to chase</span>
          <h2>More than a match</h2>
        </div>
        <div class="grid features">
{features()}
        </div>
      </div>
    </section>

    <section class="section" id="faq">
      <div class="wrap faq-wrap">
        <div class="section-head reveal">
          <span class="eyebrow">Questions</span>
          <h2>FAQ</h2>
        </div>
        <div class="faq reveal">
{faq()}
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
        <p class="lead">Sixteen classes in two halls. Walk into the <strong>Warriors Hall</strong> or the <strong>Mages Hall</strong> in the Hub and step on a class pad to pick one. Every class has its own weapons, armour and two abilities, and you can switch between matches.</p>
      </div>
    </section>

    <section class="section-tight">
      <div class="wrap showcase">
        <div class="stage" aria-roledescription="carousel" aria-label="Classes">
{class_slides()}
          <button class="stage-arrow prev" type="button" aria-label="Previous class">‹</button>
          <button class="stage-arrow next" type="button" aria-label="Next class">›</button>
        </div>
        <nav class="pickers" aria-label="Pick a class">
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
          <li><strong>Get approved</strong> and it becomes a Community Map in public Map votes, with your name on it.</li>
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
          <p><strong>Buy in game.</strong> Join <code>{ADDRESS}</code> and type <code>/store</code>. Checkout is handled by Tebex, and we never see your card details.</p>
        </div>
        <noscript><p>The store needs JavaScript. You can also buy in game with <code>/store</code>.</p></noscript>
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
          <li>Something missing after 15 minutes? Email <a href="mailto:support@battletown.store">support@battletown.store</a> or open a ticket on the <a href="{DISCORD}">Discord</a>.</li>
        </ol>
        <div class="btn-row" style="justify-content: flex-start; margin-top: 28px">
          <a class="btn" href="/store/">Back to the store</a>
        </div>
      </div>
    </section>
    <script>try {{ localStorage.removeItem("bt-store-basket"); }} catch (e) {{}}</script>
"""

# ---------------------------------------------------------------- Live stats (phase 3)

SEARCH_FORM = """<form class="store-name-row player-search" data-player-search role="search">
            <input type="text" name="name" placeholder="Search a player…" aria-label="Minecraft name" autocapitalize="off" autocorrect="off" spellcheck="false" maxlength="16" required>
            <button class="copy-btn" type="submit">Find</button>
          </form>"""

LEADERBOARDS_BODY = f"""    <section class="page-head">
      <div class="page-head-art" style="background-image: url('/assets/img/classes/stormcaller.webp')"></div>
      <div class="wrap reveal">
        <span class="eyebrow">Live from the Hub</span>
        <h1>Leaderboards</h1>
        <p class="lead">The same boards that stand in the Hub's halls of fame, updated about every minute. Tap a name to see their profile.</p>
        {SEARCH_FORM}
        <div class="online-now" data-online-now hidden>
          <span class="online-label"><span class="dot is-online"></span> Online now: <span data-online-count></span></span>
          <ul></ul>
        </div>
      </div>
    </section>

    <section class="section-tight">
      <div class="wrap" id="leaderboards">
        <p class="store-loading">Loading the leaderboards…</p>
      </div>
    </section>

    <section class="section-tight" data-recent-matches="12" hidden>
      <div class="wrap faq-wrap">
        <h2>Recent matches</h2>
        <ol class="recent-matches"></ol>
      </div>
    </section>
"""


def classes_json():
    import json
    return json.dumps({c["id"]: {"name": c["name"], "colour": accent(c)} for c in CARDS}, separators=(",", ":"))


PLAYER_BODY = f"""    <section class="section-tight">
      <div class="wrap">
        <div class="profile-search">{SEARCH_FORM}</div>
        <div id="profile"><p class="store-loading">Loading player…</p></div>
      </div>
    </section>
    <script>window.BT_CLASSES = {classes_json()};</script>
"""

# ---------------------------------------------------------------- Map names (for recent matches)


def map_names():
    """Map id -> display name from the live maps.yml (official Maps)."""
    import json
    names, current = {}, None
    try:
        for line in open(MAPS_YML):
            top = re.match(r"^  ([a-z0-9_]+):\s*$", line)
            if top:
                current = top.group(1)
                continue
            shown = re.match(r"^    display-name:\s*(.+?)\s*$", line)
            if shown and current and current not in names:
                names[current] = shown.group(1).strip("'\"")
    except OSError:
        pass
    return json.dumps(names, separators=(",", ":"))


MAPS_SCRIPT = f"    <script>window.BT_MAPS = {map_names()};</script>\n"

# ---------------------------------------------------------------- One page per class


def class_page(i, c):
    prev_c, next_c = CARDS[i - 1], CARDS[(i + 1) % len(CARDS)]
    abilities = "".join(
        f'<li><strong>{html.escape(n)}</strong><span>{html.escape(e)}</span></li>' for n, e in c["abilities"])
    weapons = "".join(
        f"<li><strong>{html.escape(n)}</strong>{(' · ' + html.escape(k)) if k else ''}</li>"
        for n, k in map(weapon_name, c["weapons"]))
    supplies = "".join(f"<li>{html.escape(x)}</li>" for x in c["supplies"])
    mates = [m for m in CARDS if m["hall"] == c["hall"] and m["id"] != c["id"]]
    mate_links = "".join(
        f'<a href="/classes/{m["id"]}/" style="--pick: {accent(m)}"><img src="/assets/img/classes/{m["id"]}-thumb.webp" alt="" loading="lazy" width="480" height="270"><span>{m["name"]}</span></a>'
        for m in mates)
    return f"""    <section class="class-hero" style="--accent: {accent(c)}">
      <img class="class-hero-img" src="/assets/img/classes/{c['id']}.webp" alt="The {c['name']} shrine in the {c['hall']}" width="1600" height="900" fetchpriority="high">
      <div class="wrap class-hero-text reveal">
        <p class="slide-hall">{c['hall']} · {html.escape(c['role'])}</p>
        <h1 class="slide-name">{c['name']}</h1>
        <p class="slide-motto">{html.escape(c['tagline'])}</p>
        <p class="slide-line">{html.escape(c['playstyle'])}</p>
      </div>
    </section>

    <section class="section-tight" style="--accent: {accent(c)}">
      <div class="wrap">
        <div class="class-detail">
          <div class="reveal">
            <h2>Abilities</h2>
            <ul class="abilities abilities-big">{abilities}</ul>
          </div>
          <div class="reveal" style="--delay: 0.1s">
            <h2>Kit</h2>
            <ul class="chips">{weapons}{supplies}<li>{hearts_text(c['id'])}</li></ul>
            <p class="lead" style="margin-top: 18px">Pick the {c['name']} on a class pad in the <strong>{c['hall']}</strong> in the Hub. You can switch class between matches.</p>
            <div class="btn-row" style="justify-content: flex-start">
              <a class="btn" href="/#join">Play now</a>
              <button class="btn btn-ghost" type="button" data-copy="https://battletown.store/classes/{c['id']}/">Copy link</button>
            </div>
          </div>
        </div>

        <h2 class="reveal" style="margin-top: 48px">More in the {c['hall']}</h2>
        <div class="picker reveal">{mate_links}</div>

        <div class="class-nav">
          <a class="btn btn-small" href="/classes/{prev_c['id']}/">‹ {prev_c['name']}</a>
          <a class="btn btn-small" href="/classes/">All classes</a>
          <a class="btn btn-small" href="/classes/{next_c['id']}/">{next_c['name']} ›</a>
        </div>
      </div>
    </section>
"""


def write_calendar():
    """alpha.ics: the public alpha as a calendar event (Apple, Outlook, Google import)."""
    ics = "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//BattleTown//Website//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        "BEGIN:VEVENT", "UID:battletown-public-alpha-2026@battletown.store", "DTSTAMP:20261104T000000Z",
        "DTSTART:20261201T050000Z", "DTEND:20261201T070000Z",
        "SUMMARY:BattleTown public alpha",
        "DESCRIPTION:BattleTown opens! Join at play.battletown.store (Minecraft: Java Edition 26.3). https://battletown.store",
        "LOCATION:play.battletown.store", "URL:https://battletown.store/",
        "BEGIN:VALARM", "TRIGGER:-PT30M", "ACTION:DISPLAY", "DESCRIPTION:BattleTown opens in 30 minutes", "END:VALARM",
        "END:VEVENT", "END:VCALENDAR", ""])
    with open(os.path.join(SITE, "alpha.ics"), "w", newline="") as f:
        f.write(ics)


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
    t = t.replace("support@battletown.store", '<a href="mailto:support@battletown.store">support@battletown.store</a>')
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

GOATCOUNTER_PRIVACY = ("<p>Visitor numbers are counted with GoatCounter, which sets no cookies and keeps no personal information, only which pages are visited and roughly from where.</p>"
                       if GOATCOUNTER_CODE else "")

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
        <p>The Leaderboards and player pages read BattleTown's own public stats feed (api.battletown.store). Player pages show Minecraft skins rendered by mc-heads.net, a third-party service, so your browser contacts it when you open one.</p>
        <p>The home page and Leaderboards show who is on the server right now, the same names the Minecraft server list shows, and the latest public matches. Discord buttons show the server's member count from Discord's public invite information.</p>
        {GOATCOUNTER_PRIVACY}
        <p>If you turn on the music, your browser remembers that for the rest of your visit. Music never plays until you tap it.</p>
      </div>
    </section>
"""

NOT_FOUND = """    <script>
      (function () {
        // battletown.store/player/NAME is a share-friendly profile link.
        var m = location.pathname.match(/^\\/player\\/([A-Za-z0-9_]{1,16})\\/?$/);
        if (m) { location.replace("/player/?name=" + m[1]); }
      })();
    </script>
    <section class="hero" style="min-height: 70vh">
      <canvas class="embers" aria-hidden="true"></canvas>
      <div class="wrap">
        <h1>Lost in the arena</h1>
        <p class="lead" style="margin: 0 auto 26px">That page doesn't exist.</p>
        <div class="btn-row"><a class="btn" href="/">Back to the Hub</a></div>
      </div>
    </section>
"""

HOME = HOME + MAPS_SCRIPT
LEADERBOARDS_BODY = LEADERBOARDS_BODY + MAPS_SCRIPT
page("/", None, "BattleTown: class-based PvP arenas for Minecraft Java 26.3. Join at play.battletown.store. Public alpha 1 December 2026.", HOME,
     scripts=("/assets/js/stats.js",))
page("/leaderboards/", "Leaderboards", "Live BattleTown leaderboards: Champions, Records and Builders, straight from the Hub.", LEADERBOARDS_BODY,
     scripts=("/assets/js/stats.js",))
page("/player/", "Player", "A BattleTown player's profile: rank, wins, kills, best classes and leaderboard places.", PLAYER_BODY,
     scripts=("/assets/js/stats.js",))
for _i, _c in enumerate(CARDS):
    page(f"/classes/{_c['id']}/", _c["name"],
         f"{_c['name']}, {_c['role']} in BattleTown's {_c['hall']}: {_c['tagline'].capitalize()}. "
         + " ".join(f"{n}: {e}" for n, e in _c["abilities"]),
         class_page(_i, _c), image=f"https://battletown.store/assets/img/classes/{_c['id']}.webp")
write_calendar()

page("/classes/", "Classes", "All 16 BattleTown classes, from Acrobat to Warden.", CLASSES_BODY, scripts=("/assets/js/classes.js",),
     image="https://battletown.store/assets/img/classes/knight.webp")
page("/modes/", "Game modes", "BattleTown game modes: Duel, Free For All, Team Deathmatch and Last Alive.", MODES_BODY)
page("/maps/", "Maps", "BattleTown's official Maps, and how to build your own Map and get it into public matches.", MAPS_BODY)
page("/store/", "Store", "The BattleTown store: BattleBucks, XP Boosts, Class Collections and bundles, with checkout by Tebex.", STORE_BODY, scripts=("/assets/js/store.js",),
     image="https://battletown.store/assets/img/art/cat-collections.webp")
page("/store/thanks/", "Thank you", "Thanks for supporting BattleTown. Your purchase is on its way to your account.", THANKS_BODY)
page("/rules/", "Rules & Terms", "BattleTown Server Rules, Terms of Service and Privacy Policy.", RULES_BODY)
page("/404", "Page not found", "This page doesn't exist. Head back to BattleTown: class-based PvP for Minecraft Java.", NOT_FOUND)
with open(os.path.join(SITE, "sitemap.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for path in PAGES:
        f.write(f"  <url><loc>{SITE_URL}{path}</loc></url>\n")
    f.write("</urlset>\n")

with open(os.path.join(SITE, "robots.txt"), "w") as f:
    f.write(f"User-agent: *\nAllow: /\nDisallow: /store/thanks/\n\nSitemap: {SITE_URL}/sitemap.xml\n")

print("ok", sum(len(v) for v in docs.values()), "rule blocks,", len(CARDS), "class cards,", len(PAGES), "pages in sitemap")
