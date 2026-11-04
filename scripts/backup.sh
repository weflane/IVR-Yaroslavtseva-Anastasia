#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
docker compose run --rm --no-deps -e ONCE=1 backup
