$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

docker compose up -d suite-mariadb suite-redis suite-frappe
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker compose cp install.sh suite-frappe:/tmp/install-suite.sh
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker compose cp patches suite-frappe:/tmp/suite-patches
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker compose exec -T suite-frappe bash /tmp/install-suite.sh
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker compose restart suite-frappe
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Open: http://suite.localhost:8010"
Write-Host "Login: Administrator / admin"
