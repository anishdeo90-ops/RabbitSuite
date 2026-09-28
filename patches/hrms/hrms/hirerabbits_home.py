"""HireRabbits /desk home: KPI cards + team board. Every number comes from frappe.get_list,
so it is permission-filtered; a card or tab is left out when the user can't read its DocType."""

import frappe
from frappe.utils import add_days, add_months, get_first_day, nowdate

BOARD_LIMIT = 50  # cards fetched per tab; column counts are real totals


def _can(doctype):
	return frappe.db.exists("DocType", doctype) and frappe.has_permission(doctype, "read")


def _count(doctype, filters=None):
	return frappe.get_list(doctype, filters=filters or {}, fields=[{"COUNT": "*", "as": "n"}])[0].n


def _group_counts(doctype, field, filters=None):
	rows = frappe.get_list(doctype, filters=filters or {}, fields=[field, {"COUNT": "*", "as": "n"}], group_by=field)
	return {r[field]: r.n for r in rows}


def _revenue():
	company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
	if not company:
		return None
	this_month = get_first_day(nowdate())
	last_month = add_months(this_month, -1)

	def total(start, end):
		filters = {"docstatus": 1, "company": company, "posting_date": ["between", [start, end]]}
		return frappe.get_list("Sales Invoice", filters=filters, fields=[{"SUM": "base_grand_total", "as": "t"}])[0].t or 0

	current = total(this_month, nowdate())
	previous = total(last_month, add_days(this_month, -1))
	return {
		"key": "revenue",
		"label": "Revenue this month",
		"value": current,
		"currency": frappe.get_cached_value("Company", company, "default_currency"),
		"change_pct": round((current - previous) * 100 / previous) if previous else None,
		"route": "/desk/erp/sales-invoice",
	}


@frappe.whitelist()
def get_home_data():
	month_start = str(get_first_day(nowdate()))
	stats = []

	if _can("Sales Invoice"):
		stats.append(_revenue())
	if _can("Customer"):
		stats.append({
			"key": "customers",
			"label": "Active customers",
			"value": _count("Customer", {"disabled": 0}),
			"new_this_month": _count("Customer", {"disabled": 0, "creation": [">=", month_start]}),
			"route": "/desk/erp/customer",
		})
	if _can("HD Ticket"):
		stats.append({
			"key": "tickets",
			"label": "Open tickets",
			"value": _count("HD Ticket", {"status_category": "Open"}),
			"new_this_month": _count("HD Ticket", {"creation": [">=", month_start]}),
			"route": "/helpdesk/tickets",
		})
	if _can("Employee"):
		stats.append({
			"key": "team",
			"label": "Team members",
			"value": _count("Employee", {"status": "Active"}),
			"new_this_month": _count("Employee", {"status": "Active", "date_of_joining": [">=", month_start]}),
			"route": "/desk/hrms/employee",
		})

	return {"stats": [s for s in stats if s], "boards": _boards()}


def _options(doctype, field):
	return [o for o in (frappe.get_meta(doctype).get_field(field).options or "").split("\n") if o]


def _board(key, label, doctype, columns, fields, card, list_route, order_by="modified desc"):
	counts = _group_counts(doctype, "status")
	rows = frappe.get_list(doctype, fields=["name", "status", *fields], order_by=order_by, limit_page_length=BOARD_LIMIT)
	return {
		"key": key,
		"label": label,
		"route": list_route,
		"columns": [{**c, "count": counts.get(c["status"], 0)} for c in columns],
		"cards": [{"status": r.status, **card(r)} for r in rows],
	}


def _boards():
	boards = []

	if _can("CRM Task"):
		def task_route(r):
			if r.reference_doctype == "CRM Deal":
				return f"/crm/deals/{r.reference_docname}"
			if r.reference_doctype == "CRM Lead":
				return f"/crm/leads/{r.reference_docname}"
			return "/crm/tasks/view/list"

		boards.append(_board(
			"tasks", "Tasks", "CRM Task",
			[{"status": s, "label": s} for s in _options("CRM Task", "status")],
			["title", "priority", "assigned_to", "reference_doctype", "reference_docname"],
			lambda r: {"title": r.title, "tag": r.priority, "user": r.assigned_to, "route": task_route(r)},
			"/crm/tasks/view/list",
		))

	if _can("CRM Deal"):
		statuses = frappe.get_all("CRM Deal Status", fields=["name", "color"], order_by="position asc")
		boards.append(_board(
			"deals", "Deals", "CRM Deal",
			[{"status": s.name, "label": s.name, "color": s.color} for s in statuses],
			["organization", "lead_name", "deal_owner"],
			lambda r: {"title": r.organization or r.lead_name or r.name, "tag": "CRM", "user": r.deal_owner, "route": f"/crm/deals/{r.name}"},
			"/crm/deals/view/kanban",
		))

	if _can("HD Ticket"):
		statuses = frappe.get_all("HD Ticket Status", filters={"enabled": 1}, fields=["name", "label_agent", "color"], order_by="order asc")
		boards.append(_board(
			"tickets", "Tickets", "HD Ticket",
			[{"status": s.name, "label": s.label_agent or s.name, "color": (s.color or "").lower()} for s in statuses],
			["subject", "priority", "_assign"],
			lambda r: {"title": f"#{r.name} {r.subject or ''}".strip(), "tag": r.priority, "user": (frappe.parse_json(r._assign or "[]") or [None])[0], "route": f"/helpdesk/tickets/{r.name}"},
			"/helpdesk/tickets",
		))

	if _can("Job Applicant"):
		boards.append(_board(
			"hiring", "Hiring", "Job Applicant",
			[{"status": s, "label": s} for s in _options("Job Applicant", "status")],
			["applicant_name", "designation"],
			lambda r: {"title": r.applicant_name or r.name, "tag": r.designation, "user": None, "route": f"/desk/hrms/job-applicant/{r.name}"},
			"/desk/hrms/job-applicant",
		))

	return boards
