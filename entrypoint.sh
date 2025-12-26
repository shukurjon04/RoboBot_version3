#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z $DB_HOST 5432; do
  sleep 1
done
echo "Database is ready!"

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Start the bot
echo "Starting bot..."
exec python main.py
