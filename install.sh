#!/usr/bin/env bash
set -euo pipefail

SITE="${SITE:-suite.localhost}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-admin}"
BENCH=/home/frappe/frappe-bench

FRAPPE_BRANCH="${FRAPPE_BRANCH:-version-16}"
ERPNEXT_BRANCH="${ERPNEXT_BRANCH:-version-16}"
HRMS_BRANCH="${HRMS_BRANCH:-version-16}"
INDIA_PAYROLL_BRANCH="${INDIA_PAYROLL_BRANCH:-version-16}"
TELEPHONY_BRANCH="${TELEPHONY_BRANCH:-develop}"
HELPDESK_BRANCH="${HELPDESK_BRANCH:-main}"
CRM_BRANCH="${CRM_BRANCH:-main}"

cd /home/frappe

if [ ! -d "$BENCH" ]; then
  bench init --skip-redis-config-generation --frappe-branch "$FRAPPE_BRANCH" frappe-bench
fi

cd "$BENCH"

sed -i '/^watch:/d' Procfile
bench set-config -g live_reload false
bench set-config -g db_host suite-mariadb
bench set-config -g db_port 3306
bench set-config -g redis_cache redis://suite-redis:6379/0
bench set-config -g redis_queue redis://suite-redis:6379/1
bench set-config -g redis_socketio redis://suite-redis:6379/2

get_app() {
  app="$1"
  branch="$2"
  url="$3"

  if [ -d "apps/$app" ]; then
    echo "app exists: $app"
  else
    bench get-app --branch "$branch" "$url"
  fi
}

get_app erpnext "$ERPNEXT_BRANCH" https://github.com/frappe/erpnext
get_app hrms "$HRMS_BRANCH" https://github.com/frappe/hrms
get_app india_payroll "$INDIA_PAYROLL_BRANCH" https://github.com/frappe/india-payroll
get_app telephony "$TELEPHONY_BRANCH" https://github.com/frappe/telephony
get_app helpdesk "$HELPDESK_BRANCH" https://github.com/frappe/helpdesk
get_app crm "$CRM_BRANCH" https://github.com/frappe/crm

copy_patch() {
  src="/tmp/suite-patches/$1"
  dest="$BENCH/apps/$1"

  if [ -f "$src" ]; then
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
  fi
}

copy_patch crm/frontend/src/components/UserDropdown.vue
copy_patch crm/frontend/vite.config.js
copy_patch helpdesk/desk/src/composables/useApps.ts
copy_patch helpdesk/desk/vite.config.js
copy_patch hrms/hrms/hooks.py
copy_patch hrms/frontend/vite.config.js

if [ ! -d "sites/$SITE" ]; then
  bench new-site "$SITE" \
    --db-host suite-mariadb \
    --db-port 3306 \
    --mariadb-root-username root \
    --mariadb-root-password "$DB_ROOT_PASSWORD" \
    --admin-password "$ADMIN_PASSWORD" \
    --no-mariadb-socket \
    --set-default
fi

install_app() {
  app="$1"

  if bench --site "$SITE" list-apps 2>/dev/null | awk '{print $1}' | grep -qx "$app"; then
    echo "installed: $app"
  else
    bench --site "$SITE" install-app "$app"
  fi
}

install_app erpnext
install_app hrms
install_app india_payroll
install_app telephony
install_app helpdesk
install_app crm

bench --site "$SITE" migrate
