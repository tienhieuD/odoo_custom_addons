# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
from odoo.tests import HttpCase, tagged

from .sample_engine import patch_sample_engine


@tagged("post_install", "-at_install")
class TestAttPreviewTour(HttpCase):

    def _partner_with(self, *files):
        """files: (name, raw, mimetype); returns the partner whose chatter shows them in one message."""
        patch_sample_engine(self)
        partner = self.env["res.partner"].create({"name": "Tour Partner"})
        atts = self.env["ir.attachment"].create([{
            "name": name, "raw": raw, "mimetype": mimetype,
            "res_model": "res.partner", "res_id": partner.id} for name, raw, mimetype in files])
        partner.message_post(body="file", attachment_ids=atts.ids)
        return partner

    def test_tour_open_preview_from_chatter(self):
        # large dialog, icon next to the title, toolbar, full screen
        partner = self._partner_with(("notes.sample", b"tour content", "application/x-dwo-sample"))
        self.start_tour("/odoo/res.partner/%d" % partner.id, "dwo_attpreview_core_tour", login="admin")

    def test_tour_unsupported_file_shows_toast_not_dialog(self):
        partner = self._partner_with(("data.xyz", b"\x00\x01binary", "application/octet-stream"))
        self.start_tour("/odoo/res.partner/%d" % partner.id, "dwo_attpreview_core_tour_unsupported", login="admin")

    def test_tour_several_files_previous_next(self):
        partner = self._partner_with(
            ("first.sample", b"first content", "application/x-dwo-sample"),
            ("second.sample", b"second content", "application/x-dwo-sample"))
        self.start_tour("/odoo/res.partner/%d" % partner.id, "dwo_attpreview_core_tour_several", login="admin")
