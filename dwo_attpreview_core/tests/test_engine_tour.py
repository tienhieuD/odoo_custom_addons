# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestEngineTicksTour(HttpCase):
    # Odoo 17: Chrome needs "w,h" (the default "1366x768" of 17 is ignored) and URLs are /web#... (no /odoo/...)
    browser_size = "1366,768"

    def _module_state(self, db_state):
        """Put the mail engine module in this state in the database (rolled back after the test): ``uninstallable``
        is what a module that is not in the addons path looks like, ``uninstalled`` a module that can be installed."""
        self.env["ir.module.module"].sudo().search([("name", "=", "dwo_attpreview_mail")]).state = db_state
        self.env.flush_all()

    def test_tour_engine_not_in_addons_opens_popup(self):
        self._module_state("uninstallable")
        self.start_tour("/web#action=base_setup.action_general_configuration",
                        "dwo_attpreview_core_tour_engine_popup", login="admin")

    def test_tour_engine_in_addons_ticks_normally(self):
        self._module_state("uninstalled")
        self.start_tour("/web#action=base_setup.action_general_configuration",
                        "dwo_attpreview_core_tour_engine_tick", login="admin")
