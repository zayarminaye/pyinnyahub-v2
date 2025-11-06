#!/usr/bin/env bash
# Build script for Render deployment
# This runs automatically on every deploy

set -o errexit  # Exit on error

echo "🚀 Starting build process..."

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🗂️  Collecting static files..."
python manage.py collectstatic --no-input

echo "🗄️  Running database migrations..."
python manage.py migrate

echo "📧 Initializing notification settings..."
python manage.py init_notification_settings || echo "⚠️  Notification settings may already exist"

echo "✅ Build completed successfully!"
