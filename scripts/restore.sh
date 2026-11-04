#!/bin/bash
set -e
cd "$(dirname "$0")/.."
FILE="${1:?Укажите файл копии, например backups/bookmatch-YYYYMMDD-HHMMSS.archive.gz}"
[ -f "$FILE" ] || { echo "Файл не найден: $FILE"; exit 1; }
read -r -p "Заменить данные в базе данными из $FILE? [y/N] " answer
[ "$answer" = "y" ] || { echo "Отменено"; exit 0; }
docker compose run --rm --no-deps \
  -v "$(pwd)/$FILE:/restore.archive.gz:ro" \
  --entrypoint bash backup -c '
    base=$(echo "$MONGODB_URL" | sed -E "s#^(mongodb(\+srv)?://[^/]+)/[^?]*#\1/#")
    mongorestore --uri="$base" --archive=/restore.archive.gz --gzip \
      --nsInclude="${MONGODB_DB_NAME:-bookmatch}.*" --drop'
echo "Готово"
