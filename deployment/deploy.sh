#!/bin/bash

# Deployment script for Telegram bot
# This script updates and redeploys the bot safely

set -e

echo "========================================="
echo "Bot Deployment Script"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "Error: main.py not found. Are you in the project root?"
    exit 1
fi

# Backup current database
echo ""
echo "Step 1: Creating backup..."
if [ -f "data/botrobo.db" ]; then
    BACKUP_NAME="data/backup_$(date +%Y%m%d_%H%M%S).db"
    cp data/botrobo.db "$BACKUP_NAME"
    print_success "Database backed up to $BACKUP_NAME"
else
    print_warning "No database file found to backup"
fi

# Pull latest code (if using git)
echo ""
echo "Step 2: Updating code..."
if [ -d ".git" ]; then
    git pull
    print_success "Code updated from git"
else
    print_warning "Not a git repository, skipping git pull"
fi

# Stop the bot
echo ""
echo "Step 3: Stopping bot..."
docker-compose down
print_success "Bot stopped"

# Rebuild Docker image
echo ""
echo "Step 4: Rebuilding Docker image..."
docker-compose build --no-cache
print_success "Docker image rebuilt"

# Start the bot
echo ""
echo "Step 5: Starting bot..."
docker-compose up -d
print_success "Bot started"

# Wait a bit for startup
echo ""
echo "Waiting for bot to initialize..."
sleep 10

# Check health
echo ""
echo "Step 6: Checking health..."
if docker-compose exec -T app python healthcheck.py; then
    print_success "Health check passed!"
else
    print_error "Health check failed!"
    echo ""
    echo "Showing recent logs:"
    docker-compose logs --tail=50
    exit 1
fi

# Show status
echo ""
echo "========================================="
echo "Deployment completed successfully!"
echo "========================================="
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop bot:         docker-compose down"
echo "  Restart bot:      docker-compose restart"
echo "  Check status:     docker-compose ps"
echo ""
