#!/usr/bin/env bash
# Nightly backup: Postgres dump + uploaded media, keeps last 14 days.
# Install on the server:  crontab -e
#   0 3 * * * cd /home/ubuntu/django-app && ./scripts/backup.sh >> backups/backup.log 2>&1
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p backups
STAMP=$(date +%F)

docker compose exec -T db pg_dump -U gt gtorthocare | gzip > "backups/db-$STAMP.sql.gz"
docker compose cp app:/app/media "backups/media-$STAMP" >/dev/null && tar czf "backups/media-$STAMP.tar.gz" -C backups "media-$STAMP" && rm -rf "backups/media-$STAMP"

# retention: 14 days
find backups -name "*.gz" -mtime +14 -delete

echo "$(date -Is) backup ok: db-$STAMP.sql.gz, media-$STAMP.tar.gz"
