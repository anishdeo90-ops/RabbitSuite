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
		"link": "/desk/hrms",
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
		"link": "/desk/erp",
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

SINGLES = {
	("System Settings", "app_name"): "Hire Rabbits",
	("System Settings", "otp_issuer_name"): "Hire Rabbits",
	("Website Settings", "app_name"): "Hire Rabbits",
	("Website Settings", "title_prefix"): "Hire Rabbits",
	("Website Settings", "favicon"): "/files/hirerabbits-icon.png",
	("Website Settings", "app_logo"): "/files/hirerabbits-banner.png",
	("Website Settings", "splash_image"): "/files/hirerabbits-banner.png",
	("Website Settings", "brand_html"): '<img src="/files/hirerabbits-banner.png" alt="Hire Rabbits" style="height:32px; width:auto;">',
	("Website Settings", "banner_html"): '<img src="/files/hirerabbits-banner.png" alt="Hire Rabbits" style="max-width:260px; height:auto;">',
	("Website Settings", "footer_powered"): '<span class="text-muted">Hire Rabbits</span>',
	("Navbar Settings", "app_logo"): "/files/hirerabbits-banner.png",
	("OAuth Settings", "resource_name"): "Hire Rabbits Application",
}

WORKSPACES = {
	"ERPNext Settings": "Hire Rabbits Settings",
	"Frappe CRM": "Hire Rabbits CRM",
}

HRMS_DOCTYPE_OVERRIDES = {
	"Branch",
	"Department",
	"Designation",
	"Employee",
	"Employment Type",
	"Holiday List",
}

AREA_BY_APP = {
	"erpnext": "erp",
	"frappe": "admin",
	"hrms": "hrms",
	"india_payroll": "hrms",
}


def _slug(name):
	return (name or "").lower().replace(" ", "-")


@frappe.whitelist()
def get_route_map():
	modules = {
		row.name: row.app_name
		for row in frappe.get_all("Module Def", fields=["name", "app_name"], limit_page_length=0)
	}
	routes = {}

	for row in frappe.get_all(
		"DocType",
		fields=["name", "module"],
		filters={"istable": 0},
		limit_page_length=0,
	):
		area = "hrms" if row.name in HRMS_DOCTYPE_OVERRIDES else AREA_BY_APP.get(modules.get(row.module))
		if area:
			routes[_slug(row.name)] = area

	for row in frappe.get_all(
		"Workspace",
		fields=["name", "module", "app"],
		limit_page_length=0,
	):
		area = AREA_BY_APP.get(row.app or modules.get(row.module))
		if area:
			routes[_slug(row.name)] = area

	routes.update(
		{
			"erp": "erp",
			"hrms": "hrms",
			"admin": "admin",
			"erpnext-settings": "erp",
			"hr-setup": "hrms",
			"shift-&-attendance": "hrms",
		}
	)
	return routes


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

	for (doctype, field), value in SINGLES.items():
		if frappe.db.exists("DocType", doctype):
			frappe.db.set_single_value(doctype, field, value)

	for name, label in WORKSPACES.items():
		if frappe.db.exists("Workspace", name):
			frappe.db.set_value("Workspace", name, {"title": label, "label": label}, update_modified=False)

	frappe.clear_cache()
	frappe.db.commit()
