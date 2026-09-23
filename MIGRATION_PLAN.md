# Hire Rabbits Suite Migration Plan

This file explains the production migration in two parts:

1. Database migration to Layerbase MariaDB.
2. App migration to a VPS/server.

The shortest safe path is to keep the same Frappe/MariaDB architecture and move only the database out of Docker. Do not convert this stack to PostgreSQL for launch.

## Target Production Architecture

```text
User Browser
  -> Domain + HTTPS
      -> VPS reverse proxy: Nginx or Caddy
          -> Frappe app container/process
              -> Layerbase MariaDB
              -> Redis on VPS
              -> persistent site files on VPS
```

Production services:

| Service | Where it runs | Why |
| --- | --- | --- |
| Frappe app | VPS | Needs Python, Node assets, workers, scheduler, socket.io |
| Redis | VPS | Required for Frappe cache, queue, socket.io |
| MariaDB | Layerbase | Managed DB, avoids VPS disk/database maintenance |
| Public/private files | VPS volume first | Fastest safe launch; can move to S3/R2 later |
| Reverse proxy | VPS | HTTPS, domain routing, websocket routing |

Current local source:

```text
C:\Users\admin\suite
```

Current local URL:

```text
http://suite.localhost:8010
```

Current local Docker services:

```text
suite-frappe
suite-mariadb
suite-redis
```

---

# Part 1: Database Migration To Layerbase

## 1.1 Goal

Move the Frappe site database from local Docker MariaDB to Layerbase MariaDB without changing the app stack.

Keep:

```text
Frappe -> MariaDB
```

Do not do:

```text
Frappe -> PostgreSQL
```

Reason: ERPNext, HRMS, India Payroll, CRM, and Helpdesk are safest on MariaDB/MySQL-compatible storage. PostgreSQL is not the launch path for this suite.

## 1.2 Layerbase Database Choice

Create a Layerbase **MariaDB** database.

Required values from Layerbase:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
TLS/SSL requirement, if any
```

Recommended naming:

```text
Database name: hirerabbits_suite
User name: hirerabbits_suite_user
```

Use a strong password and save it in a secure place. Do not commit database passwords into GitHub.

## 1.3 Pre-Migration Checklist

Before taking a dump:

```text
[ ] Local suite opens at http://suite.localhost:8010
[ ] Login works: Administrator / admin
[ ] /desk opens
[ ] /crm opens
[ ] /helpdesk opens
[ ] /desk/hr-setup opens
[ ] /hrms opens
[ ] No one is actively changing data during dump
[ ] Current repo is pushed or backed up
[ ] Docker volumes are not deleted
```

Check local containers:

```powershell
cd C:\Users\admin\suite
docker compose ps
```

Check installed apps:

```powershell
docker exec -w /home/frappe/frappe-bench suite-frappe bench --site suite.localhost list-apps
```

Expected apps:

```text
frappe
erpnext
hrms
india_payroll
telephony
helpdesk
crm
```

## 1.4 Find Current Local Database Name

Run:

```powershell
docker exec -w /home/frappe/frappe-bench suite-frappe cat sites/suite.localhost/site_config.json
```

Look for:

```json
"db_name": "..."
```

At the time this plan was written, the local DB name was:

```text
_b92b2ce89c02344d
```

But always confirm before dumping.

## 1.5 Backup Local Site Config

On the VPS and local machine, keep a copy of:

```text
sites/suite.localhost/site_config.json
sites/common_site_config.json
```

Local command:

```powershell
cd C:\Users\admin\suite
docker exec -w /home/frappe/frappe-bench suite-frappe bash -lc "mkdir -p /home/frappe/backups && cp sites/suite.localhost/site_config.json /home/frappe/backups/site_config.local.json && cp sites/common_site_config.json /home/frappe/backups/common_site_config.local.json"
```

## 1.6 Dump Local MariaDB

Use `mariadb-dump` from inside the database container.

PowerShell:

```powershell
cd C:\Users\admin\suite
docker exec suite-mariadb mariadb-dump `
  -uroot `
  -padmin `
  --single-transaction `
  --routines `
  --triggers `
  --events `
  --default-character-set=utf8mb4 `
  _b92b2ce89c02344d `
  > suite.sql
```

If the DB name is different, replace `_b92b2ce89c02344d`.

The output file should be:

```text
C:\Users\admin\suite\suite.sql
```

Check file size:

```powershell
Get-Item C:\Users\admin\suite\suite.sql | Select-Object FullName,Length
```

