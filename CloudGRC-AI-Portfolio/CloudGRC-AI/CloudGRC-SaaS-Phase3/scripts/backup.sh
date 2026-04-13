#!/bin/bash
# Daily PostgreSQL backup to S3
set -euo pipefail
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/tmp/cloudgrc_backup_$TIMESTAMP.sql.gz"
source /opt/cloudgrc/.env

echo "Creating backup: $BACKUP_FILE"
docker exec cloudgrc_postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$BACKUP_FILE"

if [[ -n "${AWS_ACCESS_KEY_ID:-}" ]]; then
  echo "Uploading to S3..."
  docker run --rm -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY \
    amazon/aws-cli s3 cp "$BACKUP_FILE" "s3://$S3_BUCKET_NAME/backups/$(basename $BACKUP_FILE)"
  echo "Backup uploaded to S3"
fi

# Keep only last 7 local backups
find /tmp -name "cloudgrc_backup_*.sql.gz" -mtime +7 -delete
echo "Backup complete: $BACKUP_FILE"
