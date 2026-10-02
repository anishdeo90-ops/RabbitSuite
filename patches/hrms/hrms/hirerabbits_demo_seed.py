import re
from collections import defaultdict
from datetime import date


SEED_MARKER = "hire_rabbits_suite_demo_seed_v5"
DEFAULT_COMPANY = "Hire Rabbits"


def stable_seed_name(doctype, label):
	parts = re.sub(r"[^A-Za-z0-9]+", "-", f"{doctype}-{label}").strip("-").upper()
	return f"HR-DEMO-{parts}"[:140]


def record(module, doctype, label, unique_by=None, **fields):
	return {
		"module": module,
		"doctype": doctype,
		"label": label,
		"name": stable_seed_name(doctype, label),
		"fields": fields,
		"unique_by": unique_by or [],
	}


SEED_RECORDS = [
	record("ERP", "Company", "hire rabbits demo", unique_by=["company_name"], company_name="Hire Rabbits Demo", abbr="HRD", country="India", default_currency="INR"),
	record("ERP", "Customer Group", "suite customers", unique_by=["customer_group_name"], customer_group_name="Suite Customers", is_group=0),
	record("ERP", "Supplier Group", "suite suppliers", unique_by=["supplier_group_name"], supplier_group_name="Suite Suppliers", is_group=0),
	record("ERP", "Item Group", "suite items", unique_by=["item_group_name"], item_group_name="Suite Items", is_group=0),
	record("ERP", "UOM", "suite nos", unique_by=["uom_name"], uom_name="Nos", enabled=1),
	record("Accounts", "Mode of Payment", "bank transfer", unique_by=["mode_of_payment"], mode_of_payment="Bank Transfer", type="Bank"),
	record("Accounts", "Payment Terms Template", "net 15", unique_by=["template_name"], template_name="Net 15"),
	record("Accounts", "Journal Entry", "opening adjustment", unique_by=["remark"], voucher_type="Journal Entry", company="$company", posting_date="$today", remark="Opening adjustment sample"),
	record("Accounts", "Payment Entry", "customer receipt", payment_type="Receive", company="$company", posting_date="$today", party_type="Customer", party="$customer", paid_amount=25000, received_amount=25000),
	record("Selling", "Customer", "acme retail", unique_by=["customer_name"], customer_name="Acme Retail", customer_type="Company", customer_group="$customer_group", territory="$territory"),
	record("Selling", "Lead", "walk in buyer", unique_by=["lead_name"], lead_name="Walk In Buyer", company_name="Walk In Buyer Co", status="Lead"),
	record("Selling", "Opportunity", "website implementation", unique_by=["opportunity_name"], opportunity_name="Website Implementation", opportunity_from="Customer", party_name="$customer", status="Open", opportunity_type="Sales", company="$company"),
	record("Selling", "Quotation", "website implementation", quotation_to="Customer", party_name="$customer", company="$company", transaction_date="$today", order_type="Sales"),
	record("Selling", "Sales Order", "website implementation", customer="$customer", company="$company", transaction_date="$today", delivery_date="$future", order_type="Sales"),
	record("Selling", "Sales Invoice", "website implementation", customer="$customer", company="$company", posting_date="$today", due_date="$future"),
	record("Stock", "Delivery Note", "website implementation", customer="$customer", company="$company", posting_date="$today", posting_time="10:00:00"),
	record("Buying", "Supplier", "global supplies", unique_by=["supplier_name"], supplier_name="Global Supplies", supplier_group="$supplier_group", supplier_type="Company"),
	record("Buying", "Request for Quotation", "office laptops", company="$company", transaction_date="$today", schedule_date="$future"),
	record("Buying", "Supplier Quotation", "office laptops", supplier="$supplier", company="$company", transaction_date="$today"),
	record("Buying", "Purchase Order", "office laptops", supplier="$supplier", company="$company", transaction_date="$today", schedule_date="$future"),
	record("Buying", "Purchase Invoice", "office laptops", supplier="$supplier", company="$company", posting_date="$today", bill_no="GS-001", bill_date="$today"),
	record("Stock", "Item", "consulting service", unique_by=["item_code"], item_code="HR-DEMO-SERVICE", item_name="Implementation Service", item_group="$item_group", stock_uom="$uom", is_stock_item=0, is_sales_item=1, is_purchase_item=1),
	record("Stock", "Item", "raw material", unique_by=["item_code"], item_code="HR-DEMO-RAW-MATERIAL", item_name="Demo Raw Material", item_group="$item_group", stock_uom="$uom", is_stock_item=1, is_sales_item=0, is_purchase_item=1),
	record("Stock", "Item", "finished kit", unique_by=["item_code"], item_code="HR-DEMO-FINISHED-KIT", item_name="Demo Finished Kit", item_group="$item_group", stock_uom="$uom", is_stock_item=1, is_sales_item=1, is_purchase_item=0),
	record("Stock", "Warehouse", "main stores", unique_by=["warehouse_name"], warehouse_name="Main Stores Demo", company="$company", is_group=0),
	record("Stock", "Material Request", "raw material request", material_request_type="Purchase", company="$company", transaction_date="$today", schedule_date="$future"),
	record("Stock", "Stock Entry", "material receipt", stock_entry_type="Material Receipt", company="$company", posting_date="$today", posting_time="10:00:00"),
	record("Stock", "Stock Entry", "material transfer", stock_entry_type="Material Transfer", company="$company", posting_date="$today", posting_time="11:00:00"),
	record("Stock", "Purchase Receipt", "office laptops receipt", supplier="$supplier", company="$company", posting_date="$today", posting_time="10:00:00"),
	record("Stock", "Pick List", "customer delivery pick", purpose="Delivery", customer="$customer", company="$company"),
	record("Stock", "Landed Cost Voucher", "freight allocation", company="$company", posting_date="$today"),
	record("Stock", "Stock Reconciliation", "opening stock count", company="$company", posting_date="$today", posting_time="10:00:00", purpose="Stock Reconciliation"),
	record("Stock", "Packing Slip", "customer package", delivery_note="$delivery_note", from_case_no=1, to_case_no=1),
	record("Stock", "Quality Inspection", "raw material inspection", inspection_type="Incoming", reference_type="Purchase Receipt", item_code="$raw_item", inspected_by="Administrator", report_date="$today", status="Accepted"),
	record("Manufacturing", "BOM", "finished kit bom", item="$finished_item", quantity=1, company="$company", is_active=1, is_default=1),
	record("Manufacturing", "Work Order", "finished kit work order", production_item="$finished_item", qty=5, company="$company", planned_start_date="$today"),
	record("Subcontracting", "Subcontracting BOM", "finished kit outsourced bom", finished_good="$finished_item", service_item="$service_item", company="$company", quantity=1),
	record("Subcontracting", "Subcontracting Order", "vendor assembly order", supplier="$supplier", company="$company", transaction_date="$today", schedule_date="$future"),
	record("Subcontracting", "Subcontracting Receipt", "vendor assembly receipt", supplier="$supplier", company="$company", posting_date="$today", posting_time="10:00:00"),
	record("Projects", "Project", "erp rollout", unique_by=["project_name"], project_name="ERP Rollout", status="Open", company="$company", expected_start_date="$today", expected_end_date="$future"),
	record("Projects", "Task", "configure selling", unique_by=["subject"], subject="Configure Selling", status="Open", project="$project", exp_start_date="$today", exp_end_date="$future"),
	record("Projects", "Timesheet", "implementation hours", company="$company", start_date="$today", end_date="$today"),
	record("Assets", "Asset Category", "laptops", unique_by=["asset_category_name"], asset_category_name="Demo Laptops"),
	record("Assets", "Asset", "office laptop", unique_by=["asset_name"], asset_name="Office Laptop", item_code="$raw_item", company="$company", asset_category="$asset_category", location="Head Office", purchase_date="$today", gross_purchase_amount=65000),
	record("Assets", "Asset Maintenance", "laptop maintenance", unique_by=["asset_name"], company="$company", asset_name="$asset"),
	record("Quality", "Quality Goal", "support quality", unique_by=["goal"], goal="Resolve 90% tickets on time", procedure="Weekly quality review"),
	record("Quality", "Quality Procedure", "ticket review", unique_by=["procedure"], procedure="Review support tickets weekly"),
	record("HRMS", "Department", "operations", unique_by=["department_name"], department_name="Operations", company="$company", is_group=0),
	record("HRMS", "Branch", "bengaluru hq", unique_by=["branch"], branch="Bengaluru HQ"),
	record("HRMS", "Designation", "operations manager", unique_by=["designation_name"], designation_name="Operations Manager"),
	record("HRMS", "Employee", "ananya operations", first_name="Ananya", last_name="Rao", employee_name="Ananya Rao", gender="Female", date_of_birth="1994-05-12", date_of_joining="$today", company="$company", status="Active", department="$department", branch="$branch", designation="$designation"),
	record("HRMS", "Attendance", "ananya present", employee="$employee", attendance_date="$today", status="Present", company="$company"),
	record("HRMS", "Leave Application", "ananya casual leave", employee="$employee", from_date="$future", to_date="$future", leave_type="$leave_type", status="Open", company="$company"),
	record("HRMS", "Expense Claim", "ananya travel claim", employee="$employee", company="$company", posting_date="$today", approval_status="Draft"),
	record("HRMS", "Job Opening", "support specialist", unique_by=["job_title"], job_title="Support Specialist", company="$company", status="Open", designation="$designation"),
	record("HRMS", "Job Applicant", "ravi support applicant", unique_by=["email_id"], applicant_name="Ravi Kumar", email_id="ravi.demo@example.com", status="Open", job_title="$job_opening"),
	record("Payroll", "Salary Component", "basic pay", unique_by=["salary_component"], salary_component="Demo Basic Pay", type="Earning"),
	record("Payroll", "Salary Structure", "standard salary", unique_by=["name"], name="Demo Standard Salary", company="$company", is_active="Yes", currency="INR"),
	record("Payroll", "Salary Structure Assignment", "ananya salary", employee="$employee", salary_structure="$salary_structure", company="$company", from_date="$today", base=60000),
	record("Payroll", "Payroll Entry", "monthly payroll", company="$company", posting_date="$today", payroll_frequency="Monthly", start_date="$today", end_date="$future"),
	record("Payroll", "Salary Slip", "ananya salary slip", employee="$employee", company="$company", posting_date="$today", start_date="$today", end_date="$future", payroll_frequency="Monthly"),
	record("CRM", "CRM Organization", "acme retail crm", unique_by=["organization_name"], organization_name="Acme Retail CRM"),
	record("CRM", "CRM Contacts", "priya acme", unique_by=["email"], first_name="Priya", last_name="Nair", email="priya.demo@example.com", organization="$crm_organization"),
	record("CRM", "CRM Lead", "acme expansion", unique_by=["email"], first_name="Priya", last_name="Nair", email="priya.demo@example.com", organization="$crm_organization", status="New", lead_owner="Administrator"),
	record("CRM", "CRM Deal", "acme support deal", organization="$crm_organization", contact="$crm_contact", deal_owner="Administrator", status="Qualification", annual_revenue=1200000),
	record("CRM", "CRM Task", "follow up acme", title="Follow up Acme", status="Backlog", assigned_to="Administrator", due_date="$future"),
	record("Helpdesk", "HD Customer", "acme support", unique_by=["customer_name"], customer_name="Acme Retail Support", domain="acme.example.com"),
	record("Helpdesk", "HD Team", "support desk", unique_by=["team_name"], team_name="Support Desk"),
	record("Helpdesk", "HD Agent", "administrator agent", user="Administrator"),
	record("Helpdesk", "HD Ticket", "login issue", subject="Cannot log in to employee portal", description="Demo support ticket for login trouble.", status="Open", priority="Medium", customer="$hd_customer", agent_group="$hd_team"),
	record("Helpdesk", "HD Article Category", "getting started", unique_by=["category_name"], category_name="Getting Started"),
	record("Helpdesk", "HD Article", "reset password", unique_by=["title"], title="How to reset your password", category="$hd_article_category", content="Use Forgot Password on the login page and follow the email link.", status="Published"),
	record("Helpdesk", "HD Service Level Agreement", "standard support", unique_by=["name"], name="Standard Support SLA", enabled=1, default_sla=1),
]


