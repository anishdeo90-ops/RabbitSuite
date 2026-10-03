# Copyright (c) 2025, Frappe Technologies and Contributors
# See license.txt

from json import loads

from frappe.tests import UnitTestCase

from frappe.desk.doctype.workspace_sidebar.workspace_sidebar import (
	add_accounts_sidebar_shortcuts,
	create_sidebar_items,
)

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class IntegrationTestWorkspaceSidebar(UnitTestCase):
	"""
	Integration tests for WorkspaceSidebar.
	Use this class for testing interactions between multiple components.
	"""

	def test_accounts_module_sidebar_adds_targeted_saved_sidebar_shortcuts(self):
		module_info = {
			"Workspace": ["Invoicing", "Financial Reports"],
			"Dashboard": ["Accounts", "Payments"],
			"DocType": ["Mode of Payment", "Bank Clearance", "Monthly Distribution"],
			"Report": ["General Ledger"],
			"Page": [],
		}
		sidebar_links = {
			"Banking": {
				"label": "Banking",
				"link_to": "Bank Clearance",
				"link_type": "DocType",
				"icon": "circle-dollar-sign",
				"route_options": '{"sidebar": "Banking"}',
			},
			"Accounts Setup": {
				"label": "Accounts Setup",
				"link_to": "Account",
				"link_type": "DocType",
				"icon": "database",
				"route_options": '{"sidebar": "Accounts Setup"}',
			},
		}

		items = create_sidebar_items(add_accounts_sidebar_shortcuts(module_info, sidebar_links))
		labels = [item.label for item in items]

		self.assertEqual(
			labels,
			[
				"Invoicing",
				"Financial Reports",
				"Dashboards",
				"Accounts",
				"Payments",
				"Banking",
				"Accounts Setup",
				"Reports",
				"General Ledger",
			],
		)

		banking = next(item for item in items if item.label == "Banking")
		self.assertEqual(banking.child, 1)
		self.assertFalse(banking.icon)
		self.assertEqual(loads(banking.route_options), {"sidebar": "Banking"})

		accounts_setup = next(item for item in items if item.label == "Accounts Setup")
		self.assertEqual(accounts_setup.child, 0)
		self.assertEqual(loads(accounts_setup.route_options), {"sidebar": "Accounts Setup"})
