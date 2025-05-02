document.addEventListener('DOMContentLoaded', function() {
  const items = document.querySelectorAll('.highlight-item');

  if (!items.length) return;

  let currentIndex = 0;
  items[0].classList.add('active');

  const nextBtn = document.querySelector('.btn-highlight-next');
  const prevBtn = document.querySelector('.btn-highlight-prev');

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

  // Auto-rotate every 5 seconds
  setInterval(() => {
    if (nextBtn) nextBtn.click();
  }, 5000);
});