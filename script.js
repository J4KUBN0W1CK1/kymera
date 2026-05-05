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

  // --- cookie banner (technický souhlas, 1 rok platnost)
  var cookieBanner = document.getElementById("cookie-banner");
  var cookieAccept = document.getElementById("cookie-accept");
  function hasCookie(name) {
    return document.cookie.split(";").some(function (c) {
      return c.trim().indexOf(name + "=") === 0;
    });
  }
  function setCookie(name, val, days) {
    var d = new Date();
    d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = name + "=" + val + ";expires=" + d.toUTCString() + ";path=/;SameSite=Lax";
  }
  if (cookieBanner && cookieAccept) {
    if (!hasCookie("kymera_cookies_ok")) {
      cookieBanner.removeAttribute("hidden");
    }
    cookieAccept.addEventListener("click", function () {
      setCookie("kymera_cookies_ok", "1", 365);
      cookieBanner.setAttribute("hidden", "");
    });
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
            var msg = (res.j && res.j.message) ? res.j.message : "Něco se nepovedlo. Zkuste to prosím znovu nebo zavolejte na +420 734 548 884.";
            status.textContent = msg;
            status.className = "form-status is-error";
          }
        })
        .catch(function () {
          status.textContent = "Spojení se nezdařilo. Zavolejte prosím na +420 734 548 884.";
          status.className = "form-status is-error";
        })
        .finally(function () {
          submitBtn.classList.remove("is-loading");
          submitBtn.disabled = false;
        });
    });
  }
})();

/* ============== LIGHTBOX (galerie) ============== */
(function(){
  var grid = document.getElementById('gallery-grid');
  var lb = document.getElementById('lightbox');
  if (!grid || !lb) return;

  var img = document.getElementById('lb-img');
  var counter = document.getElementById('lb-counter');
  var btnClose = document.getElementById('lb-close');
  var btnPrev = document.getElementById('lb-prev');
  var btnNext = document.getElementById('lb-next');
  var items = Array.prototype.slice.call(grid.querySelectorAll('.gallery-item'));
  var current = 0;

  function srcOf(idx){
    return items[idx].querySelector('img').getAttribute('src');
  }
  function altOf(idx){
    return items[idx].querySelector('img').getAttribute('alt') || '';
  }
  function show(idx){
    current = (idx + items.length) % items.length;
    img.src = srcOf(current);
    img.alt = altOf(current);
    counter.textContent = (current+1) + ' / ' + items.length;
  }
  function open(idx){
    show(idx);
    lb.hidden = false;
    document.body.style.overflow = 'hidden';
    btnClose.focus();
  }
  function close(){
    lb.hidden = true;
    document.body.style.overflow = '';
    img.src = '';
  }

  items.forEach(function(it, i){
    it.addEventListener('click', function(){ open(i); });
  });
  btnClose.addEventListener('click', close);
  btnPrev.addEventListener('click', function(){ show(current - 1); });
  btnNext.addEventListener('click', function(){ show(current + 1); });

  // klávesnice
  document.addEventListener('keydown', function(e){
    if (lb.hidden) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') show(current - 1);
    else if (e.key === 'ArrowRight') show(current + 1);
  });

  // klik mimo obrázek = zavřít
  lb.addEventListener('click', function(e){
    if (e.target === lb) close();
  });

  // swipe na mobilu
  var touchX = null;
  lb.addEventListener('touchstart', function(e){ touchX = e.touches[0].clientX; });
  lb.addEventListener('touchend', function(e){
    if (touchX === null) return;
    var dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
    touchX = null;
  });
})();
