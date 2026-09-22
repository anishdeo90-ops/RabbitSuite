# Hire Rabbits Suite Bench

One local Frappe site for the real first target:

- one login
- one employee record
- one permission system
- ERPNext + HRMS + India Payroll + Telephony + Helpdesk + CRM in one bench

## Run

```powershell
cd C:\Users\admin\suite
.\setup.ps1
```

Open:

```text
http://suite.localhost:8010
```

Login:

```text
Administrator / admin
```

App code is visible on Windows after setup:

```text
C:\Users\admin\suite\frappe-bench\apps
```

## Daily Start / Stop

```powershell
docker compose start
docker compose stop
```

Use `stop/start` for daily work. `down` stops containers too, but keep the named volumes if you want the bench and DB to stay.

## Branch Plan

Default is the lowest-risk stack from what is already working locally:

- `frappe`, `erpnext`, `hrms`, `india_payroll`: `version-16`
- `telephony`: `develop`
- `helpdesk`: `main`
- `crm`: `main`

If CRM or Helpdesk rejects v16 during install, switch the whole stack to `develop` with environment variables and rebuild from clean volumes. Do not mix v15 core with v16 payroll.

## Hostname

If `suite.localhost` does not resolve, add this line to `C:\Windows\System32\drivers\etc\hosts`:

```text
127.0.0.1 suite.localhost
```

Visible product name later: Hire Rabbits. This step is only the unified app foundation.