## 1.7 Create A Manual Backup Inside Frappe Too

This gives you a Frappe-native backup in addition to raw SQL.

```powershell
docker exec -w /home/frappe/frappe-bench suite-frappe bench --site suite.localhost backup --with-files
```

Backup files land inside:

```text
/home/frappe/frappe-bench/sites/suite.localhost/private/backups
```

Copy them out if needed:

```powershell
docker cp suite-frappe:/home/frappe/frappe-bench/sites/suite.localhost/private/backups C:\Users\admin\suite\tmp\frappe-backups
```

## 1.8 Import SQL Into Layerbase

Use any MariaDB/MySQL client that can reach Layerbase.

Example:

```powershell
mariadb `
  -h LAYERBASE_HOST `
  -P LAYERBASE_PORT `
  -u LAYERBASE_USER `
  -p `
  LAYERBASE_DB_NAME `
  < C:\Users\admin\suite\suite.sql
```

If Layerbase requires SSL/TLS, add the Layerbase-provided SSL option. The exact flag depends on what Layerbase gives you.

Common options look like:

```text
--ssl
--ssl-ca=path\to\ca.pem
```

Use whatever Layerbase dashboard documents for that database.

## 1.9 Validate Imported Database

Run basic counts on Layerbase:

```sql
show tables;
select count(*) from `tabDocType`;
select count(*) from `tabUser`;
select count(*) from `tabInstalled Applications`;
select count(*) from `tabWorkspace`;
```

Expected approximate values from current local site:

```text
DocTypes: 1064
Workspaces: 31
Roles: 59
```

Exact counts can change after migrations.

## 1.10 Layerbase Connectivity Test From App Server

From the VPS, test DB connection before starting Frappe:

```bash
mariadb -h LAYERBASE_HOST -P LAYERBASE_PORT -u LAYERBASE_USER -p LAYERBASE_DB_NAME -e "select 1;"
```

If this fails, fix networking, IP allowlist, TLS, username, password, or DB name before touching Frappe config.

## 1.11 Update Frappe Site Config For Layerbase

In production `sites/suite.localhost/site_config.json`, set:

```json
{
  "db_type": "mariadb",
  "db_host": "LAYERBASE_HOST",
  "db_port": 3306,
  "db_name": "LAYERBASE_DB_NAME",
  "db_user": "LAYERBASE_USER",
  "db_password": "LAYERBASE_PASSWORD"
}
```

Keep existing non-DB values if present.

Do not commit this file with real credentials.

## 1.12 DB Rollback Plan

If production fails after switching to Layerbase:

1. Stop Frappe app on VPS.
2. Point `site_config.json` back to old/local MariaDB or restore old DB config.
3. Restart Frappe.
4. If Layerbase import was bad, drop/recreate Layerbase DB and import again.

Do not delete local Docker volumes until production has run safely for a few days.

---

# Part 2: App Migration To Server

## 2.1 Goal

Move the Frappe app from local Docker to a VPS/server while using Layerbase for MariaDB.

Keep on VPS:

```text
Frappe app
Redis
site files
reverse proxy
```

Move out of VPS:

```text
MariaDB -> Layerbase
```

## 2.2 Server Choice

Use a VPS, not shared hosting.

Minimum launch VPS:

```text
2 vCPU
4 GB RAM
40+ GB disk
Ubuntu 22.04 or 24.04
```

Better small production VPS:

```text
4 vCPU
8 GB RAM
80+ GB disk
Ubuntu 22.04 or 24.04
```

Why VPS is required:

- Frappe needs long-running Python processes.
- Frappe needs background workers.
- Frappe needs Redis.
- Frappe needs scheduler jobs.
- Frappe needs socket.io/websocket routing.
- Shared hosting usually blocks this model.

## 2.3 Production Domain Plan

Example domains:

```text
app.hirerabbits.com
suite.hirerabbits.com
```

Point DNS A record to VPS IP:

```text
A app.hirerabbits.com -> VPS_PUBLIC_IP
```

Use HTTPS with Caddy or Nginx + Certbot.

Caddy is the shortest path if allowed:

```text
app.hirerabbits.com {
  reverse_proxy 127.0.0.1:8010
}
```

Nginx is fine too, but needs more config.

## 2.4 Production Repo Layout

On VPS:

```text
/opt/hirerabbits/suite
  docker-compose.yml
  setup.sh
  install.sh
  patches/
  brand/
  ARCHITECTURE.md
  MIGRATION_PLAN.md
```

