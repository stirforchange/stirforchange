#!/bin/bash
# Run this on the server to backup the database before any git pull
# Usage: bash backup_db.sh
BACKUP_DIR="/var/www/backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
cp /var/www/stirforchange/db.sqlite3 $BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3
echo "✅ Database backed up to $BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3"
# Keep only last 10 backups
ls -t $BACKUP_DIR/db_backup_*.sqlite3 | tail -n +11 | xargs -r rm
echo "✅ Old backups cleaned up"
