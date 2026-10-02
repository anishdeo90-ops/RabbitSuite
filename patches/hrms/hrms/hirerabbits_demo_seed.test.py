import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("hirerabbits_demo_seed.py")


def load_seed_module():
	spec = importlib.util.spec_from_file_location("hirerabbits_demo_seed", MODULE_PATH)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


class DemoSeedContractTest(unittest.TestCase):
	def test_seed_names_are_stable_and_readable(self):
		seed = load_seed_module()

		self.assertEqual(seed.stable_seed_name("HD Ticket", "login issue"), "HR-DEMO-HD-TICKET-LOGIN-ISSUE")
		self.assertEqual(
			seed.stable_seed_name("Subcontracting Order", "main flow"),
			"HR-DEMO-SUBCONTRACTING-ORDER-MAIN-FLOW",
		)

	def test_seed_specs_have_unique_names(self):
		seed = load_seed_module()
		names = [record["name"] for record in seed.SEED_RECORDS]

		self.assertEqual(len(names), len(set(names)))

	def test_seed_specs_cover_the_suite_modules(self):
		seed = load_seed_module()
		coverage = seed.seed_coverage()

		for module in [
			"ERP",
			"Accounts",
			"Selling",
			"Buying",
			"Stock",
			"Manufacturing",
			"Subcontracting",
			"Projects",
			"Assets",
			"Quality",
			"HRMS",
			"Payroll",
			"CRM",
			"Helpdesk",
		]:
			with self.subTest(module=module):
				self.assertIn(module, coverage)
				self.assertGreater(len(coverage[module]), 0)

	def test_stock_workspace_left_menu_doctypes_are_seeded(self):
		seed = load_seed_module()
		stock_doctypes = set(seed.seed_coverage()["Stock"])

		for doctype in [
			"Stock Entry",
			"Purchase Receipt",
			"Delivery Note",
			"Material Request",
			"Pick List",
			"Landed Cost Voucher",
			"Stock Reconciliation",
			"Packing Slip",
			"Quality Inspection",
		]:
			with self.subTest(doctype=doctype):
				self.assertIn(doctype, stock_doctypes)

	def test_apply_report_lists_created_skipped_and_failed(self):
		seed = load_seed_module()
		report = seed.empty_report()

		self.assertEqual(report["created"], [])
		self.assertEqual(report["skipped"], [])
		self.assertEqual(report["failed"], [])


if __name__ == "__main__":
	unittest.main()
