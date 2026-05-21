/**
 * KYMERA 360° Viewer
 * - Drag (mouse/touch) → rotation with inertia
 * - Wheel/pinch → zoom (1× – 3×)
 * - Auto-rotate at start, stops on first interaction
 * - Crossfade between frames for smooth feel
 * - Keyboard: ← →, +/-, Esc
 */
(function () {
  'use strict';

  const VIEWERS = {
    helia: {
      name: 'Helia',
      tag: 'Celopostava · patina',
      basePath: 'assets/360/helia/',
      frames: 8,
      startFrame: 1,
      dragDirection: 'left',
    },
  };

  let state = null;

  function createViewer(key) {
    const cfg = VIEWERS[key];
    if (!cfg) return;

    // Build DOM without innerHTML (Trusted Types CSP compatibility)
    const overlay = document.createElement('div');
    overlay.className = 'v360-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-label', '360° prohlížeč — ' + cfg.name);

    const backdrop = document.createElement('div');
    backdrop.className = 'v360-backdrop';

    const closeBtn = document.createElement('button');
    closeBtn.className = 'v360-close';
    closeBtn.setAttribute('aria-label', 'Zavřít');
    closeBtn.textContent = '×';

    const framesEl = document.createElement('div');
    framesEl.className = 'v360-frames';

    const hintIcon1 = document.createElement('span');
    hintIcon1.className = 'v360-hint-icon';
    hintIcon1.textContent = '↔';
    const hintSep = document.createElement('span');
    hintSep.className = 'v360-sep';
    hintSep.textContent = '·';
    const hintIcon2 = document.createElement('span');
    hintIcon2.className = 'v360-hint-icon';
    hintIcon2.textContent = '⊕';
    const hint = document.createElement('div');
    hint.className = 'v360-hint';
    hint.appendChild(hintIcon1);
    hint.appendChild(document.createTextNode(' Táhni pro rotaci '));
    hint.appendChild(hintSep);
    hint.appendChild(document.createTextNode(' '));
    hint.appendChild(hintIcon2);
    hint.appendChild(document.createTextNode(' Scroll pro zoom'));

    const titleEl = document.createElement('span');
    titleEl.className = 'v360-title';
    titleEl.textContent = cfg.name;
    const tagEl = document.createElement('span');
    tagEl.className = 'v360-tag';
    tagEl.textContent = cfg.tag;
    const meta = document.createElement('div');
    meta.className = 'v360-meta';
    meta.appendChild(titleEl);
    meta.appendChild(tagEl);

    const bar = document.createElement('div');
    bar.className = 'v360-progress-bar';
    const progress = document.createElement('div');
    progress.className = 'v360-progress';
    progress.appendChild(bar);

    const stage = document.createElement('div');
    stage.className = 'v360-stage';
    stage.appendChild(framesEl);
    stage.appendChild(hint);
    stage.appendChild(meta);
    stage.appendChild(progress);

    overlay.appendChild(backdrop);
    overlay.appendChild(closeBtn);
    overlay.appendChild(stage);
    document.body.appendChild(overlay);

    // Build image elements
    const imgs = [];
    for (let i = 1; i <= cfg.frames; i++) {
      const img = document.createElement('img');
      img.src = cfg.basePath + key + '_' + String(i).padStart(2, '0') + '.webp';
      img.alt = cfg.name + ' — pozice ' + i + '/' + cfg.frames;
      img.className = 'v360-img';
      img.draggable = false;
      img.style.opacity = '0';
      framesEl.appendChild(img);
      imgs.push(img);
    }

    // State
    let position = cfg.startFrame;
    let zoom = 1;
    let panX = 0, panY = 0;
    let interacted = false;
    let autoRotate = true;
    let lastTs = 0;
    const AUTO_RPS = 0.05;
    const FRAMES = cfg.frames;

    // Inertia state
    let velocity = 0;       // position-units per ms
    let lastMoveTime = 0;
    let inertiaRaf = null;

    function render() {
      const pos = ((position % FRAMES) + FRAMES) % FRAMES;
      const i0 = Math.floor(pos);
      const i1 = (i0 + 1) % FRAMES;
      const t = pos - i0;
      for (let k = 0; k < FRAMES; k++) {
        if (k === i0) imgs[k].style.opacity = String(1 - t);
        else if (k === i1) imgs[k].style.opacity = String(t);
        else imgs[k].style.opacity = '0';
      }
      framesEl.style.transform = 'translate(' + panX + 'px, ' + panY + 'px) scale(' + zoom + ')';
      bar.style.width = (((position % FRAMES) + FRAMES) % FRAMES / FRAMES * 100) + '%';
    }

    function stopInertia() {
      if (inertiaRaf) { cancelAnimationFrame(inertiaRaf); inertiaRaf = null; }
      velocity = 0;
    }

    function startInertia() {
      stopInertia();
      if (Math.abs(velocity) < 0.0003) return;
      var lastTs2 = performance.now();
      function step(ts) {
        if (!state) return;
        var dt = Math.min(ts - lastTs2, 64); // cap at 64ms to avoid big jumps after tab switch
        lastTs2 = ts;
        // Exponential decay: 92% retention per 16ms frame
        velocity *= Math.pow(0.92, dt / 16);
        if (Math.abs(velocity) < 0.00015) { velocity = 0; return; }
        position += velocity * dt;
        render();
        inertiaRaf = requestAnimationFrame(step);
      }
      inertiaRaf = requestAnimationFrame(step);
    }

    function loop(ts) {
      if (autoRotate && !interacted) {
        if (lastTs) {
          const dt = (ts - lastTs) / 1000;
          position += AUTO_RPS * FRAMES * dt;
        }
        lastTs = ts;
        render();
      }
      if (state) requestAnimationFrame(loop);
    }
    render();
    requestAnimationFrame(loop);

    setTimeout(function () { if (hint) hint.classList.add('v360-hint--fade'); }, 4000);

    function markInteracted() {
      if (!interacted) {
        interacted = true;
        autoRotate = false;
        hint.classList.add('v360-hint--fade');
      }
    }

    // Drag
    let dragging = false, lastX = 0, lastY = 0, dragMode = null;

    function onDown(e) {
      const ev = e.touches ? e.touches[0] : e;
      stopInertia(); // cancel any running inertia
      dragging = true;
      lastX = ev.clientX; lastY = ev.clientY;
      lastMoveTime = performance.now();
      dragMode = (zoom > 1) ? 'pan' : 'rotate';
      markInteracted();
      e.preventDefault();
    }

    function onMove(e) {
      if (!dragging) return;
      const ev = e.touches ? e.touches[0] : e;
      const dx = ev.clientX - lastX;
      const dy = ev.clientY - lastY;
      const now = performance.now();
      const dt = Math.max(now - lastMoveTime, 1);

      if (dragMode === 'pan') {
        panX += dx; panY += dy;
        const maxPan = 300 * (zoom - 1);
        panX = Math.max(-maxPan, Math.min(maxPan, panX));
        panY = Math.max(-maxPan, Math.min(maxPan, panY));
        velocity = 0;
      } else {
        const delta = (dx / 220) * FRAMES * -1;
        // Blend current velocity with new measurement for stability
        const newVelocity = delta / dt;
        velocity = velocity * 0.5 + newVelocity * 0.5;
        position += delta;
      }

      lastX = ev.clientX; lastY = ev.clientY;
      lastMoveTime = now;
      render();
      e.preventDefault();
    }

    function onUp(e) {
      if (!dragging) return;
      const wasRotating = dragMode === 'rotate';
      dragging = false;
      dragMode = null;
      if (wasRotating) startInertia();
    }

    overlay.addEventListener('mousedown', onDown);
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    overlay.addEventListener('touchstart', onDown, { passive: false });
    window.addEventListener('touchmove', onMove, { passive: false });
    window.addEventListener('touchend', onUp);

    // Wheel zoom
    overlay.addEventListener('wheel', function (e) {
      markInteracted();
      const delta = -e.deltaY * 0.002;
      zoom = Math.max(1, Math.min(3, zoom + delta));
      if (zoom === 1) { panX = 0; panY = 0; }
      render();
      e.preventDefault();
    }, { passive: false });

    // Pinch zoom
    let pinchStart = null;
    overlay.addEventListener('touchstart', function (e) {
      if (e.touches.length === 2) {
        markInteracted();
        stopInertia();
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        pinchStart = { dist: Math.hypot(dx, dy), zoom: zoom };
      }
    }, { passive: false });
    overlay.addEventListener('touchmove', function (e) {
      if (e.touches.length === 2 && pinchStart) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const dist = Math.hypot(dx, dy);
        zoom = Math.max(1, Math.min(3, pinchStart.zoom * (dist / pinchStart.dist)));
        if (zoom === 1) { panX = 0; panY = 0; }
        render();
        e.preventDefault();
      }
    }, { passive: false });
    overlay.addEventListener('touchend', function () { pinchStart = null; });

    // Keyboard
    function onKey(e) {
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowLeft')  { markInteracted(); stopInertia(); position -= 1; render(); }
      else if (e.key === 'ArrowRight') { markInteracted(); stopInertia(); position += 1; render(); }
      else if (e.key === '+' || e.key === '=') { markInteracted(); zoom = Math.min(3, zoom + 0.2); render(); }
      else if (e.key === '-' || e.key === '_') { markInteracted(); zoom = Math.max(1, zoom - 0.2); if (zoom === 1) { panX = 0; panY = 0; } render(); }
    }
    document.addEventListener('keydown', onKey);

    // Close
    function close() {
      stopInertia();
      state = null;
      document.removeEventListener('keydown', onKey);
      overlay.classList.add('v360-overlay--out');
      setTimeout(function () { overlay.remove(); }, 250);
      document.body.style.overflow = '';
    }
    closeBtn.addEventListener('click', close);
    backdrop.addEventListener('click', close);

    document.body.style.overflow = 'hidden';
    state = { close: close };
    return { close: close };
  }

  window.KymeraViewer360 = { open: createViewer };

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-v360]').forEach(function (el) {
      el.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        createViewer(el.dataset.v360);
      });
    });
  });
})();
