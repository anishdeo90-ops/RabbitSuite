# Desk Dashboard Customization Plan

## Goal

Make the custom Desk home dashboard editable by users while preserving the current Desk shell, sidebar ordering, greeting, and work boards.

Use Ponytail as the design rule: reuse Frappe's native dashboard pieces, avoid a custom drag/drop editor, avoid new dependencies, and keep defaults/admin editing separate from per-user personalization.

## What Frappe already provides

Frappe has two related dashboard systems:

- `Dashboard` DocType plus the `/app/dashboard-view/<dashboard>` page. This is what the Build screenshot shows. It stores global dashboard defaults as Dashboard documents, with child rows for Dashboard Charts and Number Cards. Dashboard Managers/System Managers can edit these in Build.
- `frappe.widget.WidgetGroup` plus `frappe.views.DashboardView`. This is the editable user layout system. It already supports sorting, hiding, deleting, resizing, creating widgets, saving custom order, discarding, and resetting through `frappe.model.user_settings`.

The Desk home should combine those instead of inventing another editor:

- Global defaults come from one normal Dashboard document, probably `Hire Rabbits Desk`.
- The Desk home renders those defaults with native `WidgetGroup`.
- Each user saves personal changes in Frappe user settings.
- Dashboard Managers can still manage the global defaults in Build.

## Constraints

- Keep the existing Desk landing page route and current visual shell.
- Keep CRM first and ERP second in the sidebar.
- Do not re-add the old "Edit Layout" button.
- Do not mutate global Dashboard defaults when a normal user customizes their own dashboard.
- Respect Number Card and Dashboard Chart permissions.
- Use native Frappe widgets and user settings rather than custom drag/drop code.

## Implementation steps

### 1. Add a backend source for the Desk dashboard

Modify `patches/hrms/hrms/hirerabbits_home.py`.

Add constants:

- `DESK_DASHBOARD_NAME = "Hire Rabbits Desk"`
- `DESK_DASHBOARD_USER_SETTINGS_KEY = "hirerabbits_desk_home"`

Add an idempotent helper:

- `ensure_desk_dashboard()`

This creates the default Dashboard document if it is missing. It should create a non-standard Dashboard so Dashboard Managers can edit it in Build without developer mode. It should also create or reuse the default Number Cards and optional Dashboard Charts.

Add a whitelisted method:

- `get_desk_dashboard()`

Return:

- dashboard name
- permitted number cards
- permitted charts
- whether the current user can manage global defaults
- user settings key

Use Frappe's existing permission helpers where possible:

- `frappe.desk.doctype.dashboard.dashboard.get_permitted_cards`
- `frappe.desk.doctype.dashboard.dashboard.get_permitted_charts`

Keep the existing `get_home_data()` for boards and summary data until the widget dashboard fully replaces the hard-coded stats.

### 2. Seed sensible default cards

Create defaults that match the current Desk stats:

- Revenue
- Customers
- Open tickets
- Team members

Prefer native Number Card documents. If a value cannot be represented cleanly as a Document Type or Report card, use a Custom Number Card method in `hirerabbits_home.py`. Keep the methods small and permission-aware.

The default Dashboard should reference these cards through the existing `Number Card Link` child table. Optional charts can be added later through Build.

### 3. Render native widgets on the Desk home

Modify `patches/hrms/hrms/public/js/hirerabbits_desk_home.js`.

Replace the hard-coded stats grid with a native dashboard area:

- dashboard controls row
- number card `WidgetGroup`
- chart `WidgetGroup`

Use `frappe.widget.WidgetGroup` with native options:

- number cards: sorting, create, delete/hide
- charts: sorting, create, delete/hide, resize

Load saved layout from:

- `frappe.get_user_settings(DESK_DASHBOARD_USER_SETTINGS_KEY).dashboard_settings`

Save with:

- `frappe.model.user_settings.save(DESK_DASHBOARD_USER_SETTINGS_KEY, "dashboard_settings", config)`

Controls:

- `Customize`
- `Save`
- `Discard`
- `Reset`
- `Manage defaults` for Dashboard Managers, linking to the Dashboard form in Build

### 4. Keep chart creation small

Do not copy the full `DashboardView` class.

Add only the thin chart-picker logic needed by `WidgetGroup` for creating charts from the Desk home. Reuse native Dashboard Chart forms and Frappe dialogs. If this becomes too large, ship the first pass with:

- add/remove/reorder/hide existing cards
- reorder/hide/resize existing charts
- "Manage defaults" for adding new charts globally

Then add per-user chart creation in a second patch.

### 5. Style the native widget region

Modify `patches/hrms/hrms/public/css/hirerabbits_desk_home.css`.

Style only the wrapper around the native widgets:

- spacing
- control row
- empty state
- mobile stacking

Avoid restyling the internal widget system unless a visible bug appears.

### 6. Tests

Extend `patches/hrms/hrms/public/js/hirerabbits_desk_home.test.js`.

Cover:

- the old Edit Layout action is still absent
- dashboard controls render
- `WidgetGroup` receives number cards and charts from backend data
- Customize calls native widget customization
- Save persists `dashboard_settings` to the chosen user settings key
- Discard reloads the saved settings
- Reset clears personal dashboard settings
- CRM remains before ERP

Add backend tests if the local bench test harness is practical:

- default Dashboard creation is idempotent
- `get_desk_dashboard()` only returns permitted cards/charts
- non-manager users cannot manage defaults
- missing dashboard self-heals

### 7. Live verification

Run local checks:

```powershell
node --check patches/hrms/hrms/public/js/hirerabbits_desk_home.js
node patches/hrms/hrms/public/js/hirerabbits_desk_home.test.js
```

Run bench checks in Docker:

```powershell
docker exec -w /home/frappe/frappe-bench suite-frappe bench --site suite.localhost execute hrms.hirerabbits_home.get_desk_dashboard
```

Then update the running site:

- copy changed files into `suite-frappe`
- clear cache
- restart the container if assets require it
- verify `/api/method/ping`
- open `/desk`
- customize the dashboard
- save
- refresh
- confirm the saved order/settings persist
- reset
- confirm defaults return

## Review focus

- A Desk User can personalize their dashboard without Build access.
- A Dashboard Manager can edit global defaults in Build.
- Global defaults do not change when a user saves a personal layout.
- Permission-filtered cards or charts disappear cleanly.
- Mobile layout stays readable.
- The existing boards and sidebar still behave as before.

