#!/bin/bash

# Exit on error
set -e

APP_DIR="your_flask_app"  # <-- Replace with your actual app directory
MYPY_REPORT_DIR="mypy_report"

echo "🔍 Running unit tests with coverage..."
coverage run -m pytest
coverage report -m
coverage html
echo "📄 HTML coverage report generated at htmlcov/index.html"

echo ""
echo "🔍 Checking type coverage with mypy..."
mypy --txt-report "$MYPY_REPORT_DIR" "$APP_DIR"
echo "📄 Type coverage report generated at $MYPY_REPORT_DIR/index.txt"
