#!/bin/bash
set -e

# Run pre-start script
echo "Run pre-start script..."
python -m app.pre_start

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Start the bot
echo "Starting bot..."
exec python main.py
