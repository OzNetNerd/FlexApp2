document.addEventListener('DOMContentLoaded', function() {
  const items = document.querySelectorAll('.highlight-item');

  if (!items.length) return;

  let currentIndex = 0;
  let autoPlayInterval;
  let isPlaying = true;

  items[0].classList.add('active');

  const nextBtn = document.querySelector('.btn-highlight-next');
  const prevBtn = document.querySelector('.btn-highlight-prev');
  const playPauseBtn = document.querySelector('.btn-highlight-playpause');

  // Add play/pause button if it doesn't exist
  if (!playPauseBtn && nextBtn && prevBtn) {
    const newBtn = document.createElement('button');
    newBtn.className = 'btn btn-sm btn-outline-secondary btn-highlight-playpause ms-1 me-1';
    newBtn.innerHTML = '<i class="fas fa-pause"></i>';
    prevBtn.insertAdjacentElement('afterend', newBtn);
  }

  // Function to start autoplay
  function startAutoPlay() {
    autoPlayInterval = setInterval(() => {
      if (nextBtn) nextBtn.click();
    }, 5000);
  }

  // Initial autoplay
  startAutoPlay();

  // Setup button event handlers
  document.querySelector('.btn-highlight-playpause').addEventListener('click', function() {
    isPlaying = !isPlaying;

    if (isPlaying) {
      this.innerHTML = '<i class="fas fa-pause"></i>';
      startAutoPlay();
    } else {
      this.innerHTML = '<i class="fas fa-play"></i>';
      clearInterval(autoPlayInterval);
    }
  });

  if (nextBtn) {
    nextBtn.addEventListener('click', function() {
      items[currentIndex].classList.remove('active');
      currentIndex = (currentIndex + 1) % items.length;
      items[currentIndex].classList.add('active');
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', function() {
      items[currentIndex].classList.remove('active');
      currentIndex = (currentIndex - 1 + items.length) % items.length;
      items[currentIndex].classList.add('active');
    });
  }
});