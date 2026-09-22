# Hire Rabbits Suite Architecture

This document explains the current local Hire Rabbits Suite build in `C:\Users\admin\suite`.

The suite is one Frappe site with multiple Frappe apps installed into the same bench. It is not a custom rewrite yet. The current goal is:

- one login
- one database
- one permission system
- one employee record
- ERP, HRMS, Payroll, Support, and CRM available from one site
- light branding and app-switching patches on top

## Current Status

Local URL:

```text
http://suite.localhost:8010
```

Login:

```text
Administrator / admin
```

Primary entry points:

| Area | URL | Type | Main user |
| --- | --- | --- | --- |
| Main Desk / ERP | `/desk` | Frappe Desk | Admin, managers, operations |
| HRMS admin | `/desk/hr-setup` | Frappe Desk workspace | HR, managers |
| HRMS employee app | `/hrms` | Vue/Ionic PWA | Employees |
| CRM | `/crm` | Vue SPA/PWA | Sales users, sales managers |
| Support | `/helpdesk` | Vue SPA/PWA | Support agents, support managers |
| Support customer portal | `/helpdesk/my-tickets` | Vue SPA/PWA | Customers |

ERPNext does not have a separate `/erp` app. ERPNext lives inside Frappe Desk as workspaces such as Organization, Accounting, Selling, Buying, Stock, Assets, Projects, Quality, Manufacturing, and ERPNext Settings.

## Code Lineage

Current upstream apps and branches:

| App | Source repo | Branch | Installed version |
| --- | --- | --- | --- |
| Frappe Framework | `https://github.com/frappe/frappe` | `version-16` | `16.34.0` |
| ERPNext | `https://github.com/frappe/erpnext` | `version-16` | `16.35.0` |
| HRMS | `https://github.com/frappe/hrms` | `version-16` | `16.19.0` |
| India Payroll | `https://github.com/frappe/india-payroll` | `version-16` | `16.0.4` |
| Telephony | `https://github.com/frappe/telephony` | `develop` | `0.0.1` |
| Helpdesk | `https://github.com/frappe/helpdesk` | `main` | `1.30.1` |
| CRM | `https://github.com/frappe/crm` | `main` | `1.84.0` |

The local repo does not store the full upstream app source. It stores:

- Docker orchestration
- install scripts
- brand assets
- patch overlays

The live app source is inside the Docker volume at:

```text
/home/frappe/frappe-bench/apps
```

The local overlay files live at:

```text
C:\Users\admin\suite\patches
```

During setup, `install.sh` copies those patches into the live app source inside the container.

## Runtime Architecture

Docker services:

| Service | Container | Purpose |
| --- | --- | --- |
| `suite-frappe` | `suite-frappe` | Frappe bench, Python backend, frontend assets, workers, socket server |
| `suite-mariadb` | `suite-mariadb` | MariaDB database |
| `suite-redis` | `suite-redis` | Cache, queue, socket.io broker |

Published ports:

| Host port | Container port | Purpose |
| --- | --- | --- |
| `8010` | `8000` | Frappe web server |
| `9010` | `9000` | Socket.io |

Main config:

```text
sites/common_site_config.json
sites/suite.localhost/site_config.json
```

Current site database config:

```text
db_type: mariadb
db_host: suite-mariadb
db_port: 3306
redis_cache: redis://suite-redis:6379/0
redis_queue: redis://suite-redis:6379/1
redis_socketio: redis://suite-redis:6379/2
```

## Setup Flow

Windows entry:

```powershell
cd C:\Users\admin\suite
.\setup.ps1
```

Linux/macOS entry:

```bash
cd /path/to/suite
./setup.sh
```

What setup does:

1. Starts MariaDB, Redis, and Frappe containers.
2. Copies `install.sh` into `suite-frappe`.
3. Copies `patches/` into `suite-frappe`.
4. Runs `/tmp/install-suite.sh` inside the container.
5. Restarts `suite-frappe`.

