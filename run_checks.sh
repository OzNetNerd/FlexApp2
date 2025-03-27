#!/bin/bash

set -e

APP_DIR="app"                # <-- Replace with your actual Flask app dir
MYPY_REPORT_DIR="mypy_report"
LINE_LENGTH=120

echo "🧼 Formatting code with black (line length $LINE_LENGTH)..."
black --line-length $LINE_LENGTH "$APP_DIR"

echo ""
echo "🔍 Running unit tests with coverage..."
coverage run -m pytest
coverage report -m
coverage html
echo "📄 HTML test coverage report generated at htmlcov/index.html"

echo ""
echo "🔍 Checking type coverage with mypy..."
mypy --txt-report "$MYPY_REPORT_DIR" "$APP_DIR"
echo "📄 Type coverage report generated at $MYPY_REPORT_DIR/index.txt"

echo ""
echo "✅ Done. Open htmlcov/index.html in your browser to view the coverage report."
