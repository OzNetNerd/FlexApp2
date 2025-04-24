// Highlights animation
document.addEventListener('DOMContentLoaded', function () {
    const highlights = document.querySelectorAll('.highlight-item');
    let currentHighlight = 0;
    let interval;

    // Initialize first highlight
    if (highlights.length > 0) {
        highlights[0].classList.add('active');
    }

    function showHighlight(index) {
        highlights.forEach(item => item.classList.remove('active'));
        highlights[index].classList.add('active');
        currentHighlight = index;
    }

    function nextHighlight() {
        let next = currentHighlight + 1;
        if (next >= highlights.length) next = 0;
        showHighlight(next);
    }

    function prevHighlight() {
        let prev = currentHighlight - 1;
        if (prev < 0) prev = highlights.length - 1;
        showHighlight(prev);
    }

    function startRotation() {
        interval = setInterval(nextHighlight, 4000);
    }

    function stopRotation() {
        clearInterval(interval);
    }

    const nextBtn = document.querySelector('.btn-highlight-next');
    const prevBtn = document.querySelector('.btn-highlight-prev');

    if (nextBtn && prevBtn) {
        nextBtn.addEventListener('click', function () {
            stopRotation();
            nextHighlight();
            startRotation();
        });

        prevBtn.addEventListener('click', function () {
            stopRotation();
            prevHighlight();
            startRotation();
        });

        startRotation();
    }
});