What `install.sh` does:

1. Creates `/home/frappe/frappe-bench` if missing.
2. Configures Frappe to use `suite-mariadb` and `suite-redis`.
3. Clones apps into the bench if they are missing.
4. Copies patch overlays into the app source.
5. Creates the `suite.localhost` site if missing.
6. Installs apps in this order:
   - `erpnext`
   - `hrms`
   - `india_payroll`
   - `telephony`
   - `helpdesk`
   - `crm`
7. Runs `bench --site suite.localhost migrate`.

Daily start/stop:

```powershell
docker compose start
docker compose stop
```

Avoid `docker compose down -v` unless you want to delete the database and bench volumes.

## Data Model

Frappe stores metadata and business records in MariaDB tables. Each DocType maps to a SQL table named:

```text
tab{DocType Name}
```

Examples:

| DocType | Table |
| --- | --- |
| User | `tabUser` |
| Employee | `tabEmployee` |
| Company | `tabCompany` |
| Customer | `tabCustomer` |
| Item | `tabItem` |
| CRM Lead | `tabCRM Lead` |
| CRM Deal | `tabCRM Deal` |
| HD Ticket | `tabHD Ticket` |
| Salary Slip | `tabSalary Slip` |

Current live metadata counts:

| Metadata | Count |
| --- | ---: |
| DocTypes | 1064 |
| Workspaces | 31 |
| Roles | 59 |

DocType JSON files by app source:

| App | DocType JSON files |
| --- | ---: |
| Frappe | 287 |
| ERPNext | 626 |
| HRMS | 160 |
| India Payroll | 6 |
| Telephony | 8 |
| Helpdesk | 36 |
| CRM | 44 |

## Main Business Objects

Core identity:

| Object | Owner app | Purpose |
| --- | --- | --- |
| User | Frappe | Login identity and roles |
| Role | Frappe | Named permission bundle |
| Role Profile | Frappe | Assign many roles to a user |
| User Permission | Frappe | Row-level style restriction by linked record |
| Employee | ERPNext + HRMS override | Person in company |
| Company | ERPNext | Legal/company entity |
| Department | ERPNext/HRMS | Org structure |
| Branch | ERPNext/HRMS | Location/org split |
| Designation | ERPNext/HRMS | Job title |

ERP:

| Object | Purpose |
| --- | --- |
| Customer | Customer master |
| Supplier | Supplier master |
| Item | Product/service master |
| Sales Order | Sales order |
| Sales Invoice | Billing |
| Purchase Order | Procurement |
| Stock Entry | Inventory movement |
| Project | Project tracking |

HRMS and payroll:

| Object | Purpose |
| --- | --- |
| Leave Application | Employee leave request |
| Attendance | Attendance record |
| Employee Checkin | Punch/check-in record |
| Expense Claim | Employee reimbursement |
| Salary Component | Salary earning/deduction part |
| Salary Structure | Salary rules |
| Salary Structure Assignment | Employee salary assignment |
| Payroll Entry | Payroll run |
| Salary Slip | Employee salary slip |
| Income Tax Slab | Tax rules |
| Form 16 | India payroll tax document |
| TDS Return | India payroll statutory return |

CRM:

| Object | Purpose |
| --- | --- |
| CRM Lead | Sales lead |
| CRM Deal | Sales opportunity |
| CRM Organization | Company/account |
| CRM Contacts | Person/contact |
| CRM Task | Follow-up work |
| FCRM Note | Notes |
| CRM Call Log | Calls |
| CRM Product | CRM product mapping |

Support:

| Object | Purpose |
| --- | --- |
| HD Ticket | Support ticket |
| HD Agent | Support agent |
| HD Team | Support team |
| HD Customer | Helpdesk customer |
| HD Article | Knowledge base article |
| HD Service Level Agreement | SLA policy |
| HD Ticket Status | Ticket status |
| HD Ticket Priority | Ticket priority |

## Frontend Architecture

