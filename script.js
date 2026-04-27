/* =========================================================
   KYMERA — interakce
   - rok ve footeru
   - mobilní menu
   - jemný reveal on scroll
   - Web3Forms odeslání s loading / success / error stavem
   ========================================================= */

(function () {
  // --- rok ve footeru
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();

  // --- mobilní menu
  var toggle = document.querySelector(".nav-toggle");
  var mobileNav = document.getElementById("mobile-nav");
  if (toggle && mobileNav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      if (open) {
        mobileNav.setAttribute("hidden", "");
      } else {
        mobileNav.removeAttribute("hidden");
      }
    });
    mobileNav.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        toggle.setAttribute("aria-expanded", "false");
        mobileNav.setAttribute("hidden", "");
      });
    });
  }

  // --- reveal on scroll (jemné)
  var revealEls = document.querySelectorAll(
    ".section-head, .collection, .work, .about-body, .about-media, .trade-card, .contact-intro, .contact-form, .statement"
  );
  var prefersReduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function showAll() {
    revealEls.forEach(function (el) { el.classList.add("is-in"); });
  }

  if (prefersReduced) {
    // bez animací – rovnou viditelné, bez .reveal třídy
    showAll();
  } else {
    revealEls.forEach(function (el) { el.classList.add("reveal"); });

    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add("is-in");
            io.unobserve(e.target);
          }
        });
      }, { rootMargin: "0px 0px -10% 0px", threshold: 0.08 });
      revealEls.forEach(function (el) { io.observe(el); });

      // fail-safe: po 2,5 s ukázat vše tak jako tak (printscreen, headless prohlížeče,
      // velmi pomalý scroll, native lazy-render apod.)
      setTimeout(showAll, 2500);
    } else {
      showAll();
    }
  }

  // --- formulář (Web3Forms)
  var form = document.getElementById("contactForm");
  var submitBtn = document.getElementById("submitBtn");
  var status = document.getElementById("formStatus");

  if (form && submitBtn && status) {
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();

      // honeypot
      var bot = form.querySelector('input[name="botcheck"]');
      if (bot && bot.checked) return;

      // jednoduchá validace
      if (!form.checkValidity()) {
        status.textContent = "Vyplňte prosím jméno a e-mail.";
        status.className = "form-status is-error";
        form.reportValidity();
        return;
      }

      submitBtn.classList.add("is-loading");
      submitBtn.disabled = true;
      status.textContent = "Odesílám…";
      status.className = "form-status";

      var data = new FormData(form);

      fetch("https://api.web3forms.com/submit", {
        method: "POST",
        body: data,
        headers: { "Accept": "application/json" }
      })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (res.ok && res.j && res.j.success) {
            status.textContent = "Děkujeme. Ozveme se osobně, zpravidla do 48 hodin.";
            status.className = "form-status is-success";
            form.reset();
          } else {
            var msg = (res.j && res.j.message) ? res.j.message : "Něco se nepovedlo. Zkuste to prosím znovu nebo napište na atelier@kymera.art.";
            status.textContent = msg;
            status.className = "form-status is-error";
          }
        })
        .catch(function () {
          status.textContent = "Spojení se nezdařilo. Napište prosím na atelier@kymera.art.";
          status.className = "form-status is-error";
        })
        .finally(function () {
          submitBtn.classList.remove("is-loading");
          submitBtn.disabled = false;
        });
    });
  }
})();
