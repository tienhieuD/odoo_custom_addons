# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestFormFocusTour(HttpCase):
    """The three layouts of a form view and the shortcut; they only exist on forms that have a chatter."""

    def test_01_layouts(self):
        if not self.env["ir.module.module"].search([("name", "=", "mail"), ("state", "=", "installed")]):
            self.skipTest("the layouts need a form with a chatter: Discuss (mail) is not installed")
        partner = self.env["res.partner"].create({"name": "Form focus"})
        self.start_tour("/web#id=%d&model=res.partner&view_type=form" % partner.id, "dwo_form_focus_mode_tour", login="admin")

    def test_02_form_without_chatter(self):
        """A form that has no chatter shows no button and no bar, even when a layout is remembered."""
        self.start_tour("/web#action=base.action_country", "dwo_form_focus_mode_nochatter_tour", login="admin")
