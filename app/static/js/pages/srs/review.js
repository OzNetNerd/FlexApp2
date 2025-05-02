let intervalPreviewMap = {
  0: 0.04, // 1 hour
  1: 0.08, // 2 hours
  2: 1,    // 1 day
  3: 3,    // 3 days
  4: 7,    // 7 days
  5: 15    // 15 days
};

function describeDelay(days) {
  if (days < 1) {
    const mins = Math.round(days * 24 * 60);
    return mins < 60 ? `${mins} min` : `${Math.round(mins / 60)} hr`;
  }
  if (days < 30) return `${Math.round(days)} day${days >= 2 ? 's' : ''}`;
  const months = Math.round(days / 30);
  return `${months} month${months > 1 ? 's' : ''}`;
}

async function fetchPreviewIntervals() {
  const entityId = document.getElementById('review-form').dataset.entityId;
  console.log("Fetching preview intervals for entity ID:", entityId);

  // Set loading state
  document.getElementById('delay-preview').textContent = "(loading...)";

  try {
    // Log the request URL for debugging
    const url = `/api/srs/${entityId}/preview`;
    console.log("Fetching from:", url);

    const response = await fetch(url);
    if (!response.ok) {
      console.error("Failed to fetch preview intervals:", response.status);
      document.getElementById('delay-preview').textContent = "(using defaults)";
      updateAllRatingLabels();
      return;
    }

    // Log the raw response for debugging
    const responseText = await response.text();
    console.log("Raw response:", responseText);

    try {
      // Parse the JSON response
      const data = JSON.parse(responseText);
      console.log("Parsed interval previews:", data);

      // Check if we got valid data
      if (data && Object.keys(data).length > 0) {
        intervalPreviewMap = data;
      } else {
        console.warn("Empty response data, using defaults");
      }

      updateAllRatingLabels();
      updateLivePreview(document.getElementById('rating-slider').value || "0");
    } catch (parseError) {
      console.error("JSON parse error:", parseError);
      document.getElementById('delay-preview').textContent = "(using defaults)";
      updateAllRatingLabels();
    }
  } catch (err) {
    console.error("Network error fetching preview intervals:", err);
    document.getElementById('delay-preview').textContent = "(using defaults)";
    updateAllRatingLabels();
  }
}

function updateAllRatingLabels() {
  const select = document.getElementById('rating-select');

  // Default rating descriptions
  const ratingDescriptions = {
    0: "No recall",
    1: "Failed",
    2: "Difficult",
    3: "Hesitant",
    4: "Easy",
    5: "Perfect"
  };

  for (let i = 1; i < select.options.length; i++) {
    const option = select.options[i];
    const rating = option.value;
    const baseText = ratingDescriptions[rating] || "";
    const delay = intervalPreviewMap[rating] !== undefined ? describeDelay(intervalPreviewMap[rating]) : "?";
    option.textContent = `${rating} - ${baseText} (${delay})`;
  }
}

function updateLivePreview(value) {
  const preview = document.getElementById('delay-preview');
  const tooltip = document.getElementById('rating-slider');

  if (value === "") {
    preview.textContent = "(select rating)";
    tooltip.title = "Drag to select rating";
    return;
  }

  const days = intervalPreviewMap[value];
  const delay = days !== undefined ? describeDelay(days) : "?";
  preview.textContent = `(${delay})`;
  tooltip.title = `Next review in ${delay}`;
}

function updateRating(value) {
  if (value === "") {
    document.getElementById('rating-select').value = "";
    updateProgressBar(0);
    updateLivePreview("");
    return;
  }

  document.getElementById('rating-select').value = value;
  updateProgressBar(value);
  updateLivePreview(value);
}

function updateSlider(value) {
  document.getElementById('rating-slider').value = value;
  updateProgressBar(value === "" ? 0 : value);
  updateLivePreview(value);
}

function updateProgressBar(value) {
  const percentage = (value / 5) * 100;
  const progressBar = document.getElementById('progress-bar');
  progressBar.style.width = percentage + '%';
  progressBar.className = 'progress-bar';

  if (value <= 1) {
    progressBar.classList.add('bg-danger');
  } else if (value <= 3) {
    progressBar.classList.add('bg-warning');
  } else {
    progressBar.classList.add('bg-success');
  }
}

function toggleAnswer() {
  const answerContainer = document.getElementById('answer-container');
  const showBtn = document.getElementById('show-answer-btn');
  const visible = !answerContainer.classList.contains('d-none');
  answerContainer.classList.toggle('d-none');
  showBtn.textContent = visible ? 'Show Answer' : 'Hide Answer';
}

function updateStats(stats) {
  console.log("Updating stats:", stats);
  document.getElementById('total-cards').textContent = stats.total_cards || 0;
  document.getElementById('cards-due').textContent = stats.cards_due || 0;
  document.getElementById('cards-reviewed').textContent = stats.cards_reviewed_today || 0;
}

