// BattleTown website: small helpers shared by every page.

// Copy buttons: <button class="copy-btn" data-copy="text">.
document.querySelectorAll("[data-copy]").forEach(function (button) {
  var label = button.textContent;

  button.addEventListener("click", function () {
    var text = button.getAttribute("data-copy");

    copyText(text).then(function () {
      button.textContent = "Copied!";
      button.classList.add("copied");
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

// Marks the current page in the nav.
(function () {
  var here = location.pathname.replace(/index\.html$/, "");

  document.querySelectorAll(".nav a").forEach(function (link) {
    var path = new URL(link.href).pathname;

    if (path === here || (path !== "/" && here.indexOf(path) === 0)) {
      link.setAttribute("aria-current", "page");
    }
  });
})();
