# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestFormFocusTour(HttpCase):
    """The three layouts of a form view and the shortcut (the chatter checks run when Discuss is installed)."""

    def test_01_layouts(self):
        partner = self.env["res.partner"].create({"name": "Form focus"})
        self.start_tour("/odoo/res.partner/%d" % partner.id, "dwo_form_focus_mode_tour", login="admin")
