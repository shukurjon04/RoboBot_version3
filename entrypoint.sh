#!/bin/bash
set -e

echo "========================================="
echo "Bot Startup Sequence"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="

# Function for error handling
error_exit() {
    echo "ERROR: $1" >&2
    exit 1
}

# Check if .env file exists
if [ ! -f .env ]; then
    error_exit ".env file not found!"
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs data

# Run pre-start script
echo "Running pre-start checks..."
python -m app.pre_start || error_exit "Pre-start script failed"

# Run migrations
echo "Running database migrations..."
alembic upgrade head || error_exit "Migration failed"

# Check database connection
echo "Checking database connection..."
python -u check_db_tables.py || echo "WARNING: Database check failed (non-critical)"

echo "-----------------------------------------"
echo "Startup checks completed."
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Starting main.py now..."
echo "========================================="

# Start the bot with unbuffered output
exec python -u main.py