Clone:

```bash
sudo mkdir -p /opt/hirerabbits
sudo chown -R $USER:$USER /opt/hirerabbits
cd /opt/hirerabbits
git clone https://github.com/anishdeo90-ops/RabbitSuite.git suite
cd suite
```

## 2.5 App Environment File

Create a production `.env` on VPS:

```env
SITE=app.hirerabbits.com
ADMIN_PASSWORD=CHANGE_THIS
DB_ROOT_PASSWORD=not-used-if-no-local-db
FRAPPE_BRANCH=version-16
ERPNEXT_BRANCH=version-16
HRMS_BRANCH=version-16
INDIA_PAYROLL_BRANCH=version-16
TELEPHONY_BRANCH=develop
HELPDESK_BRANCH=main
CRM_BRANCH=main
```

Do not commit `.env`.

## 2.6 Production Docker Compose Shape

For production with Layerbase, the compose should run:

```text
suite-frappe
suite-redis
```

It should not require `suite-mariadb` once Layerbase is connected.

Recommended production compose idea:

```yaml
services:
  suite-redis:
    image: redis:8-alpine
    restart: unless-stopped
    volumes:
      - suite_redis_data:/data

  suite-frappe:
    image: frappe/bench:latest
    restart: unless-stopped
    depends_on:
      - suite-redis
    working_dir: /home/frappe
    command: >
      bash -lc 'cd /home/frappe/frappe-bench && bench start'
    environment:
      SITE: ${SITE}
      ADMIN_PASSWORD: ${ADMIN_PASSWORD}
      FRAPPE_BRANCH: ${FRAPPE_BRANCH:-version-16}
      ERPNEXT_BRANCH: ${ERPNEXT_BRANCH:-version-16}
      HRMS_BRANCH: ${HRMS_BRANCH:-version-16}
      INDIA_PAYROLL_BRANCH: ${INDIA_PAYROLL_BRANCH:-version-16}
      TELEPHONY_BRANCH: ${TELEPHONY_BRANCH:-develop}
      HELPDESK_BRANCH: ${HELPDESK_BRANCH:-main}
      CRM_BRANCH: ${CRM_BRANCH:-main}
    ports:
      - "8010:8000"
      - "9010:9000"
    volumes:
      - suite_bench:/home/frappe

volumes:
  suite_redis_data:
  suite_bench:
```

For the first production run, it is okay to temporarily keep the local MariaDB service until Layerbase is verified. The final production target should not depend on local MariaDB.

## 2.7 App Install On VPS

The existing `install.sh` creates a local site using MariaDB root credentials. For Layerbase production, the safest path is:

1. Build the bench and install apps.
2. Restore/copy the migrated `site_config.json` with Layerbase DB credentials.
3. Run migrate.

Expected commands after repo clone:

```bash
cd /opt/hirerabbits/suite
docker compose up -d suite-redis suite-frappe
docker compose cp install.sh suite-frappe:/tmp/install-suite.sh
docker compose cp patches suite-frappe:/tmp/suite-patches
```

Then enter the container:

```bash
docker exec -it suite-frappe bash
```

Inside container, expected bench path:

```bash
cd /home/frappe/frappe-bench
```

If bench does not exist yet, initialize it and get apps using the same app order as local.

## 2.8 Copy Site Files

From local Docker, copy files:

```powershell
cd C:\Users\admin\suite
docker cp suite-frappe:/home/frappe/frappe-bench/sites/suite.localhost/public/files C:\Users\admin\suite\tmp\public-files
docker cp suite-frappe:/home/frappe/frappe-bench/sites/suite.localhost/private/files C:\Users\admin\suite\tmp\private-files
```

Upload to VPS, then place them in production site:

```text
/home/frappe/frappe-bench/sites/app.hirerabbits.com/public/files
/home/frappe/frappe-bench/sites/app.hirerabbits.com/private/files
```

If the production site keeps the name `suite.localhost` internally, place files under that site folder instead. Better production name is the real domain:

```text
app.hirerabbits.com
```

## 2.9 Site Name Decision

Recommended production site name:

```text
app.hirerabbits.com
```

Local site name:

```text
suite.localhost
```

If you rename site for production, ensure:

```bash
bench setup add-domain app.hirerabbits.com --site suite.localhost
```

Or create/restore using the production site name directly.

Shortest path:

