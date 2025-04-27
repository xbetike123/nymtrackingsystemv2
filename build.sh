#!/usr/bin/env bash
# build.sh

# Install Python deps
pip install -r requirements.txt

# Migrate database
python manage.py migrate

# Collect static files (for admin_views dashboard)
python manage.py collectstatic --noinput
