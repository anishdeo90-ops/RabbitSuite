import frappe


APP_ICONS = {
	"Helpdesk": {
		"label": "Support",
		"icon_type": "App",
		"link_type": "External",
		"link": "/helpdesk",
		"app": "helpdesk",
		"logo_url": "/assets/helpdesk/desk/favicon.svg",
		"idx": 10,
	},
	"HRMS": {
		"label": "HRMS",
		"icon_type": "App",
		"link_type": "External",
		"link": "/desk/people",
		"app": "hrms",
		"logo_url": "/assets/hrms/images/frappe-hr-logo.svg",
		"idx": 20,
	},
	"CRM": {
		"label": "CRM",
		"icon_type": "App",
		"link_type": "External",
		"link": "/crm",
		"app": "crm",
		"logo_url": "/assets/crm/images/logo.svg",
		"idx": 30,
	},
	"Admin": {
		"label": "Admin",
		"icon_type": "App",
		"link_type": "Workspace Sidebar",
		"app": "frappe",
		"icon": "settings",
		"logo_url": "/assets/frappe/images/settings-gear.svg?v=2",
		"idx": 40,
	},
	"ERP": {
		"label": "ERP",
		"icon_type": "App",
		"link_type": "External",
		"link": "/app/home",
		"app": "erpnext",
		"logo_url": "/assets/erpnext/images/erpnext-logo.svg",
		"idx": 50,
	},
}

PARENTS = {
	"HRMS": (
		"Expenses",
		"HR Setup",
		"Leaves",
		"Payroll",
		"Performance",
		"Recruitment",
		"Shift & Attendance",
		"Tax & Benefits",
		"Tenure",
		"India Payroll",
	),
	"Admin": ("Users", "Build", "Automation", "Data", "Email", "Integrations", "Printing", "System", "Website"),
	"ERP": (
		"Accounting",
		"Organization",
		"Selling",
		"Buying",
		"Stock",
		"Manufacturing",
		"Projects",
		"Assets",
		"Quality",
		"Subcontracting",
		"ERPNext Settings",
	),
	"Accounting": (
		"Invoicing",
		"Payments",
		"Financial Reports",
		"Accounts Setup",
		"Taxes",
		"Banking",
		"Budget",
		"Share Management",
		"Subscription",
	),
}


def apply():
	for name, values in APP_ICONS.items():
		if not frappe.db.exists("Desktop Icon", name):
			frappe.get_doc({"doctype": "Desktop Icon", **values}).insert(ignore_permissions=True)

		for field, value in {**values, "hidden": 0, "standard": 0, "parent_icon": None}.items():
			frappe.db.set_value("Desktop Icon", name, field, value, update_modified=False)

	for label in ("Framework", "Frappe Framework", "ERPNext"):
		name = frappe.db.exists("Desktop Icon", {"label": label})
		if name:
			frappe.db.set_value("Desktop Icon", name, "hidden", 1, update_modified=False)

	for parent, children in PARENTS.items():
		for child in children:
			if frappe.db.exists("Desktop Icon", child):
				frappe.db.set_value("Desktop Icon", child, "parent_icon", parent, update_modified=False)

	frappe.clear_cache()
	frappe.db.commit()
