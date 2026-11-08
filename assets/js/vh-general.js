function removeTopBar(){
    const topBar = document.getElementById('topBar');
    topBar.classList.add('d-none');

    fetch(window.location.href, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'hide_topbar=1'
    });
}

//---------------------- Pausing what moves on its own ----------------------
// WCAG 2.2.2: anything that moves for more than five seconds needs a way to stop it. The
// home globe (globe.js), the typewriter and the sliding strips (below) each get their own
// copy of the pause button that footer.html renders once in <template id="vhMotionToggle">,
// and each says where it goes. A visitor who asks for reduced motion gets them paused from
// the start. Defined outside DOMContentLoaded, as globe.js loads first and calls it then.
window.vhMotion = {
    reduce: !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches),
    // control: { pause(), resume() }; place(button): puts the button where it belongs;
    // host, if given, takes .vh-motion-paused, which stops the CSS animations inside it too.
    add: function (control, place, host) {
        const template = document.getElementById('vhMotionToggle');
        const button = template ? template.content.firstElementChild.cloneNode(true) : null;
        let paused = false;
        const set = value => {
            paused = value;
            if (value) control.pause(); else control.resume();
            if (host) host.classList.toggle('vh-motion-paused', value);
            if (button) button.setAttribute('aria-pressed', value ? 'true' : 'false');
        };
        if (button) {
            button.addEventListener('click', () => set(!paused));
            place(button);
        }
        if (this.reduce) set(true);
    }
};

//---------------------- CTA click tracking ----------------------
// One dataLayer event per click on any [data-vh-track] element, so GTM can forward
// it to GA4 as a custom event (see .docs/components.md, "CTA tracking"). Nothing
// here talks to Google directly, and the click itself is never delayed or blocked.
document.addEventListener('click', function (e) {
    const el = e.target.closest('[data-vh-track]');
    if (!el) return;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
        event: 'vh_cta_click',
        vh_cta: el.dataset.vhTrack,
        vh_href: el.getAttribute('href') || ''
    });
});

