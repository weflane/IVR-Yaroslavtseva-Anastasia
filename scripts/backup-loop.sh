#!/bin/bash
set -u
INTERVAL=$(( ${BACKUP_INTERVAL_HOURS:-24} * 3600 ))
KEEP=${BACKUP_KEEP_DAYS:-14}
mkdir -p /backups

while true; do
  file="/backups/bookmatch-$(date -u +%Y%m%d-%H%M%S).archive.gz"
  if mongodump --uri="$MONGODB_URL" --archive="$file.tmp" --gzip --quiet; then
    mv "$file.tmp" "$file"
    echo "[backup] OK: $file ($(du -h "$file" | cut -f1))"
  else
    rm -f "$file.tmp"
    echo "[backup] ОШИБКА: не удалось сделать копию" >&2
    [ "${ONCE:-0}" = "1" ] && exit 1
  fi
  find /backups -name 'bookmatch-*.archive.gz' -mtime +"$KEEP" -delete
  [ "${ONCE:-0}" = "1" ] && exit 0
  sleep "$INTERVAL"
done