def seed_coverage():
	coverage = defaultdict(list)
	for record_spec in SEED_RECORDS:
		coverage[record_spec["module"]].append(record_spec["doctype"])
	return dict(coverage)


def empty_report():
	return {"created": [], "skipped": [], "failed": []}


def apply():
	import frappe

	if frappe.db.get_default(SEED_MARKER):
		return {
			"created": 0,
			"skipped": ["Suite demo seed already applied"],
			"failed": [],
			"coverage": seed_coverage(),
		}

	report = empty_report()
	context = _build_context(frappe, report)
	_run_erpnext_demo(frappe, report, context)
	_run_crm_demo(frappe, report)
	context = _build_context(frappe, report)

	for record_spec in SEED_RECORDS:
		_insert_record(frappe, record_spec, context, report)

	_backfill_dashboard_visible_data(frappe, context, report)

	if not report["failed"]:
		frappe.db.set_default(SEED_MARKER, "1")
	frappe.db.commit()
	return {
		"created": len(report["created"]),
		"skipped": len(report["skipped"]),
		"failed": report["failed"],
		"coverage": seed_coverage(),
	}


def dashboard_health():
	import frappe

	company = frappe.defaults.get_user_default("Company", user="Administrator")
	month_start = date.today().replace(day=1).isoformat()
	return {
		"default_company": company,
		"active_employees": frappe.db.count("Employee", {"status": "Active", "company": company}),
		"new_hires_this_year": frappe.db.count(
			"Employee",
			{
				"company": company,
				"date_of_joining": [">=", f"{date.today().year}-01-01"],
			},
		),
		"submitted_attendance_this_month": frappe.db.count(
			"Attendance",
			{
				"company": company,
				"docstatus": 1,
				"attendance_date": [">=", month_start],
			},
		),
		"employee_checkins": frappe.db.count("Employee Checkin"),
		"assigned_helpdesk_tickets": frappe.db.count("HD Ticket", {"_assign": ["like", "%Administrator%"]}),
		"sla_alert_tickets": frappe.db.count(
			"HD Ticket",
			{
				"_assign": ["like", "%Administrator%"],
				"sla": ["is", "set"],
				"agreement_status": ["in", ["First Response Due", "Resolution Due"]],
				"status_category": "Open",
			},
		),
		"resolved_helpdesk_tickets": frappe.db.count(
			"HD Ticket", {"_assign": ["like", "%Administrator%"], "status_category": "Resolved"}
		),
	}


