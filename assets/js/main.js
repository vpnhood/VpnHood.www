/**
 * VpnHood site interactions — header/footer behaviour.
 *
 * Vanilla JS, no jQuery and no Joomla/Helix dependency. This replaces the
 * former Helix Ultimate `main.js`; only the behaviours this static site
 * actually uses are kept: preloader (fires `vhPlayAnimate` for AOS), sticky
 * header, scroll-to-top, the mega-menu layout helper, and the mobile
 * off-canvas menu. All the Joomla admin/blog/article cruft was dropped.
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

    // The desktop mega-menu opens on hover via CSS (.vh-mega-menu:hover) and the
    // mobile off-canvas menu and its submenus are handled declaratively by
    // Bootstrap's Offcanvas + Collapse components (data-bs-* attributes in the
    // header/footer markup) — no custom JS needed here.

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
