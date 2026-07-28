/**
 * Human Design Engine — Free Chart Widget
 * ==========================================
 * A single self-contained script that renders an interactive Human Design
 * chart widget. Drop it on any page — no build step, no dependencies.
 *
 * Usage:
 *   <div class="hde-chart-widget" data-api="https://api.humandesignengine.com"></div>
 *   <script src="widget.js"></script>
 *
 * Or manually:  HDEWidget.init('#my-container', { apiUrl: '...' });
 *
 * License: AGPLv3
 * Version: 1.0.0
 */
(function () {
  'use strict';

  var HDE_GA4_FUNNEL_EVENT_MAP = {
    'hde_chart_generated': 'view_item',
    'hde_transit_prompt_viewed': 'select_content',
    'hde_nervous_system_practice_started': 'begin_checkout',
    'hde_nervous_system_practice_completed': 'complete_registration'
  };
  function hdeDispatchGa4(eventName, params) {
    var ga4 = HDE_GA4_FUNNEL_EVENT_MAP[eventName];
    if (ga4 && typeof window.gtag === 'function') {
      try { window.gtag('event', ga4, params || {}); } catch (e) {}
    }
  }


  // ── Config ──────────────────────────────────────────────────────────────
  var DEFAULT_API = 'https://api.humandesignengine.com';
  var BRAND = {
    gradient: 'linear-gradient(135deg, #2F3631 0%, #5F7261 100%)',
    primary: '#2F3631',
    accent: '#5F7261',
    light: '#4B5C4E',
    bg: '#FAF7F0',
    card: 'rgba(255,255,255,0.86)',
    border: 'rgba(95,114,97,0.18)',
    text: '#2F3631',
    muted: '#5C625E',
    dim: '#4B514E',
    success: '#5F7261',
    error: '#B4534A',
  };

  // ── Type data ───────────────────────────────────────────────────────────
  var TYPE_INFO = {
    'manifestor': { icon: '⚡', desc: 'You\'re here to initiate and impact. Your aura is closed and repelling — people feel you before you speak.' },
    'generator': { icon: '🔥', desc: 'You\'re the life force of the planet. Your aura is open and enveloping — opportunities come to you.' },
    'manifesting generator': { icon: '🌟', desc: 'Generator energy with Manifestor speed. Multi-passionate and fast — don\'t let anyone slow you down.' },
    'projector': { icon: '🔮', desc: 'You\'re here to guide and see deeply into others. Your aura is focused and absorbing.' },
    'reflector': { icon: '🌙', desc: 'The rarest type — a mirror of the community. You sample and reflect the energy around you.' },
  };

  var CENTER_ICONS = {
    'Head': '🧠', 'Ajna': '💡', 'Throat': '🗣️', 'G': '💎',
    'Heart/Ego': '❤️', 'Sacral': '☀️', 'Spleen': '🛡️',
    'Solar Plexus': '🌊', 'Root': '⛽'
  };

  // ── Helpers ─────────────────────────────────────────────────────────────
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

  function pageContext() {
    return {
      page_path: window.location.pathname,
      page_title: document.title || '',
      widget_source: 'free_reading_widget'
    };
  }

  function trackEvent(eventName, params) {
    var detail = Object.assign({}, pageContext(), params || {});
    try {
      window.dispatchEvent(new CustomEvent('hde:analytics', {
        detail: Object.assign({ event: eventName }, detail)
      }));
    } catch (e) {}

    if (window.dataLayer && typeof window.dataLayer.push === 'function') {
      window.dataLayer.push(Object.assign({ event: eventName }, detail));
    }
    if (typeof window.gtag === 'function') {
      window.gtag('event', eventName, detail);
    }
    if (typeof window.hdeTrackEvent === 'function') {
      window.hdeTrackEvent(eventName, detail);
    }
  }

  // ── Widget CSS injector ─────────────────────────────────────────────────
  var CSS_INJECTED = false;
  function injectCSS(prefix) {
    if (CSS_INJECTED) return;
    CSS_INJECTED = true;
    var css =
      prefix + ' * { box-sizing:border-box; margin:0; padding:0; font-family:"Outfit",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }\n' +
      prefix + ' { max-width:500px; width:100%; margin:0 auto; }\n' +
      prefix + '-card { background:' + BRAND.card + '; border:1px solid ' + BRAND.border + '; border-radius:20px; overflow:hidden; box-shadow:0 14px 40px rgba(47,54,49,0.08); }\n' +
      prefix + '-header { background:' + BRAND.gradient + '; padding:28px 24px; text-align:center; color:#FAF7F0; }\n' +
      prefix + '-header h2 { font-size:1.15rem; font-weight:700; letter-spacing:-0.02em; }\n' +
      prefix + '-header p { font-size:0.82rem; opacity:0.85; margin-top:4px; }\n' +
      prefix + '-body { padding:24px; }\n' +
      prefix + '-form-group { margin-bottom:16px; }\n' +
      prefix + '-form-group label { display:block; font-size:0.78rem; font-weight:600; color:' + BRAND.light + '; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.05em; }\n' +
      prefix + '-form-group input { width:100%; padding:12px 14px; background:#FDFBF7; border:1px solid ' + BRAND.border + '; border-radius:10px; color:' + BRAND.text + '; font-size:0.92rem; transition:border-color 0.2s; outline:none; }\n' +
      prefix + '-form-group input:focus { border-color:' + BRAND.primary + '; box-shadow:0 0 0 3px rgba(95,114,97,0.14); }\n' +
      prefix + '-form-group input::placeholder { color:' + BRAND.dim + '; }\n' +
      prefix + '-form-row { display:flex; gap:12px; }\n' +
      prefix + '-form-row > * { flex:1; }\n' +
      prefix + '-btn { width:100%; padding:14px; background:' + BRAND.gradient + '; color:#FAF7F0; border:none; border-radius:12px; font-size:0.95rem; font-weight:700; cursor:pointer; letter-spacing:0.02em; transition:transform 0.15s,box-shadow 0.2s; }\n' +
      prefix + '-btn:hover { transform:translateY(-1px); box-shadow:0 10px 26px rgba(47,54,49,0.16); }\n' +
      prefix + '-btn:active { transform:translateY(0); }\n' +
      prefix + '-btn:disabled { opacity:0.5; cursor:not-allowed; transform:none; box-shadow:none; }\n' +
      prefix + '-spinner { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:48px 24px; }\n' +
      prefix + '-spinner-ring { width:48px; height:48px; border:4px solid ' + BRAND.border + '; border-top-color:' + BRAND.primary + '; border-radius:50%; animation:' + prefix.slice(1) + '-spin 0.8s linear infinite; }\n' +
      prefix + '-spinner-text { margin-top:16px; color:' + BRAND.muted + '; font-size:0.85rem; }\n' +
      '@keyframes ' + prefix.slice(1) + '-spin { to { transform:rotate(360deg); } }\n' +
      prefix + '-result { padding:24px; }\n' +
      prefix + '-result-name { font-size:1.2rem; font-weight:700; color:' + BRAND.text + '; text-align:center; margin-bottom:20px; }\n' +
      prefix + '-result-name span { color:' + BRAND.light + '; }\n' +
      prefix + '-type-badge { text-align:center; margin-bottom:20px; }\n' +
      prefix + '-type-icon { font-size:2.2rem; margin-bottom:4px; }\n' +
      prefix + '-type-label { display:inline-block; padding:6px 20px; background:' + BRAND.gradient + '; color:#FAF7F0; border-radius:20px; font-size:0.95rem; font-weight:700; }\n' +
      prefix + '-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:20px; }\n' +
      prefix + '-stat { background:rgba(253,251,247,0.74); border:1px solid ' + BRAND.border + '; border-radius:12px; padding:14px; text-align:center; }\n' +
      prefix + '-stat-label { font-size:0.7rem; text-transform:uppercase; letter-spacing:0.06em; color:' + BRAND.dim + '; margin-bottom:4px; }\n' +
      prefix + '-stat-value { font-size:0.92rem; font-weight:600; color:' + BRAND.text + '; }\n' +
      prefix + '-centers { margin-bottom:20px; }\n' +
      prefix + '-centers h4 { font-size:0.78rem; text-transform:uppercase; letter-spacing:0.06em; color:' + BRAND.primary + '; margin-bottom:10px; }\n' +
      prefix + '-center-badges { display:flex; flex-wrap:wrap; gap:8px; }\n' +
      prefix + '-center-badge { display:inline-flex; align-items:center; gap:6px; padding:5px 12px; background:rgba(95,114,97,0.10); border:1px solid rgba(95,114,97,0.20); border-radius:20px; font-size:0.8rem; color:' + BRAND.light + '; }\n' +
      prefix + '-signature { background:rgba(95,114,97,0.10); border:1px solid rgba(95,114,97,0.20); border-radius:14px; padding:18px; text-align:center; margin-bottom:20px; }\n' +
      prefix + '-signature-label { font-size:0.72rem; text-transform:uppercase; letter-spacing:0.07em; color:' + BRAND.accent + '; margin-bottom:4px; }\n' +
      prefix + '-signature-value { font-size:1rem; font-weight:700; color:' + BRAND.light + '; }\n' +
      prefix + '-signature-desc { font-size:0.78rem; color:' + BRAND.muted + '; margin-top:4px; }\n' +
      prefix + '-cta { text-align:center; padding:0 24px 24px; }\n' +
      prefix + '-cta-link { display:inline-block; padding:12px 28px; background:transparent; border:2px solid ' + BRAND.accent + '; color:' + BRAND.light + '; border-radius:12px; font-size:0.88rem; font-weight:600; text-decoration:none; transition:all 0.2s; }\n' +
      prefix + '-cta-link:hover { background:rgba(95,114,97,0.12); border-color:' + BRAND.light + '; }\n' +
      prefix + '-daily-work { margin:0 24px 20px; padding:18px; border:1px solid ' + BRAND.border + '; border-radius:14px; background:rgba(95,114,97,0.08); }\n' +
      prefix + '-daily-work h4 { color:' + BRAND.primary + '; font-size:0.92rem; margin-bottom:8px; }\n' +
      prefix + '-daily-work p { color:' + BRAND.muted + '; font-size:0.82rem; line-height:1.45; margin-bottom:12px; }\n' +
      prefix + '-practice-actions { display:flex; gap:10px; flex-wrap:wrap; }\n' +
      prefix + '-practice-btn { flex:1 1 120px; padding:10px 12px; border:1px solid ' + BRAND.accent + '; border-radius:10px; background:#FDFBF7; color:' + BRAND.light + '; cursor:pointer; font-size:0.78rem; font-weight:700; }\n' +
      prefix + '-practice-btn:hover { background:rgba(95,114,97,0.12); }\n' +
      prefix + '-error { padding:32px 24px; text-align:center; color:' + BRAND.error + '; }\n' +
      prefix + '-error-title { font-size:1rem; font-weight:600; margin-bottom:8px; }\n' +
      prefix + '-error-msg { font-size:0.82rem; color:' + BRAND.muted + '; margin-bottom:16px; }\n' +
      prefix + '-reset-btn { padding:10px 24px; background:#FDFBF7; border:1px solid ' + BRAND.border + '; color:' + BRAND.muted + '; border-radius:10px; cursor:pointer; font-size:0.82rem; }\n' +
      prefix + '-reset-btn:hover { color:' + BRAND.text + '; border-color:' + BRAND.dim + '; }\n' +
      prefix + '-powered { text-align:center; padding:0 24px 16px; font-size:0.7rem; color:' + BRAND.dim + '; }\n' +
      prefix + '-powered a { color:' + BRAND.light + '; text-decoration:none; }\n' +
      '@media (max-width:400px) { ' + prefix + '-grid { grid-template-columns:1fr; } ' + prefix + '-form-row { flex-direction:column; gap:0; } }\n';
    var style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
  }

  // ── Widget Class ────────────────────────────────────────────────────────
  function Widget(container, options) {
    this.container = container;
    this.options = options || {};
    this.apiUrl = this.options.apiUrl || this.container.getAttribute('data-api') || DEFAULT_API;
    // strip trailing slash
    if (this.apiUrl.slice(-1) === '/') this.apiUrl = this.apiUrl.slice(0, -1);
    this.idx = ++Widget._counter;
    this.prefix = '.hde-w-' + this.idx;
    this._injectCSS();
    this._renderForm();
  }

  Widget._counter = 0;

  Widget.prototype._injectCSS = function () {
    injectCSS(this.prefix);
  };

  // ── Form ────────────────────────────────────────────────────────────────
  Widget.prototype._renderForm = function () {
    var c = this.container;
    c.innerHTML = '';
    var card = el('div', this.prefix.slice(1) + '-card');
    card.innerHTML =
      '<div class="' + this.prefix.slice(1) + '-header">' +
        '<h2>Free Human Design Chart</h2>' +
        '<p>Discover your Type, Strategy &amp; Authority</p>' +
      '</div>' +
      '<form class="' + this.prefix.slice(1) + '-body" novalidate></form>' +
      '<div class="' + this.prefix.slice(1) + '-powered">Powered by <a href="https://humandesignengine.com" target="_blank" rel="noopener">Human Design Engine</a></div>';
    c.appendChild(card);

    var form = c.querySelector('form');
    var self = this;

    // Name
    var g1 = el('div', this.prefix.slice(1) + '-form-group');
    g1.innerHTML = '<label for="hde-name">Your Name</label><input id="hde-name" type="text" name="name" placeholder="e.g. Jane Doe" maxlength="100" required>';
    form.appendChild(g1);

    // Birth date
    var g2 = el('div', this.prefix.slice(1) + '-form-group');
    g2.innerHTML = '<label for="hde-birthdate">Birth Date</label><input id="hde-birthdate" type="date" name="birthdate" required>';
    form.appendChild(g2);

    // Birth time + location row
    var row = el('div', this.prefix.slice(1) + '-form-row');
    var g3 = el('div', this.prefix.slice(1) + '-form-group');
    g3.innerHTML = '<label for="hde-birthtime">Birth Time</label><input id="hde-birthtime" type="time" name="birthtime" required>';
    row.appendChild(g3);

    var g4 = el('div', this.prefix.slice(1) + '-form-group');
    g4.innerHTML = '<label for="hde-location">Location <span style="font-weight:400;font-size:0.7rem;color:' + BRAND.dim + '">(optional)</span></label><input id="hde-location" type="text" name="location" placeholder="e.g. New York, USA" maxlength="200">';
    row.appendChild(g4);
    form.appendChild(row);

    // Submit
    var btn = el('button', this.prefix.slice(1) + '-btn', 'Calculate My Chart');
    btn.type = 'submit';
    form.appendChild(btn);

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = Object.fromEntries(new FormData(form));
      if (!data.name.trim() || !data.birthdate || !data.birthtime) {
        self._shake(form);
        return;
      }
      data.name = data.name.trim();
      self._compute(data);
    });
  };

  Widget.prototype._shake = function (el) {
    el.style.animation = 'none';
    el.offsetHeight;
    el.style.animation = 'hde-shake 0.4s ease';
  };

  // Inject shake keyframe
  (function onceShake() {
    if (document.getElementById('hde-shake-kf')) return;
    var s = document.createElement('style');
    s.id = 'hde-shake-kf';
    s.textContent = '@keyframes hde-shake { 0%,100% { transform:translateX(0); } 25% { transform:translateX(-6px); } 50% { transform:translateX(6px); } 75% { transform:translateX(-4px); } }';
    document.head.appendChild(s);
  })();

  // ── Loading ─────────────────────────────────────────────────────────────
  Widget.prototype._showLoading = function () {
    var card = this.container.querySelector('.' + this.prefix.slice(1) + '-card');
    var body = card.querySelector('.' + this.prefix.slice(1) + '-body');
    var footer = card.querySelector('.' + this.prefix.slice(1) + '-powered');
    if (body) body.style.display = 'none';
    if (footer) footer.style.display = 'none';

    // Remove any existing result/error
    var old = card.querySelector('.' + this.prefix.slice(1) + '-spinner');
    if (old) old.remove();
    old = card.querySelector('.' + this.prefix.slice(1) + '-result');
    if (old) old.remove();
    old = card.querySelector('.' + this.prefix.slice(1) + '-cta');
    if (old) old.remove();
    old = card.querySelector('.' + this.prefix.slice(1) + '-error');
    if (old) old.remove();

    var spinner = el('div', this.prefix.slice(1) + '-spinner');
    spinner.innerHTML =
      '<div class="' + this.prefix.slice(1) + '-spinner-ring"></div>' +
      '<div class="' + this.prefix.slice(1) + '-spinner-text">Computing your chart&hellip;</div>';
    card.appendChild(spinner);
  };

  // ── API call ────────────────────────────────────────────────────────────
  Widget.prototype._compute = function (formData) {
    this._showLoading();
    var self = this;

    // Parse date/time
    var d = formData.birthdate.split('-');
    var t = formData.birthtime.split(':');
    var year = parseInt(d[0], 10);
    var month = parseInt(d[1], 10);
    var day = parseInt(d[2], 10);
    var hour = parseInt(t[0], 10);
    var minute = parseInt(t[1], 10) || 0;

    var payload = {
      name: formData.name,
      year: year,
      month: month,
      day: day,
      hour: hour,
      minute: minute,
      lat: 0,
      lon: 0,
      timezone: 'UTC',
    };

    if (formData.location && formData.location.trim()) {
      payload.location = formData.location.trim();
    }

    var endpoint = this.apiUrl + '/api/public/compute-chart';

    var xhr = new XMLHttpRequest();
    xhr.open('POST', endpoint, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.timeout = 15000;

    xhr.onload = function () {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          var resp = JSON.parse(xhr.responseText);
          if (resp.success && resp.data) {
            self._renderResult(resp.data);
            trackEvent('hde_chart_generated', {
              chart_type: resp.data.hd_type || 'Unknown',
              authority: resp.data.authority || 'Unknown',
              profile: resp.data.profile || 'Unknown',
              defined_centers_count: (resp.data.defined_centers || []).length
            });
           hdeDispatchGa4('hde_chart_generated', { chart_type: params.chart_type, authority: params.authority, profile: params.profile, defined_centers_count: params.defined_centers_count });;
hdeDispatchGa4('hde_chart_generated', {
              chart_type: resp.data.hd_type || 'Unknown',
              authority: resp.data.authority || 'Unknown',
              profile: resp.data.profile || 'Unknown',
              defined_centers_count: (resp.data.defined_centers || []).length
            });
            return;
          }
          self._renderError((resp.error || 'Unknown error from server'));
        } catch (e) {
          self._renderError('Invalid response from server');
        }
      } else {
        self._renderError('Server error (' + xhr.status + '). Please try again.');
      }
    };

    xhr.onerror = function () {
      self._renderError('Network error. Check your connection and try again.');
    };

    xhr.ontimeout = function () {
      self._renderError('Request timed out. Please try again.');
    };

    xhr.send(JSON.stringify(payload));
  };

  // ── Result rendering ────────────────────────────────────────────────────
  Widget.prototype._renderResult = function (data) {
    var card = this.container.querySelector('.' + this.prefix.slice(1) + '-card');
    // Remove spinner, form, footer
    var kids = card.querySelectorAll('.' + this.prefix.slice(1) + '-spinner, .' + this.prefix.slice(1) + '-body, .' + this.prefix.slice(1) + '-powered, .' + this.prefix.slice(1) + '-error, .' + this.prefix.slice(1) + '-cta');
    kids.forEach(function (k) { k.remove(); });

    var typeName = (data.hd_type || 'Unknown').toLowerCase();
    var ti = TYPE_INFO[typeName] || { icon: '✨', desc: 'Your unique Human Design is ready to explore.' };
    var centers = data.defined_centers || [];

    var result = el('div', this.prefix.slice(1) + '-result');
    var prefix = this.prefix;

    var html = '';

    // Name
    html += '<div class="' + this.prefix.slice(1) + '-result-name">Hi <span>' + escHtml(data.name || 'Friend') + '</span> 👋</div>';

    // Type badge
    html += '<div class="' + this.prefix.slice(1) + '-type-badge">';
    html += '<div class="' + this.prefix.slice(1) + '-type-icon">' + ti.icon + '</div>';
    html += '<div class="' + this.prefix.slice(1) + '-type-label">' + escHtml(data.hd_type || 'Unknown') + '</div>';
    html += '</div>';

    // Stats grid
    html += '<div class="' + this.prefix.slice(1) + '-grid">';
    html += statCard('Profile', data.profile || '—');
    html += statCard('Authority', data.authority || '—');
    html += statCard('Strategy', data.strategy || '—');
    html += statCard('Definition', data.definition || '—');
    html += '</div>';

    // Defined centers
    if (centers.length) {
      html += '<div class="' + this.prefix.slice(1) + '-centers">';
      html += '<h4>Defined Centers (' + centers.length + ')</h4>';
      html += '<div class="' + this.prefix.slice(1) + '-center-badges">';
      centers.forEach(function (c) {
        var icon = CENTER_ICONS[c] || '🔹';
        html += '<span class="' + this.prefix.slice(1) + '-center-badge">' + icon + ' ' + escHtml(c) + '</span>';
      }, this);
      html += '</div></div>';
    }

    // Signature
    if (data.signature) {
      html += '<div class="' + this.prefix.slice(1) + '-signature">';
      html += '<div class="' + this.prefix.slice(1) + '-signature-label">Your Signature</div>';
      html += '<div class="' + this.prefix.slice(1) + '-signature-value">' + escHtml(data.signature) + '</div>';
      if (data.not_self_theme) {
        html += '<div class="' + this.prefix.slice(1) + '-signature-desc">Not-self theme: ' + escHtml(data.not_self_theme) + '</div>';
      }
      html += '</div>';
    }

    result.innerHTML = html;
    card.appendChild(result);

    // Daily work prompt
    var dailyWork = el('div', this.prefix.slice(1) + '-daily-work');
    dailyWork.innerHTML =
      '<h4>Today&rsquo;s embodied experiment</h4>' +
      '<p>Notice where your Strategy can become one concrete nervous-system practice today. Start with one slow breath before making the next decision.</p>' +
      '<div class="' + this.prefix.slice(1) + '-practice-actions">' +
        '<button type="button" class="' + this.prefix.slice(1) + '-practice-btn" data-hde-practice="start">Start practice</button>' +
        '<button type="button" class="' + this.prefix.slice(1) + '-practice-btn" data-hde-practice="complete">Mark complete</button>' +
      '</div>';
    card.appendChild(dailyWork);
    trackEvent('hde_transit_prompt_viewed', { prompt_source: 'free_reading_result' });;
hdeDispatchGa4('hde_transit_prompt_viewed', { prompt_source: 'free_reading_result' });
    dailyWork.addEventListener('click', function (e) {
      var target = e.target && e.target.closest ? e.target.closest('[data-hde-practice]') : null;
      if (!target) return;
      var action = target.getAttribute('data-hde-practice');
      var hdePracticeName = action === 'complete' ? 'hde_nervous_system_practice_completed' : 'hde_nervous_system_practice_started'; trackEvent(hdePracticeName, { practice_source: 'free_reading_result' }); hdeDispatchGa4(hdePracticeName, { practice_source: 'free_reading_result' });
    });

    // CTA
    var cta = el('div', this.prefix.slice(1) + '-cta');
    var reportUrl = this.options.reportUrl || 'buy-report.html';
    cta.innerHTML = '<a class="' + this.prefix.slice(1) + '-cta-link" href="' + reportUrl + '" target="_blank" rel="noopener">Want your full report?<br><small>Get the complete PDF →</small></a>';
    var ctaLink = cta.querySelector('a');
    if (ctaLink) {
      ctaLink.addEventListener('click', function () {
        trackEvent('hde_daily_work_cta_clicked', { cta_target: reportUrl, cta_source: 'free_reading_result' });
      });
    }
    card.appendChild(cta);

    // Powered by
    var pw = el('div', this.prefix.slice(1) + '-powered');
    pw.innerHTML = 'Powered by <a href="https://humandesignengine.com" target="_blank" rel="noopener">Human Design Engine</a>';
    card.appendChild(pw);

    function statCard(label, value) {
      return '<div class="' + prefix.slice(1) + '-stat">' +
        '<div class="' + prefix.slice(1) + '-stat-label">' + label + '</div>' +
        '<div class="' + prefix.slice(1) + '-stat-value">' + escHtml(value) + '</div>' +
        '</div>';
    }

    function escHtml(s) {
      if (!s) return '';
      return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
  };

  // ── Error rendering ─────────────────────────────────────────────────────
  Widget.prototype._renderError = function (msg) {
    var card = this.container.querySelector('.' + this.prefix.slice(1) + '-card');
    var kids = card.querySelectorAll('.' + this.prefix.slice(1) + '-spinner, .' + this.prefix.slice(1) + '-body, .' + this.prefix.slice(1) + '-powered, .' + this.prefix.slice(1) + '-result, .' + this.prefix.slice(1) + '-cta');
    kids.forEach(function (k) { k.remove(); });

    var err = el('div', this.prefix.slice(1) + '-error');
    err.innerHTML =
      '<div class="' + this.prefix.slice(1) + '-error-title">⚠️ Oops!</div>' +
      '<div class="' + this.prefix.slice(1) + '-error-msg">' + msg + '</div>' +
      '<button class="' + this.prefix.slice(1) + '-reset-btn">Try Again</button>';
    card.appendChild(err);

    var self = this;
    err.querySelector('button').addEventListener('click', function () {
      self._renderForm();
    });
  };

  // ── Public API ──────────────────────────────────────────────────────────
  function init(selector, options) {
    var containers;
    if (typeof selector === 'string') {
      containers = document.querySelectorAll(selector);
    } else if (selector && selector.nodeType) {
      containers = [selector];
    } else {
      containers = [];
    }
    var widgets = [];
    containers.forEach(function (c) {
      widgets.push(new Widget(c, options));
    });
    return widgets;
  }

  // ── Auto-discovery ──────────────────────────────────────────────────────
  function autoInit() {
    var els = document.querySelectorAll('.hde-chart-widget');
    els.forEach(function (c) {
      if (!c._hde_widget) {
        c._hde_widget = new Widget(c);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoInit);
  } else {
    autoInit();
  }

  // ── Expose global ───────────────────────────────────────────────────────
  window.HDEWidget = { init: init, Widget: Widget, trackEvent: trackEvent };

})();