def helpdesk_pending_health():
	import frappe

	filters = [
		["sla", "is", "set"],
		["agreement_status", "in", ["First Response Due", "Resolution Due"]],
		["status_category", "=", "Open"],
		["_assign", "like", "%Administrator%"],
		["creation", "between", [frappe.utils.add_months(frappe.utils.today(), -6), frappe.utils.today()]],
	]
	return {
		"count": frappe.get_list("HD Ticket", filters=filters, fields=["name", "subject", "status", "status_category", "agreement_status", "sla", "creation"], limit=20),
		"sample_assigned": frappe.get_all(
			"HD Ticket",
			filters={"_assign": ["like", "%Administrator%"]},
			fields=["name", "status", "status_category", "agreement_status", "sla", "creation"],
			limit_page_length=20,
			order_by="creation desc",
		),
	}


def list_seed_health():
	import frappe

	doctypes = [
		"Pick List",
		"Landed Cost Voucher",
		"Stock Entry",
		"Material Request",
		"Purchase Order",
		"Purchase Receipt",
		"Sales Order",
		"Sales Invoice",
		"Delivery Note",
		"Attendance",
		"Employee Checkin",
		"HD Ticket",
	]
	return {doctype: frappe.db.count(doctype) for doctype in doctypes if _doctype_exists(frappe, doctype)}


def buying_dashboard_health():
	import frappe

	company = frappe.defaults.get_user_default("Company", user="Administrator")
	year_start = f"{date.today().year}-01-01"
	return {
		"default_company": company,
		"annual_purchase": frappe.db.sql(
			"""
			select coalesce(sum(base_net_total), 0)
			from `tabPurchase Order`
			where company = %s
			  and transaction_date >= %s
			  and docstatus = 1
			  and status not in ('Draft', 'Cancelled', 'Closed')
			""",
			(company, year_start),
		)[0][0],
		"purchase_orders_to_receive": frappe.db.count(
			"Purchase Order",
			{"company": company, "docstatus": 1, "status": ["in", ["To Receive and Bill", "To Receive"]]},
		),
		"purchase_orders_to_bill": frappe.db.count(
			"Purchase Order",
			{"company": company, "docstatus": 1, "status": ["in", ["To Receive and Bill", "To Bill"]]},
		),
		"submitted_purchase_orders": frappe.db.count("Purchase Order", {"company": company, "docstatus": 1}),
		"submitted_material_requests": frappe.db.count(
			"Material Request",
			{"company": company, "docstatus": 1, "material_request_type": "Purchase"},
		),
		"submitted_purchase_receipts": frappe.db.count(
			"Purchase Receipt", {"company": company, "docstatus": 1}
		),
	}


def erp_dashboard_health():
	import frappe

	company = frappe.defaults.get_user_default("Company", user="Administrator")
	year_start = f"{date.today().year}-01-01"
	return {
		"default_company": company,
		"annual_sales": frappe.db.sql(
			"""
			select coalesce(sum(base_net_total), 0)
			from `tabSales Order`
			where company = %s
			  and modified >= %s
			  and docstatus = 1
			  and status not in ('Draft', 'Cancelled', 'Closed')
			""",
			(company, year_start),
		)[0][0],
		"sales_orders_to_deliver": frappe.db.count(
			"Sales Order",
			{"company": company, "docstatus": 1, "status": ["in", ["To Deliver and Bill", "To Deliver"]]},
		),
		"sales_orders_to_bill": frappe.db.count(
			"Sales Order",
			{"company": company, "docstatus": 1, "status": ["in", ["To Deliver and Bill", "To Bill"]]},
		),
		"submitted_sales_orders": frappe.db.count("Sales Order", {"company": company, "docstatus": 1}),
		"submitted_sales_invoices": frappe.db.count("Sales Invoice", {"company": company, "docstatus": 1}),
		"submitted_delivery_notes": frappe.db.count("Delivery Note", {"company": company, "docstatus": 1}),
		"submitted_purchase_invoices": frappe.db.count("Purchase Invoice", {"company": company, "docstatus": 1}),
		"stock_value": frappe.db.sql("select coalesce(sum(stock_value), 0) from `tabBin`")[0][0],
		"submitted_work_orders": frappe.db.count("Work Order", {"company": company, "docstatus": 1}),
		"completed_work_orders": frappe.db.count("Work Order", {"company": company, "docstatus": 1, "status": "Completed"}),
		"submitted_quality_inspections": frappe.db.count("Quality Inspection", {"docstatus": 1}),
	}


