# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# License: GNU General Public License v3. See license.txt

import frappe
from erpnext.setup.doctype.employee.test_employee import make_employee
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.permissions import add_user_permission, reset_perms, update_permission_property
from hrms.payroll.doctype.salary_structure.test_salary_structure import (
	create_salary_structure_assignment,
	make_salary_structure,
)
from hrms.tests.utils import HRMSTestSuite

from india_payroll.india_payroll.page.tax_regime_selector.tax_regime_selector import (
	NEW_REGIME_SLAB,
	OLD_REGIME_SLAB,
	build_prefill_declarations,
	compute_tax_comparison,
	get_employee_details,
	get_employee_salary_data,
	notify_employee_to_select_tax_regime,
	set_tax_regime,
	setup_if_missing,
)
from india_payroll.india_payroll.tax_exemption_setup import setup_tax_exemption_categories
from india_payroll.install import create_income_tax_slabs, get_custom_fields

COMPANY = "_Test Company"

# base * 12 earnings: Basic = base, HRA = base / 2 -> monthly gross = 1.5 * base
EARNINGS = [
	{
		"salary_component": "Basic Salary",
		"abbr": "BS",
		"formula": "base",
		"type": "Earning",
		"amount_based_on_formula": 1,
	},
	{
		"salary_component": "House Rent Allowance",
		"abbr": "HRA",
		"formula": "base / 2",
		"type": "Earning",
		"amount_based_on_formula": 1,
	},
]


def ensure_salary_components():
	for name, abbr, ctype in (
		("Basic Salary", "BS", "Earning"),
		("House Rent Allowance", "HRA", "Earning"),
		("Employee Provident Fund", "PF", "Deduction"),
	):
		if not frappe.db.exists("Salary Component", name):
			frappe.get_doc(
				{
					"doctype": "Salary Component",
					"salary_component": name,
					"salary_component_abbr": abbr,
					"type": ctype,
				}
			).insert()


DEDUCTIONS = [
	{
		"salary_component": "Employee Provident Fund",
		"abbr": "PF",
		"amount": 1800,
		"type": "Deduction",
	},
]


def make_structure(employee, base, from_date="2026-04-01"):
	ensure_salary_components()
	structure = make_salary_structure(
		"IP Tax Regime Test Structure",
		"Monthly",
		employee=employee,
		company=COMPANY,
		currency="INR",
		from_date=from_date,
		base=base,
		earnings=EARNINGS,
		deductions=DEDUCTIONS,
	)
	return structure


def make_draft_assignment(employee, base=100000, income_tax_slab=OLD_REGIME_SLAB):
	"""Structure without an employee, then a draft assignment for that employee."""
	ensure_salary_components()
	make_salary_structure(
		"IP Tax Regime Test Structure",
		"Monthly",
		company=COMPANY,
		currency="INR",
		earnings=EARNINGS,
		deductions=DEDUCTIONS,
	)
	return frappe.get_doc(
		{
			"doctype": "Salary Structure Assignment",
			"employee": employee,
			"salary_structure": "IP Tax Regime Test Structure",
			"from_date": "2026-04-01",
			"base": base,
			"company": COMPANY,
			"currency": "INR",
			"income_tax_slab": income_tax_slab,
		}
	).insert()


def make_cancelled_assignment(employee, from_date):
	ensure_salary_components()
	make_salary_structure(
		"IP Tax Regime Test Structure",
		"Monthly",
		company=COMPANY,
		currency="INR",
		earnings=EARNINGS,
		deductions=DEDUCTIONS,
	)
	ssa = frappe.get_doc(
		{
			"doctype": "Salary Structure Assignment",
			"employee": employee,
			"salary_structure": "IP Tax Regime Test Structure",
			"from_date": from_date,
			"base": 100000,
			"company": COMPANY,
			"currency": "INR",
			"income_tax_slab": OLD_REGIME_SLAB,
		}
	).insert()
	ssa.submit()
	ssa.cancel()
	return ssa


