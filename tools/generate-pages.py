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


def page(path, title, description, body):
    nav = "\n".join(f'        <a href="{href}">{label}</a>' for href, label in NAV)
    full_title = "BattleTown" if title is None else f"{title} · BattleTown"
    out = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{full_title}</title>
  <meta name="description" content="{html.escape(description)}">
  <meta name="theme-color" content="#0a0a0d">
  <meta property="og:title" content="{full_title}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:image" content="https://battletown.store/assets/img/logo-512.png">
  <meta property="og:url" content="https://battletown.store{path}">
  <link rel="icon" href="/assets/img/icon-32.png" sizes="32x32">
  <link rel="apple-touch-icon" href="/assets/img/icon-180.png">
  <link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="/"><img src="/assets/img/icon-192.png" alt="" width="36" height="36">BattleTown</a>
      <nav class="nav" aria-label="Main">
{nav}
      </nav>
    </div>
  </header>

  <main>
{body}
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <p>BattleTown · <code>{ADDRESS}</code> · Minecraft Java 26.3</p>
      <nav aria-label="Footer">
        <a href="{DISCORD}">Discord</a>
        <a href="/rules/">Server Rules</a>
        <a href="/rules/#terms">Terms</a>
        <a href="/rules/#privacy">Privacy</a>
      </nav>
      <p>Not an official Minecraft product. Not approved by or associated with Mojang or Microsoft.</p>
    </div>
  </footer>

  <script src="/assets/js/config.js"></script>
  <script src="/assets/js/site.js"></script>
</body>
</html>
"""
    dest = os.path.join(SITE, path.strip("/"), "index.html") if path != "/404" else os.path.join(SITE, "404.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as f:
        f.write(out)


# ---------------------------------------------------------------- Home

HOME = f"""    <section class="hero">
      <div class="wrap">
        <picture>
          <source srcset="/assets/img/logo-1024.webp" type="image/webp">
          <img class="hero-logo" src="/assets/img/logo-512.png" alt="BattleTown crowned BT logo" width="420" height="420">
        </picture>
        <h1>BattleTown</h1>
        <p class="lead">Class-based PvP arenas for Minecraft Java. Pick one of 16 classes, jump into a fast match, and build your own Maps.</p>

        <div class="ip-box">
          <code id="server-address">{ADDRESS}</code>
          <button class="copy-btn" type="button" data-copy="{ADDRESS}" aria-label="Copy the server address">Copy</button>
        </div>

        <ul class="facts">
          <li>Minecraft <strong>Java 26.3</strong></li>
          <li>Public alpha <strong>1 December 2026</strong></li>
        </ul>

        <div class="btn-row">
          <a class="btn btn-discord" href="{DISCORD}">Join the Discord</a>
          <a class="btn" href="/classes/">See the classes</a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <h2>How to join</h2>
        <ol class="steps">
          <li>Open <strong>Minecraft: Java Edition 26.3</strong>.</li>
          <li>Go to <strong>Multiplayer</strong>, then <strong>Add Server</strong>.</li>
          <li>Type <strong>{ADDRESS}</strong> as the server address, then join.</li>
          <li>Say <strong>yes</strong> to the BattleTown resource pack. The game needs it.</li>
        </ol>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <h2>What's inside</h2>
        <div class="grid">
          <a class="card" href="/classes/">
            <h3>16 classes</h3>
            <p>Knights, Assassins, Frostborn, Necromancers and more. Each one has its own weapons and abilities.</p>
          </a>
          <a class="card" href="/modes/">
            <h3>4 game modes</h3>
            <p>Duel, Free For All, Team Deathmatch and Last Alive. Matches last about 4 to 7 minutes.</p>
          </a>
          <a class="card" href="/maps/">
            <h3>Maps you build</h3>
            <p>Buy a Map, build an arena in Creative, and send it to BattleTown to join public matches.</p>
          </a>
          <a class="card" href="/store/">
            <h3>Store</h3>
            <p>BattleBucks bundles. The web store is coming soon.</p>
          </a>
        </div>
      </div>
    </section>
