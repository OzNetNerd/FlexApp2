"""Constants for the SRS spaced repetition algorithm."""

# Time intervals
MIN_INTERVAL = 1 / 144  # 10 minutes in days
SHORT_INTERVAL = 1 / 24  # 1 hour in days
MEDIUM_INTERVAL = 1 / 4  # 6 hours in days
DAY_INTERVAL = 1.0  # 1 day

# Initial intervals
GOOD_INITIAL_INTERVAL = 3.0  # 3 days for good initial rating

# Multipliers for intervals
EASY_MULTIPLIER = 2.0  # Multiplier for "easy" rating
GOOD_MULTIPLIER = 1.5  # Multiplier for "good" rating
HARD_MULTIPLIER = 1.2  # Multiplier for "hard" rating

# Ease factor parameters
DEFAULT_EASE_FACTOR = 2.0  # Starting ease factor for new cards
MIN_EASE_FACTOR = 1.3  # Minimum ease factor
MAX_EASE_FACTOR = 2.5  # Maximum ease factor

# Ease factor adjustments
FAIL_EASE_PENALTY = 0.2  # Penalty for "again" rating
HARD_EASE_PENALTY = 0.15  # Penalty for "hard" rating
EASY_EASE_BONUS = 0.1  # Bonus for "easy" rating

# Maximum allowed interval
MAX_INTERVAL = 365  # Max 1 year interval

# Rating mappings from UI ratings (0-5) to FSRS/SM2 ratings (1-4)
UI_TO_FSRS_RATING = {0: 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 4}

# Learning stage thresholds (in days)
LEARNING_THRESHOLD = 1.0  # Cards with interval <= 1 day are in learning phase
REVIEWING_THRESHOLD = 21.0  # Cards with interval <= 21 days are in review phase
MASTERY_THRESHOLD = 30.0  # Cards with interval >= 30 days are considered mastered

# Difficulty thresholds (ease factor)
HARD_THRESHOLD = 1.5  # Cards with ease factor <= 1.5 are hard
MEDIUM_THRESHOLD = 2.0  # Cards with ease factor < 2.0 are medium difficulty
# Cards with ease factor >= 2.0 are easy

# Performance thresholds (success percentage)
STRUGGLING_THRESHOLD = 60  # Cards with success rate < 60% are struggling
AVERAGE_THRESHOLD = 85  # Cards with success rate <= 85% are average
# Cards with success rate > 85% are strong