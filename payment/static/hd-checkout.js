/**
 * <hd-checkout> Web Component
 * Self-contained, themeable payment component for HDE + Beyondsaas
 * Mode: inline | modal
 */
class HdCheckout extends HTMLElement {
  static get observedAttributes() {
    return ['mode', 'product', 'api-url', 'debug', 'poster-image-url', 'print-file-url', 'mockup-url'];
  }

  constructor() {
    super();
    this._shadow = this.attachShadow({ mode: 'open' });
    this._state = 'idle'; // idle | loading | error
    this._error = null;
    this._values = {};
    this._debug = false;
    this._previouslyFocusedElement = null;
  }

  connectedCallback() {
    this._debug = this.hasAttribute('debug');
    this._render();
    this._bind();
    this._loadFont();
  }

  attributeChangedCallback(name, old, val) {
    if (old === val) return;
    if (name === 'debug') { this._debug = this.hasAttribute('debug'); return; }
    if (!this.isConnected) return;
    this._render();
    this._bind();
    this._loadFont();
  }

  _loadFont() {
    const family = getComputedStyle(this).getPropertyValue('--hd-font-family').trim();
    if (family && !family.includes('-apple-system') && !family.includes('sans-serif') && !family.includes('Inter')) {
      const match = family.match(/['"]?([a-zA-Z0-9\s]+)['"]?/);
      if (match) {
        const fontName = match[1].trim();
        const linkId = `hd-font-${fontName.replace(/\s+/g, '-').toLowerCase()}`;
        if (!document.getElementById(linkId)) {
          const link = document.createElement('link');
          link.id = linkId;
          link.rel = 'stylesheet';
          link.href = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(fontName)}:wght@400;500;600;700&display=swap`;
          document.head.appendChild(link);
        }
      }
    }
  }

  // ── Public API ──────────────────────────────────────────────

  openModal() {
    const overlay = this._shadow.querySelector('.modal-overlay');
    if (overlay) {
      this._previouslyFocusedElement = document.activeElement || this._shadow.activeElement;
      overlay.removeAttribute('hidden');
      this._trapFocus();
      document.body.style.overflow = 'hidden';
    }
  }

  closeModal() {
    const overlay = this._shadow.querySelector('.modal-overlay');
    if (overlay) {
      overlay.setAttribute('hidden', '');
      document.body.style.overflow = '';
      if (this._previouslyFocusedElement && typeof this._previouslyFocusedElement.focus === 'function') {
        this._previouslyFocusedElement.focus();
      }
    }
  }

  // ── Internal ────────────────────────────────────────────────

  get _mode() {
    return this.getAttribute('mode') || 'inline';
  }

  get _product() {
    return this.getAttribute('product') || 'natal';
  }

  get _apiUrl() {
    return this.getAttribute('api-url') || '';
  }

  get _isPosterProduct() {
    return ['poster', 'print-poster', 'poster-print'].includes(this._product);
  }

  get _posterImageUrl() {
    return this.getAttribute('poster-image-url') || this.getAttribute('mockup-url') || '';
  }

  get _printFileUrl() {
    return this.getAttribute('print-file-url') || this._posterImageUrl;
  }

  get _productData() {
    const map = {
      natal:    { name: 'Natal Report',           price: 19, priceId: 'price_1TjZKVKfvDG04zCAZkiCFrnL', requiresBirthData: true },
      synastry: { name: 'Synastry Report',        price: 29, priceId: 'price_1TjZKXKfvDG04zCAZjq1c8hZ', requiresBirthData: true },
      transit:  { name: 'Transit Report',          price: 29, priceId: 'price_1TjZKYKfvDG04zCAdAZVIJXw', requiresBirthData: true },
      bundle:   { name: 'Full Bundle',            price: 59, priceId: 'price_1TjZKZKfvDG04zCAPKttOFgK', requiresBirthData: true },
      "belief-standard": {
        name: "Standard Deconditioning Workbook",
        description: "300–500 belief pairs, PDF delivered via email",
        price: 19,
        priceId: "price_1TjeSgKfvDG04zCAk7b36taY",
        requiresBirthData: false
      },
      "belief-comprehensive": {
        name: "Comprehensive Deconditioning Workbook",
        description: "800–1,200+ belief pairs, full PDF delivered via email",
        price: 29,
        priceId: "price_1TjeSkKfvDG04zCA18ZU5S1a",
        requiresBirthData: false
      },
      "unchained-digital": {
        name: "Unchained Wholeness Digital",
        description: "Full 8-week personalized deconditioning program",
        price: 997,
        priceId: "price_1TjeZIKfvDG04zCAQEYgJnJB",
        requiresBirthData: false
      },
      "unchained-retreat": {
        name: "Unchained Wholeness + Hawaii Retreat",
        description: "Full program + all-inclusive 5-day Hawaii retreat",
        price: 5997,
        priceId: "price_1TjeZLKfvDG04zCAspTyCRZd",
        requiresBirthData: false
      },
      poster: {
        name: "Premium Matte Poster",
        description: "Premium matte Human Design poster printed and shipped by Printful",
        price: 59,
        sizes: { '12x18': 39, '18x24': 59, '24x36': 79 },
        requiresBirthData: true
      }
    };
    return map[this._product] || (this._isPosterProduct ? map.poster : map.natal);
  }

  _log(...args) {
    if (this._debug) console.log('[hd-checkout]', ...args);
  }

  // ── Render ──────────────────────────────────────────────────

  _render() {
    const mode = this._mode;
    this._shadow.innerHTML = `
      <style>${this._css()}</style>
      ${mode === 'inline' ? this._inlineTemplate() : this._modalTemplate()}
    `;
    this._restoreValues();
  }

  _css() {
    return `
      :host {
        display: block;
        font-family: var(--hd-font-family, 'Inter', -apple-system, sans-serif);
        font-size: var(--hd-font-size-base, 16px);
        color: var(--hd-color-text, #1a202c);
        --hd-color-primary: var(--hd-color-primary, #0d7377);
        --hd-color-primary-hover: var(--hd-color-primary-hover, #0a5c5f);
        --hd-color-bg: var(--hd-color-bg, #ffffff);
        --hd-color-surface: var(--hd-color-surface, #f7fafc);
        --hd-color-border: var(--hd-color-border, #e2e8f0);
        --hd-color-text: var(--hd-color-text, #1a202c);
        --hd-color-text-muted: var(--hd-color-text-muted, #718096);
        --hd-font-family: var(--hd-font-family, 'Inter', -apple-system, sans-serif);
        --hd-font-size-sm: var(--hd-font-size-sm, 14px);
        --hd-font-size-lg: var(--hd-font-size-lg, 18px);
        --hd-font-size-xl: var(--hd-font-size-xl, 22px);
        --hd-space-sm: var(--hd-space-sm, 8px);
        --hd-space-md: var(--hd-space-md, 16px);
        --hd-space-lg: var(--hd-space-lg, 24px);
        --hd-space-xl: var(--hd-space-xl, 32px);
        --hd-radius-sm: var(--hd-radius-sm, 6px);
        --hd-radius-md: var(--hd-radius-md, 10px);
        --hd-radius-lg: var(--hd-radius-lg, 16px);
        --hd-shadow-md: var(--hd-shadow-md, 0 4px 12px rgba(0,0,0,0.10));
        --hd-transition: var(--hd-transition, 150ms ease);
      }

      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

      /* ── Form Card ── */
      .checkout-card {
        background: var(--hd-color-bg);
        border: 1px solid var(--hd-color-border);
        border-radius: var(--hd-radius-lg);
        padding: var(--hd-space-xl, 32px);
        box-shadow: var(--hd-shadow-md);
        max-width: 520px;
        width: 100%;
      }

      .checkout-card h3 {
        font-size: var(--hd-font-size-xl, 22px);
        font-weight: 600;
        margin-bottom: var(--hd-space-sm, 8px);
        color: var(--hd-color-text);
      }

      .product-label {
        font-size: var(--hd-font-size-sm, 14px);
        color: var(--hd-color-text-muted);
        margin-bottom: var(--hd-space-lg, 24px);
      }

      .product-label strong {
        color: var(--hd-color-primary);
        font-size: var(--hd-font-size-lg, 18px);
      }

      /* ── Form Grid ── */
      .form-grid {
        display: grid;
        gap: var(--hd-space-md, 16px);
      }

      .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--hd-space-md, 16px);
      }

      .form-group {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }

      label {
        font-size: var(--hd-font-size-sm, 14px);
        font-weight: 500;
        color: var(--hd-color-text);
      }

      label .req { color: #e53e3e; margin-left: 2px; }

      input, select {
        padding: 10px 14px;
        border: 1px solid var(--hd-checkout-input-border, var(--hd-color-border));
        border-radius: var(--hd-radius-sm);
        font-size: var(--hd-font-size-base, 16px);
        font-family: inherit;
        background: var(--hd-checkout-input-bg, var(--hd-color-bg));
        color: var(--hd-checkout-input-text, var(--hd-color-text));
        transition: border-color var(--hd-transition), box-shadow var(--hd-transition);
        width: 100%;
      }

      input:focus, select:focus {
        outline: none;
        border-color: var(--hd-color-primary);
        box-shadow: 0 0 0 3px color-mix(in srgb, var(--hd-color-primary) 15%, transparent);
      }

      input[aria-invalid="true"], select[aria-invalid="true"] {
        border-color: #e53e3e;
      }

      .field-error {
        font-size: 12px;
        color: #e53e3e;
        min-height: 16px;
      }

      input::placeholder { color: var(--hd-checkout-input-placeholder, var(--hd-color-text-muted)); }

      /* ── Tax Notice ── */
      .tax-notice {
        display: none;
        background: #fffbeb;
        border: 1px solid #f6e05e;
        border-radius: var(--hd-radius-sm);
        padding: var(--hd-space-sm, 8px) var(--hd-space-md, 16px);
        font-size: var(--hd-font-size-sm, 14px);
        color: #744210;
        align-items: center;
        gap: var(--hd-space-sm, 8px);
      }

      .tax-notice.show { display: flex; }
      .tax-notice svg { flex-shrink: 0; }

      /* ── Poster Preview ── */
      .poster-preview {
        display: grid;
        grid-template-columns: 120px 1fr;
        gap: var(--hd-space-md, 16px);
        align-items: center;
        border: 1px solid var(--hd-color-border);
        border-radius: var(--hd-radius-md);
        padding: var(--hd-space-md, 16px);
        background: var(--hd-color-surface);
      }

      .poster-preview img {
        width: 120px;
        aspect-ratio: 2 / 3;
        object-fit: cover;
        border-radius: var(--hd-radius-sm);
        box-shadow: var(--hd-shadow-md);
        background: #fff;
      }

      .poster-preview p {
        color: var(--hd-color-text-muted);
        font-size: var(--hd-font-size-sm, 14px);
        line-height: 1.45;
      }

      /* ── Submit Button ── */
      .btn-submit {
        width: 100%;
        padding: 14px 24px;
        background: var(--hd-color-primary);
        color: #fff;
        border: none;
        border-radius: var(--hd-radius-md);
        font-size: var(--hd-font-size-lg, 18px);
        font-weight: 600;
        font-family: inherit;
        cursor: pointer;
        transition: background var(--hd-transition), transform 80ms;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--hd-space-sm, 8px);
        margin-top: var(--hd-space-md, 16px);
      }

      .btn-submit:hover:not(:disabled) { background: var(--hd-color-primary-hover); }
      .btn-submit:active:not(:disabled) { transform: scale(0.99); }
      .btn-submit:disabled { opacity: 0.65; cursor: not-allowed; }

      .spinner {
        width: 18px; height: 18px;
        border: 2.5px solid color-mix(in srgb, currentColor 35%, transparent);
        border-top-color: currentColor;
        border-radius: 50%;
        animation: hd-spin 0.65s linear infinite;
        display: none;
      }
      .btn-submit.loading .spinner { display: block; }
      .btn-submit.loading .btn-text { display: none; }

      @keyframes hd-spin { to { transform: rotate(360deg); } }

      /* ── Error Banner ── */
      .error-banner {
        display: none;
        background: #fff5f5;
        border: 1px solid #feb2b2;
        border-radius: var(--hd-radius-sm);
        padding: var(--hd-space-md, 16px);
        color: #c53030;
        font-size: var(--hd-font-size-sm, 14px);
        margin-bottom: var(--hd-space-md, 16px);
      }
      .error-banner.show { display: block; }

      /* ── Divider ── */
      .stripe-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--hd-space-sm, 8px);
        margin-top: var(--hd-space-md, 16px);
        font-size: 12px;
        color: var(--hd-color-text-muted);
      }

      /* ── Modal Overlay ── */
      .modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.55);
        backdrop-filter: blur(3px);
        z-index: 9998;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: var(--hd-space-md, 16px);
        opacity: 1;
        visibility: visible;
        transition: opacity var(--hd-transition), visibility var(--hd-transition);
      }

      .modal-overlay[hidden] {
        opacity: 0;
        visibility: hidden;
        pointer-events: none;
      }

      .modal-card {
        background: var(--hd-color-bg);
        border-radius: var(--hd-radius-lg);
        padding: var(--hd-space-xl, 32px);
        max-width: 520px;
        width: 100%;
        max-height: 90vh;
        overflow-y: auto;
        position: relative;
        box-shadow: 0 20px 60px rgba(0,0,0,0.2);
      }

      .modal-close {
        position: absolute;
        top: var(--hd-space-md, 16px);
        right: var(--hd-space-md, 16px);
        background: none;
        border: none;
        cursor: pointer;
        color: var(--hd-color-text-muted);
        padding: 4px;
        border-radius: var(--hd-radius-sm);
        font-size: 20px;
        line-height: 1;
        transition: color var(--hd-transition);
      }
      .modal-close:hover { color: var(--hd-color-text); }

      /* ── Inline adjustments ── */
      :host([mode="inline"]) .checkout-card {
        box-shadow: none;
        border: none;
        padding: 0;
        max-width: 100%;
      }

      /* ── Responsive ── */
      @media (max-width: 520px) {
        .form-row { grid-template-columns: 1fr; }
        .checkout-card, .modal-card { padding: var(--hd-space-lg, 24px); }
        .poster-preview { grid-template-columns: 1fr; }
      }
    `;
  }

  _inlineTemplate() {
    return `<div class="checkout-card">${this._formHTML()}</div>`;
  }

  _modalTemplate() {
    return `
      <slot name="trigger">
        <button class="modal-trigger-btn" type="button">Book Now</button>
      </slot>
      <div class="modal-overlay" hidden>
        <div class="modal-card" role="dialog" aria-modal="true" aria-label="Checkout">
          <button class="modal-close" type="button" aria-label="Close checkout">×</button>
          ${this._formHTML()}
        </div>
      </div>
    `;
  }

  _formHTML() {
    const p = this._productData;
    const posterPreview = this._isPosterProduct ? `
          <div class="poster-preview">
            ${this._posterImageUrl ? `<img src="${this._posterImageUrl}" alt="Poster mockup preview">` : '<div aria-hidden="true"></div>'}
            <div>
              <div class="form-group">
                <label for="hd-poster-size">Poster Size <span class="req" aria-hidden="true">*</span></label>
                <select id="hd-poster-size" name="poster_size" required aria-required="true" aria-describedby="hd-poster-size-error">
                  <option value="12x18">12×18 — $39</option>
                  <option value="18x24" selected>18×24 — $59</option>
                  <option value="24x36">24×36 — $79</option>
                </select>
                <span class="field-error" id="hd-poster-size-error" aria-live="polite"></span>
              </div>
              <p>Printed on premium matte paper and shipped directly by Printful after Stripe checkout.</p>
            </div>
          </div>
    ` : '';
    return `
      <h3>Checkout</h3>
      <p class="product-label"><strong>$${p.price}</strong> — ${p.name}</p>

      <div class="error-banner" role="alert"></div>

      <form novalidate>
        <div class="form-grid">
          <!-- Name + Email -->
          <div class="form-row">
            <div class="form-group">
              <label for="hd-name">Full Name <span class="req" aria-hidden="true">*</span></label>
              <input type="text" id="hd-name" name="name" autocomplete="name" required minlength="2" aria-required="true" placeholder="Jane Doe" aria-describedby="hd-name-error">
              <span class="field-error" id="hd-name-error" aria-live="polite"></span>
            </div>
            <div class="form-group">
              <label for="hd-email">Email <span class="req" aria-hidden="true">*</span></label>
              <input type="email" id="hd-email" name="email" autocomplete="email" required aria-required="true" placeholder="jane@example.com" aria-describedby="hd-email-error">
              <span class="field-error" id="hd-email-error" aria-live="polite"></span>
            </div>
          </div>

          ${posterPreview}

          <!-- Birth Date + Time + City (only if required) -->
          ${p.requiresBirthData ? `
          <div class="form-row">
            <div class="form-group">
              <label for="hd-birth-date">Birth Date <span class="req" aria-hidden="true">*</span></label>
              <input type="date" id="hd-birth-date" name="birth_date" required aria-required="true" aria-describedby="hd-birth-date-error">
              <span class="field-error" id="hd-birth-date-error" aria-live="polite"></span>
            </div>
            <div class="form-group">
              <label for="hd-birth-time">Birth Time <span class="req" aria-hidden="true">*</span></label>
              <input type="time" id="hd-birth-time" name="birth_time" required aria-required="true" placeholder="HH:MM" aria-describedby="hd-birth-time-error">
              <span class="field-error" id="hd-birth-time-error" aria-live="polite"></span>
            </div>
          </div>

          <!-- Birth City -->
          <div class="form-group">
            <label for="hd-birth-city">Birth City <span class="req" aria-hidden="true">*</span></label>
            <input type="text" id="hd-birth-city" name="birth_city" required aria-required="true" autocomplete="address-level2" placeholder="Honolulu, HI" aria-describedby="hd-birth-city-error">
            <span class="field-error" id="hd-birth-city-error" aria-live="polite"></span>
          </div>
          ` : ''}

          <!-- State + Tax Notice -->
          <div class="form-group">
            <label for="hd-state">US State <span class="req" aria-hidden="true">*</span></label>
            <select id="hd-state" name="state" required aria-required="true" aria-describedby="hd-state-error">
              <option value="">Select state...</option>
              <option value="AL">Alabama</option>
              <option value="AK">Alaska</option>
              <option value="AZ">Arizona</option>
              <option value="AR">Arkansas</option>
              <option value="CA">California</option>
              <option value="CO">Colorado</option>
              <option value="CT">Connecticut</option>
              <option value="DE">Delaware</option>
              <option value="FL">Florida</option>
              <option value="GA">Georgia</option>
              <option value="HI">Hawaii</option>
              <option value="ID">Idaho</option>
              <option value="IL">Illinois</option>
              <option value="IN">Indiana</option>
              <option value="IA">Iowa</option>
              <option value="KS">Kansas</option>
              <option value="KY">Kentucky</option>
              <option value="LA">Louisiana</option>
              <option value="ME">Maine</option>
              <option value="MD">Maryland</option>
              <option value="MA">Massachusetts</option>
              <option value="MI">Michigan</option>
              <option value="MN">Minnesota</option>
              <option value="MS">Mississippi</option>
              <option value="MO">Missouri</option>
              <option value="MT">Montana</option>
              <option value="NE">Nebraska</option>
              <option value="NV">Nevada</option>
              <option value="NH">New Hampshire</option>
              <option value="NJ">New Jersey</option>
              <option value="NM">New Mexico</option>
              <option value="NY">New York</option>
              <option value="NC">North Carolina</option>
              <option value="ND">North Dakota</option>
              <option value="OH">Ohio</option>
              <option value="OK">Oklahoma</option>
              <option value="OR">Oregon</option>
              <option value="PA">Pennsylvania</option>
              <option value="RI">Rhode Island</option>
              <option value="SC">South Carolina</option>
              <option value="SD">South Dakota</option>
              <option value="TN">Tennessee</option>
              <option value="TX">Texas</option>
              <option value="UT">Utah</option>
              <option value="VT">Vermont</option>
              <option value="VA">Virginia</option>
              <option value="WA">Washington</option>
              <option value="WV">West Virginia</option>
              <option value="WI">Wisconsin</option>
              <option value="WY">Wyoming</option>
            </select>
            <span class="field-error" id="hd-state-error" aria-live="polite"></span>
          </div>

          <div class="tax-notice" id="tax-notice" role="status">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>
            Hawaii GET (4.725%) will be added as a separate line item.
          </div>

          <button type="submit" class="btn-submit">
            <span class="btn-text">Continue to Payment — $${p.price}</span>
            <span class="spinner" aria-hidden="true"></span>
          </button>

          <div class="stripe-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            Secured by Stripe
          </div>
        </div>
      </form>
    `;
  }

  // ── Bind Events ─────────────────────────────────────────────

  _bind() {
    const form = this._shadow.querySelector('form');
    if (!form) return;

    // State change → show/hide tax notice
    const stateSelect = this._shadow.querySelector('#hd-state');
    if (stateSelect) {
      stateSelect.addEventListener('change', () => {
        const notice = this._shadow.querySelector('#tax-notice');
        if (notice) notice.classList.toggle('show', stateSelect.value === 'HI');
        this._updateTaxPrice();
      });
    }

    const posterSize = this._shadow.querySelector('#hd-poster-size');
    if (posterSize) {
      posterSize.addEventListener('change', () => this._updateTaxPrice());
    }

    // Real-time validation, saving state, and input-change event dispatching
    form.querySelectorAll('input, select').forEach(field => {
      field.addEventListener('blur', () => this._validateField(field));

      const handleInput = () => {
        if (this._values[field.name] === field.value) return;
        this._values[field.name] = field.value;
        this.dispatchEvent(new CustomEvent('input-change', {
          detail: { field: field.name, value: field.value },
          bubbles: true,
          composed: true
        }));
        if (field.getAttribute('aria-invalid') === 'true') {
          this._validateField(field);
        }
      };

      field.addEventListener('input', handleInput);
      field.addEventListener('change', handleInput);
    });

    // Form submit
    form.addEventListener('submit', e => {
      e.preventDefault();
      this._handleSubmit(form);
    });

    // Modal overlay and close
    const overlay = this._shadow.querySelector('.modal-overlay');
    const closeBtn = this._shadow.querySelector('.modal-close');

    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.closeModal());
    }
    if (overlay) {
      overlay.addEventListener('click', e => {
        if (e.target === overlay) this.closeModal();
      });
    }

    // Modal trigger (fallback or custom slot)
    const triggerSlot = this._shadow.querySelector('slot[name="trigger"]');
    if (triggerSlot) {
      triggerSlot.addEventListener('click', (e) => {
        e.preventDefault();
        this.openModal();
      });
    }

    // Escape key closes modal, Tab key traps focus
    this.addEventListener('keydown', e => {
      if (this._mode !== 'modal') return;

      const ov = this._shadow.querySelector('.modal-overlay');
      if (!ov || ov.hasAttribute('hidden')) return;

      if (e.key === 'Escape') {
        this.closeModal();
        return;
      }

      if (e.key === 'Tab') {
        const modal = this._shadow.querySelector('.modal-card');
        if (!modal) return;

        const focusable = Array.from(modal.querySelectorAll(
          'button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
        )).filter(el => !el.disabled && el.tabIndex !== -1);

        if (focusable.length === 0) return;

        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        const active = this._shadow.activeElement;

        if (e.shiftKey) {
          if (active === first || !focusable.includes(active)) {
            last.focus();
            e.preventDefault();
          }
        } else {
          if (active === last || !focusable.includes(active)) {
            first.focus();
            e.preventDefault();
          }
        }
      }
    });
  }

  _updateTaxPrice() {
    const stateSelect = this._shadow.querySelector('#hd-state');
    const btn = this._shadow.querySelector('.btn-submit .btn-text');
    if (!btn) return;
    const p = this._productData;
    const posterSize = this._shadow.querySelector('#hd-poster-size');
    const displayPrice = posterSize && p.sizes ? p.sizes[posterSize.value] || p.price : p.price;
    if (stateSelect && stateSelect.value === 'HI') {
      const tax = (displayPrice * 0.04725).toFixed(2);
      btn.textContent = `Continue to Payment — $${displayPrice} + $${tax} tax`;
    } else {
      btn.textContent = `Continue to Payment — $${displayPrice}`;
    }
  }

  // ── Validation ──────────────────────────────────────────────

  _restoreValues() {
    const form = this._shadow.querySelector('form');
    if (!form) return;
    form.querySelectorAll('input, select').forEach(field => {
      if (this._values[field.name] !== undefined) {
        field.value = this._values[field.name];
      }
    });
    const stateSelect = this._shadow.querySelector('#hd-state');
    const notice = this._shadow.querySelector('#tax-notice');
    if (stateSelect && notice) {
      notice.classList.toggle('show', stateSelect.value === 'HI');
    }
    this._updateTaxPrice();
  }

  _validateField(field) {
    const errorEl = field.parentElement.querySelector('.field-error');
    let msg = '';

    if (field.required && !field.value.trim()) {
      msg = 'This field is required.';
    } else if (field.name === 'email' && field.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value)) {
      msg = 'Enter a valid email address.';
    } else if (field.name === 'birth_date' && field.value) {
      const timestamp = Date.parse(field.value);
      if (isNaN(timestamp)) {
        msg = 'Enter a valid date.';
      } else if (timestamp > Date.now()) {
        msg = 'Birth date cannot be in the future.';
      }
    } else if (field.name === 'birth_time' && field.value) {
      if (!/^\d{1,2}:\d{2}$/.test(field.value)) {
        msg = 'Enter time as HH:MM.';
      } else {
        const [h, m] = field.value.split(':').map(Number);
        if (h < 0 || h > 23 || m < 0 || m > 59) {
          msg = 'Enter a valid time.';
        }
      }
    } else if (field.name === 'name' && field.value.trim().length < 2) {
      msg = 'Name must be at least 2 characters.';
    }

    field.setAttribute('aria-invalid', msg ? 'true' : 'false');
    if (errorEl) errorEl.textContent = msg;
    return !msg;
  }

  _validateAll(form) {
    let valid = true;
    form.querySelectorAll('input, select').forEach(f => {
      if (!this._validateField(f)) valid = false;
    });
    return valid;
  }

  // ── Submit ──────────────────────────────────────────────────

  async _handleSubmit(form) {
    if (!this._validateAll(form)) {
      this._log('Validation failed');
      return;
    }

    const formData = new FormData(form);
    const payload = new URLSearchParams({
      product: this._product,
      customer_name: formData.get('name'),
      customer_email: formData.get('email'),
      birth_date: formData.get('birth_date'),
      birth_time: formData.get('birth_time'),
      birth_city: formData.get('birth_city'),
      state: formData.get('state'),
    });
    if (this._isPosterProduct) {
      payload.append('poster_size', formData.get('poster_size') || '18x24');
      if (this._posterImageUrl) payload.append('poster_image_url', this._posterImageUrl);
      if (this._printFileUrl) payload.append('print_file_url', this._printFileUrl);
      if (this.getAttribute('mockup-url')) payload.append('mockup_url', this.getAttribute('mockup-url'));
    }

    // Add tax_line for Hawaii
    if (formData.get('state') === 'HI') {
      payload.append('tax_line', 'true');
    }

    const btn = form.querySelector('.btn-submit');
    btn.classList.add('loading');
    btn.disabled = true;
    this._setError('');

    try {
      this._log('POST', this._apiUrl, payload.toString());
      const res = await fetch(this._apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: payload.toString(),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Server error: ${res.status}${text ? ' — ' + text.slice(0, 100) : ''}`);
      }

      const data = await res.json();
      const url = data.url || data.checkoutUrl;

      if (!url) throw new Error('No checkout URL in response');

      this._log('Redirecting to', url);
      this.dispatchEvent(new CustomEvent('checkout-ready', { detail: { checkoutUrl: url } }));
      window.location.href = url;

    } catch (err) {
      this._log('Error:', err.message);
      this._setError(err.message);
      btn.classList.remove('loading');
      btn.disabled = false;
      this.dispatchEvent(new CustomEvent('checkout-error', { detail: { error: err.message } }));
    }
  }

  _setError(msg) {
    const banner = this._shadow.querySelector('.error-banner');
    if (banner) {
      banner.textContent = msg;
      banner.classList.toggle('show', !!msg);
    }
  }

  // ── Focus Trap (Modal) ───────────────────────────────────────

  _trapFocus() {
    const modal = this._shadow.querySelector('.modal-card');
    if (!modal) return;
    const focusable = modal.querySelectorAll(
      'button, input, select, [tabindex]:not([tabindex="-1"])'
    );
    if (focusable.length) focusable[0].focus();
  }
}

customElements.define('hd-checkout', HdCheckout);
export default HdCheckout;
