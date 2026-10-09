// Open at the top of the page.
//
// Browsers remember how far down you were and restore it on reload and on
// back/forward. On a single long page that means a refresh drops you into the
// middle of the publication list. Turn the restoring off — unless the URL names
// a section (/#team, /#publications), where jumping there is the whole point.
(function () {
  'use strict';

  if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
  }

  function toTop() {
    if (window.location.hash) return;
    // jump, don't animate: the stylesheet's smooth scrolling is for nav clicks
    var html = document.documentElement;
    var previous = html.style.scrollBehavior;
    html.style.scrollBehavior = 'auto';
    window.scrollTo(0, 0);
    html.style.scrollBehavior = previous;
  }

  window.addEventListener('load', toTop);
  // and again when the page comes back out of the back/forward cache
  window.addEventListener('pageshow', function (e) {
    if (e.persisted) toTop();
  });
})();
