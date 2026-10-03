from unittest.mock import patch

from frappe.tests import UnitTestCase

import hrms.hooks
import hrms.setup


class TestHireRabbitsBootstrap(UnitTestCase):
	def test_after_migrate_runs_hrms_setup_and_hirerabbits_bootstrap(self):
		self.assertEqual(hrms.hooks.after_migrate, "hrms.setup.after_migrate")

		with (
			patch("hrms.setup.update_select_perm_after_install") as update_select_perm,
			patch("hrms.hirerabbits_bootstrap.apply") as apply_hirerabbits_bootstrap,
		):
			hrms.setup.after_migrate()

		update_select_perm.assert_called_once_with()
		apply_hirerabbits_bootstrap.assert_called_once_with()