def debug_counts():
	import frappe

	doctypes = [
		"Customer",
		"Supplier",
		"Item",
		"Warehouse",
		"Material Request",
		"Stock Entry",
		"Purchase Receipt",
		"Delivery Note",
		"Pick List",
		"Landed Cost Voucher",
		"Stock Reconciliation",
		"Packing Slip",
		"Sales Order",
		"Sales Invoice",
		"Purchase Order",
		"Purchase Invoice",
		"BOM",
		"Work Order",
		"Subcontracting Order",
		"Project",
		"Task",
		"Employee",
		"Attendance",
		"CRM Lead",
		"CRM Deal",
		"HD Ticket",
	]
	result = {}
	for doctype in doctypes:
		if not _doctype_exists(frappe, doctype):
			result[doctype] = {"missing": True}
			continue
		names = frappe.get_all(doctype, fields=["name", "docstatus"], limit_page_length=10)
		result[doctype] = {"count": frappe.db.count(doctype), "names": names}
	return result


def _run_erpnext_demo(frappe, report, context):
	if not _doctype_exists(frappe, "Company"):
		return
	if frappe.db.get_single_value("Global Defaults", "demo_company"):
		report["skipped"].append("ERPNext demo data already exists")
		return
	company = context.get("company")
	if not company:
		return
	try:
		from erpnext.setup.demo import setup_demo_data

		setup_demo_data(company)
		report["created"].append("ERPNext built-in demo data")
	except Exception as exc:
		report["failed"].append({"doctype": "ERPNext Demo", "name": company, "error": str(exc)})


def _run_crm_demo(frappe, report):
	if not _doctype_exists(frappe, "CRM Lead"):
		return
	if frappe.db.get_default("crm_demo_data_created"):
		report["skipped"].append("CRM demo data already exists")
		return
	try:
		from crm.demo.api import create_demo_data

		create_demo_data()
		report["created"].append("CRM built-in demo data")
	except Exception as exc:
		report["failed"].append({"doctype": "CRM Demo", "name": "crm.demo.api.create_demo_data", "error": str(exc)})


def _backfill_dashboard_visible_data(frappe, context, report):
	company = context.get("company") or _first_existing(frappe, "Company")
	if company:
		_set_administrator_company_default(frappe, company)
		_backfill_buying_dashboard(frappe, company, context, report)
		_backfill_erp_dashboards(frappe, company, context, report)
		_backfill_hrms_dashboard(frappe, company, report)
	_backfill_helpdesk_dashboard(frappe, report)


def _backfill_buying_dashboard(frappe, company, context, report):
	if not _doctype_exists(frappe, "Purchase Order"):
		return

	supplier = context.get("supplier") or _first_existing(frappe, "Supplier")
	item = context.get("raw_item") or _first_existing(frappe, "Item", {"is_stock_item": 1})
	warehouse = _first_existing(frappe, "Warehouse", {"company": company, "is_group": 0})
	uom = context.get("uom") or "Nos"
	if not (supplier and item):
		return

	today_obj = date.today()
	amounts = [42000, 68000, 91000, 54000, 76000, 83000]
	for index, amount in enumerate(amounts, start=1):
		transaction_date = _month_date(today_obj.year, max(1, today_obj.month - (6 - index)), 10)
		qty = index + 2
		rate = round(amount / qty, 2)
		_create_submitted_material_request(
			frappe, company, item, warehouse, uom, qty, transaction_date, index
		)
		po_name, po_item_name = _create_submitted_purchase_order(
			frappe, company, supplier, item, warehouse, uom, qty, rate, transaction_date, index
		)
		if index <= 3:
			_create_submitted_purchase_receipt(
				frappe,
				company,
				supplier,
				item,
				warehouse,
				uom,
				qty,
				rate,
				transaction_date,
				index,
				po_name,
				po_item_name,
			)

	report["created"].append("Buying dashboard backfill")


def _backfill_erp_dashboards(frappe, company, context, report):
	customer = context.get("customer") or _first_existing(frappe, "Customer")
	supplier = context.get("supplier") or _first_existing(frappe, "Supplier")
	sales_item = context.get("finished_item") or _first_existing(frappe, "Item")
	raw_item = context.get("raw_item") or sales_item
	warehouse = _first_existing(frappe, "Warehouse", {"company": company, "is_group": 0})
	uom = context.get("uom") or "Nos"
	if not (customer and supplier and sales_item and warehouse):
		return

	today_obj = date.today()
	for index, amount in enumerate([125000, 96000, 73000, 154000, 88000, 112000], start=1):
		posting_date = _month_date(today_obj.year, max(1, today_obj.month - (6 - index)), 12)
		qty = index + 1
		rate = round(amount / qty, 2)
		so_name, so_item_name = _create_submitted_sales_order(
			frappe, company, customer, sales_item, warehouse, uom, qty, rate, posting_date, index
		)
		_create_submitted_sales_invoice(
			frappe, company, customer, sales_item, warehouse, uom, qty, rate, posting_date, index, so_name, so_item_name
		)
		if index <= 4:
			_create_submitted_delivery_note(
				frappe, company, customer, sales_item, warehouse, uom, qty, rate, posting_date, index, so_name, so_item_name
			)
		_create_submitted_purchase_invoice(
			frappe, company, supplier, raw_item, warehouse, uom, qty, round(rate * 0.55, 2), posting_date, index
		)

	for index, qty in enumerate([35, 42, 28], start=1):
		_create_stock_bin(frappe, raw_item if index % 2 else sales_item, warehouse, qty, 750 + index * 125, index)

	for index, qty in enumerate([8, 5, 11], start=1):
		_create_submitted_work_order(frappe, company, sales_item, warehouse, qty, index)
	_create_submitted_quality_inspections(frappe, raw_item)

	report["created"].append("ERP dashboard backfill")


def _create_submitted_sales_order(frappe, company, customer, item, warehouse, uom, qty, rate, transaction_date, index):
	name = f"HR-DASH-SO-{date.today().year}-{index:02d}"
	item_name = f"{name}-ITEM-1"
	amount = round(qty * rate, 2)
	if frappe.db.exists("Sales Order", name):
		return name, item_name
	_db_insert(
		frappe,
		"Sales Order",
		{
			"name": name,
			"docstatus": 1,
			"status": "To Deliver and Bill",
			"customer": customer,
			"customer_name": frappe.db.get_value("Customer", customer, "customer_name") or customer,
			"company": company,
			"transaction_date": transaction_date,
			"delivery_date": transaction_date,
			"currency": frappe.db.get_value("Company", company, "default_currency") or "INR",
			"conversion_rate": 1,
			"selling_price_list": "Standard Selling",
			"price_list_currency": frappe.db.get_value("Company", company, "default_currency") or "INR",
			"plc_conversion_rate": 1,
			"set_warehouse": warehouse,
			"base_net_total": amount,
			"net_total": amount,
			"base_grand_total": amount,
			"grand_total": amount,
			"rounded_total": amount,
			"base_rounded_total": amount,
			"per_delivered": 0,
			"per_billed": 0,
		},
	)
	_db_insert(
		frappe,
		"Sales Order Item",
		{
			"name": item_name,
			"parent": name,
			"parenttype": "Sales Order",
			"parentfield": "items",
			"idx": 1,
			"docstatus": 1,
			"item_code": item,
			"item_name": frappe.db.get_value("Item", item, "item_name") or item,
			"delivery_date": transaction_date,
			"warehouse": warehouse,
			"qty": qty,
			"stock_qty": qty,
			"delivered_qty": 0,
			"billed_amt": 0,
			"rate": rate,
			"base_rate": rate,
			"amount": amount,
			"base_amount": amount,
			"net_amount": amount,
			"base_net_amount": amount,
			"uom": uom,
			"stock_uom": uom,
			"conversion_factor": 1,
		},
	)
	return name, item_name