There are two frontend types.

Frappe Desk:

- URL prefix: `/desk`
- Rendered by Frappe Framework.
- Uses Workspaces, DocType forms, list views, reports, dashboards, permissions, and server-rendered boot data.
- ERPNext, HRMS manager/admin, Payroll, India Payroll, and Admin live here.

Standalone app frontends:

- CRM: Vue app at `/crm`
- Helpdesk: Vue app at `/helpdesk`
- HRMS employee app: Vue/Ionic app at `/hrms`

These standalone frontends still use the same Frappe backend session, database, permissions, and `/api/method` endpoints.

## App Navigation

The intended high-level user experience is:

```text
Login
  -> Desk launcher
      -> ERP       -> /desk
      -> Admin     -> /app or Desk admin workspace/pages
      -> HRMS      -> /desk/hr-setup
      -> CRM       -> /crm
      -> Support   -> /helpdesk
```

Inside CRM and Support, the app dropdown shows sibling apps:

```text
ERP      -> /desk
HRMS     -> /desk/hr-setup
CRM      -> /crm
Support  -> /helpdesk
```

Inside HRMS Desk, the header dropdown is the normal Frappe Desk dropdown. The custom patch adds an `Install app` option only there, pointing users toward the HRMS employee PWA.

## Desk Workspaces

Current visible/internal workspaces:

| Workspace | Module | Notes |
| --- | --- | --- |
| Financial Reports | Accounts | ERP reports |
| Invoicing | Accounts | ERP invoicing |
| Assets | Assets | ERP fixed assets |
| Buying | Buying | ERP purchasing |
| Users | Core | User/admin area |
| Helpdesk | Helpdesk | Helpdesk desk workspace |
| Expenses | HR | HRMS |
| HR Setup | HR | Main manager/HR HRMS entry |
| Leaves | HR | HRMS leave management |
| Performance | HR | HRMS performance |
| Recruitment | HR | HRMS hiring |
| Shift & Attendance | HR | HRMS attendance |
| Tenure | HR | HRMS tenure |
| India Payroll | India Payroll | India statutory payroll |
| Integrations | Integrations | Integration settings |
| Manufacturing | Manufacturing | ERP manufacturing |
| Payroll | Payroll | Payroll |
| Tax & Benefits | Payroll | Payroll/tax |
| Projects | Projects | ERP projects |
| Quality | Quality Management | ERP quality |
| Selling | Selling | ERP sales |
| ERPNext Settings | Setup | ERP settings |
| Home | Setup | Desk home |
| Stock | Stock | ERP inventory |
| Subcontracting | Subcontracting | ERP subcontracting |
| Website | Website | Frappe website tools |

Hidden but installed workspaces include Build, Welcome Workspace, CRM, and Support.

## Route Map

Routes in this suite are connected in two ways:

1. Browser-level navigation between apps, for example `/helpdesk` to `/crm`.
2. In-app navigation inside one frontend, for example `/crm/leads/view/list` to `/crm/leads/{leadId}`.

Frappe keeps the same login session across all of them, so moving between apps does not create a new login boundary.

### CRM Routes

Base path: `/crm`

| Route | Purpose |
| --- | --- |
| `/` | Default CRM page |
| `/dashboard` | CRM dashboard |
| `/notifications` | Notifications |
| `/leads/view/:viewType?` | Lead list/view |
| `/leads/:leadId` | Lead detail |
| `/deals/view/:viewType?` | Deal list/view |
| `/deals/:dealId` | Deal detail |
| `/notes/view/:viewType?` | Notes |
| `/tasks/view/:viewType?` | Tasks |
| `/contacts/view/:viewType?` | Contacts list/view |
| `/contacts/:contactId` | Contact detail |
| `/organizations/view/:viewType?` | Organization list/view |
| `/organizations/:organizationId` | Organization detail |
| `/call-logs/view/:viewType?` | Call logs |
| `/data-import` | Data import list |
| `/data-import/doctype/:doctype` | New import for DocType |
| `/data-import/:importName` | Import detail |
| `/welcome` | Welcome/onboarding |
| `/onboarding` | Onboarding flow |
| `/not-permitted` | Permission failure |

