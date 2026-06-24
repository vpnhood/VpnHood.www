/**
 * VpnHood site interactions — header/footer behaviour.
  */
(function () {
  'use strict';

  // ---- Preloader → dispatch `vhPlayAnimate` (AOS init in the footer waits on it) ----
  window.addEventListener('load', function () {
    var loader = document.querySelector('.sp-pre-loader');
    var play = function () {
      document.dispatchEvent(new CustomEvent('vhPlayAnimate'));
    };
    if (!loader) {
      play();
      return;
    }
    var done = false;
    var finish = function () {
      if (done) return;
      done = true;
      loader.remove();
      play();
    };
    loader.style.transition = 'opacity 400ms';
    loader.style.opacity = '0';
    loader.addEventListener('transitionend', finish, { once: true });
    window.setTimeout(finish, 450); // fallback if transitionend never fires
  });

  document.addEventListener('DOMContentLoaded', function () {
    // ---- Sticky header ----
    var header = document.getElementById('sp-header');
    if (header && document.body.classList.contains('sticky-header')) {
      var placeholder = document.querySelector('.sticky-header-placeholder');
      var headerHeight = header.offsetHeight;
      var offsetTop = header.getBoundingClientRect().top + window.pageYOffset;
      var STICKY_OFFSET = 100;
      var onScroll = function () {
        if (window.pageYOffset >= offsetTop + STICKY_OFFSET) {
          header.classList.add('header-sticky');
          if (placeholder) placeholder.style.height = headerHeight + 'px';
        } else if (header.classList.contains('header-sticky')) {
          header.classList.remove('header-sticky');
          if (placeholder) placeholder.style.height = '';
        }
      };
      onScroll();
      window.addEventListener('scroll', onScroll, { passive: true });
    }

    // ---- Scroll-to-top button (.sp-scroll-up is display:none until shown) ----
    var scrollUp = document.querySelector('.sp-scroll-up');
    if (scrollUp) {
      var setVisible = function (visible) {
        if (visible) {
          scrollUp.style.display = 'flex';
          scrollUp.style.opacity = '1';
        } else {
          scrollUp.style.opacity = '0';
          window.setTimeout(function () {
            if (scrollUp.style.opacity === '0') scrollUp.style.display = 'none';
          }, 300);
        }
      };
      window.addEventListener('scroll', function () {
        setVisible(window.pageYOffset > 100);
      }, { passive: true });
      scrollUp.addEventListener('click', function (e) {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }

    // The desktop mega-menu opens on hover via CSS (.vh-mega-menu:hover); the mobile
    // off-canvas menu + submenus are Bootstrap Offcanvas/Collapse (declarative data-bs-*).

    // ---- Drawer ↔ burger sync (mirror Bootstrap's offcanvas open state onto the
    // header burger so it animates into an X, and lift the header above the backdrop
    // so the burger stays the visible close control while the drawer is open). ----
    var drawer = document.getElementById('mobileMenu');
    var burger = document.getElementById('offcanvas-toggler');
    var header = document.getElementById('sp-header');
    if (drawer && burger) {
      drawer.addEventListener('show.bs.offcanvas', function () {
        burger.classList.add('is-open');
        if (header) header.classList.add('menu-open');
      });
      drawer.addEventListener('hide.bs.offcanvas', function () {
        burger.classList.remove('is-open');
        if (header) header.classList.remove('menu-open');
      });
    }

    // ---- Optional Bootstrap tooltips/popovers (no-op unless a page opts in) ----
    if (window.bootstrap) {
      document.querySelectorAll('[data-bs-toggle="tooltip"], .hasTooltip').forEach(function (el) {
        new bootstrap.Tooltip(el, { html: true });
      });
      document.querySelectorAll('[data-bs-toggle="popover"], .hasPopover').forEach(function (el) {
        new bootstrap.Popover(el);
      });
    }
  });
})();