```text
Keep site folder as suite.localhost internally, add production domain as route.
```

Cleaner long-term path:

```text
Use app.hirerabbits.com as the production site folder.
```

For first launch, shortest path wins.

## 2.10 Configure Redis On VPS

In `sites/common_site_config.json`:

```json
{
  "redis_cache": "redis://suite-redis:6379/0",
  "redis_queue": "redis://suite-redis:6379/1",
  "redis_socketio": "redis://suite-redis:6379/2",
  "socketio_port": 9000,
  "webserver_port": 8000
}
```

## 2.11 Run App Migrations

After DB config points to Layerbase:

```bash
docker exec -w /home/frappe/frappe-bench suite-frappe bench --site suite.localhost migrate
docker exec -w /home/frappe/frappe-bench suite-frappe bench --site suite.localhost clear-cache
docker compose restart suite-frappe
```

If production site is named `app.hirerabbits.com`, use that instead of `suite.localhost`.

## 2.12 Build Assets

Run:

```bash
docker exec -w /home/frappe/frappe-bench suite-frappe bench build
```

If only one app changed later:

```bash
docker exec -w /home/frappe/frappe-bench suite-frappe bench build --app crm
docker exec -w /home/frappe/frappe-bench suite-frappe bench build --app helpdesk
docker exec -w /home/frappe/frappe-bench suite-frappe bench build --app hrms
```

## 2.13 Reverse Proxy Requirements

Proxy must support:

```text
HTTP
WebSocket/socket.io
large uploads
long requests
HTTPS
```

Caddy short config idea:

```text
app.hirerabbits.com {
  reverse_proxy 127.0.0.1:8010
}
```

If socket.io has issues, route socket traffic explicitly to port `9010`.

Nginx idea:

```nginx
server {
    server_name app.hirerabbits.com;

    client_max_body_size 100m;

    location / {
        proxy_pass http://127.0.0.1:8010;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:9010;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 2.14 Production Smoke Test

After deployment, test these URLs:

```text
https://app.hirerabbits.com/api/method/ping
https://app.hirerabbits.com/desk
https://app.hirerabbits.com/crm
https://app.hirerabbits.com/helpdesk
https://app.hirerabbits.com/desk/hr-setup
https://app.hirerabbits.com/hrms
```

Expected ping:

```json
{"message":"pong"}
```

Manual workflow tests:

```text
[ ] Login works
[ ] Desk opens
[ ] ERP workspace opens
[ ] HR Setup opens
[ ] CRM lead list opens
[ ] Create test CRM lead
[ ] Helpdesk opens
[ ] Create test ticket
[ ] HRMS employee PWA opens
[ ] File upload works
[ ] PDF/print works if needed
[ ] App dropdown routes work
[ ] PWA install prompt appears where expected
```

## 2.15 Backups After Production

Minimum backup plan:

```text
Layerbase DB backup/manual snapshot
VPS /home/frappe/frappe-bench/sites backup
GitHub repo backup
```

Daily backup target:

```text
DB dump + public files + private files
```

Do not rely only on Docker volumes.

## 2.16 App Rollback Plan

If production app fails:

1. Keep Layerbase DB untouched.
2. Stop Frappe container.
3. Roll back repo to previous commit.
4. Re-run setup/patch copy/build.
5. Restart Frappe.
6. If DB migration already ran and caused schema problems, restore Layerbase DB backup.

Rollback commands depend on the deployment script, but the idea is:

```bash
git checkout PREVIOUS_COMMIT
docker compose restart suite-frappe
```

If code and DB schema both changed, DB restore may be required.

## 2.17 Final Go-Live Order

Use this exact order:

```text
1. Create Layerbase MariaDB.
2. Dump local DB.
3. Import DB into Layerbase.
4. Verify Layerbase DB counts.
5. Provision VPS.
6. Clone RabbitSuite repo to VPS.
7. Start Redis and Frappe app.
8. Point Frappe site_config to Layerbase.
9. Copy public/private files.
10. Run migrate + build + clear-cache.
11. Configure reverse proxy + HTTPS.
12. Test all routes.
13. Point real DNS.
14. Keep local Docker untouched as rollback for a few days.
```

## 2.18 What Not To Do Yet

Skip these for first launch:

```text
Postgres migration
Supabase migration
Kubernetes
Multi-server workers
S3/R2 file storage
Custom auth rewrite
Custom API gateway
Separate frontend deployment
```

Add them only after the MariaDB + VPS version is stable.