document.addEventListener('DOMContentLoaded', function () {

    // The desktop mega-menu opens on CSS :hover (or keyboard focus), and the overlay
    // (#vhOverlay) follows it in CSS too, so the menu still works with no JS at all. JS adds
    // the two things hover alone cannot express, both about a pointer that is on its way
    // somewhere, plus Escape for the keyboard:
    //
    //   .vh-mega-hold     marks the open panel, from the moment it opens until 250ms after
    //                     the pointer leaves the item, so a gap the CSS hover bridge cannot
    //                     predict (a wrapped header, a promo bar above the nav) does not
    //                     close the menu mid-travel. It goes on when the panel opens, not
    //                     when the pointer leaves: Chrome restyles once between dropping
    //                     :hover and running mouseleave, and a class added there came one
    //                     pass late, so the panel counted as closed and its fade-in replayed
    //                     from nothing on the way out.
    //   .vh-mega-suppress holds a panel shut for 150ms when the pointer arrives on an item
    //                     while another panel is open. The panel is centred and far wider
    //                     than its item, so reaching a link on its far side means crossing a
    //                     neighbouring item: without this, that neighbour's panel took over
    //                     and the link moved out from under the pointer.
    //   .vh-mega-swap     a panel that replaces another one appears at once; only a menu
    //                     opening from nothing fades in. Fading in from zero after the wait
    //                     left a blank beat between the two panels.
    //
    // Entering a panel counts as entering its item (the panel is a descendant), so the pointer
    // reaching its own panel cancels the hold's countdown.
    const HOLD_MS = 250, INTENT_MS = 150;
    const megaItems = [...document.querySelectorAll('.vh-mega-menu')];
    const holdTimers = new Map(), intentTimers = new Map();
    let pending = null; // the item waiting out INTENT_MS
    const isOpen = el => el.classList.contains('vh-mega-hold') && !el.classList.contains('vh-mega-suppress');
    // Only ever called for an item the pointer is not on, so dropping .vh-mega-swap can never
    // replay the fade-in on a panel that is still showing.
    const close = el => {
        clearTimeout(holdTimers.get(el));
        el.classList.remove('vh-mega-hold', 'vh-mega-swap');
    };
    const open = (item, swap) => {
        clearTimeout(intentTimers.get(item));
        if (pending === item) pending = null;
        megaItems.forEach(el => { if (el !== item) close(el); }); // nothing stacks behind it
        item.classList.remove('vh-mega-suppress');
        item.classList.toggle('vh-mega-swap', swap);
        item.classList.add('vh-mega-hold');
    };
    megaItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            clearTimeout(holdTimers.get(item));
            // Back on its own panel (crossing from the label into the panel leaves and
            // re-enters the item): it stays as it is.
            if (isOpen(item)) return;
            // Nothing else open: open at once, so a first hover never feels laggy.
            if (!megaItems.some(isOpen)) { open(item, false); return; }
            // Another panel is still up. Wait to see whether the pointer stays here or is
            // only passing through on its way to that panel.
            item.classList.add('vh-mega-suppress');
            pending = item;
            clearTimeout(intentTimers.get(item));
            intentTimers.set(item, setTimeout(() => open(item, true), INTENT_MS));
        });
        item.addEventListener('mouseleave', () => {
            clearTimeout(intentTimers.get(item));
            if (pending === item) pending = null;
            // Shut means only passing through, or closed with Escape: nothing to hold open.
            const shut = item.classList.contains('vh-mega-suppress');
            item.classList.remove('vh-mega-suppress');
            if (shut) return;
            item.classList.add('vh-mega-hold'); // already there unless focus-out dropped it
            clearTimeout(holdTimers.get(item));
            holdTimers.set(item, setTimeout(() => {
                close(item);
                // A neighbour still waiting out INTENT_MS takes over now, not after a gap.
                if (pending) open(pending, true);
            }, HOLD_MS));
        });
    });
    // Leaving the navbar entirely (the header buttons, the page below) ends the grace period
    // at once, so a closed menu never lingers. Anything still inside `.vh-navbar` keeps it:
    // the few pixels of pill padding between two items are not a menu item either, and
    // dropping the hold there would close the panel while the pointer slides along the pill.
    document.addEventListener('mouseover', e => {
        if (!e.target.closest('.vh-navbar')) megaItems.forEach(close);
    }, { passive: true });
    // Keyboard. The label is a link or a button, so Tab reaches it, and a keyboard focus
    // anywhere in the item holds the panel open (:focus-visible, so a mouse click on the
    // label never pins it). The hold is what carries the panel through the blur/focus
    // handoff from the label into its first link: a pure CSS :has(:focus-visible) closes it
    // between the two and the link is unfocusable when focus arrives. Escape shuts the panel
    // via .vh-mega-suppress and returns focus to the label; the class clears once focus
    // leaves the item, so Shift+Tab back onto the label opens it again, and so does
    // Enter/Space on the Resources button.
    megaItems.forEach(item => {
        const toggle = item.querySelector('.vh-mega-toggle');
        item.addEventListener('focusin', e => {
            if (!e.target.matches(':focus-visible')) return;
            clearTimeout(holdTimers.get(item));
            item.classList.add('vh-mega-hold');
        });
        item.addEventListener('focusout', e => {
            if (!item.contains(e.relatedTarget)) item.classList.remove('vh-mega-hold', 'vh-mega-suppress');
        });
        item.addEventListener('keydown', e => {
            if (e.key !== 'Escape') return;
            item.classList.add('vh-mega-suppress');
            toggle.focus();
        });
        toggle.addEventListener('click', e => {
            if (e.detail === 0) item.classList.remove('vh-mega-suppress'); // keyboard-initiated
        });
    });

    //---------------------- Star effect ----------------------
    const stars = document.querySelectorAll('.star-effect');
    const checkStarsInView = () => {
        stars.forEach((star) => {
            const rect = star.getBoundingClientRect();
            const isOnScreen = rect.top < window.innerHeight && rect.bottom > 0;

            if (isOnScreen) {
                star.classList.add('visible');
            } else {
                star.classList.remove('visible');
            }
        });
    };

    // Check elements in view on page load
    checkStarsInView();

    // Add scroll event listener
    window.addEventListener('scroll', checkStarsInView);

    //---------------------- Light box effect ----------------------
    const containers = document.querySelectorAll('.light-box-wrapper');

    containers.forEach(container => {
        container.addEventListener('mousemove', function (e) {
            const rect = container.getBoundingClientRect();
            const x = e.clientX - rect.left; // x position within the element.
            const y = e.clientY - rect.top;  // y position within the element.
            container.style.setProperty('--light-x', `${x}px`);
            container.style.setProperty('--light-y', `${y}px`);
            container.style.setProperty('--light-opacity', `0.8`);
        });

        container.addEventListener('mouseleave', function () {
            container.style.removeProperty('--light-opacity');
        });
    });

    //---------------------- Linear slider ----------------------
    const carouselContainer = document.querySelectorAll('.linear-slider-items');

    carouselContainer.forEach(container => {
        // Clone the carousel content to create a continuous loop. The clones are
        // presentation only, so hide them from assistive tech or every item is
        // announced twice.
        const originalCount = container.children.length;
        if (!originalCount) return;
        container.innerHTML += container.innerHTML;
        Array.from(container.children).slice(originalCount).forEach(el => el.setAttribute('aria-hidden', 'true'));

        // Set up animation
        let scrollLeft = 0;
        const scrollSpeed = 3; // Adjust the scroll speed as needed
        let paused = false;
        let held = null; // the pointer holding the strip, and its last x

        // Puts the strip at x, wrapped into one loop whichever way it went. A loop runs from the
        // first item to its copy, the gap after the last item included: half the strip's width
        // came half a gap short, and the strip skipped that much at every wrap.
        const moveTo = x => {
            const loop = container.children[originalCount].offsetLeft - container.children[0].offsetLeft;
            scrollLeft = loop > 0 ? (x % loop + loop) % loop : 0;
            container.style.transform = `translateX(-${scrollLeft}px)`;
        };

        // A strip starts with its first item in the middle, the last ones' copies before it: the
        // first item is the one a strip leads with (/free-vpn/'s connected home screen), and at
        // the left end it sat under the fade and was the first to leave.
        const first = container.children[0];
        moveTo(first.offsetLeft + first.offsetWidth / 2 - container.parentElement.clientWidth / 2);

        function animateCarousel(timestamp) {
            if (paused) return;
            // A held strip stands still, and goes on from where it was let go.
            if (!lastTimestamp || held) {
                lastTimestamp = timestamp;
            }

            const deltaTime = timestamp - lastTimestamp;
            lastTimestamp = timestamp;

            moveTo(scrollLeft + scrollSpeed * deltaTime / 60); // Normalize speed
            requestAnimationFrame(animateCarousel);
        }

        let lastTimestamp = null;
        requestAnimationFrame(animateCarousel);

        // A finger or the mouse button on the strip holds it, and a drag moves it either way,
        // paused too, so a visitor who asked for reduced motion can still see every item. Once
        // let go it goes on by itself, unless its pause button stopped it. A vertical swipe
        // still scrolls the page (touch-action in _default.scss), which lets go of the strip.
        // The window listens, not the strip: the items overflow the strip's own box, which the
        // strip carries off to the left as it moves, so a press between two items hit nothing.
        const view = container.parentElement;
        view.addEventListener('pointerdown', e => {
            if (held || e.button !== 0) return;
            held = { id: e.pointerId, x: e.clientX };
            view.setPointerCapture(e.pointerId);
        });
        view.addEventListener('pointermove', e => {
            if (!held || e.pointerId !== held.id) return;
            moveTo(scrollLeft + held.x - e.clientX);
            held.x = e.clientX;
        });
        const letGo = e => {
            if (held && e.pointerId === held.id) held = null;
        };
        view.addEventListener('pointerup', letGo);
        view.addEventListener('pointercancel', letGo);
        // A mouse drag would otherwise pick up the picture under it.
        view.addEventListener('dragstart', e => e.preventDefault());

        // The pause button goes under the strip: its ends fade under a mask, which would
        // fade a button inside it too.
        window.vhMotion.add({
            pause: () => { paused = true; },
            resume: () => {
                if (!paused) return;
                paused = false;
                lastTimestamp = null;
                requestAnimationFrame(animateCarousel);
            }
        }, button => container.parentElement.after(button), container.parentElement);
    });


    //---------------------- Copy buttons ----------------------
    // The copy buttons of _includes/terminal.html ship hidden, so a page without JS never
    // shows one that does nothing. A button copies the <pre> beside it through the
    // clipboard API, or, in a browser without one, by selecting the text and copying the
    // selection; when both fail, the text stays selected for the visitor to copy. The
    // button only swaps its icon, so a status region reads out "copied" too, in the words
    // the include put in data-vh-label-done.
    const copyButtons = document.querySelectorAll('[data-vh-copy]');
    if (copyButtons.length) {
        const copyStatus = document.createElement('div');
        copyStatus.className = 'visually-hidden';
        copyStatus.setAttribute('role', 'status');
        document.body.append(copyStatus);
        const copyTimers = new Map();
        const copySelection = pre => {
            const range = document.createRange();
            range.selectNodeContents(pre);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            let copied = false;
            try { copied = document.execCommand('copy'); } catch (e) { }
            if (copied) selection.removeAllRanges();
            return copied;
        };
        copyButtons.forEach(btn => {
            const pre = btn.parentElement.querySelector('pre');
            btn.hidden = false;
            btn.addEventListener('click', () => {
                const copy = navigator.clipboard
                    ? navigator.clipboard.writeText(pre.textContent).catch(() => copySelection(pre) || Promise.reject())
                    : (copySelection(pre) ? Promise.resolve() : Promise.reject());
                copy.then(() => {
                    btn.classList.add('vh-copied');
                    copyStatus.textContent = btn.dataset.vhLabelDone;
                    clearTimeout(copyTimers.get(btn));
                    copyTimers.set(btn, setTimeout(() => {
                        btn.classList.remove('vh-copied');
                        copyStatus.textContent = '';
                    }, 2000));
                }, () => { });
            });
        });
    }


    //---------------------- Multi text writer ----------------------
    // Each .multiTextWriter is rendered by _includes/multi-text-writer.html
    // together with a hidden <ul class="multi-text-writer-words"> holding the
    // (translated) phrases — never hardcode copy here.
    document.querySelectorAll('.multiTextWriter').forEach(element => {
        const list = element.parentElement.querySelector('.multi-text-writer-words');
        if (!list) return;
        const words = Array.from(list.querySelectorAll('li'))
            .map(li => li.textContent.trim())
            .filter(w => w.length);
        if (words.length) {
            const typer = setTyper(element, words);
            window.vhMotion.add(typer, button => element.parentElement.append(button));
        }
    });

    function setTyper(element, words) {
        const LETTER_TYPE_DELAY = 35;
        const WORD_STAY_DELAY = 1800;

        const DIRECTION_FORWARDS = 0;
        const DIRECTION_BACKWARDS = 1;

        var direction = DIRECTION_FORWARDS;
        var wordIndex = 0;
        var letterIndex = 0;

        var wordTypeInterval;
        var stayTimer;
        var paused = false;

        startTyping();

        function startTyping() {
            if (paused) return;
            wordTypeInterval = setInterval(typeLetter, LETTER_TYPE_DELAY);
        }

        function typeLetter() {
            const word = words[wordIndex];

            if (direction == DIRECTION_FORWARDS) {
                letterIndex++;

                if (letterIndex == word.length) {
                    direction = DIRECTION_BACKWARDS;
                    clearInterval(wordTypeInterval);
                    stayTimer = setTimeout(startTyping, WORD_STAY_DELAY);
                }

            } else if (direction == DIRECTION_BACKWARDS) {
                letterIndex--;

                if (letterIndex == 0) {
                    nextWord();
                }
            }

            const textToType = word.substring(0, letterIndex);

            element.textContent = textToType;
        }

        function nextWord() {
            letterIndex = 0;
            direction = DIRECTION_FORWARDS;
            wordIndex++;

            if (wordIndex == words.length) {
                wordIndex = 0;
            }
        }

        // Paused, the line shows its whole phrase, so it still reads; it goes on from there.
        return {
            pause: function () {
                paused = true;
                clearInterval(wordTypeInterval);
                clearTimeout(stayTimer);
                letterIndex = words[wordIndex].length;
                direction = DIRECTION_BACKWARDS;
                element.textContent = words[wordIndex];
                element.classList.add('vh-motion-paused');
            },
            resume: function () {
                if (!paused) return;
                paused = false;
                element.classList.remove('vh-motion-paused');
                stayTimer = setTimeout(startTyping, WORD_STAY_DELAY);
            }
        };
    }

    //---------------------- Scrollable code ----------------------
    // A command or a file wider than its box scrolls sideways, which the keyboard can only do
    // once the box takes the focus (WCAG 2.1.1). A box that overflows gets tabindex, and loses
    // it when the window grows wide enough, so a short command adds no Tab stop.
    const codeBoxes = document.querySelectorAll('#sp-main-body pre, .vh-terminal pre');
    if (codeBoxes.length) {
        const markScrollable = () => codeBoxes.forEach(pre => {
            if (pre.scrollWidth > pre.clientWidth + 1) pre.setAttribute('tabindex', '0');
            else pre.removeAttribute('tabindex');
        });
        markScrollable();
        window.addEventListener('load', markScrollable);
        let codeResize;
        window.addEventListener('resize', () => {
            clearTimeout(codeResize);
            codeResize = setTimeout(markScrollable, 150);
        });
    }


    //---------------------- Horizontal scroll position detector ----------------------

    /*const scrollContainers = document.querySelectorAll(".horizontal-scroll");


    function updateScrollClasses(scrollableItem) {
        if (scrollableItem.scrollWidth <= scrollableItem.clientWidth) {
            scrollableItem.classList.remove("scroll-on-start", "scroll-on-end", "scroll-on-middle");
        }
        else if (scrollableItem.scrollLeft === 0) {
            scrollableItem.classList.add("scroll-on-start");
            scrollableItem.classList.remove("scroll-on-end", "scroll-on-middle");
        } else if (scrollableItem.scrollLeft + scrollableItem.clientWidth >= scrollableItem.scrollWidth) {
            scrollableItem.classList.add("scroll-on-end");
            scrollableItem.classList.remove("scroll-on-start", "scroll-on-middle");
        } else {
            scrollableItem.classList.add("scroll-on-middle");
            scrollableItem.classList.remove("scroll-on-start", "scroll-on-end");
        }
    }

    // Add scroll listener for each horizontal scroll container
    scrollContainers.forEach((scrollableItem) => {
        scrollableItem.addEventListener("scroll", () => updateScrollClasses(scrollableItem));
        updateScrollClasses(scrollableItem); // Initialize class on page load
    });

    window.addEventListener("resize", function () {
        scrollContainers.forEach(updateScrollClasses);
    });*/


});