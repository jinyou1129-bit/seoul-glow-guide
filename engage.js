/* Seoul Glow Guide — stay-on-site helpers: scroll progress, K-beauty wishlist, shopping quiz. */
(function () {
  'use strict';
  var KEY = 'glow.wishlist.v1';
  var doc = document;

  function read() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY) || '[]');
      return Array.isArray(v) ? v : [];
    } catch (e) { return []; }
  }
  function write(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) {}
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  /* ---------- scroll progress ---------- */
  var bar = doc.createElement('div');
  bar.className = 'progress-bar';
  bar.setAttribute('aria-hidden', 'true');
  doc.body.appendChild(bar);
  function updateBar() {
    var h = doc.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = (h > 0 ? Math.max(0, Math.min(100, (window.scrollY / h) * 100)) : 0) + '%';
  }
  window.addEventListener('scroll', updateBar, { passive: true });
  window.addEventListener('resize', updateBar);
  updateBar();

  /* ---------- wishlist ---------- */
  var saved = read();
  var picks = [].slice.call(doc.querySelectorAll('.pick'));
  picks.forEach(function (pick, i) {
    if (!pick.id) pick.id = 'pick-' + (i + 1);
    var h2 = pick.querySelector('h2');
    if (!h2) return;
    var name = h2.textContent.trim();
    var btn = doc.createElement('button');
    btn.type = 'button';
    btn.className = 'wish-btn';
    btn.setAttribute('data-name', name);
    btn.setAttribute('data-href', location.pathname + '#' + pick.id);
    h2.insertAdjacentElement('afterend', btn);
  });

  function has(name) {
    return saved.some(function (s) { return s.name === name; });
  }

  var dock = doc.createElement('div');
  dock.className = 'saved-dock';
  dock.innerHTML =
    '<div class="saved-panel" id="wish-panel" hidden>' +
    '<div class="saved-head"><strong>My K-beauty wishlist</strong>' +
    '<button class="saved-close" type="button" aria-label="Close wishlist">✕</button></div>' +
    '<ul class="saved-list"></ul>' +
    '<p class="saved-empty">Nothing saved yet. Tap ♡ next to a product to keep it here for your next Seoul trip.</p>' +
    '<button class="saved-clear" type="button">Clear wishlist</button></div>' +
    '<button class="saved-toggle" type="button" aria-expanded="false" aria-controls="wish-panel">♡ Wishlist (0)</button>';
  doc.body.appendChild(dock);

  var panel = dock.querySelector('.saved-panel');
  var listEl = dock.querySelector('.saved-list');
  var emptyEl = dock.querySelector('.saved-empty');
  var toggle = dock.querySelector('.saved-toggle');
  var clearBtn = dock.querySelector('.saved-clear');
  var wishButtons = [].slice.call(doc.querySelectorAll('.wish-btn'));

  function render() {
    toggle.textContent = '♡ Wishlist (' + saved.length + ')';
    listEl.innerHTML = saved.map(function (s) {
      return '<li><a href="' + esc(s.href) + '">' + esc(s.name) + '</a>' +
        '<button type="button" class="saved-remove" data-name="' + esc(s.name) +
        '" aria-label="Remove ' + esc(s.name) + ' from wishlist">Remove</button></li>';
    }).join('');
    emptyEl.hidden = saved.length > 0;
    clearBtn.hidden = saved.length === 0;
    wishButtons.forEach(function (b) {
      var on = has(b.getAttribute('data-name'));
      b.setAttribute('aria-pressed', String(on));
      b.textContent = on ? '♥ Saved' : '♡ Save to wishlist';
    });
  }

  listEl.addEventListener('click', function (e) {
    var btn = e.target.closest('.saved-remove');
    if (!btn) return;
    saved = saved.filter(function (s) { return s.name !== btn.getAttribute('data-name'); });
    write(saved);
    render();
  });
  clearBtn.addEventListener('click', function () {
    saved = [];
    write(saved);
    render();
  });
  toggle.addEventListener('click', function () {
    panel.hidden = !panel.hidden;
    toggle.setAttribute('aria-expanded', String(!panel.hidden));
    if (!panel.hidden) panel.querySelector('a, button').focus();
  });
  dock.querySelector('.saved-close').addEventListener('click', function () {
    panel.hidden = true;
    toggle.setAttribute('aria-expanded', 'false');
    toggle.focus();
  });
  wishButtons.forEach(function (b) {
    b.addEventListener('click', function () {
      var name = b.getAttribute('data-name');
      if (has(name)) {
        saved = saved.filter(function (s) { return s.name !== name; });
      } else {
        saved.push({ name: name, href: b.getAttribute('data-href') });
      }
      write(saved);
      render();
    });
  });
  render();

  /* ---------- K-beauty shopping quiz ---------- */
  var quiz = doc.getElementById('glow-quiz');
  if (quiz) {
    var form = quiz.querySelector('form');
    var result = quiz.querySelector('.quiz-result');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var right = 0, missed = [];
      quiz.querySelectorAll('fieldset').forEach(function (fs) {
        var ok = data.get(fs.getAttribute('data-name')) === fs.getAttribute('data-answer');
        fs.classList.toggle('quiz-ok', ok);
        fs.classList.toggle('quiz-bad', !ok && !!data.get(fs.getAttribute('data-name')));
        if (ok) right++; else missed.push(fs.getAttribute('data-href'));
        var why = fs.querySelector('.quiz-why');
        if (why) why.hidden = ok;
      });
      var total = quiz.querySelectorAll('fieldset').length;
      var answered = form.querySelectorAll('input[type=radio]:checked').length;
      result.hidden = false;
      var head = '<strong>' + right + ' / ' + total + ' correct.</strong> ';
      if (answered < total) {
        result.innerHTML = head + 'You answered ' + answered + ' of ' + total + '. ' +
          (missed[0] ? 'The guide for the first one you missed: <a href="' + missed[0] + '">open it →</a>' : '');
      } else if (right === total) {
        result.innerHTML = head + 'You are ready for the shelf. Next: <a href="./top-10-olive-young-skincare-must-buys.html">the Olive Young shortlist</a>.';
      } else {
        result.innerHTML = head + 'Close. What you missed: <a href="' + missed[0] + '">open the guide →</a>';
      }
      result.focus();
    });
    quiz.querySelector('.quiz-reset').addEventListener('click', function () {
      form.reset();
      quiz.querySelectorAll('fieldset').forEach(function (fs) { fs.classList.remove('quiz-ok', 'quiz-bad'); });
      result.hidden = true;
    });
  }
})();