def _create_submitted_sales_invoice(
	frappe, company, customer, item, warehouse, uom, qty, rate, posting_date, index, so_name, so_item_name
):
	name = f"HR-DASH-SINV-{date.today().year}-{index:02d}"
	amount = round(qty * rate, 2)
	if frappe.db.exists("Sales Invoice", name):
		return name
	_db_insert(
		frappe,
		"Sales Invoice",
		{
			"name": name,
			"docstatus": 1,
			"status": "Unpaid",
			"customer": customer,
			"customer_name": frappe.db.get_value("Customer", customer, "customer_name") or customer,
			"company": company,
			"posting_date": posting_date,
			"due_date": posting_date,
			"currency": frappe.db.get_value("Company", company, "default_currency") or "INR",
			"conversion_rate": 1,
			"selling_price_list": "Standard Selling",
			"price_list_currency": frappe.db.get_value("Company", company, "default_currency") or "INR",
			"plc_conversion_rate": 1,
			"base_net_total": amount,
			"net_total": amount,
			"base_grand_total": amount,
			"grand_total": amount,
			"rounded_total": amount,
			"base_rounded_total": amount,
			"outstanding_amount": amount,
		},
	)
	_db_insert(
		frappe,
		"Sales Invoice Item",
		{
			"name": f"{name}-ITEM-1",
			"parent": name,
			"parenttype": "Sales Invoice",
			"parentfield": "items",
			"idx": 1,
			"docstatus": 1,
			"item_code": item,
			"item_name": frappe.db.get_value("Item", item, "item_name") or item,
			"warehouse": warehouse,
			"qty": qty,
			"stock_qty": qty,
			"rate": rate,
			"base_rate": rate,
			"amount": amount,
			"base_amount": amount,
			"net_amount": amount,
			"base_net_amount": amount,
			"uom": uom,
			"stock_uom": uom,
			"conversion_factor": 1,
			"sales_order": so_name,
			"so_detail": so_item_name,
		},
	)
	return name


def _create_submitted_delivery_note(
	frappe, company, customer, item, warehouse, uom, qty, rate, posting_date, index, so_name, so_item_name
):
	name = f"HR-DASH-DN-{date.today().year}-{index:02d}"
	amount = round(qty * rate, 2)
	if frappe.db.exists("Delivery Note", name):
		return name
	_db_insert(
		frappe,
		"Delivery Note",
		{
			"name": name,
			"docstatus": 1,
			"status": "Completed",
			"customer": customer,
			"customer_name": frappe.db.get_value("Customer", customer, "customer_name") or customer,
			"company": company,
			"posting_date": posting_date,
			"posting_time": "10:00:00",
			"set_posting_time": 1,
			"currency": frappe.db.get_value("Company", company, "default_currency") or "INR",
			"conversion_rate": 1,
			"selling_price_list": "Standard Selling",
			"price_list_currency": frappe.db.get_value("Company", company, "default_currency") or "INR",
			"plc_conversion_rate": 1,
			"base_net_total": amount,
			"net_total": amount,
			"base_grand_total": amount,
			"grand_total": amount,
		},
	)
	_db_insert(
		frappe,
		"Delivery Note Item",
		{
			"name": f"{name}-ITEM-1",
			"parent": name,
			"parenttype": "Delivery Note",
			"parentfield": "items",
			"idx": 1,
			"docstatus": 1,
			"item_code": item,
			"item_name": frappe.db.get_value("Item", item, "item_name") or item,
			"warehouse": warehouse,
			"qty": qty,
			"stock_qty": qty,
			"rate": rate,
			"base_rate": rate,
			"amount": amount,
			"base_amount": amount,
			"net_amount": amount,
			"base_net_amount": amount,
			"uom": uom,
			"stock_uom": uom,
			"conversion_factor": 1,
			"against_sales_order": so_name,
			"so_detail": so_item_name,
		},
	)
	return name


def _create_submitted_purchase_invoice(frappe, company, supplier, item, warehouse, uom, qty, rate, posting_date, index):
	name = f"HR-DASH-PINV-{date.today().year}-{index:02d}"
	amount = round(qty * rate, 2)
	if frappe.db.exists("Purchase Invoice", name):
		return name
	_db_insert(
		frappe,
		"Purchase Invoice",
		{
			"name": name,
			"docstatus": 1,
			"status": "Unpaid",
			"supplier": supplier,
			"supplier_name": frappe.db.get_value("Supplier", supplier, "supplier_name") or supplier,
			"company": company,
			"posting_date": posting_date,
			"due_date": posting_date,
			"bill_no": f"HRD-BILL-{index:02d}",
			"bill_date": posting_date,
			"currency": frappe.db.get_value("Company", company, "default_currency") or "INR",
			"conversion_rate": 1,
			"buying_price_list": "Standard Buying",
			"price_list_currency": frappe.db.get_value("Company", company, "default_currency") or "INR",
			"plc_conversion_rate": 1,
			"base_net_total": amount,
			"net_total": amount,
			"base_grand_total": amount,
			"grand_total": amount,
			"rounded_total": amount,
			"base_rounded_total": amount,
			"outstanding_amount": amount,
		},
	)
	_db_insert(
		frappe,
		"Purchase Invoice Item",
		{
			"name": f"{name}-ITEM-1",
			"parent": name,
			"parenttype": "Purchase Invoice",
			"parentfield": "items",
			"idx": 1,
			"docstatus": 1,
			"item_code": item,
			"item_name": frappe.db.get_value("Item", item, "item_name") or item,
			"warehouse": warehouse,
			"qty": qty,
			"stock_qty": qty,
			"rate": rate,
			"base_rate": rate,
			"amount": amount,
			"base_amount": amount,
			"net_amount": amount,
			"base_net_amount": amount,
			"uom": uom,
			"stock_uom": uom,
			"conversion_factor": 1,
		},
	)
	return name


