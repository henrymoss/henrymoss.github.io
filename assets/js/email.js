// Assemble email addresses client-side.
//
// The address is base64-encoded in the HTML (see _includes/email.html), so the
// plain text is never present in the served markup for an address harvester to
// pick up with a regex. Everything here is progressive enhancement: with
// JavaScript off, the <noscript> fallback in the markup still shows a readable
// "name [at] domain" form.
(function () {
  'use strict';

  function build() {
    var nodes = document.querySelectorAll('.emailAddr');
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var encoded = el.getAttribute('data-e');
      if (!encoded) continue;

      var address;
      try {
        address = atob(encoded);
      } catch (err) {
        continue; // leave the noscript fallback in place
      }

      var link = document.createElement('a');
      link.href = 'mailto:' + address;
      link.textContent = el.getAttribute('data-label') || address;

      el.textContent = '';
      el.appendChild(link);
      el.removeAttribute('data-e');
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