Key code:

```text
apps/crm/frontend/src/router.js
patches/crm/frontend/src/components/UserDropdown.vue
patches/crm/frontend/vite.config.js
```

### Helpdesk Routes

Base path: `/helpdesk`

| Route | Purpose |
| --- | --- |
| `/` | Default Helpdesk route |
| `/home` | Agent home |
| `/tickets` | Ticket list |
| `/tickets/:ticketId` | Ticket detail |
| `/tickets/new/:templateId?` | New ticket |
| `/notifications` | Notifications |
| `/kb` | Knowledge base admin |
| `/search` | Search |
| `/kb/articles/:articleId` | Article detail |
| `/articles/new/:id` | New article |
| `/customers` | Customer list |
| `/customers/:id` | Customer detail |
| `/contacts` | Contact list |
| `/contacts/:id` | Contact detail |
| `/agents` | Agent list |
| `/teams` | Team list |
| `/teams/:teamId` | Team detail |
| `/dashboard` | Helpdesk dashboard |
| `/call-logs` | Call logs |
| `/my-tickets` | Customer portal tickets |
| `/my-tickets/:ticketId` | Customer ticket detail |
| `/my-tickets/new` | Customer new ticket |
| `/kb-public` | Public/customer KB |
| `/kb-public/:categoryId` | Public/customer KB category |
| `/kb-public/articles/:articleId` | Public/customer KB article |
| `/onboarding` | Onboarding |

Key code:

```text
apps/helpdesk/desk/src/router/index.ts
patches/helpdesk/desk/src/composables/useApps.ts
patches/helpdesk/desk/src/components/layouts/Sidebar.vue
patches/helpdesk/desk/src/components/layouts/MobileSidebar.vue
patches/helpdesk/desk/vite.config.js
```

### HRMS Employee PWA Routes

Base path: `/hrms`

| Route | Purpose |
| --- | --- |
| `/` | HRMS app shell |
| `/home` | Employee home |
| `/dashboard/attendance` | Attendance dashboard |
| `/dashboard/leaves` | Leaves dashboard |
| `/dashboard/expense-claims` | Expense dashboard |
| `/dashboard/salary-slips` | Salary slips dashboard |
| `/login` | Login |
| `/forgot-password` | Forgot password |
| `/profile` | Employee profile |
| `/notifications` | Notifications |
| `/settings` | App settings |
| `/change-password` | Change password |
| `/invalid-employee` | Missing employee mapping |
| `/leave-applications` | Leave applications |
| `/leave-applications/new` | New leave application |
| `/leave-applications/:id` | Leave detail |
| `/expense-claims` | Expense claims |
| `/expense-claims/new` | New expense claim |
| `/expense-claims/:id` | Expense claim detail |
| `/attendance-requests` | Attendance requests |
| `/attendance-requests/new` | New attendance request |
| `/attendance-requests/:id` | Attendance request detail |
| `/shift-requests` | Shift requests |
| `/shift-requests/new` | New shift request |
| `/shift-requests/:id` | Shift request detail |
| `/shift-assignments` | Shift assignments |
| `/shift-assignments/new` | New shift assignment |
| `/shift-assignments/:id` | Shift assignment detail |
| `/employee-checkins` | Employee checkins |
| `/employee-advances` | Employee advances |
| `/employee-advances/new` | New employee advance |
| `/employee-advances/:id` | Employee advance detail |
| `/salary-slips/:id` | Salary slip detail |

Key code:

```text
apps/hrms/frontend/src/router/index.js
apps/hrms/frontend/src/router/leaves.js
apps/hrms/frontend/src/router/claims.js
apps/hrms/frontend/src/router/attendance.js
apps/hrms/frontend/src/router/advances.js
apps/hrms/frontend/src/router/salary_slips.js
patches/hrms/frontend/src/views/Profile.vue
patches/hrms/frontend/src/components/InstallPrompt.vue
patches/hrms/frontend/vite.config.js
```

