#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

docker compose up -d suite-mariadb suite-redis suite-frappe
docker compose cp install.sh suite-frappe:/tmp/install-suite.sh
docker compose cp patches suite-frappe:/tmp/suite-patches
docker compose exec -T suite-frappe bash /tmp/install-suite.sh
docker compose restart suite-frappe

echo "Open: http://suite.localhost:8010"
echo "Login: Administrator / admin"
