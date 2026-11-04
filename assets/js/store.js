// BattleTown web store (phase 2): Tebex Headless.
//
// Lists the Tebex packages, keeps a basket, and hands checkout to Tebex
// (pay.tebex.io). Tebex is the merchant of record: card details never
// touch this site. Only the PUBLIC webstore token is used here.
//
// Flow: the player types their Minecraft name -> we create a Tebex basket
// for that name -> packages are added one at a time -> CHECKOUT opens the
// basket's Tebex checkout link. Tebex then runs the same package commands
// as an in-game purchase, so delivery is unchanged.
(function () {
  "use strict";

  var config = window.BT_CONFIG || {};
  var token = config.tebexWebstoreToken;
  var app = document.getElementById("store-app");
  var soon = document.getElementById("store-coming-soon");

  if (!token || !app) {
    return;
  }

  var API = "https://headless.tebex.io/api";
  var ACCOUNT = API + "/accounts/" + encodeURIComponent(token);
  var SAVED = "bt-store-basket";
  var NAME_RULE = /^[A-Za-z0-9_]{3,16}$/;

  // Display names for Tebex categories, where the game words differ.
  var CATEGORY_NAMES = { "Battle Bucks": "BattleBucks" };

  // Banner art for each Tebex category (from ~/Documents/BattleTown Art).
  // "titled" art already has the category name painted in, so the heading
  // is kept for screen readers only.
  var CATEGORY_ART = {
    "Battle Bundles": { src: "/assets/img/art/cat-deals.webp", titled: true },
    "Battle Bucks": { src: "/assets/img/art/header.webp", titled: false },
    "XP Boosts": { src: "/assets/img/art/cat-xp.webp", titled: true },
    "Collections": { src: "/assets/img/art/cat-collections.webp", titled: true }
  };

  var state = {
    categories: [],
    username: "",
    basket: null,
    busy: false
  };

  app.hidden = false;
  if (soon) {
    soon.hidden = true;
  }

  var els = {
    nameForm: app.querySelector("#store-name-form"),
    nameInput: app.querySelector("#store-name"),
    nameStatus: app.querySelector("#store-name-status"),
    catNav: app.querySelector("#store-cats"),
    shelves: app.querySelector("#store-shelves"),
    basketList: app.querySelector("#basket-items"),
    basketTotal: app.querySelector("#basket-total"),
    basketNote: app.querySelector("#basket-note"),
    checkout: app.querySelector("#basket-checkout"),
    message: app.querySelector("#store-message"),
    basket: app.querySelector("#basket"),
    basketBar: app.querySelector("#basket-bar")
  };

  // ---------------------------------------------------------------- API

  function request(method, url, body) {
    var options = { method: method, headers: { "Accept": "application/json" } };

    if (body) {
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(body);
    }

    return fetch(url, options).then(function (response) {
      return response.json().catch(function () { return {}; }).then(function (json) {
        if (!response.ok) {
          var error = new Error(json.title || json.detail || ("HTTP " + response.status));
          error.status = response.status;
          throw error;
        }
        return json;
      });
    });
  }

  function loadCategories() {
    return request("GET", ACCOUNT + "/categories?includePackages=1").then(function (json) {
      state.categories = (json.data || [])
        .filter(function (category) { return (category.packages || []).length > 0; })
        .sort(byOrder);
      state.categories.forEach(function (category) {
        category.packages.sort(byOrder);
      });
    });
  }

  function createBasket(username) {
    var here = location.origin;

    return request("POST", ACCOUNT + "/baskets", {
      username: username,
      complete_url: here + "/store/thanks/",
      cancel_url: here + "/store/",
      complete_auto_redirect: true
    }).then(function (json) {
      return json.data;
    });
  }

  function fetchBasket(ident) {
    return request("GET", ACCOUNT + "/baskets/" + encodeURIComponent(ident)).then(function (json) {
      return json.data;
    });
  }

  function addPackage(ident, packageId) {
    return request("POST", API + "/baskets/" + encodeURIComponent(ident) + "/packages", {
      package_id: String(packageId),
      quantity: 1
    }).then(function (json) {
      return json.data;
    });
  }

  function removePackage(ident, packageId) {
    return request("POST", API + "/baskets/" + encodeURIComponent(ident) + "/packages/remove", {
      package_id: String(packageId)
    }).then(function (json) {
      return json.data;
    });
  }

  // ---------------------------------------------------------------- Saved basket

  function save() {
    try {
      if (state.basket) {
        localStorage.setItem(SAVED, JSON.stringify({ ident: state.basket.ident, username: state.username }));
      } else if (state.username) {
        localStorage.setItem(SAVED, JSON.stringify({ username: state.username }));
      } else {
        localStorage.removeItem(SAVED);
      }
    } catch (ignored) {
      // Private mode or blocked storage: the basket just won't survive a reload.
    }
  }

  function restore() {
    var saved = null;

    try {
      saved = JSON.parse(localStorage.getItem(SAVED) || "null");
    } catch (ignored) {
      saved = null;
    }

    if (!saved || !saved.username) {
      return Promise.resolve();
    }

    state.username = saved.username;
    els.nameInput.value = saved.username;

    if (!saved.ident) {
      return Promise.resolve();
    }

    return fetchBasket(saved.ident).then(function (basket) {
      if (basket && !basket.complete) {
        state.basket = basket;
      }
    }).catch(function () {
      // Expired or unknown basket: start fresh on the next add.
      state.basket = null;
    });
  }

  // ---------------------------------------------------------------- Actions

  function setName(event) {
    event.preventDefault();
    var name = els.nameInput.value.trim();

    if (!NAME_RULE.test(name)) {
      nameStatus("That doesn't look like a Minecraft name: 3 to 16 letters, numbers or _.", true);
      return;
    }

    if (name === state.username && state.basket) {
      nameStatus("Buying for " + name + ".", false);
      return;
    }

    busy(true);
    createBasket(name).then(function (basket) {
      state.username = basket.username || name;
      state.basket = basket;
      els.nameInput.value = state.username;
      nameStatus("Buying for " + state.username + ".", false);
      save();
      render();
    }).catch(function (error) {
      if (error.status === 404) {
        nameStatus("We couldn't find the Minecraft account \"" + name + "\". Check the spelling.", true);
      } else {
        nameStatus("Something went wrong. Please try again.", true);
      }
    }).then(function () {
      busy(false);
    });
  }

  function add(packageId, from) {
    if (!state.username) {
      nameStatus("Type your Minecraft name first, so we know who to deliver to.", true);
      els.nameInput.focus();
      return;
    }

    busy(true);
    var ready = state.basket ? Promise.resolve(state.basket) : createBasket(state.username);

    ready.then(function (basket) {
      state.basket = basket;
      return addPackage(basket.ident, packageId);
    }).catch(function (error) {
      // The basket may have expired. Make a new one for the same name and retry once.
      if (error.status === 422 || error.status === 404) {
        return createBasket(state.username).then(function (basket) {
          state.basket = basket;
          return addPackage(basket.ident, packageId);
        });
      }
      throw error;
    }).then(function (basket) {
      state.basket = basket;
      save();
      message("");
      render();
      celebrate(from);
    }).catch(function (error) {
      message("Couldn't add that: " + error.message, true);
    }).then(function () {
      busy(false);
    });
  }

  function remove(packageId) {
    busy(true);
    removePackage(state.basket.ident, packageId).then(function (basket) {
      state.basket = basket;
      save();
      render();
    }).catch(function (error) {
      message("Couldn't remove that: " + error.message, true);
    }).then(function () {
      busy(false);
    });
  }

  function checkout() {
    var link = state.basket && state.basket.links && state.basket.links.checkout;

    if (!link) {
      message("Your basket is empty.", true);
      return;
    }

    location.href = link;
  }

  // ---------------------------------------------------------------- Rendering

  function render() {
    renderShelves();
    renderBasket();
  }

  function renderShelves() {
    var inBasket = basketIds();

    els.catNav.innerHTML = "";
    els.shelves.innerHTML = "";

    state.categories.forEach(function (category) {
      var name = CATEGORY_NAMES[category.name] || category.name;
      var anchor = "cat-" + category.id;

      var link = document.createElement("a");
      link.href = "#" + anchor;
      link.className = "btn btn-small";
      link.textContent = name;
      els.catNav.appendChild(link);

      var section = document.createElement("section");
      section.className = "shelf";
      section.id = anchor;

      var heading = document.createElement("h2");
      heading.textContent = name;

      var art = CATEGORY_ART[category.name];

      if (art) {
        var banner = document.createElement("div");
        banner.className = "shelf-banner" + (art.titled ? " is-titled" : "");
        banner.style.backgroundImage = "url('" + art.src + "')";
        if (art.titled) {
          heading.className = "sr-only";
        }
        banner.appendChild(heading);
        section.appendChild(banner);
      } else {
        section.appendChild(heading);
      }

      var grid = document.createElement("div");
      grid.className = "grid";

      category.packages.forEach(function (pkg) {
        grid.appendChild(productCard(pkg, inBasket[pkg.id]));
      });

      section.appendChild(grid);
      els.shelves.appendChild(section);
    });

    if (window.BT_TILT) {
      window.BT_TILT(els.shelves);
    }
  }

  function productCard(pkg, added) {
    var card = document.createElement("article");
    card.className = "card product tilt";

    if (pkg.image) {
      var img = document.createElement("img");
      img.src = pkg.image;
      img.alt = "";
      img.loading = "lazy";
      img.className = "product-img";
      card.appendChild(img);
    }

    var title = document.createElement("h3");
    title.textContent = productName(pkg);
    card.appendChild(title);

    var price = document.createElement("p");
    price.className = "price";
    price.textContent = money(pkg.total_price, pkg.currency);
    card.appendChild(price);

    var description = cleanHtml(pkg.description || "");
    var first = description.querySelector("p");

    if (first) {
      var summary = document.createElement("p");
      summary.className = "product-summary";
      summary.textContent = first.textContent;
      card.appendChild(summary);
    }

    if (description.children.length > 1) {
      var details = document.createElement("details");
      var label = document.createElement("summary");
      label.textContent = "Details";
      details.appendChild(label);
      details.appendChild(description);
      card.appendChild(details);
    }

    var button = document.createElement("button");
    button.type = "button";
    button.className = "copy-btn buy-btn";

    if (added) {
      button.textContent = "In basket";
      button.disabled = true;
    } else {
      button.textContent = "Add to basket";
      button.addEventListener("click", function () { add(pkg.id, button); });
    }

    card.appendChild(button);
    return card;
  }

  function renderBasket() {
    var packages = (state.basket && state.basket.packages) || [];

    els.basketList.innerHTML = "";

    packages.forEach(function (pkg) {
      var row = document.createElement("li");

      var name = document.createElement("span");
      name.textContent = productName(pkg);
      row.appendChild(name);

      var price = document.createElement("span");
      price.className = "basket-price";
      price.textContent = money(pkg.in_basket && pkg.in_basket.price, state.basket.currency);
      row.appendChild(price);

      var drop = document.createElement("button");
      drop.type = "button";
      drop.className = "link-btn";
      drop.textContent = "Remove";
      drop.setAttribute("aria-label", "Remove " + productName(pkg));
      drop.addEventListener("click", function () { remove(pkg.id); });
      row.appendChild(drop);

      els.basketList.appendChild(row);
    });

    if (!packages.length) {
      var empty = document.createElement("li");
      empty.className = "basket-empty";
      empty.textContent = "Your basket is empty.";
      els.basketList.appendChild(empty);
    }

    els.basketTotal.textContent = packages.length ? money(state.basket.total_price, state.basket.currency) : "";
    els.basketNote.textContent = state.username ? "Delivered to " + state.username + " on play.battletown.store." : "Type your Minecraft name to start.";
    els.checkout.disabled = !packages.length || state.busy;

    els.basketBar.classList.toggle("has-items", packages.length > 0);
    els.basketBar.textContent = "Basket (" + packages.length + ") · " + money(state.basket ? state.basket.total_price : 0, state.basket && state.basket.currency);
  }

  // A gold coin flies from the button to the basket, which bumps.
  function celebrate(from) {
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var target = window.innerWidth <= 900 && els.basketBar.offsetParent ? els.basketBar : els.basket;

    function bump() {
      target.classList.remove("is-bumped");
      void target.offsetWidth;
      target.classList.add("is-bumped");
    }

    if (reduce || !from || !from.getBoundingClientRect) {
      bump();
      return;
    }

    var a = from.getBoundingClientRect();
    var b = target.getBoundingClientRect();
    var coin = document.createElement("span");
    coin.className = "fly";
    coin.style.left = (a.left + a.width / 2 - 13) + "px";
    coin.style.top = (a.top + a.height / 2 - 13) + "px";
    document.body.appendChild(coin);

    var dx = b.left + b.width / 2 - (a.left + a.width / 2);
    var dy = Math.max(20, b.top + 40) - (a.top + a.height / 2);

    coin.animate([
      { transform: "translate(0, 0) scale(1)", opacity: 1 },
      { transform: "translate(" + dx * 0.5 + "px," + (dy * 0.5 - 120) + "px) scale(1.4)", opacity: 1, offset: 0.5 },
      { transform: "translate(" + dx + "px," + dy + "px) scale(0.6)", opacity: 0.2 }
    ], { duration: 750, easing: "cubic-bezier(.5,0,.3,1)" }).onfinish = function () {
      coin.remove();
      bump();
      if (window.BT_BURST) {
        window.BT_BURST(target);
      }
    };
  }

  // ---------------------------------------------------------------- Helpers

  function basketIds() {
    var ids = {};
    ((state.basket && state.basket.packages) || []).forEach(function (pkg) {
      ids[pkg.id] = true;
    });
    return ids;
  }

  // Every BattleBucks package is called "Battle Bucks" in Tebex, so name it by its amount.
  function productName(pkg) {
    if (/^battle ?bucks$/i.test(pkg.name || "")) {
      var amount = /\$([\d,]+)/.exec(pkg.description || "");
      if (amount) {
        return amount[1] + " BattleBucks";
      }
    }
    return pkg.name;
  }

  function money(amount, currency) {
    if (typeof amount !== "number") {
      return "";
    }
    return "$" + amount.toFixed(2) + (currency ? " " + currency : "");
  }

  function byOrder(a, b) {
    return (a.order || 0) - (b.order || 0);
  }

  // Package descriptions come from the Tebex panel as HTML. Keep only
  // simple text tags so nothing else can run on this page.
  var ALLOWED = { P: 1, STRONG: 1, B: 1, EM: 1, I: 1, BR: 1, UL: 1, OL: 1, LI: 1 };

  function cleanHtml(source) {
    var parsed = new DOMParser().parseFromString(source, "text/html");
    var out = document.createElement("div");
    out.className = "product-details";

    function copy(from, to) {
      from.childNodes.forEach(function (node) {
        if (node.nodeType === 3) {
          to.appendChild(document.createTextNode(node.textContent));
        } else if (node.nodeType === 1) {
          if (ALLOWED[node.tagName]) {
            var el = document.createElement(node.tagName.toLowerCase());
            copy(node, el);
            to.appendChild(el);
          } else {
            copy(node, to);
          }
        }
      });
    }

    copy(parsed.body, out);
    return out;
  }

  function busy(on) {
    state.busy = on;
    app.classList.toggle("is-busy", on);
    els.checkout.disabled = on || !(state.basket && state.basket.packages && state.basket.packages.length);
  }

  function nameStatus(text, isError) {
    els.nameStatus.textContent = text;
    els.nameStatus.classList.toggle("is-error", !!isError);
  }

  function message(text, isError) {
    els.message.textContent = text;
    els.message.hidden = !text;
    els.message.classList.toggle("is-error", !!isError);
  }

  // ---------------------------------------------------------------- Start

  els.nameForm.addEventListener("submit", setName);
  els.checkout.addEventListener("click", checkout);

  busy(true);
  Promise.all([loadCategories(), restore()]).then(function () {
    if (state.username) {
      nameStatus("Buying for " + state.username + ".", false);
    }
    render();
  }).catch(function () {
    message("The store couldn't load right now. You can still buy in game with /buy.", true);
  }).then(function () {
    busy(false);
  });
})();