def _create_stock_bin(frappe, item, warehouse, qty, valuation_rate, index):
	name = f"HR-DASH-BIN-{index:02d}"
	value = round(qty * valuation_rate, 2)
	existing = frappe.db.exists("Bin", {"item_code": item, "warehouse": warehouse})
	if existing:
		frappe.db.set_value(
			"Bin",
			existing,
			{"actual_qty": qty, "projected_qty": qty, "stock_value": value, "valuation_rate": valuation_rate},
			update_modified=False,
		)
		return existing
	if frappe.db.exists("Bin", name):
		frappe.db.set_value("Bin", name, {"actual_qty": qty, "stock_value": value, "valuation_rate": valuation_rate}, update_modified=False)
		return name
	_db_insert(
		frappe,
		"Bin",
		{
			"name": name,
			"item_code": item,
			"warehouse": warehouse,
			"actual_qty": qty,
			"projected_qty": qty,
			"stock_value": value,
			"valuation_rate": valuation_rate,
		},
	)
	return name


def _create_submitted_work_order(frappe, company, item, warehouse, qty, index):
	name = f"HR-DASH-WO-{date.today().year}-{index:02d}"
	if frappe.db.exists("Work Order", name):
		return name
	_db_insert(
		frappe,
		"Work Order",
		{
			"name": name,
			"docstatus": 1,
			"status": "Completed" if index <= 2 else "In Process",
			"company": company,
			"production_item": item,
			"qty": qty,
			"produced_qty": qty if index <= 2 else 0,
			"material_transferred_for_manufacturing": qty,
			"wip_warehouse": warehouse,
			"fg_warehouse": warehouse,
			"planned_start_date": date.today().isoformat(),
			"creation": "2020-06-20 10:00:00",
			"modified": "2020-06-20 10:00:00",
		},
	)
	return name


def _create_submitted_quality_inspections(frappe, item):
	for index in range(1, 5):
		name = f"HR-DASH-QI-{date.today().year}-{index:02d}"
		if frappe.db.exists("Quality Inspection", name):
			continue
		_db_insert(
			frappe,
			"Quality Inspection",
			{
				"name": name,
				"docstatus": 1,
				"inspection_type": "Incoming",
				"item_code": item,
				"inspected_by": "Administrator",
				"report_date": date.today().isoformat(),
				"status": "Accepted",
			},
		)


def _create_submitted_material_request(frappe, company, item, warehouse, uom, qty, transaction_date, index):
	name = f"HR-DASH-MR-{date.today().year}-{index:02d}"
	if frappe.db.exists("Material Request", name):
		return name
	_db_insert(
		frappe,
		"Material Request",
		{
			"name": name,
			"docstatus": 1,
			"status": "Pending",
			"company": company,
			"material_request_type": "Purchase",
			"transaction_date": transaction_date,
			"schedule_date": transaction_date,
			"set_warehouse": warehouse,
			"title": "Dashboard Purchase Material Request",
		},
	)
	_db_insert(
		frappe,
		"Material Request Item",
		{
			"name": f"{name}-ITEM-1",
			"parent": name,
			"parenttype": "Material Request",
			"parentfield": "items",
			"idx": 1,
			"docstatus": 1,
			"item_code": item,
			"item_name": frappe.db.get_value("Item", item, "item_name") or item,
			"schedule_date": transaction_date,
			"warehouse": warehouse,
			"qty": qty,
			"stock_qty": qty,
			"uom": uom,
			"stock_uom": uom,
			"conversion_factor": 1,
		},
	)
	return name


def _create_submitted_purchase_order(frappe, company, supplier, item, warehouse, uom, qty, rate, transaction_date, index):
	name = f"HR-DASH-PO-{date.today().year}-{index:02d}"
	item_name = f"{name}-ITEM-1"
	amount = round(qty * rate, 2)
	if frappe.db.exists("Purchase Order", name):
		return name, item_name
	_db_insert(
		frappe,
		"Purchase Order",
		{
			"name": name,
			"docstatus": 1,
			"status": "To Receive and Bill",
			"supplier": supplier,
			"supplier_name": frappe.db.get_value("Supplier", supplier, "supplier_name") or supplier,
			"company": company,
			"transaction_date": transaction_date,
			"schedule_date": transaction_date,
			"currency": frappe.db.get_value("Company", company, "default_currency") or "INR",
			"conversion_rate": 1,
			"buying_price_list": "Standard Buying",
			"price_list_currency": frappe.db.get_value("Company", company, "default_currency") or "INR",
			"plc_conversion_rate": 1,
			"set_warehouse": warehouse,
			"base_net_total": amount,
			"net_total": amount,
			"base_grand_total": amount,
			"grand_total": amount,
			"rounded_total": amount,
			"base_rounded_total": amount,
			"per_received": 0,
			"per_billed": 0,
		},
	)
	_db_insert(
		frappe,
		"Purchase Order Item",
		{
			"name": item_name,
			"parent": name,
			"parenttype": "Purchase Order",
			"parentfield": "items",
			"idx": 1,
			"docstatus": 1,
			"item_code": item,
			"item_name": frappe.db.get_value("Item", item, "item_name") or item,
			"schedule_date": transaction_date,
			"warehouse": warehouse,
			"qty": qty,
			"stock_qty": qty,
			"received_qty": 0,
			"billed_amt": 0,
			"rate": rate,
			"base_rate": rate,
			"amount": amount,
			"base_amount": amount,
			"net_amount": amount,
			"base_net_amount": amount,
			"uom": uom,
			"stock_uom": uom,
			"conversion_factor": 1,
		},
	)
	return name, item_name