def ensure_self_user_permission(employee):
	"""ERPNext adds this on Employee insert; assert it so a permission test that
	depends on it fails loudly rather than silently passing."""
	user = frappe.db.get_value("Employee", employee, "user_id")
	if not frappe.db.exists("User Permission", {"allow": "Employee", "for_value": employee, "user": user}):
		add_user_permission("Employee", employee, user, ignore_permissions=True)
	return user


def make_hr_user(email="ip_trs_hr@indiapayroll.com"):
	if not frappe.db.exists("User", email):
		frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": "IP TRS HR",
				"send_welcome_email": 0,
				"roles": [{"doctype": "Has Role", "role": "HR Manager"}],
			}
		).insert(ignore_permissions=True)
	return email


class TestTaxRegimeSelector(HRMSTestSuite):
	def setUp(self):
		frappe.set_user("Administrator")
		create_custom_fields(get_custom_fields())
		create_income_tax_slabs()
		setup_tax_exemption_categories()

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_annual_gross_sourced_from_assignment(self):
		"""get_employee_salary_data reads the SSA's computed annual_gross_earning."""
		employee = make_employee("ip_trs_gross@indiapayroll.com", company=COMPANY)
		make_structure(employee, base=100000)

		ssa = frappe.db.get_value(
			"Salary Structure Assignment",
			{"employee": employee, "docstatus": 1},
			["name", "annual_gross_earning"],
			as_dict=True,
		)
		self.assertTrue(ssa.annual_gross_earning)

		data = get_employee_salary_data(employee)
		self.assertEqual(data["annual_gross"], ssa.annual_gross_earning)
		# Basic + HRA = 1.5 * base * 12
		self.assertEqual(data["annual_gross"], 100000 * 1.5 * 12)
		self.assertTrue(data["has_hra"])
		self.assertEqual(data["annual_hra"], 50000 * 12)

	def test_regime_comparison_returns_recommendation(self):
		employee = make_employee("ip_trs_compare@indiapayroll.com", company=COMPANY)
		make_structure(employee, base=100000)

		result = compute_tax_comparison(employee, declarations={})
		self.assertIn(result["recommended"], ("old", "new"))
		self.assertEqual(
			result["savings"],
			abs(result["old_regime"]["tax"] - result["new_regime"]["tax"]),
		)
		# With no declarations, the new regime (higher standard deduction, lower
		# slabs) should win for this salary.
		self.assertEqual(result["recommended"], "new")

	def test_hra_exemption_applied_in_old_regime(self):
		employee = make_employee("ip_trs_hra@indiapayroll.com", company=COMPANY)
		make_structure(employee, base=100000)

		result = compute_tax_comparison(
			employee,
			declarations={},
			rent_monthly=40000,
			city_type="metro",
		)
		breakdown = result["old_regime"]["breakdown"]
		# min(annual_hra=600000, 50% basic=600000, rent 480000 - 10% basic 120000=360000)
		self.assertEqual(breakdown["hra_exemption"], 360000)

		# New regime ignores HRA entirely.
		self.assertNotIn("hra_exemption", result["new_regime"]["breakdown"])

	def test_80cce_combined_cap(self):
		employee = make_employee("ip_trs_80c@indiapayroll.com", company=COMPANY)
		make_structure(employee, base=100000)

		result = compute_tax_comparison(employee, declarations={"80C": 200000})
		via = result["old_regime"]["breakdown"]["via_deductions"]
		cce = next(v for k, v in via.items() if k.startswith("80CCE"))
		self.assertEqual(cce, 150000)

	def test_prefill_fuzzy_match(self):
		"""Statutory deductions fuzzy-match exemption sub-categories by name."""
		cat_list = [
			{"name": "80C", "sub_categories": [{"name": "Employee Provident Fund (EPF)"}]},
			{"name": "80CCD(1)", "sub_categories": [{"name": "Employee NPS Contribution - 80CCD(1)"}]},
		]
		deductions = [
			{"component": "Employee Provident Fund", "annual_amount": 21600},
			{"component": "Professional Tax", "annual_amount": 2400},  # no match
		]
		prefill = build_prefill_declarations(deductions, cat_list)
		self.assertEqual(prefill, {"80C": {"Employee Provident Fund (EPF)": 21600}})

	def test_prefill_via_get_employee_details(self):
		employee = make_employee("ip_trs_prefill@indiapayroll.com", company=COMPANY)
		make_structure(employee, base=100000)

		data = get_employee_details(employee)
		# EPF deduction of 1800/month -> 21600/year, matched to 80C EPF sub.
		self.assertEqual(data["prefill_declarations"]["80C"]["Employee Provident Fund (EPF)"], 1800 * 12)

	def test_senior_citizen_flag(self):
		employee = make_employee(
			"ip_trs_senior@indiapayroll.com",
			company=COMPANY,
			date_of_birth="1960-01-01",
		)
		make_structure(employee, base=100000)

		data = get_employee_salary_data(employee)
		self.assertTrue(data["is_senior_citizen"])

	def test_set_tax_regime_blocked_when_submitted(self):
		employee = make_employee("ip_trs_submitted@indiapayroll.com", company=COMPANY)
		make_structure(employee, base=100000)  # submitted SSA

		self.assertRaises(frappe.ValidationError, set_tax_regime, employee, NEW_REGIME_SLAB)

	def test_set_tax_regime_allowed_when_draft(self):
		employee = make_employee("ip_trs_draft@indiapayroll.com", company=COMPANY)
		ssa = make_draft_assignment(employee)

		result = set_tax_regime(employee, NEW_REGIME_SLAB)
		self.assertEqual(result["assignment"], ssa.name)
		self.assertEqual(
			frappe.db.get_value("Salary Structure Assignment", ssa.name, "income_tax_slab"),
			NEW_REGIME_SLAB,
		)

	def test_cancelled_assignment_is_skipped(self):
		"""A cancelled assignment can hold the latest from_date. get_latest_assignment
		must skip it and return the draft instead of writing to a cancelled document."""
		employee = make_employee("ip_trs_cancelled@indiapayroll.com", company=COMPANY)
		draft = make_draft_assignment(employee)
		cancelled = make_cancelled_assignment(employee, "2026-07-01")

		result = set_tax_regime(employee, NEW_REGIME_SLAB)

		self.assertEqual(result["assignment"], draft.name)
		self.assertEqual(
			frappe.db.get_value("Salary Structure Assignment", cancelled.name, "income_tax_slab"),
			OLD_REGIME_SLAB,
		)

	def test_only_cancelled_assignment_reports_none_found(self):
		employee = make_employee("ip_trs_only_cancelled@indiapayroll.com", company=COMPANY)
		make_cancelled_assignment(employee, "2026-04-01")

		self.assertRaises(frappe.ValidationError, set_tax_regime, employee, NEW_REGIME_SLAB)

	def test_set_tax_regime_rejects_unknown_slab(self):
		employee = make_employee("ip_trs_badslab@indiapayroll.com", company=COMPANY)
		ssa = make_draft_assignment(employee)

		self.assertRaises(frappe.ValidationError, set_tax_regime, employee, "Not A Real Slab")
		self.assertEqual(
			frappe.db.get_value("Salary Structure Assignment", ssa.name, "income_tax_slab"),
			OLD_REGIME_SLAB,
		)

	def test_set_tax_regime_allowed_for_own_employee(self):
		"""Self-service: the Employee role has no write permission on the assignment,
		so the employee's own user must still be allowed through."""
		employee = make_employee("ip_trs_self@indiapayroll.com", company=COMPANY)
		ssa = make_draft_assignment(employee)
		user = ensure_self_user_permission(employee)

		frappe.set_user(user)
		set_tax_regime(employee, NEW_REGIME_SLAB)

		frappe.set_user("Administrator")
		self.assertEqual(
			frappe.db.get_value("Salary Structure Assignment", ssa.name, "income_tax_slab"),
			NEW_REGIME_SLAB,
		)

	def test_set_tax_regime_blocked_for_other_employee(self):
		attacker = make_employee("ip_trs_attacker@indiapayroll.com", company=COMPANY)
		victim = make_employee("ip_trs_victim@indiapayroll.com", company=COMPANY)
		make_draft_assignment(attacker)
		victim_ssa = make_draft_assignment(victim)
		attacker_user = ensure_self_user_permission(attacker)
		ensure_self_user_permission(victim)

		frappe.set_user(attacker_user)
		self.assertRaises(frappe.PermissionError, set_tax_regime, victim, NEW_REGIME_SLAB)

		frappe.set_user("Administrator")
		self.assertEqual(
			frappe.db.get_value("Salary Structure Assignment", victim_ssa.name, "income_tax_slab"),
			OLD_REGIME_SLAB,
		)

	def test_read_endpoints_blocked_for_other_employee(self):
		attacker = make_employee("ip_trs_reader@indiapayroll.com", company=COMPANY)
		victim = make_employee("ip_trs_read_victim@indiapayroll.com", company=COMPANY)
		make_draft_assignment(attacker)
		make_draft_assignment(victim)
		attacker_user = ensure_self_user_permission(attacker)
		ensure_self_user_permission(victim)

		frappe.set_user(attacker_user)
		self.assertRaises(frappe.PermissionError, get_employee_details, victim)
		self.assertRaises(frappe.PermissionError, compute_tax_comparison, victim, {})

		# own record still readable
		self.assertTrue(get_employee_details(attacker)["annual_gross"])

	def test_notify_blocked_for_employee_role(self):
		attacker = make_employee("ip_trs_notify_attacker@indiapayroll.com", company=COMPANY)
		victim = make_employee("ip_trs_notify_victim@indiapayroll.com", company=COMPANY)
		make_draft_assignment(attacker)
		victim_ssa = make_draft_assignment(victim)
		attacker_user = ensure_self_user_permission(attacker)

		frappe.set_user(attacker_user)
		self.assertRaises(frappe.PermissionError, notify_employee_to_select_tax_regime, victim_ssa.name)

	def test_self_service_works_without_assignment_permission(self):
		"""Most sites give the Employee role no access to Salary Structure Assignment.
		Self-service must still work, because the guard matches user_id before it
		checks permissions. Cross-employee access must stay blocked."""
		employee = make_employee("ip_trs_noperm@indiapayroll.com", company=COMPANY)
		victim = make_employee("ip_trs_noperm_victim@indiapayroll.com", company=COMPANY)
		ssa = make_draft_assignment(employee)
		make_draft_assignment(victim)
		user = ensure_self_user_permission(employee)

		try:
			update_permission_property("Salary Structure Assignment", "Employee", 0, "select", 0)
			update_permission_property("Salary Structure Assignment", "Employee", 0, "read", 0)
			frappe.clear_cache()

			frappe.set_user(user)
			self.assertFalse(frappe.has_permission("Salary Structure Assignment", "read"))

			self.assertTrue(get_employee_details(employee)["annual_gross"])
			set_tax_regime(employee, NEW_REGIME_SLAB)

			self.assertRaises(frappe.PermissionError, get_employee_details, victim)
			self.assertRaises(frappe.PermissionError, set_tax_regime, victim, NEW_REGIME_SLAB)
		finally:
			frappe.set_user("Administrator")
			reset_perms("Salary Structure Assignment")
			frappe.clear_cache()

		self.assertEqual(
			frappe.db.get_value("Salary Structure Assignment", ssa.name, "income_tax_slab"),
			NEW_REGIME_SLAB,
		)

	def test_setup_if_missing_blocked_for_employee_role(self):
		employee = make_employee("ip_trs_setup@indiapayroll.com", company=COMPANY)
		user = ensure_self_user_permission(employee)
		self.assertTrue(setup_if_missing()["ok"])

		frappe.set_user(user)
		self.assertRaises(frappe.PermissionError, setup_if_missing)

	def test_hr_user_can_set_regime_for_other_employee(self):
		employee = make_employee("ip_trs_hr_target@indiapayroll.com", company=COMPANY)
		ssa = make_draft_assignment(employee)
		hr_user = make_hr_user()

		frappe.set_user(hr_user)
		set_tax_regime(employee, NEW_REGIME_SLAB)
		self.assertTrue(get_employee_details(employee)["annual_gross"])

		frappe.set_user("Administrator")
		self.assertEqual(
			frappe.db.get_value("Salary Structure Assignment", ssa.name, "income_tax_slab"),
			NEW_REGIME_SLAB,
		)
