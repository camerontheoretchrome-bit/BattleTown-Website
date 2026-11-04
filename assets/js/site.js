// BattleTown website: shared effects and helpers for every page.
(function () {
  "use strict";

  var config = window.BT_CONFIG || {};
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  // ---------------------------------------------------------------- Copy buttons
  // <button class="copy-btn" data-copy="text">

  document.querySelectorAll("[data-copy]").forEach(function (button) {
    var label = button.textContent;

    button.addEventListener("click", function () {
      copyText(button.getAttribute("data-copy")).then(function () {
        button.textContent = "Copied!";
        button.classList.add("copied");
        burst(button);
        setTimeout(function () {
          button.textContent = label;
          button.classList.remove("copied");
        }, 1800);
      });
    });
  });

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }

    // Fallback for old browsers and plain http previews.
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "absolute";
    area.style.left = "-9999px";
    document.body.appendChild(area);
    area.select();
    document.execCommand("copy");
    document.body.removeChild(area);
    return Promise.resolve();
  }

  // A small shower of gold sparks from an element.
  function burst(element) {
    if (reduceMotion) {
      return;
    }

    var box = element.getBoundingClientRect();
    var cx = box.left + box.width / 2;
    var cy = box.top + box.height / 2;

    for (var i = 0; i < 18; i++) {
      var spark = document.createElement("span");
      var angle = Math.random() * Math.PI * 2;
      var distance = 40 + Math.random() * 70;
      spark.style.cssText = "position:fixed;z-index:50;pointer-events:none;width:6px;height:6px;border-radius:1px;" +
        "background:" + (i % 3 ? "#ffd45c" : "#e0313a") + ";left:" + cx + "px;top:" + cy + "px;";
      document.body.appendChild(spark);
      spark.animate([
        { transform: "translate(-50%,-50%) rotate(0deg)", opacity: 1 },
        { transform: "translate(" + (Math.cos(angle) * distance - 3) + "px," + (Math.sin(angle) * distance - 3) + "px) rotate(" + (Math.random() * 360) + "deg)", opacity: 0 }
      ], { duration: 700 + Math.random() * 300, easing: "cubic-bezier(.16,1,.3,1)" }).onfinish = (function (s) {
        return function () { s.remove(); };
      })(spark);
    }
  }

  window.BT_BURST = burst;

  // ---------------------------------------------------------------- Nav and header

  (function () {
    var here = location.pathname.replace(/index\.html$/, "");

    document.querySelectorAll(".nav a:not(.nav-play)").forEach(function (link) {
      var path = new URL(link.href).pathname;

      if (path === here || (path !== "/" && here.indexOf(path) === 0)) {
        link.setAttribute("aria-current", "page");
      }
    });
  })();

  // Phone menu.
  var menuBtn = document.querySelector(".menu-btn");
  var nav = document.querySelector(".nav");

  function setMenu(open) {
    menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    nav.classList.toggle("is-open", open);
    document.body.classList.toggle("menu-open", open);
  }

  if (menuBtn && nav) {
    menuBtn.addEventListener("click", function () {
      setMenu(menuBtn.getAttribute("aria-expanded") !== "true");
    });
    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) {
        setMenu(false);
      }
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        setMenu(false);
      }
    });
  }

  var header = document.querySelector(".site-header");
  var progress = document.querySelector(".progress");

  function onScroll() {
    var y = window.scrollY;
    var max = document.documentElement.scrollHeight - window.innerHeight;

    if (header) {
      header.classList.toggle("is-scrolled", y > 10);
    }

    if (progress) {
      progress.style.setProperty("--progress", max > 0 ? Math.min(1, y / max) : 0);
    }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // ---------------------------------------------------------------- Scroll reveal

  var revealables = document.querySelectorAll(".reveal");

  if ("IntersectionObserver" in window && !reduceMotion) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

    revealables.forEach(function (el) { observer.observe(el); });
  } else {
    revealables.forEach(function (el) { el.classList.add("is-in"); });
  }

  // ---------------------------------------------------------------- Pointer tilt

  window.BT_TILT = function (root) {
    if (!finePointer || reduceMotion) {
      return;
    }

    (root || document).querySelectorAll(".tilt").forEach(function (card) {
      if (card.dataset.tilt) {
        return;
      }
      card.dataset.tilt = "1";

      card.addEventListener("pointermove", function (event) {
        var box = card.getBoundingClientRect();
        var x = (event.clientX - box.left) / box.width;
        var y = (event.clientY - box.top) / box.height;
        card.style.setProperty("--ry", ((x - 0.5) * 10).toFixed(2) + "deg");
        card.style.setProperty("--rx", ((0.5 - y) * 10).toFixed(2) + "deg");
        card.style.setProperty("--mx", (x * 100).toFixed(1) + "%");
        card.style.setProperty("--my", (y * 100).toFixed(1) + "%");
      });

      card.addEventListener("pointerleave", function () {
        card.style.setProperty("--rx", "0deg");
        card.style.setProperty("--ry", "0deg");
      });
    });
  };

  window.BT_TILT();

  // ---------------------------------------------------------------- Embers
  // <canvas class="embers"> inside a positioned section.

  document.querySelectorAll("canvas.embers").forEach(function (canvas) {
    if (reduceMotion) {
      return;
    }

    var ctx = canvas.getContext("2d");
    var sparks = [];
    var width = 0;
    var height = 0;
    var ratio = Math.min(window.devicePixelRatio || 1, 2);
    var running = true;

    function resize() {
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = width * ratio;
      canvas.height = height * ratio;
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    }

    function spawn(anywhere) {
      return {
        x: Math.random() * width,
        y: anywhere ? Math.random() * height : height + 10,
        r: 0.6 + Math.random() * 2.2,
        vy: 0.25 + Math.random() * 0.9,
        vx: (Math.random() - 0.5) * 0.3,
        wobble: Math.random() * Math.PI * 2,
        life: 0.4 + Math.random() * 0.6,
        hue: Math.random() < 0.15 ? 355 : 38 + Math.random() * 12
      };
    }

    resize();
    var count = Math.round(Math.min(90, width / 14));
    for (var i = 0; i < count; i++) {
      sparks.push(spawn(true));
    }

    window.addEventListener("resize", resize);

    new IntersectionObserver(function (entries) {
      running = entries[0].isIntersecting;
      if (running) {
        requestAnimationFrame(tick);
      }
    }).observe(canvas);

    function tick() {
      if (!running || document.hidden) {
        return;
      }

      ctx.clearRect(0, 0, width, height);
      ctx.globalCompositeOperation = "lighter";

      sparks.forEach(function (s, index) {
        s.y -= s.vy;
        s.wobble += 0.03;
        s.x += s.vx + Math.sin(s.wobble) * 0.25;

        var fade = Math.max(0, Math.min(1, s.y / height)) * s.life;
        var glow = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 4);
        glow.addColorStop(0, "hsla(" + s.hue + ",100%,70%," + fade + ")");
        glow.addColorStop(1, "hsla(" + s.hue + ",100%,50%,0)");
        ctx.fillStyle = glow;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r * 4, 0, Math.PI * 2);
        ctx.fill();

        if (s.y < -10) {
          sparks[index] = spawn(false);
        }
      });

      requestAnimationFrame(tick);
    }

    document.addEventListener("visibilitychange", function () {
      if (!document.hidden && running) {
        requestAnimationFrame(tick);
      }
    });
  });

  // ---------------------------------------------------------------- Hero slideshow
  // <div class="hero-bg"><img>…</div>: crossfades the images.

  document.querySelectorAll(".hero-bg").forEach(function (box) {
    var images = box.querySelectorAll("img");
    var index = 0;

    if (!images.length) {
      return;
    }

    images[0].classList.add("is-on");

    if (reduceMotion || images.length < 2) {
      return;
    }

    setInterval(function () {
      images[index].classList.remove("is-on");
      index = (index + 1) % images.length;
      images[index].classList.add("is-on");
    }, 5000);
  });

  // ---------------------------------------------------------------- Server status
  // [data-server-status]: a pill filled from the public status of the server.

  var statusEl = document.querySelector("[data-server-status]");

  if (statusEl && config.serverAddress) {
    fetch("https://api.mcsrvstat.us/3/" + encodeURIComponent(config.serverAddress))
      .then(function (response) { return response.json(); })
      .then(function (data) {
        var dot = statusEl.querySelector(".dot");
        var text = statusEl.querySelector(".status-text");

        if (data && data.online) {
          dot.classList.add("is-online");
          var players = data.players && data.players.online;
          text.innerHTML = players > 0
            ? "<strong>" + players + "</strong> playing now"
            : "Server <strong>online</strong>";
        } else {
          dot.classList.add("is-offline");
          text.textContent = "Server offline";
        }
      })
      .catch(function () {
        statusEl.hidden = true;
      });
  }

  // ---------------------------------------------------------------- Countdown
  // [data-countdown="ISO date"]

  document.querySelectorAll("[data-countdown]").forEach(function (el) {
    var target = new Date(el.getAttribute("data-countdown")).getTime();
    var out = el.querySelector(".countdown");
    var label = el.querySelector(".countdown-label");

    function pad(n) { return (n < 10 ? "0" : "") + n; }

    function draw() {
      var left = Math.max(0, target - Date.now());

      if (!left) {
        label.textContent = "Public alpha is";
        out.innerHTML = "<span>LIVE</span>";
        return;
      }

      var s = Math.floor(left / 1000);
      var d = Math.floor(s / 86400);
      var h = Math.floor((s % 86400) / 3600);
      var m = Math.floor((s % 3600) / 60);
      out.innerHTML = "<span>" + d + "d</span><span>" + pad(h) + "h</span><span>" + pad(m) + "m</span><span>" + pad(s % 60) + "s</span>";
      setTimeout(draw, 1000);
    }

    draw();
  });

  // ---------------------------------------------------------------- Music
  // Opt-in only: nothing plays until the visitor taps the button. The track
  // and position carry over between pages within the same visit.

  var TRACKS = [
    { title: "Welcome to BattleTown", src: "/assets/audio/welcome-to-battletown.mp3" },
    { title: "Choose Your Fighter", src: "/assets/audio/choose-your-fighter.mp3" },
    { title: "Built for Battle", src: "/assets/audio/built-for-battle.mp3" },
    { title: "Winners' Walk", src: "/assets/audio/winners-walk.mp3" }
  ];

  var KEY = "bt-music";
  var music = document.createElement("button");
  music.type = "button";
  music.className = "music";
  music.setAttribute("aria-label", "Play BattleTown music");
  music.innerHTML = '<span class="music-icon"><span class="bars"><i></i><i></i><i></i><i></i></span></span>' +
    '<span class="music-label"><b>Play the soundtrack</b><small>BattleTown Hub music</small></span>';
  document.body.appendChild(music);

  // Phones start with just the icon; bigger screens show the label first.
  if (window.innerWidth <= 820) {
    music.classList.add("is-compact");
  } else {
    setTimeout(function () { music.classList.add("is-compact"); }, 6000);
  }

  var audio = new Audio();
  audio.preload = "none";
  audio.volume = 0.45;

  var saved = readSaved();
  var current = saved.track || 0;

  function readSaved() {
    try {
      return JSON.parse(sessionStorage.getItem(KEY) || "{}");
    } catch (ignored) {
      return {};
    }
  }

  function writeSaved(on) {
    try {
      sessionStorage.setItem(KEY, JSON.stringify({ on: on, track: current, time: audio.currentTime || 0 }));
    } catch (ignored) {
      // Storage blocked: music just won't carry over between pages.
    }
  }

  function label(title, sub) {
    music.querySelector("b").textContent = title;
    music.querySelector("small").textContent = sub;
  }

  function play(time) {
    var track = TRACKS[current];

    if (audio.getAttribute("data-src") !== track.src) {
      audio.src = track.src;
      audio.setAttribute("data-src", track.src);
    }

    if (time) {
      audio.currentTime = time;
    }

    return audio.play().then(function () {
      music.classList.add("is-playing");
      music.setAttribute("aria-label", "Pause BattleTown music");
      label(track.title, "Now playing · tap to pause");
      writeSaved(true);
    });
  }

  function pause() {
    audio.pause();
    music.classList.remove("is-playing");
    music.setAttribute("aria-label", "Play BattleTown music");
    label("Play the soundtrack", TRACKS[current].title);
    writeSaved(false);
  }

  music.addEventListener("click", function () {
    if (audio.paused) {
      play().catch(function () {
        label("Couldn't play music", "Tap to try again");
      });
    } else {
      pause();
    }
  });

  audio.addEventListener("ended", function () {
    current = (current + 1) % TRACKS.length;
    play();
  });

  window.addEventListener("pagehide", function () {
    if (!audio.paused) {
      writeSaved(true);
    }
  });

  // Music was on when the visitor left the last page: try to carry on.
  // Browsers may block this until the next tap, so fall back to a prompt.
  if (saved.on) {
    play(saved.time).catch(function () {
      label("Tap to resume music", TRACKS[current].title);
    });
  }
})();