def _create_submitted_purchase_receipt(
	frappe, company, supplier, item, warehouse, uom, qty, rate, posting_date, index, po_name, po_item_name
):
	name = f"HR-DASH-PR-{date.today().year}-{index:02d}"
	amount = round(qty * rate, 2)
	if frappe.db.exists("Purchase Receipt", name):
		return name
	_db_insert(
		frappe,
		"Purchase Receipt",
		{
			"name": name,
			"docstatus": 1,
			"status": "Completed",
			"supplier": supplier,
			"supplier_name": frappe.db.get_value("Supplier", supplier, "supplier_name") or supplier,
			"company": company,
			"posting_date": posting_date,
			"posting_time": "10:00:00",
			"set_posting_time": 1,
			"currency": frappe.db.get_value("Company", company, "default_currency") or "INR",
			"conversion_rate": 1,
			"buying_price_list": "Standard Buying",
			"price_list_currency": frappe.db.get_value("Company", company, "default_currency") or "INR",
			"plc_conversion_rate": 1,
			"set_warehouse": warehouse,
			"base_net_total": amount,
			"net_total": amount,
			"base_grand_total": amount,
			"grand_total": amount,
			"rounded_total": amount,
			"base_rounded_total": amount,
		},
	)
	_db_insert(
		frappe,
		"Purchase Receipt Item",
		{
			"name": f"{name}-ITEM-1",
			"parent": name,
			"parenttype": "Purchase Receipt",
			"parentfield": "items",
			"idx": 1,
			"docstatus": 1,
			"item_code": item,
			"item_name": frappe.db.get_value("Item", item, "item_name") or item,
			"warehouse": warehouse,
			"qty": qty,
			"stock_qty": qty,
			"rate": rate,
			"base_rate": rate,
			"amount": amount,
			"base_amount": amount,
			"net_amount": amount,
			"base_net_amount": amount,
			"uom": uom,
			"stock_uom": uom,
			"conversion_factor": 1,
			"purchase_order": po_name,
			"purchase_order_item": po_item_name,
		},
	)
	return name


def _db_insert(frappe, doctype, values):
	values = _valid_fields(frappe, doctype, values, {})
	doc = frappe.get_doc({"doctype": doctype, **values})
	doc.db_insert()
	return doc.name


def _month_date(year, month, day):
	return date(year, month, min(day, 28)).isoformat()


def _set_administrator_company_default(frappe, company):
	try:
		frappe.defaults.set_user_default("Company", company, "Administrator")
		frappe.defaults.set_global_default("company", company)
		frappe.db.set_default("company", company)
	except Exception:
		frappe.db.set_default("company", company)


def _backfill_hrms_dashboard(frappe, company, report):
	if not _doctype_exists(frappe, "Employee"):
		return

	employees = frappe.get_all(
		"Employee",
		fields=["name"],
		limit_page_length=40,
		order_by="creation asc",
	)
	today_str = date.today().isoformat()
	for row in employees:
		try:
			frappe.db.set_value(
				"Employee",
				row.name,
				{
					"company": company,
					"status": "Active",
					"date_of_joining": today_str,
				},
				update_modified=False,
			)
		except Exception:
			continue

	attendance_dates = _current_month_weekdays(limit=12)
	for employee in [row.name for row in employees[:12]]:
		for attendance_date in attendance_dates:
			name = f"HR-DASH-{employee}-{attendance_date}"
			if not frappe.db.exists("Attendance", name):
				doc = frappe.get_doc(
					{
						"doctype": "Attendance",
						"name": name,
						"employee": employee,
						"company": company,
						"attendance_date": attendance_date,
						"status": "Present",
						"docstatus": 1,
					}
				)
				try:
					doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
				except Exception:
					doc.db_insert()
			else:
				frappe.db.set_value(
					"Attendance",
					name,
					{"company": company, "status": "Present", "docstatus": 1},
					update_modified=False,
				)

			checkin_name = f"HR-DASH-CHECKIN-{employee}-{attendance_date}"
			if _doctype_exists(frappe, "Employee Checkin") and not frappe.db.exists("Employee Checkin", checkin_name):
				try:
					frappe.get_doc(
						{
							"doctype": "Employee Checkin",
							"name": checkin_name,
							"employee": employee,
							"time": f"{attendance_date} 09:30:00",
							"log_type": "IN",
						}
					).insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
				except Exception:
					pass

	report["created"].append("HRMS dashboard backfill")


def _backfill_helpdesk_dashboard(frappe, report):
	if not _doctype_exists(frappe, "HD Ticket"):
		return

	now = frappe.utils.now_datetime()
	sla = _first_existing(frappe, "HD Service Level Agreement")
	team = _first_existing(frappe, "HD Team")
	open_status = _first_existing(frappe, "HD Ticket Status", {"category": "Open"}) or "Open"
	resolved_status = _first_existing(frappe, "HD Ticket Status", {"category": "Resolved"}) or "Resolved"
	tickets = frappe.get_all("HD Ticket", fields=["name"], limit_page_length=20, order_by="creation desc")

	for index, ticket in enumerate(tickets):
		created_on = frappe.utils.add_to_date(now, days=-(index % 21 + 2))
		values = {
			"_assign": '["Administrator"]',
			"agent_group": team,
			"priority": ["Urgent", "High", "Medium", "Low"][index % 4],
			"status_category": "Open",
			"status": open_status,
			"sla": sla,
			"agreement_status": "Resolution Due" if index % 2 else "First Response Due",
			"response_by": frappe.utils.add_to_date(now, hours=2 + index),
			"resolution_by": frappe.utils.add_to_date(now, days=1 + (index % 3)),
			"last_customer_response": frappe.utils.add_to_date(now, hours=-(index + 1)),
			"first_responded_on": frappe.utils.add_to_date(now, minutes=15 + index),
			"first_response_time": 900 + index * 60,
			"resolution_time": 3600 * (4 + index),
		}
		if index % 5 == 0:
			created_on = frappe.utils.add_to_date(now, days=-(index % 30 + 8))
			values.update(
				{
					"status_category": "Resolved",
					"status": resolved_status,
					"agreement_status": "Fulfilled",
					"resolution_date": now,
					"feedback_rating": 0.8,
					"feedback": "Helpful and fast resolution.",
				}
			)
		frappe.db.set_value("HD Ticket", ticket.name, values, update_modified=False)
		frappe.db.sql(
			"""
			update `tabHD Ticket`
			set creation = %s,
				modified = %s,
				_assign = %s,
				agent_group = %s,
				priority = %s,
				status_category = %s,
				status = %s,
				sla = %s,
				agreement_status = %s,
				response_by = %s,
				resolution_by = %s,
				last_customer_response = %s,
				first_responded_on = %s,
				first_response_time = %s,
				resolution_time = %s
			where name = %s
			""",
			(
				created_on,
				now,
				values.get("_assign"),
				values.get("agent_group"),
				values.get("priority"),
				values.get("status_category"),
				values.get("status"),
				values.get("sla"),
				values.get("agreement_status"),
				values.get("response_by"),
				values.get("resolution_by"),
				values.get("last_customer_response"),
				values.get("first_responded_on"),
				values.get("first_response_time"),
				values.get("resolution_time"),
				ticket.name,
			),
		)
		_ensure_assignment(frappe, ticket.name)

	report["created"].append("Helpdesk dashboard backfill")


