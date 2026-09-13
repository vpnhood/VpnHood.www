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

    // The desktop mega-menu opens on CSS :hover, and the overlay (#vhOverlay) follows it in
    // CSS too, so the menu still works with no JS at all. JS adds the two things hover alone
    // cannot express, both about a pointer that is on its way somewhere:
    //
    //   .vh-mega-hold     keeps a panel open for 250ms after the pointer leaves the item, so
    //                     a gap the CSS hover bridge cannot predict (a wrapped header, a
    //                     promo bar above the nav) does not close the menu mid-travel.
    //   .vh-mega-suppress holds a panel shut for 150ms when the pointer arrives on an item
    //                     while another panel is open. The panel is centred and far wider
    //                     than its item, so reaching a link on its far side means crossing a
    //                     neighbouring item: without this, that neighbour's panel took over
    //                     and the link moved out from under the pointer.
    //
    // Entering a panel counts as entering its item (the panel is a descendant), which is what
    // makes the hold self-clearing.
    const HOLD_MS = 250, INTENT_MS = 150;
    const megaItems = document.querySelectorAll('.vh-mega-menu');
    const holdTimers = new Map(), intentTimers = new Map();
    const dropHold = () => megaItems.forEach(el => {
        clearTimeout(holdTimers.get(el));
        el.classList.remove('vh-mega-hold');
    });
    const heldOther = self => [...megaItems].some(el => el !== self && el.classList.contains('vh-mega-hold'));
    megaItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            // Re-entering this item (crossing the gap from the heading into its own panel
            // leaves and re-enters it) ends its own hold. Suppressing here would hide the
            // very panel the pointer just reached.
            clearTimeout(holdTimers.get(item));
            item.classList.remove('vh-mega-hold');
            // Nothing else open: open at once, so a first hover never feels laggy.
            if (!heldOther(item)) { dropHold(); return; }
            // Another panel is still up. Wait to see whether the pointer stays here or is
            // only passing through on its way to that panel.
            item.classList.add('vh-mega-suppress');
            clearTimeout(intentTimers.get(item));
            intentTimers.set(item, setTimeout(() => {
                item.classList.remove('vh-mega-suppress');
                dropHold(); // it stayed: this item wins, and nothing stacks behind it
            }, INTENT_MS));
        });
        item.addEventListener('mouseleave', () => {
            clearTimeout(intentTimers.get(item));
            item.classList.remove('vh-mega-suppress');
            item.classList.add('vh-mega-hold');
            clearTimeout(holdTimers.get(item));
            holdTimers.set(item, setTimeout(() => item.classList.remove('vh-mega-hold'), HOLD_MS));
        });
    });
    // Leaving the navbar entirely (the header buttons, the page below) ends the grace period
    // at once, so a closed menu never lingers. Anything still inside `.vh-navbar` keeps it:
    // the few pixels of pill padding between two items are not a menu item either, and
    // dropping the hold there would close the panel while the pointer slides along the pill.
    document.addEventListener('mouseover', e => {
        if (!e.target.closest('.vh-navbar')) dropHold();
    }, { passive: true });

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
        container.innerHTML += container.innerHTML;
        Array.from(container.children).slice(originalCount).forEach(el => el.setAttribute('aria-hidden', 'true'));

        // Set up animation
        let scrollLeft = 0;
        const scrollSpeed = 3; // Adjust the scroll speed as needed

        function animateCarousel(timestamp) {
            if (!lastTimestamp) {
                lastTimestamp = timestamp;
            }

            const deltaTime = timestamp - lastTimestamp;
            lastTimestamp = timestamp;

            scrollLeft += scrollSpeed * deltaTime / 60; // Normalize speed
            if (scrollLeft >= container.scrollWidth / 2) {
                scrollLeft = 0;
            }
            container.style.transform = `translateX(-${scrollLeft}px)`;
            requestAnimationFrame(animateCarousel);
        }

        let lastTimestamp = null;
        requestAnimationFrame(animateCarousel);
    });


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
        if (words.length) setTyper(element, words);
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

        startTyping();

        function startTyping() {
            wordTypeInterval = setInterval(typeLetter, LETTER_TYPE_DELAY);
        }

        function typeLetter() {
            const word = words[wordIndex];

            if (direction == DIRECTION_FORWARDS) {
                letterIndex++;

                if (letterIndex == word.length) {
                    direction = DIRECTION_BACKWARDS;
                    clearInterval(wordTypeInterval);
                    setTimeout(startTyping, WORD_STAY_DELAY);
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