#!/bin/bash

# Backup script for bot database and logs
# Can be run manually or via cron job

set -e

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_DIR=$(date +%Y%m)

# Create backup directory structure
mkdir -p "$BACKUP_DIR/$DATE_DIR"

echo "========================================="
echo "Bot Backup Script"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="

# Backup database
if [ -f "data/botrobo.db" ]; then
    DB_BACKUP="$BACKUP_DIR/$DATE_DIR/db_$TIMESTAMP.db"
    cp data/botrobo.db "$DB_BACKUP"
    echo "✓ Database backed up to: $DB_BACKUP"
    
    # Compress it
    gzip "$DB_BACKUP"
    echo "✓ Database compressed: $DB_BACKUP.gz"
else
    echo "⚠ No database file found"
fi

# Backup logs
if [ -d "logs" ] && [ "$(ls -A logs)" ]; then
    LOGS_BACKUP="$BACKUP_DIR/$DATE_DIR/logs_$TIMESTAMP.tar.gz"
    tar -czf "$LOGS_BACKUP" logs/
    echo "✓ Logs backed up to: $LOGS_BACKUP"
else
    echo "⚠ No logs directory or empty"
fi

# Clean old backups (keep last 30 days)
echo ""
echo "Cleaning old backups (keeping last 30 days)..."
find "$BACKUP_DIR" -type f -mtime +30 -delete
find "$BACKUP_DIR" -type d -empty -delete
echo "✓ Old backups cleaned"

echo ""
echo "========================================="
echo "Backup completed successfully!"
echo "========================================="

# Show backup size
du -sh "$BACKUP_DIR"