def _ensure_assignment(frappe, ticket_name):
	if frappe.db.exists(
		"ToDo",
		{"reference_type": "HD Ticket", "reference_name": ticket_name, "allocated_to": "Administrator"},
	):
		return
	try:
		frappe.get_doc(
			{
				"doctype": "ToDo",
				"allocated_to": "Administrator",
				"assigned_by": "Administrator",
				"reference_type": "HD Ticket",
				"reference_name": ticket_name,
				"description": f"Follow up ticket {ticket_name}",
				"status": "Open",
				"priority": "Medium",
			}
		).insert(ignore_permissions=True)
	except Exception:
		pass


def _current_month_weekdays(limit=10):
	first = date.today().replace(day=1)
	days = []
	day = first
	while day.month == first.month and len(days) < limit:
		if day.weekday() < 5:
			days.append(day.isoformat())
		day = day.fromordinal(day.toordinal() + 1)
	return days


def _build_context(frappe, report):
	today = date.today().isoformat()
	future = date(date.today().year, 12, 31).isoformat()
	company = _first_existing(frappe, "Company") or DEFAULT_COMPANY
	context = {
		"today": today,
		"future": future,
		"company": company,
		"territory": _first_existing(frappe, "Territory") or "All Territories",
		"customer_group": _first_existing(frappe, "Customer Group") or stable_seed_name("Customer Group", "suite customers"),
		"supplier_group": _first_existing(frappe, "Supplier Group") or stable_seed_name("Supplier Group", "suite suppliers"),
		"item_group": _first_existing(frappe, "Item Group") or stable_seed_name("Item Group", "suite items"),
		"uom": _first_existing(frappe, "UOM") or "Nos",
		"customer": _first_existing(frappe, "Customer") or stable_seed_name("Customer", "acme retail"),
		"supplier": _first_existing(frappe, "Supplier") or stable_seed_name("Supplier", "global supplies"),
		"delivery_note": _first_existing(frappe, "Delivery Note") or stable_seed_name("Delivery Note", "website implementation"),
		"service_item": _first_existing(frappe, "Item", {"is_stock_item": 0}) or "HR-DEMO-SERVICE",
		"raw_item": _first_existing(frappe, "Item", {"is_stock_item": 1}) or "HR-DEMO-RAW-MATERIAL",
		"finished_item": "HR-DEMO-FINISHED-KIT",
		"project": _first_existing(frappe, "Project") or stable_seed_name("Project", "erp rollout"),
		"asset_category": _first_existing(frappe, "Asset Category") or stable_seed_name("Asset Category", "laptops"),
		"asset": _first_existing(frappe, "Asset") or stable_seed_name("Asset", "office laptop"),
		"department": _first_existing(frappe, "Department") or stable_seed_name("Department", "operations"),
		"branch": _first_existing(frappe, "Branch") or stable_seed_name("Branch", "bengaluru hq"),
		"designation": _first_existing(frappe, "Designation") or stable_seed_name("Designation", "operations manager"),
		"employee": _first_existing(frappe, "Employee") or stable_seed_name("Employee", "ananya operations"),
		"leave_type": _first_existing(frappe, "Leave Type") or "Casual Leave",
		"job_opening": _first_existing(frappe, "Job Opening") or stable_seed_name("Job Opening", "support specialist"),
		"salary_structure": _first_existing(frappe, "Salary Structure") or stable_seed_name("Salary Structure", "standard salary"),
		"crm_organization": _first_existing(frappe, "CRM Organization") or stable_seed_name("CRM Organization", "acme retail crm"),
		"crm_contact": _first_existing(frappe, "CRM Contacts") or stable_seed_name("CRM Contacts", "priya acme"),
		"hd_customer": _first_existing(frappe, "HD Customer") or stable_seed_name("HD Customer", "acme support"),
		"hd_team": _first_existing(frappe, "HD Team") or stable_seed_name("HD Team", "support desk"),
		"hd_article_category": _first_existing(frappe, "HD Article Category") or stable_seed_name("HD Article Category", "getting started"),
	}
	return context


def _insert_record(frappe, record_spec, context, report):
	doctype = record_spec["doctype"]
	name = record_spec["name"]

	if not _doctype_exists(frappe, doctype):
		report["skipped"].append(f"{doctype}: missing DocType")
		return
	if frappe.db.exists(doctype, name):
		report["skipped"].append(f"{doctype}: {name}")
		return

	fields = _valid_fields(frappe, doctype, record_spec["fields"], context)
	existing = _existing_by_unique_fields(frappe, doctype, fields, record_spec.get("unique_by", []))
	if existing:
		report["skipped"].append(f"{doctype}: {existing}")
		return
	try:
		doc = frappe.new_doc(doctype)
		doc.name = name
		for field, value in fields.items():
			doc.set(field, value)
		_set_insert_flags(doc)
		doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
		report["created"].append(f"{doctype}: {doc.name}")
	except Exception:
		try:
			doc = frappe.get_doc({"doctype": doctype, "name": name, **fields})
			_set_insert_flags(doc)
			doc.db_insert()
			report["created"].append(f"{doctype}: {name}")
		except Exception as exc:
			report["failed"].append({"doctype": doctype, "name": name, "error": str(exc)})


def _set_insert_flags(doc):
	doc.flags.ignore_permissions = True
	doc.flags.ignore_mandatory = True
	doc.flags.ignore_links = True
	doc.flags.ignore_validate = True
	doc.flags.ignore_children = True


def _valid_fields(frappe, doctype, fields, context):
	meta = frappe.get_meta(doctype)
	valid_columns = set(meta.get_valid_columns())
	result = {}
	for field, value in fields.items():
		if field in valid_columns:
			result[field] = _resolve(value, context)
	return result


def _existing_by_unique_fields(frappe, doctype, fields, unique_fields):
	for field in unique_fields:
		value = fields.get(field)
		if value and frappe.db.exists(doctype, {field: value}):
			return frappe.db.get_value(doctype, {field: value}, "name")
	return None


def _resolve(value, context):
	if isinstance(value, str) and value.startswith("$"):
		return context.get(value[1:], value)
	return value


def _doctype_exists(frappe, doctype):
	return bool(frappe.db.exists("DocType", doctype))


def _first_existing(frappe, doctype, filters=None):
	if not _doctype_exists(frappe, doctype):
		return None
	try:
		rows = frappe.get_all(doctype, filters=filters or {}, pluck="name", limit_page_length=1)
		return rows[0] if rows else None
	except Exception:
		return None
