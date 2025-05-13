#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p staticfiles
mkdir -p staticfiles/img

# Check if favicon exists in static/img and copy it if it does
if [ -f static/img/favicon.ico ]; then
  cp static/img/favicon.ico staticfiles/img/
else
  echo "Warning: favicon.ico not found in static/img/"
  # Create a blank favicon to prevent errors
  touch staticfiles/img/favicon.ico
fi

# Collect static files and migrate database
python manage.py collectstatic --noinput
python manage.py migrate 