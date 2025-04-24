#!/usr/bin/env bash
set -e

echo "Creating JavaScript structure under static/js/..."

# Base directory
BASE_DIR="static/js"

# Directories to create
dirs=(
  "services"
  "utils"
  "components"
  "table"
  "pages"
)

# Create base and subdirs
mkdir -p "$BASE_DIR"
for d in "${dirs[@]}"; do
  mkdir -p "$BASE_DIR/$d"
done

# Files to touch
files=(
  "services/apiService.js"
  "services/logger.js"
  "utils/domUtils.js"

  "components/autoComplete.js"
  "components/toasts.js"
  "components/headerButtons.js"
  "components/footerButtons.js"
  "components/pillsNav.js"

  "table/init.js"
  "table/config.js"
  "table/utils.js"
  "table/custom.js"

  "pages/base.js"
  "pages/tabs.js"
  "pages/contact.js"
  "pages/task.js"
  "pages/edit.js"
  "pages/index.js"
  "pages/notes.js"

  "main.js"
)

# Create files
for f in "${files[@]}"; do
  touch "$BASE_DIR/$f" || touch "$f"
done

echo "Structure created successfully."