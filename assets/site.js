// Mobile menu
(function () {
  var btn = document.querySelector('.menu-toggle');
  var nav = document.querySelector('.nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
})();

// Lightbox for galleries: tap to open, swipe or arrows to browse
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('.grid a, .lightbox'));
  if (!links.length) return;

  var lb = document.createElement('div');
  lb.className = 'lb';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.innerHTML =
    '<span class="count"></span>' +
    '<figure><img alt=""><figcaption></figcaption></figure>' +
    '<button class="close" aria-label="Close">&times;</button>' +
    '<button class="prev" aria-label="Previous">&#8249;</button>' +
    '<button class="next" aria-label="Next">&#8250;</button>';
  document.body.appendChild(lb);

  var img = lb.querySelector('img');
  var cap = lb.querySelector('figcaption');
  var count = lb.querySelector('.count');
  var current = 0;

  function show(i) {
    current = (i + links.length) % links.length;
    var a = links[current];
    var thumb = a.querySelector('img');
    img.src = a.getAttribute('href');
    img.alt = thumb ? thumb.alt : '';
    cap.textContent = a.getAttribute('data-caption') || '';
    count.textContent = (current + 1) + ' / ' + links.length;
    // preload neighbours
    [current + 1, current - 1].forEach(function (n) {
      var l = links[(n + links.length) % links.length];
      (new Image()).src = l.getAttribute('href');
    });
  }
  function open(i) { show(i); lb.classList.add('open'); document.body.style.overflow = 'hidden'; }
  function close() { lb.classList.remove('open'); document.body.style.overflow = ''; img.src = ''; }

  links.forEach(function (a, i) {
    a.addEventListener('click', function (e) { e.preventDefault(); open(i); });
  });
  lb.querySelector('.close').addEventListener('click', close);
  lb.querySelector('.prev').addEventListener('click', function (e) { e.stopPropagation(); show(current - 1); });
  lb.querySelector('.next').addEventListener('click', function (e) { e.stopPropagation(); show(current + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(current - 1);
    if (e.key === 'ArrowRight') show(current + 1);
  });

  var startX = null, startY = null;
  lb.addEventListener('touchstart', function (e) {
    startX = e.touches[0].clientX; startY = e.touches[0].clientY;
  }, { passive: true });
  lb.addEventListener('touchend', function (e) {
    if (startX === null) return;
    var dx = e.changedTouches[0].clientX - startX;
    var dy = e.changedTouches[0].clientY - startY;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(current + (dx < 0 ? 1 : -1));
    else if (dy > 90) close();
    startX = null;
  });
})();

// Contact buttons: the address is rebuilt only when someone taps,
// so spam bots reading the page never see it.
(function () {
  function dec(t) { return atob(t).split('').reverse().join(''); }
  document.querySelectorAll('a.mail').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var addr = dec(a.getAttribute('data-u')) + '@' + dec(a.getAttribute('data-d'));
      var shown = a.parentNode.nextElementSibling;
      if (shown && shown.classList.contains('mail-shown')) {
        shown.textContent = addr;
        shown.hidden = false;
      }
      window.location.href = 'mailto:' + addr + '?subject=' + encodeURIComponent(a.getAttribute('data-s') || '');
    });
  });
})();
