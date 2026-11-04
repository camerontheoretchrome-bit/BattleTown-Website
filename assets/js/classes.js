// BattleTown website: the Classes page showcase.
//
// The page lists every class as a slide inside .stage, with a picker of
// thumbnails linking to #<class id>. This script shows one slide at a time,
// recolours the page in the class accent, and supports arrows, keys,
// swipes and deep links. Without it the slides simply stack.
(function () {
  "use strict";

  var showcase = document.querySelector(".showcase");

  if (!showcase) {
    return;
  }

  var slides = Array.prototype.slice.call(showcase.querySelectorAll(".class-slide"));
  var picks = Array.prototype.slice.call(showcase.querySelectorAll(".picker a"));
  var stage = showcase.querySelector(".stage");
  var index = 0;

  function show(next, fromHash) {
    index = (next + slides.length) % slides.length;

    slides.forEach(function (slide, i) {
      slide.classList.toggle("is-active", i === index);
      slide.setAttribute("aria-hidden", i === index ? "false" : "true");
    });

    picks.forEach(function (pick, i) {
      pick.setAttribute("aria-current", i === index ? "true" : "false");
    });

    var slide = slides[index];
    showcase.style.setProperty("--accent", slide.style.getPropertyValue("--accent"));

    if (!fromHash && history.replaceState) {
      history.replaceState(null, "", "#" + slide.dataset.id);
    }
  }

  function fromHash() {
    var id = location.hash.slice(1);

    for (var i = 0; i < slides.length; i++) {
      if (slides[i].dataset.id === id) {
        return i;
      }
    }
    return 0;
  }

  picks.forEach(function (pick, i) {
    pick.addEventListener("click", function (event) {
      event.preventDefault();
      show(i);
      if (window.innerWidth < 900) {
        stage.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    });
  });

  showcase.querySelector(".stage-arrow.prev").addEventListener("click", function () { show(index - 1); });
  showcase.querySelector(".stage-arrow.next").addEventListener("click", function () { show(index + 1); });

  document.addEventListener("keydown", function (event) {
    if (event.target.closest && event.target.closest("input, textarea")) {
      return;
    }
    if (event.key === "ArrowRight") { show(index + 1); }
    if (event.key === "ArrowLeft") { show(index - 1); }
  });

  // Swipe on touch screens.
  var startX = null;
  stage.addEventListener("touchstart", function (event) { startX = event.touches[0].clientX; }, { passive: true });
  stage.addEventListener("touchend", function (event) {
    if (startX === null) {
      return;
    }
    var dx = event.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 40) {
      show(index + (dx < 0 ? 1 : -1));
    }
    startX = null;
  });

  window.addEventListener("hashchange", function () { show(fromHash(), true); });

  show(fromHash(), true);
})();