### HRMS Manager/Admin Routes

Base path: `/desk`

Important HRMS workspaces:

| Route | Purpose |
| --- | --- |
| `/desk/hr-setup` | Main HR setup/home |
| `/desk/employee` | Employee list |
| `/desk/leave-application` | Leave applications |
| `/desk/attendance` | Attendance |
| `/desk/employee-checkin` | Checkins |
| `/desk/expense-claim` | Expense claims |
| `/desk/payroll-entry` | Payroll runs |
| `/desk/salary-slip` | Salary slips |

Frappe Desk routes are generated from DocType and Workspace metadata. A DocType route usually follows:

```text
/desk/{doctype-route-name}
```

Example:

```text
Employee -> /desk/employee
Salary Slip -> /desk/salary-slip
HD Ticket -> /desk/hd-ticket
```

## Route Connection Flow

This is the practical forward/backtracking map for the current app.

### Global App Switching

Forward path from main suite:

```text
/desk
  -> app launcher/dropdown
      -> /desk              ERP/Admin
      -> /desk/hr-setup     HRMS manager/admin
      -> /crm               CRM
      -> /helpdesk          Support
      -> /hrms              HRMS employee PWA when opened directly
```

Backtracking path:

```text
/crm or /helpdesk
  -> app dropdown
      -> ERP    -> /desk
      -> HRMS   -> /desk/hr-setup
      -> CRM    -> /crm
      -> Support -> /helpdesk

/desk/hr-setup
  -> Desk breadcrumb / browser back / app launcher
      -> other Desk workspaces
      -> app launcher apps
```

Code controlling this:

```text
patches/crm/frontend/src/components/UserDropdown.vue
patches/helpdesk/desk/src/composables/useApps.ts
patches/hrms/hrms/hooks.py
```

### CRM Forward/Backtracking

Forward path:

```text
/crm
  -> /crm/leads/view/:viewType?
      -> /crm/leads/:leadId
          -> related notes/tasks/comments/calls
  -> /crm/deals/view/:viewType?
      -> /crm/deals/:dealId
  -> /crm/contacts/view/:viewType?
      -> /crm/contacts/:contactId
  -> /crm/organizations/view/:viewType?
      -> /crm/organizations/:organizationId
```

Backtracking path:

```text
detail page
  -> browser back or list breadcrumb
      -> same list/viewType
          -> CRM sidebar
              -> another CRM module or app dropdown
```

Main data touched:

```text
CRM Lead
CRM Deal
CRM Contacts
CRM Organization
CRM Task
FCRM Note
CRM Call Log
```

Main APIs live in:

```text
apps/crm/crm/api
```

### Helpdesk Forward/Backtracking

Forward path for agents:

```text
/helpdesk
  -> /helpdesk/home
  -> /helpdesk/tickets
      -> /helpdesk/tickets/:ticketId
          -> comments / replies / assignment / SLA activity
  -> /helpdesk/contacts
      -> /helpdesk/contacts/:id
  -> /helpdesk/customers
      -> /helpdesk/customers/:id
  -> /helpdesk/kb
      -> /helpdesk/kb/articles/:articleId
```

Forward path for customers:

```text
/helpdesk/my-tickets
  -> /helpdesk/my-tickets/new
  -> /helpdesk/my-tickets/:ticketId
  -> /helpdesk/kb-public
      -> /helpdesk/kb-public/:categoryId
      -> /helpdesk/kb-public/articles/:articleId
```

Backtracking path:

```text
ticket/detail page
  -> browser back or sidebar
      -> ticket list / home
          -> app dropdown
              -> ERP / HRMS / CRM
```

Main data touched:

```text
HD Ticket
HD Agent
HD Team
HD Customer
HD Article
HD Service Level Agreement
```

