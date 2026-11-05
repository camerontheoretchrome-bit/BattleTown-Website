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
// The feed refreshes about once a minute (the Hub boards' own rebuild), and
// the home and Leaderboards live bits (status, online now, totals, podium,
// recent matches) re-read it every minute while the tab is visible. The
// Leaderboards tables and profiles load once per visit.
// If it can't be reached the page says so instead of breaking.
(function () {
  "use strict";

  var config = window.BT_CONFIG || {};
  var base = (config.statsFeedUrl || "").replace(/\/+$/, "");
  var CLASSES = window.BT_CLASSES || {};
  var MAPS = window.BT_MAPS || {};

  var MODES = { duel: "Duel", ffa: "Free For All", tdm: "Team Deathmatch", elimination: "Last Alive" };
  var HALLS = [
    { id: "champion", name: "Champions", blurb: "Who is best at fighting. Public match wins, win rate, K/D." },
    { id: "record", name: "Records", blurb: "The biggest raw numbers on the server." },
    { id: "builder", name: "Builders", blurb: "The players whose Maps everyone plays." }
  ];

  function fetchJson(path) {
    return fetch(base + path, { headers: { Accept: "application/json" } }).then(function (response) {
      if (!response.ok) {
        var error = new Error("HTTP " + response.status);
        error.status = response.status;
        throw error;
      }
      return response.json();
    });
  }

  // A dropped connection gets one retry, so a blip or a server restart
  // doesn't blank the page. Real answers (404 no such player) don't retry.
  function get(path) {
    if (!base) {
      return Promise.reject(new Error("no feed"));
    }
    return fetchJson(path).catch(function (error) {
      if (error.status) {
        throw error;
      }
      return new Promise(function (resolve) { setTimeout(resolve, 2500); }).then(function () {
        return fetchJson(path);
      });
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

  // Titles from servers before the fix read "ELIMINATION Champion": show the game's words.
  var MODE_TITLES = { DUEL: "Duel", FFA: "Free For All", TDM: "Team Deathmatch", ELIMINATION: "Last Alive" };

  function titleText(t) {
    var m = /^(DUEL|FFA|TDM|ELIMINATION) Champion$/.exec(t || "");
    return m ? MODE_TITLES[m[1]] + " Champion" : t;
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

  // The live bits redraw from one summary.json read a minute (BT_every in
  // site.js, paused while the tab is hidden). Each part gets the feed's answer,
  // or null when the feed didn't answer, which usually means the server is off.
  var summaryParts = [];

  function onSummary(draw) {
    summaryParts.push(draw);
  }

  function startSummary() {
    if (!summaryParts.length) {
      return;
    }
    window.BT_every(60000, function () {
      get("/v1/summary.json").then(function (doc) {
        window.BT_feedStatus(doc.online || 0);
        summaryParts.forEach(function (draw) { draw(doc); });
      }, function () {
        window.BT_feedStatus(null);
        summaryParts.forEach(function (draw) { draw(null); });
      });
    });
  }

  function mapName(id) {
    if (!id) {
      return "a Map";
    }
    return MAPS[id] || id.replace(/[_-]+/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  function ago(ms) {
    var minutes = Math.max(0, Math.round((Date.now() - ms) / 60000));
    if (minutes < 1) {
      return "just now";
    }
    if (minutes < 60) {
      return minutes + " min ago";
    }
    var hrs = Math.round(minutes / 60);
    if (hrs < 48) {
      return hrs + (hrs === 1 ? " hour ago" : " hours ago");
    }
    return Math.round(hrs / 24) + " days ago";
  }

  function clock(seconds) {
    var m = Math.floor((seconds || 0) / 60);
    var sec = (seconds || 0) % 60;
    return m + ":" + (sec < 10 ? "0" : "") + sec;
  }

  function nameLink(name, linked, className) {
    var node = el(linked ? "a" : "span", className || "", name);
    if (linked) {
      node.href = profileLink(name);
    }
    return node;
  }

  function head(name) {
    var img = el("img", "mini-head");
    img.src = "https://mc-heads.net/avatar/" + encodeURIComponent(name) + "/32";
    img.alt = "";
    img.width = 24;
    img.height = 24;
    img.loading = "lazy";
    return img;
  }

  // ---------------------------------------------------------------- Online now

  document.querySelectorAll("[data-online-now]").forEach(function (box) {
    onSummary(function (doc) {
      var people = (doc && doc.onlinePlayers) || [];
      var list = box.querySelector("ul");
      list.innerHTML = "";
      box.hidden = !people.length;
      people.forEach(function (p) {
        var li = el("li");
        var link = nameLink(p.name, p.profile, "online-name");
        link.prepend(head(p.name));
        li.appendChild(link);
        list.appendChild(li);
      });
      box.querySelector("[data-online-count]").textContent = people.length === 1 ? "1 player" : people.length + " players";
    });
  });

  // ---------------------------------------------------------------- Recent matches

  // With the feed down the last list stays up: those matches still happened.
  document.querySelectorAll("[data-recent-matches]").forEach(function (box) {
    onSummary(function (doc) {
      if (!doc) {
        return;
      }
      var matches = (doc.recentMatches || []).slice(0, Number(box.getAttribute("data-recent-matches")) || 6);
      var list = box.querySelector("ol");
      list.innerHTML = "";
      box.hidden = !matches.length;
      matches.forEach(function (m) {
        var li = el("li", "match-row");
        var what = el("p", "match-what");
        if (m.winners && m.winners.length) {
          m.winners.forEach(function (w, i) {
            if (i) {
              what.appendChild(document.createTextNode(i === m.winners.length - 1 ? " & " : ", "));
            }
            what.appendChild(nameLink(w, true, "match-winner"));
          });
          what.appendChild(document.createTextNode(" won "));
        } else {
          what.appendChild(document.createTextNode("A match of "));
        }
        what.appendChild(el("strong", "", m.mode));
        what.appendChild(document.createTextNode(" on "));
        what.appendChild(el("strong", "", mapName(m.map)));
        li.appendChild(what);

        var meta = el("p", "match-meta");
        var bits = [clock(m.durationSeconds), m.players + " fighters", ago(m.endedAt)];
        meta.textContent = bits.join(" · ");
        if (m.topPlayer) {
          meta.appendChild(document.createTextNode(" · Top: "));
          meta.appendChild(nameLink(m.topPlayer.name, m.topPlayer.profile));
          meta.appendChild(document.createTextNode(" (" + m.topPlayer.kills + " " + (m.topPlayer.kills === 1 ? "kill" : "kills") + ")"));
        }
        li.appendChild(meta);
        list.appendChild(li);
      });
    });
  });

  // ---------------------------------------------------------------- Discord
  // Discord's public invite info (CORS allows battletown.store).

  var discordButtons = document.querySelectorAll("a.btn-discord");
  var discordLive = document.querySelectorAll("[data-discord-live]");
  var invite = (config.discordUrl || "").split("/").pop();

  if ((discordButtons.length || discordLive.length) && invite) {
    window.BT_every(300000, function () {
      fetch("https://discord.com/api/v10/invites/" + encodeURIComponent(invite) + "?with_counts=true")
        .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
        .then(function (data) {
          var members = data.approximate_member_count;
          if (!members) {
            return;
          }
          discordButtons.forEach(function (button) {
            var badge = button.querySelector(".discord-count") || button.appendChild(el("span", "discord-count"));
            badge.textContent = number(members) + (members === 1 ? " member" : " members");
          });
          var online = data.approximate_presence_count;
          discordLive.forEach(function (live) {
            live.textContent = number(members) + (members === 1 ? " member" : " members") + (online ? " · " + number(online) + " online" : "");
            live.hidden = false;
          });
        }).catch(function () {});
    });
  }

  // ---------------------------------------------------------------- Home summary

  // With the feed down the last totals stay up: they are still true.
  document.querySelectorAll("[data-live-summary]").forEach(function (box) {
    onSummary(function (summary) {
      if (!summary) {
        return;
      }
      box.innerHTML = "";
      [
        [summary.players, "player", "players"],
        [summary.kills, "kill", "kills"],
        [summary.communityMaps, "Community Map", "Community Maps"]
      ].forEach(function (item) {
        if (!item[0]) {
          return; // Before launch a zero reads as empty; leave it out.
        }
        var pill = el("span", "pill");
        pill.appendChild(el("strong", "", number(item[0])));
        pill.appendChild(document.createTextNode(" " + (item[0] === 1 ? item[1] : item[2])));
        box.appendChild(pill);
      });
      box.hidden = !box.children.length;
    });
  });

  startSummary();

  // ---------------------------------------------------------------- Podium
  // The Grand Champion board's top three, as a podium (2nd, 1st, 3rd).

  var OVERALL = "champions.overall";

  function podium(board) {
    var rows = (board.rows || []).slice(0, 3);
    var wrap = el("div", "podium");
    [1, 0, 2].forEach(function (i) {
      var row = rows[i];
      if (!row) {
        return;
      }
      var step = el(row.profile ? "a" : "div", "podium-step place-" + row.rank);
      if (row.profile) {
        step.href = profileLink(row.name);
      }
      var skin = el("img", "podium-skin");
      skin.src = "https://mc-heads.net/body/" + encodeURIComponent(row.name) + "/160";
      skin.alt = "";
      skin.loading = "lazy";
      skin.onerror = function () { skin.remove(); };
      step.appendChild(skin);
      step.appendChild(el("span", "podium-rank", "#" + row.rank));
      step.appendChild(el("strong", "podium-name", row.name));
      step.appendChild(el("span", "podium-value", (row.value || "") + (row.unit ? " " + row.unit : "")));
      wrap.appendChild(step);
    });
    return wrap;
  }

  document.querySelectorAll("[data-home-podium]").forEach(function (section) {
    window.BT_every(60000, function () {
      get("/v1/leaderboards.json").then(function (doc) {
        var board = (doc.boards || []).filter(function (b) { return b.id === OVERALL; })[0];
        if (!board || !(board.rows || []).length) {
          return; // Nothing to show before the first public wins.
        }
        var holder = section.querySelector("[data-podium]");
        holder.innerHTML = "";
        holder.appendChild(podium(board));
        section.hidden = false;
      }).catch(function () {});
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

        var boards = (doc.boards || []).filter(function (b) { return b.hall === hall.id; });

        // A subheading every board in the hall shares says nothing; drop it.
        var subs = {};
        boards.forEach(function (b) { subs[b.subheading] = (subs[b.subheading] || 0) + 1; });

        var featured = boards.filter(function (b) { return b.id === OVERALL && (b.rows || []).length; })[0];
        if (featured) {
          var top = el("div", "card board-featured");
          top.appendChild(el("h3", "", title(featured.heading)));
          top.appendChild(podium(featured));
          panel.appendChild(top);
        }

        var grid = el("div", "grid boards");
        var empty = [];

        boards.forEach(function (board) {
          if (board === featured) {
            return;
          }
          if (!(board.rows || []).length) {
            empty.push(board);
            return;
          }
          grid.appendChild(boardCard(board, subs[board.subheading] > 1));
        });

        panel.appendChild(grid);

        if (empty.length) {
          var open = el("div", "boards-open");
          open.appendChild(el("h3", "", "Be the first"));
          open.appendChild(el("p", "", "No one is on these boards yet. Play public matches to claim a spot."));
          var chips = el("ul", "chips");
          empty.forEach(function (b) { chips.appendChild(el("li", "", title(b.heading))); });
          open.appendChild(chips);
          panel.appendChild(open);
        }

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

  function boardCard(board, hideSubheading) {
    var card = el("article", "card board tilt");
    card.appendChild(el("h3", "", title(board.heading)));
    if (board.subheading && !hideSubheading) {
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
    // Skin render by mc-heads.net (third party, see Privacy).
    skin.src = "https://mc-heads.net/body/" + encodeURIComponent(p.uuid.replace(/-/g, "")) + "/300";
    skin.alt = p.name + "'s Minecraft skin";
    skin.loading = "lazy";
    skin.onerror = function () { skin.remove(); };
    head.appendChild(skin);

    var who = el("div", "profile-who");
    who.appendChild(el("span", "eyebrow", "Player"));
    who.appendChild(el("h1", "", p.name));
    var level = el("p", "profile-level");
    level.appendChild(el("span", "level-badge", String(p.level)));
    level.appendChild(document.createTextNode(" Rank level " + p.level + " of 100" + (p.rank && p.rank.tier ? " · " + p.rank.tier : "")));
    who.appendChild(level);

    if (p.rank) {
      var bar = el("div", "rank-bar");
      bar.setAttribute("role", "progressbar");
      bar.setAttribute("aria-valuemin", "0");
      bar.setAttribute("aria-valuemax", "100");
      bar.setAttribute("aria-valuenow", String(p.rank.percent));
      var fill = el("span", "rank-fill");
      fill.style.width = (p.rank.maxed ? 100 : p.rank.percent) + "%";
      bar.appendChild(fill);
      who.appendChild(bar);
      who.appendChild(el("p", "rank-next", p.rank.maxed
        ? "Max level reached."
        : number(p.rank.xpToNext) + " XP to level " + (p.level + 1)));
    }

    if (p.titles && p.titles.length) {
      var titles = el("ul", "chips profile-titles");
      p.titles.forEach(function (t) { titles.appendChild(el("li", "", titleText(t))); });
      who.appendChild(titles);
    }
    var share = el("button", "btn btn-small share-btn", "Copy profile link");
    share.type = "button";
    share.setAttribute("data-copy", location.origin + profileLink(p.name));
    share.addEventListener("click", function () {
      var link = share.getAttribute("data-copy");
      (navigator.clipboard ? navigator.clipboard.writeText(link) : Promise.reject()).then(function () {
        share.textContent = "Link copied!";
        if (window.BT_BURST) {
          window.BT_BURST(share);
        }
        setTimeout(function () { share.textContent = "Copy profile link"; }, 1800);
      }).catch(function () {
        window.prompt("Copy this link:", link);
      });
    });
    who.appendChild(share);

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
