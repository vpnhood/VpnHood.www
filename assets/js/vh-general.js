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

document.addEventListener('DOMContentLoaded', function () {

    // The desktop mega-menu hover overlay (#vhOverlay) is now driven purely by CSS
    // (body:has(.vh-mega-menu:hover) #vhOverlay) — no JS handler needed.

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
        // Clone the carousel content to create a continuous loop
        const carouselItems = container.innerHTML;
        container.innerHTML += carouselItems;

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
    // get all the elements
    const textsElements = document.querySelectorAll('.multiTextWriter');

    // make an array of word arrays, each sub-array for a different .typing-text element
    const wordsSets = [
        ["More ultra-fast servers on the more locations.", "Always connect with Resilient servers.", "Include and exclude IP addresses.", "Include, exclude, or block domains.", "DNS leak protection.", "Stay Protected with Always-on VPN."],
    ];

    // apply the typing effect to each element
    textsElements.forEach((element, index) => {
        if (index < wordsSets.length) {
            setTyper(element, wordsSets[index]);
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