Main APIs live in:

```text
apps/helpdesk/helpdesk/api
```

### HRMS Forward/Backtracking

There are two HRMS flows.

Manager/HR flow:

```text
/desk/hr-setup
  -> Employee
      -> /desk/employee
      -> /desk/employee/{employeeId}
  -> Leaves
      -> /desk/leave-application
  -> Attendance
      -> /desk/attendance
      -> /desk/employee-checkin
  -> Payroll
      -> /desk/payroll-entry
      -> /desk/salary-slip
```

Employee PWA flow:

```text
/hrms
  -> /hrms/home
  -> /hrms/leave-applications
      -> /hrms/leave-applications/new
      -> /hrms/leave-applications/:id
  -> /hrms/attendance-requests
      -> /hrms/attendance-requests/new
      -> /hrms/attendance-requests/:id
  -> /hrms/expense-claims
      -> /hrms/expense-claims/new
      -> /hrms/expense-claims/:id
  -> /hrms/profile
      -> Install app
```

Backtracking path:

```text
employee action/detail
  -> app back button / browser back
      -> list
          -> home/dashboard/profile

manager Desk form
  -> Desk breadcrumb
      -> list
          -> HR Setup workspace
```

Main data touched:

```text
Employee
Leave Application
Attendance
Attendance Request
Employee Checkin
Expense Claim
Payroll Entry
Salary Slip
```

Main APIs live in:

```text
apps/hrms/hrms/api
```

### ERP Forward/Backtracking

ERPNext is not a separate SPA. It is Desk metadata and DocType routes.

Forward path:

```text
/desk
  -> ERP workspace
      -> list view
          -> document form
              -> linked document / report / print
```

Example:

```text
/desk
  -> Selling
      -> Customer
          -> /desk/customer
              -> /desk/customer/{customerId}
```

Backtracking path:

```text
document form
  -> breadcrumb
      -> list view
          -> workspace
              -> Desk home/app launcher
```

Main data touched:

```text
Company
Customer
Supplier
Item
Sales Order
Sales Invoice
Purchase Order
Stock Entry
Project
```

## Backend/API Architecture

Frappe provides two API styles.

Resource API:

```text
/api/resource/{DocType}
/api/resource/{DocType}/{name}
```

Examples:

```text
/api/resource/Employee
/api/resource/CRM Lead
/api/resource/HD Ticket
/api/resource/Salary Slip
```

Method API:

```text
/api/method/{python.dotted.path}
```

Examples already used by these apps:

```text
/api/method/ping
/api/method/frappe.apps.get_apps
/api/method/helpdesk.api.onboarding.get_first_ticket
/api/method/helpdesk.api.onboarding.get_general_category_id
/api/method/hrms.api.get_reports_to_employee_name
/api/method/hrms.api.get_doctype_fields
```

Important API source folders:

```text
apps/crm/crm/api
apps/helpdesk/helpdesk/api
apps/hrms/hrms/api
apps/erpnext/erpnext/crm/frappe_crm_api.py
```

Frontend data calls use Frappe session cookies. The apps do not have separate auth systems.

## Authentication

The whole suite uses Frappe authentication:

| Layer | Detail |
| --- | --- |
| Login page | Frappe login |
| Session | Frappe session cookie |
| User record | `User` DocType |
| Employee mapping | `Employee` linked to user |
| App access | Role and permission checks |

One login works across `/desk`, `/crm`, `/helpdesk`, and `/hrms`.

## Permission Architecture

Frappe does not use Supabase-style SQL RLS. The permission layer is application-level and metadata-driven.

Core permission tools:

| Tool | Purpose |
| --- | --- |
| Role | Grants permission groups |
| Role Profile | Assigns many roles to one user |
| DocType Permission | Controls read/write/create/delete per DocType |
| User Permission | Restricts records by linked value, like Company, Employee, Department |
| Permission Query Conditions | Python filters for list queries |
| Has Permission Hook | Python decision for individual records |
| Workflow | Approval/state transitions |