"""

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


def class_cards():
    cards = []
    for cid, name, accent, motto, line, hall, hearts in CLASSES:
        # Ranger's dark green needs a lighter tint to read on black.
        shown = "#5FAE5D" if cid == "ranger" else accent
        cards.append(f"""          <article class="card class-card" id="{cid}" style="--accent: {shown}">
            <h3>{name}</h3>
            <p class="motto">{html.escape(motto)}</p>
            <p>{html.escape(line)}</p>
            <p class="meta">Class Hall {hall} · {hearts} hearts</p>
          </article>""")
    return "\n".join(cards)


CLASSES_BODY = f"""    <section class="page-head">
      <div class="wrap">
        <h1>Classes</h1>
        <p>BattleTown has 16 classes. Walk into a Class Hall in the Hub and step on a class pad to pick one. Every class has its own weapons, armour and abilities, and you can switch between matches.</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="grid">
{class_cards()}
        </div>
      </div>
    </section>
"""

# ---------------------------------------------------------------- Modes

MODES_BODY = """    <section class="page-head">
      <div class="wrap">
        <h1>Game modes</h1>
        <p>Step onto a Battle Plaza platform in the Hub, or type <code>/play</code>. Quick Play puts you in whichever mode fills first. Players vote on the Map, then the fight starts.</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="grid grid-2">
          <article class="card mode-card">
            <h3>Duel</h3>
            <p class="players">1 vs 1</p>
            <ul>
              <li>Best of 3 rounds. Win 2 rounds to win the Duel.</li>
              <li>Each round lasts up to 90 seconds.</li>
              <li>If time runs out, the player with more health left wins the round.</li>
            </ul>
          </article>
          <article class="card mode-card">
            <h3>Free For All</h3>
            <p class="players">3 to 8 players</p>
            <ul>
              <li>Everyone for themselves. You respawn after 5 seconds.</li>
              <li>First to 10 kills wins, or most kills after 6 minutes.</li>
              <li>No teaming.</li>
            </ul>
          </article>
          <article class="card mode-card">
            <h3>Team Deathmatch</h3>
            <p class="players">2 vs 2 or 4 vs 4</p>
            <ul>
              <li>Blue team against Red team. You respawn after 5 seconds.</li>
              <li>First team to 10 kills (2v2) or 20 kills (4v4) wins.</li>
              <li>Bring your friends: party up and queue together.</li>
            </ul>
          </article>
          <article class="card mode-card">
            <h3>Last Alive</h3>
            <p class="players">4 or 8 players</p>
            <ul>
              <li>One life each. The last fighter standing wins.</li>
              <li>Out of the fight? Watch the rest of the match as a spectator.</li>
              <li>No teaming.</li>
            </ul>
          </article>
        </div>

        <div class="callout">
          <strong>Every finished public match pays BattleBucks and rank XP.</strong> Win, get kills and assists, and spend it on cosmetics or your own Map.
        </div>
      </div>
    </section>
"""

# ---------------------------------------------------------------- Maps

MAPS = ["Castle", "Apocalypse", "BackRooms", "Sky Temple", "Atlantis", "Volcano", "IceBound",
        "Oriental", "Mesa", "Fantasy", "Jungle", "Nether", "Aqua", "End"]

MAP_SIZES = [("Micro", "64 × 64", "$100,000"), ("Mini", "96 × 96", "$300,000"),
             ("Small", "144 × 144", "$1,000,000"), ("Medium", "216 × 216", "$5,000,000"),
             ("Large", "288 × 288", "$10,000,000"), ("Huge", "388 × 388", "$20,000,000")]

map_items = "\n".join(f"          <li>{m}</li>" for m in MAPS)
size_rows = "\n".join(f"            <tr><td>{n}</td><td>{a}</td><td>{p}</td></tr>" for n, a, p in MAP_SIZES)

MAPS_BODY = f"""    <section class="page-head">
      <div class="wrap">
        <h1>Maps</h1>
        <p>Every match is played on a Map. Before a match starts, players vote on which one to fight on. BattleTown has {len(MAPS)} official Maps, and players can build more.</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <h2>Official Maps</h2>
        <ul class="map-list">
{map_items}
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <h2>Build your own Map</h2>
        <p>Buy a Map at the Creative Shop in the Hub and build your own arena in Creative. If BattleTown approves it, it joins public matches.</p>
        <ol class="steps">
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
        <h2>Map sizes</h2>
        <table class="prices">
          <thead><tr><th>Size</th><th>Build area</th><th>Price</th></tr></thead>
          <tbody>
{size_rows}
          </tbody>
        </table>
        <p class="note" style="color: var(--muted)">Prices are in-game BattleBucks. You can grow a Map to a bigger size later.</p>
      </div>
    </section>
