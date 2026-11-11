(function () {
  var btn = document.querySelector("[data-menu]");
  var nav = document.querySelector("[data-nav]");
  if (!btn || !nav) return;
  btn.addEventListener("click", function () {
    var open = nav.classList.toggle("is-open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  });
  nav.addEventListener("click", function (event) {
    if (event.target.closest("a")) {
      nav.classList.remove("is-open");
      btn.setAttribute("aria-expanded", "false");
    }
  });
})();