Planned practical model:

| Person type | Frappe mapping |
| --- | --- |
| Employee | User + Employee + Employee Self Service style roles |
| Manager | User + Employee + reports_to hierarchy + manager roles |
| HR Manager | HR roles + Employee/Leave/Attendance/Payroll permissions as needed |
| Payroll Manager | Payroll roles + salary/tax access |
| Support Agent | Helpdesk agent roles + HD Agent record |
| Sales User | CRM user roles |
| Sales Manager | CRM manager roles |
| System Manager | Full admin role |

Record isolation should be handled in this order:

1. Native DocType permissions.
2. Role Profiles for bundles.
3. User Permissions for company/employee/department/team scoping.
4. Permission query hooks only when native rules cannot express it.
5. Custom `has_permission` hooks only for special cases.

## App Connections

High-level data connections:

```text
User
  -> Employee
      -> Department / Branch / Designation / Manager
      -> Leave / Attendance / Expense / Payroll

CRM Lead / Deal
  -> CRM Organization / CRM Contacts
  -> Customer or ERPNext sync where configured

HD Ticket
  -> HD Customer / Contact
  -> Agent / Team
  -> SLA / Article / Reply

ERPNext
  -> Customer / Supplier / Item / Sales / Buying / Stock / Accounts
```

Navigation connections:

```text
Desk launcher
  -> ERP workspaces
  -> HR Setup workspace
  -> CRM SPA
  -> Helpdesk SPA

CRM dropdown
  -> ERP / HRMS / Helpdesk

Helpdesk dropdown
  -> ERP / HRMS / CRM

HRMS desk dropdown
  -> Install app action for HRMS employee PWA
```

## Branding and PWA Install

Brand files:

```text
brand/hirerabbits-mark.svg
brand/hirerabbits-icon.png
brand/hirerabbits-banner.png
```

Current PWA names:

| App | Manifest name | Start URL |
| --- | --- | --- |
| CRM | Hire Rabbits CRM | `/crm` |
| Helpdesk | Hire Rabbits Helpdesk | `/helpdesk` |
| HRMS employee app | Hire Rabbits HRMS | `/hrms` |

Install buttons:

| Location | Code |
| --- | --- |
| CRM dropdown | `patches/crm/frontend/src/components/UserDropdown.vue` |
| Helpdesk desktop dropdown | `patches/helpdesk/desk/src/components/layouts/Sidebar.vue` |
| Helpdesk mobile dropdown | `patches/helpdesk/desk/src/components/layouts/MobileSidebar.vue` |
| HRMS employee profile | `patches/hrms/frontend/src/views/Profile.vue` |
| HRMS Desk dropdown | `patches/hrms/hrms/public/js/hirerabbits_desk_install.js` |

ERPNext currently has no separate installable app. If an ERP install action is added later, it should install/open the main Desk route `/desk`.

## Patch Overlay Map

The custom code is intentionally small.

| Patch file | Applies to | What it changes |
| --- | --- | --- |
| `patches/crm/frontend/src/components/UserDropdown.vue` | CRM | Adds app switcher overrides, hides internal apps, adds install action |
| `patches/crm/frontend/vite.config.js` | CRM | Rebrands PWA manifest |
| `patches/helpdesk/desk/src/composables/useApps.ts` | Helpdesk | App switcher routes: ERP, HRMS, CRM, Support |
| `patches/helpdesk/desk/src/components/layouts/Sidebar.vue` | Helpdesk | Adds install action and Hire Rabbits help title |
| `patches/helpdesk/desk/src/components/layouts/MobileSidebar.vue` | Helpdesk | Adds mobile install action |
| `patches/helpdesk/desk/vite.config.js` | Helpdesk | Rebrands PWA manifest |
| `patches/hrms/hrms/hooks.py` | HRMS | Sets HRMS Desk home to `/desk/hr-setup`, includes custom Desk JS |
| `patches/hrms/hrms/public/js/hirerabbits_desk_install.js` | HRMS Desk | Adds Install app item to HR Setup dropdown |
| `patches/hrms/frontend/src/components/InstallPrompt.vue` | HRMS employee PWA | Rebrands install prompt and handles install event |
| `patches/hrms/frontend/src/views/Profile.vue` | HRMS employee PWA | Adds Install app row in profile settings |
| `patches/hrms/frontend/vite.config.js` | HRMS employee PWA | Rebrands PWA manifest |

