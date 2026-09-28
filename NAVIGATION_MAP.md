# Hire Rabbits Navigation Map

`/desk` is the neutral logged-in Desk shell. It is not ERP.

## Canonical Roots

| Area | Root |
| --- | --- |
| Desk shell | `/desk` |
| ERP manager/admin | `/desk/erp` |
| HRMS manager/admin | `/desk/hrms` |
| HRMS employee PWA | `/hrms` |
| CRM | `/crm` |
| Support | `/helpdesk` |
| Support customer portal | `/helpdesk/my-tickets` |
| Frappe admin/system | `/desk/admin` |

## Workspace Map

| Workspace | App/module | Target route |
| --- | --- | --- |
| Financial Reports | ERPNext / Accounts | `/desk/erp/financial-reports` |
| Invoicing | ERPNext / Accounts | `/desk/erp/invoicing` |
| Assets | ERPNext / Assets | `/desk/erp/assets` |
| Buying | ERPNext / Buying | `/desk/erp/buying` |
| Manufacturing | ERPNext / Manufacturing | `/desk/erp/manufacturing` |
| Projects | ERPNext / Projects | `/desk/erp/projects` |
| Quality | ERPNext / Quality Management | `/desk/erp/quality` |
| Selling | ERPNext / Selling | `/desk/erp/selling` |
| Hire Rabbits Settings | ERPNext / Setup | `/desk/erp/settings` |
| Home | ERPNext / Setup | `/desk/erp/home` |
| Stock | ERPNext / Stock | `/desk/erp/stock` |
| Subcontracting | ERPNext / Subcontracting | `/desk/erp/subcontracting` |
| ERP CRM | ERPNext / CRM, hidden | `/desk/erp/crm` |
| ERP Support | ERPNext / Support, hidden | `/desk/erp/support` |
| Expenses | HRMS / HR | `/desk/hrms/expenses` |
| HR Setup | HRMS / HR | `/desk/hrms` |
| Leaves | HRMS / HR | `/desk/hrms/leaves` |
| Performance | HRMS / HR | `/desk/hrms/performance` |
| Recruitment | HRMS / HR | `/desk/hrms/recruitment` |
| Shift & Attendance | HRMS / HR | `/desk/hrms/shift-attendance` |
| Tenure | HRMS / HR | `/desk/hrms/tenure` |
| Payroll | HRMS / Payroll | `/desk/hrms/payroll` |
| Tax & Benefits | HRMS / Payroll | `/desk/hrms/tax-benefits` |
| India Payroll | India Payroll | `/desk/hrms/india-payroll` |
| Users | Frappe / Core | `/desk/admin/users` |
| Integrations | Frappe / Integrations | `/desk/admin/integrations` |
| Website | Frappe / Website | `/desk/admin/website` |
| Build | Frappe / Core, hidden | `/desk/admin/build` |

## DocType Route Rules

All DocType routes use the kebab-case DocType name after the area root.

| Source | Rule |
| --- | --- |
| ERPNext modules | `/desk/erp/<doctype-slug>` |
| HRMS `HR` module | `/desk/hrms/<doctype-slug>` |
| HRMS `Payroll` module | `/desk/hrms/<doctype-slug>` |
| India Payroll module | `/desk/hrms/<doctype-slug>` |
| Frappe core/admin modules | `/desk/admin/<doctype-slug>` |
| CRM standalone app | `/crm/...` |
| Helpdesk standalone app | `/helpdesk/...` |
| HRMS employee app | `/hrms/...` |

ERPNext modules covered by `/desk/erp`: Accounts, Assets, Bulk Transaction, Buying, Communication, CRM, EDI, ERPNext Integrations, Maintenance, Manufacturing, Portal, Projects, Quality Management, Regional, Selling, Setup, Stock, Subcontracting, Support, Telephony, Utilities.

HRMS modules covered by `/desk/hrms`: HR, Payroll, India Payroll.

Admin modules covered by `/desk/admin`: Automation, Contacts, Core, Custom, Desk, Email, Geo, Integrations, Printing, Website, Workflow.

## HRMS Overrides

These are ERPNext/shared master DocTypes but should appear under HRMS because users experience them as people/HR records:

| DocType | Target route |
| --- | --- |
| Employee | `/desk/hrms/employee` |
| Department | `/desk/hrms/department` |
| Designation | `/desk/hrms/designation` |
| Branch | `/desk/hrms/branch` |
| Holiday List | `/desk/hrms/holiday-list` |
| Employment Type | `/desk/hrms/employment-type` |

## Must-Fix Crumbs

| Current crumb | Correct target |
| --- | --- |
| ERP app switcher route `/desk` | `/desk/erp` |
| ERP desktop icon `/app/home` | `/desk/erp` |
| HRMS app switcher route `/desk/hr-setup` | `/desk/hrms` |
| HRMS desktop icon `/desk/people` | `/desk/hrms` |
| HRMS manager workspace `/desk/hr-setup` | `/desk/hrms` |
| Employee list `/desk/employee` | `/desk/hrms/employee` |
| Leave list `/desk/leave-application` | `/desk/hrms/leave-application` |
| Customer list `/desk/customer` | `/desk/erp/customer` |

## Implementation Rule

Do not maintain a manual page list. Read DocType module metadata, apply the rules above, then apply the HRMS override table. That covers every current and future DocType without missing new upstream pages.
