/**
 * HD Bodygraph Widget — Renders an interactive SVG bodygraph inline.
 * 
 * Usage: <div class="hde-bodygraph-widget" data-api="https://api.humandesignengine.com"></div>
 * 
 * Calls POST /bodygraph with birth data, receives SVG, embeds it on the page.
 * Gracefully degrades: if API is unreachable, shows a friendly message with setup instructions.
 * 
 * Dependencies: none (vanilla JS, no frameworks)
 * License: AGPLv3
 */
(function() {
  'use strict';

  // ── Configuration ──────────────────────────────────────────────────
  const DEFAULT_API = 'http://localhost:8081';
  const BODYGRAPH_PATH = '/api/public/bodygraph';
  const THEME = 'canonical';

  // ── Type descriptions ───────────────────────────────────────────────
  const TYPE_INFO = {
    'Generator': { icon: '🔥', desc: 'The life force of the planet. Your aura is open and enveloping.' },
    'Manifesting Generator': { icon: '🌟', desc: 'Generator energy with Manifestor speed. Multi-passionate and fast.' },
    'Manifestor': { icon: '⚡', desc: 'You are here to initiate and impact. Your aura is closed and repelling.' },
    'Projector': { icon: '🔮', desc: 'You are here to guide others. Your aura is focused and absorbing.' },
    'Reflector': { icon: '🌙', desc: 'The rarest type — a mirror of the community. You sample and reflect energy.' }
  };

  // ── DOM helpers ─────────────────────────────────────────────────────
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  // ── Widget class ────────────────────────────────────────────────────
  function BodygraphWidget(container, options) {
    this.container = container;
    this.options = options || {};
    this.apiUrl = this.options.apiUrl || 
                  this.container.getAttribute('data-api') || 
                  DEFAULT_API;
    // Strip trailing slash
    if (this.apiUrl.slice(-1) === '/') this.apiUrl = this.apiUrl.slice(0, -1);
    
    this._render();
  }

  BodygraphWidget.prototype._render = function() {
    var self = this;
    var w = this.container;
    w.innerHTML = '';

    // Card wrapper
    var card = el('div', 'bdg-card');
    
    // Header
    var header = el('div', 'bdg-header');
    header.innerHTML = '<span class="bdg-header-icon">✦</span> Free Bodygraph';
    card.appendChild(header);

    // Form
    var form = el('form', 'bdg-form');
    form.innerHTML = 
      '<div class="bdg-form-row">' +
        '<input type="text" class="bdg-input" name="name" placeholder="Your name" required>' +
      '</div>' +
      '<div class="bdg-form-row bdg-date-row">' +
        '<input type="number" class="bdg-input bdg-input-sm" name="month" placeholder="MM" min="1" max="12" required>' +
        '<input type="number" class="bdg-input bdg-input-sm" name="day" placeholder="DD" min="1" max="31" required>' +
        '<input type="number" class="bdg-input bdg-input-md" name="year" placeholder="YYYY" min="1900" max="2100" required>' +
      '</div>' +
      '<div class="bdg-form-row bdg-time-row">' +
        '<input type="number" class="bdg-input bdg-input-sm" name="hour" placeholder="HH" min="0" max="23" required>' +
        '<span class="bdg-time-sep">:</span>' +
        '<input type="number" class="bdg-input bdg-input-sm" name="minute" placeholder="MM" min="0" max="59" value="0">' +
        '<select class="bdg-select" name="ampm"><option value="am">AM</option><option value="pm">PM</option></select>' +
      '</div>' +
      '<div class="bdg-form-row">' +
        '<input type="text" class="bdg-input" name="location" placeholder="City, State (optional)">' +
      '</div>' +
      '<button type="submit" class="bdg-btn">Generate My Bodygraph →</button>' +
      '<p class="bdg-privacy">Free · No email required · Computed on the fly</p>';

    card.appendChild(form);

    // Result container (hidden initially)
    var result = el('div', 'bdg-result');
    result.style.display = 'none';
    card.appendChild(result);

    // Error container
    var error = el('div', 'bdg-error');
    error.style.display = 'none';
    card.appendChild(error);

    w.appendChild(card);

    // Handle form submit
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      self._compute(form, result, error);
    });
  };

  BodygraphWidget.prototype._compute = function(form, resultEl, errorEl) {
    var self = this;
    var btn = form.querySelector('button');
    var origText = btn.textContent;
    btn.textContent = 'Computing...';
    btn.disabled = true;
    errorEl.style.display = 'none';
    resultEl.style.display = 'none';

    var fd = new FormData(form);
    var hour = parseInt(fd.get('hour')) || 12;
    if (fd.get('ampm') === 'pm' && hour < 12) hour += 12;
    if (fd.get('ampm') === 'am' && hour === 12) hour = 0;

    var payload = {
      name: fd.get('name') || 'Unknown',
      year: parseInt(fd.get('year')),
      month: parseInt(fd.get('month')),
      day: parseInt(fd.get('day')),
      hour: hour,
      minute: parseInt(fd.get('minute')) || 0,
      location: fd.get('location') || 'UTC',
      theme: THEME
    };

    fetch(self.apiUrl + BODYGRAPH_PATH, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(function(r) {
      if (!r.ok) throw new Error('Server returned ' + r.status);
      return r.text();
    })
    .then(function(svg) {
      self._showResult(resultEl, svg, payload);
    })
    .catch(function(err) {
      self._showError(errorEl, err.message);
    })
    .finally(function() {
      btn.textContent = origText;
      btn.disabled = false;
    });
  };

  BodygraphWidget.prototype._showResult = function(el, svg, payload) {
    el.innerHTML = 
      '<div class="bdg-result-header">' +
        '<span class="bdg-result-icon">✦</span>' +
        '<span>' + payload.name + '</span>' +
      '</div>' +
      '<div class="bdg-svg-container">' + svg + '</div>' +
      '<div class="bdg-result-footer">' +
        '<p class="bdg-footer-text">Want the full 20+ page report with transit forecasts and practical experiments?</p>' +
        '<a href="buy-report.html" class="bdg-btn bdg-btn-secondary">Get Your Full Report →</a>' +
      '</div>';
    el.style.display = 'block';
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  BodygraphWidget.prototype._showError = function(el, msg) {
    var help = '';
    if (msg.indexOf('Failed to fetch') !== -1 || msg.indexOf('NetworkError') !== -1) {
      help = '<p class="bdg-error-help">The chart service is currently being set up. Check back soon — this will be live shortly!</p>';
    }
    el.innerHTML = 
      '<p class="bdg-error-title">⚠️ Unable to generate chart</p>' +
      '<p class="bdg-error-msg">' + msg + '</p>' +
      help;
    el.style.display = 'block';
  };

  // ── Auto-init ───────────────────────────────────────────────────────
  function init() {
    var widgets = document.querySelectorAll('.hde-bodygraph-widget');
    for (var i = 0; i < widgets.length; i++) {
      if (!widgets[i]._bdg_widget) {
        widgets[i]._bdg_widget = new BodygraphWidget(widgets[i]);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
