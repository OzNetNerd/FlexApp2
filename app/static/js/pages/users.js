// Initialize the highlights slider
document.addEventListener('DOMContentLoaded', function() {
  const container = document.querySelector('.highlights-container');
  const items = document.querySelectorAll('.highlight-item');
  let currentIndex = 0;

  document.querySelector('.btn-highlight-next').addEventListener('click', function() {
    currentIndex = (currentIndex + 1) % items.length;
    container.scrollTo({
      left: currentIndex * container.offsetWidth,
      behavior: 'smooth'
    });
  });

  document.querySelector('.btn-highlight-prev').addEventListener('click', function() {
    currentIndex = (currentIndex - 1 + items.length) % items.length;
    container.scrollTo({
      left: currentIndex * container.offsetWidth,
      behavior: 'smooth'
    });
  });

  // Auto-scroll highlights
  setInterval(() => {
    document.querySelector('.btn-highlight-next').click();
  }, 5000);

  // Initialize user activity chart
  const ctx = document.getElementById('userActivityChart').getContext('2d');
  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: JSON.parse('{{ activity_data.labels|tojson }}'),
      datasets: [
        {
          label: 'Notes Created',
          borderColor: 'rgba(40, 167, 69, 0.8)',
          backgroundColor: 'rgba(40, 167, 69, 0.1)',
          tension: 0.3,
          data: JSON.parse('{{ activity_data.notes|tojson }}')
        },
        {
          label: 'Opportunities Created',
          borderColor: 'rgba(0, 123, 255, 0.8)',
          backgroundColor: 'rgba(0, 123, 255, 0.1)',
          tension: 0.3,
          data: JSON.parse('{{ activity_data.opportunities|tojson }}')
        },
        {
          label: 'Logins',
          borderColor: 'rgba(255, 193, 7, 0.8)',
          backgroundColor: 'rgba(255, 193, 7, 0.1)',
          tension: 0.3,
          borderDash: [5, 5],
          data: JSON.parse('{{ activity_data.logins|tojson }}')
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: {
            display: false
          }
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Activity Count'
          }
        }
      },
      plugins: {
        tooltip: {
          mode: 'index',
          intersect: false
        },
        legend: {
          position: 'top'
        }
      }
    }
  });
});