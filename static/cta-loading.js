/**
 * Consistent loading state for primary/secondary action buttons (fetch / async work).
 * Exposes setCtaLoading(el, bool, opts?) and withCtaLoading(el, asyncFn, opts?).
 */
(function (global) {
  'use strict';

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function setCtaLoading(el, loading, options) {
    options = options || {};
    if (!el) return;
    if (el.tagName !== 'BUTTON' && !(el.tagName === 'INPUT' && el.type === 'submit')) return;

    var labelText = options.label != null ? options.label : 'Loading…';
    var spinnerOnly = Boolean(options.spinnerOnly) || labelText === '';

    if (loading) {
      if (el.dataset.ctaBusy === '1') return;
      el.dataset.ctaBusy = '1';
      el.dataset.ctaOriginalHtml = el.innerHTML;
      var w = el.offsetWidth;
      if (w) el.style.minWidth = w + 'px';
      el.setAttribute('aria-busy', 'true');
      el.disabled = true;

      var inner =
        '<span class="inline-flex items-center justify-center gap-2 whitespace-nowrap">' +
        '<span class="cta-spinner" aria-hidden="true"></span>';
      if (!spinnerOnly) {
        inner += '<span>' + escapeHtml(labelText) + '</span>';
      }
      inner += '</span>';
      el.innerHTML = inner;
    } else {
      if (el.dataset.ctaBusy !== '1') return;
      el.dataset.ctaBusy = '';
      el.removeAttribute('aria-busy');
      el.style.minWidth = '';
      el.disabled = false;
      if (el.dataset.ctaOriginalHtml != null) {
        el.innerHTML = el.dataset.ctaOriginalHtml;
        delete el.dataset.ctaOriginalHtml;
      }
    }
  }

  function withCtaLoading(el, fn, options) {
    setCtaLoading(el, true, options);
    return Promise.resolve()
      .then(function () {
        return fn();
      })
      .finally(function () {
        setCtaLoading(el, false, options);
      });
  }

  global.setCtaLoading = setCtaLoading;
  global.withCtaLoading = withCtaLoading;
})(typeof window !== 'undefined' ? window : this);