"""

# ---------------------------------------------------------------- Store

STORE_BODY = f"""    <section class="page-head">
      <div class="wrap">
        <h1>Store</h1>
        <p>The BattleTown web store is coming soon.</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <!-- Phase 2: the Tebex Headless store renders into #store-app. -->
        <div id="store-app" hidden></div>

        <div class="callout" id="store-coming-soon">
          <p><strong>Until then, buy BattleBucks in game.</strong> Join <code>{ADDRESS}</code> and type <code>/buy</code>. Checkout is handled by Tebex, and we never see your card details.</p>
        </div>

        <p>Everything you buy is covered by the <a href="/rules/#terms">Terms of Service</a>.</p>
      </div>
    </section>
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
      <div class="wrap">
        <h1>Rules &amp; Terms</h1>
        <p>The same Server Rules, Terms of Service and Privacy Policy you agree to in game with <code>/rules</code>.</p>
        <div class="doc-tabs">
          <a class="btn" href="#rules">Server Rules</a>
          <a class="btn" href="#terms">Terms of Service</a>
          <a class="btn" href="#privacy">Privacy Policy</a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap doc">
        <h2>In short</h2>
        <ol class="short">
{short_rules_html}
        </ol>
        <p>{html.escape(short_punish)}</p>
        <ul>
{short_terms_html}
        </ul>
      </div>
    </section>

    <section class="section" id="rules">
      <div class="wrap doc">
        <h2>Server Rules</h2>
{render_doc(docs["RULES_PAGES"])}
      </div>
    </section>

    <section class="section" id="terms">
      <div class="wrap doc">
        <h2>Terms of Service</h2>
{render_doc(docs["TERMS_PAGES"])}
      </div>
    </section>

    <section class="section" id="privacy">
      <div class="wrap doc">
        <h2>Privacy Policy</h2>
{render_doc(docs["PRIVACY_PAGES"])}
        <h3>THIS WEBSITE</h3>
        <p>battletown.store is a plain website hosted on GitHub Pages. It sets no cookies and has no ads or trackers. GitHub may log your IP address when you visit, to run and protect its service.</p>
      </div>
    </section>
"""

NOT_FOUND = """    <section class="page-head">
      <div class="wrap">
        <h1>Page not found</h1>
        <p>That page doesn't exist. <a href="/">Back to the home page</a>.</p>
      </div>
    </section>
"""

page("/", None, "BattleTown: class-based PvP arenas for Minecraft Java 26.3. Join at play.battletown.store. Public alpha 1 December 2026.", HOME)
page("/classes/", "Classes", "All 16 BattleTown classes, from Acrobat to Warden.", CLASSES_BODY)
page("/modes/", "Game modes", "BattleTown game modes: Duel, Free For All, Team Deathmatch and Last Alive.", MODES_BODY)
page("/maps/", "Maps", "BattleTown's official Maps, and how to build your own Map and get it into public matches.", MAPS_BODY)
page("/store/", "Store", "The BattleTown store. Buy BattleBucks in game with /buy until the web store opens.", STORE_BODY)
page("/rules/", "Rules & Terms", "BattleTown Server Rules, Terms of Service and Privacy Policy.", RULES_BODY)
page("/404", "Page not found", "Page not found.", NOT_FOUND)
print("ok", sum(len(v) for v in docs.values()), "rule blocks")
