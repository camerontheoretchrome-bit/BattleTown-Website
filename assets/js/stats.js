// BattleTown website: live stats (phase 3).
//
// Reads the plugin's read-only JSON feed at BT_CONFIG.statsFeedUrl
// (https://api.battletown.store, served by the BattleTown plugin through
// Bloom's HTTPS proxy) and draws:
//
//   [data-live-summary]   home page: players online, players, kills
//   #leaderboards         /leaderboards/: every Hub board, by hall
//   #profile              /player/?name=NAME: one player's profile
//
// The feed refreshes about once a minute (the Hub boards' own rebuild).
// If it can't be reached the page says so instead of breaking.
(function () {
  "use strict";

  var config = window.BT_CONFIG || {};
  var base = (config.statsFeedUrl || "").replace(/\/+$/, "");
  var CLASSES = window.BT_CLASSES || {};

  var MODES = { duel: "Duel", ffa: "Free For All", tdm: "Team Deathmatch", elimination: "Last Alive" };
  var HALLS = [
    { id: "champion", name: "Champions", blurb: "Who is best at fighting. Public match wins, win rate, K/D." },
    { id: "record", name: "Records", blurb: "The biggest raw numbers on the server." },
    { id: "builder", name: "Builders", blurb: "The players whose Maps everyone plays." }
  ];

  function get(path) {
    if (!base) {
      return Promise.reject(new Error("no feed"));
    }
    return fetch(base + path, { headers: { Accept: "application/json" } }).then(function (response) {
      if (!response.ok) {
        var error = new Error("HTTP " + response.status);
        error.status = response.status;
        throw error;
      }
      return response.json();
    });
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) {
      node.className = className;
    }
    if (text !== undefined && text !== null) {
      node.textContent = text;
    }
    return node;
  }

  function number(n) {
    return (n || 0).toLocaleString("en-US");
  }

  function hours(seconds) {
    var h = Math.floor((seconds || 0) / 3600);
    if (h >= 24) {
      return Math.floor(h / 24) + "d " + (h % 24) + "h";
    }
    return h + "h " + Math.floor(((seconds || 0) % 3600) / 60) + "m";
  }

  function ratio(a, b) {
    return b > 0 ? (a / b).toFixed(2) : (a > 0 ? a.toFixed(2) : "0.00");
  }

  function percent(a, b) {
    return b > 0 ? Math.round((a / b) * 100) + "%" : "–";
  }

  function profileLink(name) {
    return "/player/" + encodeURIComponent(name);
  }

  function title(text) {
    // Board headings come in capitals from the game; show them as written.
    return text || "";
  }

  function updated(ms) {
    if (!ms) {
      return "";
    }
    var seconds = Math.max(0, Math.round((Date.now() - ms) / 1000));
    return seconds < 90 ? "Updated just now" : "Updated " + Math.round(seconds / 60) + " min ago";
  }

  function offline(target, message) {
    target.innerHTML = "";
    var box = el("div", "callout");
    box.appendChild(el("p", "", message || "Live stats are offline right now. Please check back soon."));
    target.appendChild(box);
  }

  // ---------------------------------------------------------------- Home summary

  document.querySelectorAll("[data-live-summary]").forEach(function (box) {
    get("/v1/summary.json").then(function (summary) {
      box.innerHTML = "";
      [
        [number(summary.players), "players"],
        [number(summary.kills), "kills"],
        [number(summary.communityMaps), "Community Maps"]
      ].forEach(function (item) {
        var pill = el("span", "pill");
        pill.appendChild(el("strong", "", item[0]));
        pill.appendChild(document.createTextNode(" " + item[1]));
        box.appendChild(pill);
      });
      box.hidden = false;

      var status = document.querySelector("[data-server-status] .status-text");
      if (status && summary.online > 0) {
        status.innerHTML = "<strong>" + number(summary.online) + "</strong> playing now";
      }
    }).catch(function () {
      box.hidden = true;
    });
  });

  // ---------------------------------------------------------------- Player search

  document.querySelectorAll("[data-player-search]").forEach(function (form) {
    var input = form.querySelector("input");
    var list = document.createElement("datalist");
    list.id = "bt-player-names";
    input.setAttribute("list", list.id);
    form.appendChild(list);

    get("/v1/players.json").then(function (doc) {
      (doc.players || []).forEach(function (p) {
        var option = document.createElement("option");
        option.value = p.name;
        list.appendChild(option);
      });
    }).catch(function () {});

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var name = input.value.trim();
      if (/^[A-Za-z0-9_]{1,16}$/.test(name)) {
        location.href = profileLink(name);
      } else {
        input.focus();
      }
    });
  });

  // ---------------------------------------------------------------- Leaderboards

  var boardsRoot = document.getElementById("leaderboards");

  if (boardsRoot) {
    get("/v1/leaderboards.json").then(function (doc) {
      boardsRoot.innerHTML = "";
      var tabs = el("div", "hall-tabs");
      tabs.setAttribute("role", "tablist");
      var panels = [];

      HALLS.forEach(function (hall, i) {
        var tab = el("button", "btn btn-small" + (i === 0 ? " is-active" : ""), hall.name);
        tab.type = "button";
        tab.setAttribute("role", "tab");
        tab.setAttribute("aria-selected", i === 0 ? "true" : "false");
        tabs.appendChild(tab);

        var panel = el("section", "hall-panel");
        panel.hidden = i !== 0;
        panel.appendChild(el("p", "lead", hall.blurb));
        var grid = el("div", "grid boards");

        (doc.boards || []).filter(function (b) { return b.hall === hall.id; }).forEach(function (board) {
          grid.appendChild(boardCard(board));
        });

        panel.appendChild(grid);
        panels.push(panel);

        tab.addEventListener("click", function () {
          tabs.querySelectorAll("button").forEach(function (t, j) {
            t.classList.toggle("is-active", j === i);
            t.setAttribute("aria-selected", j === i ? "true" : "false");
          });
          panels.forEach(function (p, j) { p.hidden = j !== i; });
        });
      });

      boardsRoot.appendChild(tabs);
      panels.forEach(function (p) { boardsRoot.appendChild(p); });
      boardsRoot.appendChild(el("p", "stats-updated", updated(doc.builtAt || doc.generatedAt)));

      if (window.BT_TILT) {
        window.BT_TILT(boardsRoot);
      }
    }).catch(function () {
      offline(boardsRoot);
    });
  }

  function boardCard(board) {
    var card = el("article", "card board tilt");
    card.appendChild(el("h3", "", title(board.heading)));
    if (board.subheading) {
      card.appendChild(el("p", "board-sub", board.subheading));
    }

    var rows = board.rows || [];
    if (!rows.length) {
      card.appendChild(el("p", "board-empty", "No one yet. Play public matches to get on the board."));
      return card;
    }

    var list = el("ol", "board-rows");
    rows.slice(0, 10).forEach(function (row) {
      var li = el("li", row.rank <= 3 ? "top-" + row.rank : "");
      li.appendChild(el("span", "board-rank", String(row.rank)));

      var who = row.profile ? el("a", "board-name", row.name) : el("span", "board-name", row.name);
      if (row.profile) {
        who.href = profileLink(row.name);
      }
      li.appendChild(who);
      li.appendChild(el("span", "board-value", (row.value || "") + (row.unit ? " " + row.unit : "")));
      list.appendChild(li);
    });

    card.appendChild(list);
    return card;
  }

  // ---------------------------------------------------------------- Profile

  var profileRoot = document.getElementById("profile");

  if (profileRoot) {
    var name = new URLSearchParams(location.search).get("name") || "";

    if (!/^[A-Za-z0-9_]{1,16}$/.test(name)) {
      offline(profileRoot, "Search for a player by their Minecraft name.");
    } else {
      document.title = name + " · BattleTown";
      get("/v1/players/" + encodeURIComponent(name) + ".json").then(drawProfile).catch(function (error) {
        offline(profileRoot, error.status === 404
          ? "No BattleTown player called \"" + name + "\" yet. Check the spelling, or join and play a match!"
          : null);
      });
    }
  }

  function tile(value, label) {
    var t = el("div", "stat-tile");
    t.appendChild(el("strong", "", value));
    t.appendChild(el("span", "", label));
    return t;
  }

  function drawProfile(p) {
    profileRoot.innerHTML = "";
    document.title = p.name + " · BattleTown";

    var head = el("div", "profile-head reveal is-in");
    var skin = el("img", "profile-skin");
    // 3D skin render by Crafatar (third party, see Privacy).
    skin.src = "https://crafatar.com/renders/body/" + encodeURIComponent(p.uuid) + "?overlay&scale=8";
    skin.alt = p.name + "'s Minecraft skin";
    skin.loading = "lazy";
    skin.onerror = function () { skin.remove(); };
    head.appendChild(skin);

    var who = el("div", "profile-who");
    who.appendChild(el("span", "eyebrow", "Player"));
    who.appendChild(el("h1", "", p.name));
    var level = el("p", "profile-level");
    level.appendChild(el("span", "level-badge", String(p.level)));
    level.appendChild(document.createTextNode(" Rank level " + p.level + " of 100"));
    who.appendChild(level);

    if (p.titles && p.titles.length) {
      var titles = el("ul", "chips profile-titles");
      p.titles.forEach(function (t) { titles.appendChild(el("li", "", t)); });
      who.appendChild(titles);
    }
    head.appendChild(who);
    profileRoot.appendChild(head);

    var tiles = el("div", "stat-tiles");
    tiles.appendChild(tile(number(p.wins), "Wins"));
    tiles.appendChild(tile(number(p.kills), "Kills"));
    tiles.appendChild(tile(ratio(p.kills, p.deaths), "K/D"));
    tiles.appendChild(tile(percent(p.wins, p.matches), "Win rate"));
    tiles.appendChild(tile(number(p.matches), "Matches"));
    tiles.appendChild(tile(number(p.assists), "Assists"));
    tiles.appendChild(tile(number(p.deaths), "Deaths"));
    tiles.appendChild(tile(hours(p.playtimeSeconds), "Played"));
    profileRoot.appendChild(tiles);

    var cols = el("div", "profile-cols");

    // Modes
    var modes = el("section", "card");
    modes.appendChild(el("h3", "", "Game modes"));
    var table = el("table", "mode-table");
    table.innerHTML = "<thead><tr><th>Mode</th><th>Matches</th><th>Wins</th><th>Kills</th></tr></thead>";
    var body = el("tbody");
    Object.keys(MODES).forEach(function (id) {
      var m = (p.modes || {})[id] || { matches: 0, wins: 0, kills: 0 };
      var tr = el("tr");
      [MODES[id], number(m.matches), number(m.wins), number(m.kills)].forEach(function (v) { tr.appendChild(el("td", "", v)); });
      body.appendChild(tr);
    });
    table.appendChild(body);
    modes.appendChild(table);
    cols.appendChild(modes);

    // Classes
    var classes = el("section", "card");
    classes.appendChild(el("h3", "", "Best classes"));
    if (p.classes && p.classes.length) {
      var list = el("ul", "class-list");
      p.classes.forEach(function (c) {
        var info = CLASSES[c.id] || { name: c.id, colour: "#f5b82e" };
        var li = el("li");
        li.style.setProperty("--accent", info.colour);
        var img = el("img");
        img.src = "/assets/img/classes/" + c.id + "-thumb.webp";
        img.alt = "";
        img.loading = "lazy";
        li.appendChild(img);
        var text = el("div");
        var link = el("a", "class-name", info.name);
        link.href = "/classes/#" + c.id;
        text.appendChild(link);
        text.appendChild(el("span", "", number(c.matches) + " matches · " + number(c.wins) + " wins · " + number(c.kills) + " kills"));
        li.appendChild(text);
        list.appendChild(li);
      });
      classes.appendChild(list);
    } else {
      classes.appendChild(el("p", "", "No public matches yet."));
    }
    cols.appendChild(classes);
    profileRoot.appendChild(cols);

    // Board placings
    if (p.placings && p.placings.length) {
      var boards = el("section", "card");
      boards.appendChild(el("h3", "", "On the leaderboards"));
      var chips = el("ul", "chips placings");
      p.placings.forEach(function (pl) {
        var li = el("li", pl.rank <= 3 ? "top-" + pl.rank : "");
        li.appendChild(el("strong", "", "#" + pl.rank));
        li.appendChild(document.createTextNode(" " + pl.heading));
        chips.appendChild(li);
      });
      boards.appendChild(chips);
      profileRoot.appendChild(boards);
    }

    // Maps
    if (p.maps) {
      var maps = el("section", "card");
      maps.appendChild(el("h3", "", "Community Maps"));
      var text = number(p.maps.published) + " published · " + number(p.maps.plays) + " public plays";
      if (p.maps.topMap) {
        text += " · Most played: " + p.maps.topMap + " (" + number(p.maps.topMapPlays) + ")";
      }
      maps.appendChild(el("p", "", text));
      profileRoot.appendChild(maps);
    }

    profileRoot.appendChild(el("p", "stats-updated", updated(p.generatedAt)));
  }
})();
