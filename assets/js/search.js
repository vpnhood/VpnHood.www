// Site search (/search/): reads ?q=, gets a Cloudflare Turnstile token, asks the search
// Worker (workers/search/) for this language's pages and lists them. The page renders every
// message (data-vh-msg-*) and the Worker answers { results: [{ link, title, snippet }] };
// anything else - its daily cap reached, a failed check, no network - reads as
// "unavailable". Google's snippets are HTML, so they are parsed inert and only their text
// and <b> survive. Turnstile can't be self-hosted: Cloudflare serves api.js itself, and only
// this page loads it.
(function () {
  var TURNSTILE = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';

  function msg(box, key, query) {
    return (box.getAttribute('data-vh-msg-' + key) || '').split('[query]').join(query || '');
  }

  function loadTurnstile() {
    return new Promise(function (resolve, reject) {
      if (window.turnstile) return resolve(window.turnstile);
      var script = document.createElement('script');
      script.src = TURNSTILE;
      script.async = true;
      script.onload = function () { window.turnstile ? resolve(window.turnstile) : reject(); };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  // Invisible unless Cloudflare wants the reader to tick a box; then it shows above the
  // status line, in the page's theme.
  function getToken(box) {
    return loadTurnstile().then(function (turnstile) {
      return new Promise(function (resolve, reject) {
        turnstile.render(box.querySelector('.vh-search-check'), {
          sitekey: box.getAttribute('data-vh-sitekey'),
          action: 'search',
          appearance: 'interaction-only',
          theme: document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark',
          callback: resolve,
          'error-callback': function () { reject(); return true; }
        });
      });
    });
  }

  function textOf(html) {
    return new DOMParser().parseFromString(html || '', 'text/html').body.textContent.trim();
  }

  function appendSnippet(into, html) {
    var body = new DOMParser().parseFromString(html, 'text/html').body;
    (function walk(node) {
      node.childNodes.forEach(function (child) {
        if (child.nodeType === 3) into.appendChild(document.createTextNode(child.nodeValue));
        else if (child.nodeName === 'SCRIPT' || child.nodeName === 'STYLE') return;
        else if (child.nodeName === 'B') {
          var bold = document.createElement('b');
          bold.textContent = child.textContent;
          into.appendChild(bold);
        } else if (child.nodeType === 1) walk(child);
      });
    })(body);
  }

  function render(box, query, results) {
    var list = box.querySelector('.vh-search-results');
    var status = box.querySelector('.vh-search-status');
    list.textContent = '';
    results.forEach(function (result) {
      var url;
      try { url = new URL(result.link); } catch (e) { return; }
      if (url.protocol !== 'https:' || url.hostname !== 'www.vpnhood.com') return;
      var path = url.pathname;
      try { path = decodeURI(path); } catch (e) {}

      var item = document.createElement('li');
      var link = document.createElement('a');
      link.href = url.href;
      link.textContent = textOf(result.title).replace(/\s*[|–-]\s*VpnHood!‎?\s*$/, '') || path;
      item.appendChild(link);

      var address = document.createElement('p');
      address.className = 'vh-search-url';
      var ltr = document.createElement('span');
      ltr.dir = 'ltr';
      ltr.textContent = url.host + path;
      address.appendChild(ltr);
      item.appendChild(address);

      if (result.snippet) {
        var snippet = document.createElement('p');
        appendSnippet(snippet, result.snippet);
        item.appendChild(snippet);
      }
      list.appendChild(item);
    });
    status.textContent = msg(box, list.children.length ? 'results' : 'none', query);
  }

  function init() {
    var box = document.getElementById('vhSearch');
    if (!box) return;
    var query = (new URLSearchParams(location.search).get('q') || '').trim().slice(0, 200);
    var input = document.querySelector('#vhSearchMain .vh-search-input');
    if (input) {
      input.value = query;
      if (!query) input.focus();
    }
    if (!query) return;

    var status = box.querySelector('.vh-search-status');
    status.textContent = msg(box, 'searching');
    getToken(box).then(function (token) {
      // text/plain keeps it a simple request, so the browser sends no CORS preflight
      return fetch(box.getAttribute('data-vh-endpoint'), {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: JSON.stringify({ q: query, lang: box.getAttribute('data-vh-search-lang'), token: token })
      });
    }).then(function (response) {
      if (!response.ok) throw new Error(response.status);
      return response.json();
    }).then(function (data) {
      render(box, query, data.results || []);
    }).catch(function () {
      status.textContent = msg(box, 'unavailable');
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