function showFinishedModal() {
  const modal = new bootstrap.Modal(document.getElementById('finishedModal'));
  modal.show();
}

document.addEventListener('keydown', function (event) {
  // Only process next/prev keyboard shortcuts if the buttons exist
  if (event.shiftKey && event.key === 'ArrowRight') {
    const nextBtn = document.getElementById('next-btn');
    if (nextBtn) {
      event.preventDefault();
      window.location.href = nextBtn.getAttribute('href');
    }
  }
  if (event.shiftKey && event.key === 'ArrowLeft') {
    const prevBtn = document.getElementById('prev-btn');
    if (prevBtn) {
      event.preventDefault();
      window.location.href = prevBtn.getAttribute('href');
    }
  }
  if (event.key === ' ' && document.activeElement.tagName !== 'TEXTAREA') {
    event.preventDefault();
    toggleAnswer();
  }
  if (
    document.activeElement.tagName !== 'TEXTAREA' &&
    document.activeElement.tagName !== 'SELECT' &&
    !isNaN(parseInt(event.key)) &&
    parseInt(event.key) >= 0 &&
    parseInt(event.key) <= 5
  ) {
    updateRating(event.key);
  }
});

document.getElementById('review-form').addEventListener('submit', function (e) {
  e.preventDefault();

  // Store the answer given
  const answerGiven = document.querySelector('textarea[name="answer_given"]').value || "";

  // Show the answer container
  document.getElementById('answer-container').classList.remove('d-none');

  // Show the rating section
  document.getElementById('rating-section').classList.remove('d-none');

  // Show the rating controls
  document.getElementById('rating-controls').classList.remove('d-none');

  // Hide the original submit button
  const submitBtn = document.getElementById('submit-btn');
  submitBtn.style.display = 'none';

  // Add a "Next" button
  const nextBtn = document.createElement('button');
  nextBtn.type = 'button';
  nextBtn.id = 'next-btn';
  nextBtn.className = 'btn btn-success';
  nextBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i> Next';

  // Add event listener for the next button
  nextBtn.addEventListener('click', function() {
    const rating = parseInt(document.getElementById('rating-select').value);

    // Check if rating is selected
    if (isNaN(rating)) {
      alert('Please select a rating before proceeding.');
      return;
    }

    // Call the submit review function with the collected data
    submitReview(answerGiven, rating);
  });

  // Add the next button to the container
  document.getElementById('next-button-container').appendChild(nextBtn);
});

// Function for submitting the review
async function submitReview(answerGiven, rating) {
  const form = document.getElementById('review-form');
  const entityId = form.dataset.entityId;

  // Find CSRF token by checking various possible implementations
  let csrfToken = "";
  const csrfInputs = form.querySelectorAll('input[type="hidden"]');
  for (const input of csrfInputs) {
    if (input.name && (input.name.includes('csrf') || input.name.includes('token'))) {
      csrfToken = input.value;
      break;
    }
  }

  console.log("Submitting review:", { entityId, rating, answer_given: answerGiven.substring(0, 20) + "..." });

  try {
    const response = await fetch(`/api/srs/${entityId}/review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        rating,
        answer_given: answerGiven
      })
    });

    if (!response.ok) {
      console.error("Failed to submit review:", response.status);
      throw new Error('Failed to submit review');
    }

    console.log("Review submitted successfully");

    // Refresh stats before redirecting
    const statsResponse = await fetch('/api/srs/stats');
    if (statsResponse.ok) {
      const stats = await statsResponse.json();
      console.log("Received updated stats:", stats);
      updateStats(stats);
    } else {
      console.error("Failed to fetch updated stats:", statsResponse.status);
    }

    const nextItemId = APP_CONFIG.nextItemId;
    console.log("Next item ID:", nextItemId);

    if (nextItemId) {
      window.location.href = `/srs/review/${nextItemId}`;
    } else {
      // Show the "finished" modal instead of redirecting
      showFinishedModal();
    }
  } catch (err) {
    console.error("Error submitting review:", err);
    alert('An error occurred submitting your review. Please try again.');
  }
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("Page loaded, initializing...");
  document.getElementById('rating-slider').value = "";
  fetchPreviewIntervals();
  updateAllRatingLabels();
  updateProgressBar(0);

  // Set a timeout to ensure we have values displayed even if API fails
  setTimeout(() => {
    const delayEl = document.getElementById('delay-preview');
    if (delayEl.textContent === "(loading...)") {
      console.log("API request timed out or failed, using default values");
      delayEl.textContent = "(using defaults)";
      updateAllRatingLabels();
    }
  }, 3000); // 3 second timeout
});