## Build and Asset Flow

Frappe backend assets:

```text
bench build
bench build --app hrms
bench build --app crm
bench build --app helpdesk
```

Frontend output paths:

| App | Frontend source | Built assets |
| --- | --- | --- |
| CRM | `apps/crm/frontend` | `apps/crm/crm/public/frontend` |
| Helpdesk | `apps/helpdesk/desk` | `apps/helpdesk/helpdesk/public/desk` |
| HRMS PWA | `apps/hrms/frontend` | `apps/hrms/hrms/public/frontend` |

After patching frontend code, rebuild the affected app and restart/clear cache if the browser still serves old assets.

Useful commands:

```bash
docker exec -w /home/frappe/frappe-bench suite-frappe bench --site suite.localhost clear-cache
docker compose restart suite-frappe
```

## Deployment Shape

Current local deployment:

```text
Windows repo
  -> docker compose
      -> suite-frappe
          -> /home/frappe/frappe-bench
              -> apps/*
              -> sites/suite.localhost
      -> suite-mariadb
      -> suite-redis
```

Production should use the same shape:

```text
Server
  -> app container / bench
  -> MariaDB database
  -> Redis
  -> persistent files volume
  -> reverse proxy + HTTPS
```

Do not move this stack to PostgreSQL/Supabase right now. Frappe Framework has some Postgres support, but ERPNext/HRMS/Payroll are MariaDB-first and MariaDB is the tested path. For fastest safe launch, keep MariaDB.

Layerbase or another managed MariaDB-compatible service can replace `suite-mariadb` later if it supports the MariaDB version/features Frappe needs. The app container still needs Redis and persistent files.

## What To Explain To Another Developer

This is the clean short version:

```text
Hire Rabbits Suite is a single Frappe v16 site called suite.localhost.
It installs ERPNext, HRMS, India Payroll, Telephony, Helpdesk, and CRM into one bench.
MariaDB stores all business data and Frappe metadata.
Redis handles cache, queues, and socket events.
Frappe Desk is the ERP/admin/HR manager interface.
CRM, Helpdesk, and HRMS employee app are separate Vue PWAs using the same Frappe session and backend APIs.
Custom code is currently only patch overlays for branding, app switching, PWA names, install actions, and HRMS routing.
Permissions should be built with Frappe Roles, Role Profiles, User Permissions, and only then custom permission hooks.
```

## Next Architecture Decisions

These are the next decisions before heavy customization:

1. Final role matrix: employee, manager, HR manager, payroll manager, sales, support, admin.
2. Company/department scoping rules for records.
3. Whether CRM contacts should sync into ERPNext Customer/Contact.
4. Whether Helpdesk customers should sync into ERPNext Customer/Contact.
5. Whether ERP install should mean browser PWA for `/desk`.
6. Production database provider: local MariaDB, managed MariaDB, or cloud VM MariaDB.
7. Backup plan for database plus private/public files.

## Local Verification Commands

Check app list:

```bash
docker exec -w /home/frappe/frappe-bench suite-frappe bench --site suite.localhost list-apps
```

Check site config:

```bash
docker exec -w /home/frappe/frappe-bench suite-frappe cat sites/suite.localhost/site_config.json
```

Check server health:

```powershell
Invoke-WebRequest http://suite.localhost:8010/api/method/ping
```

Expected response:

```json
{"message":"pong"}
```
