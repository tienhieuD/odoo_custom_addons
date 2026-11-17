# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestHeaderFilterTour(HttpCase):
    """The filter icons of the attachments list: checkboxes, quick dates, operators, and the facet in the search bar."""

    def setUp(self):
        super().setUp()
        self.env["ir.attachment"].create([
            {"name": "dwo-hf-a.txt", "raw": b"a"},
            {"name": "dwo-hf-b.txt", "raw": b"b"},
            {"name": "dwo-hf-link", "type": "url", "url": "https://example.com/"},
        ])

    def test_01_filters_and_search_bar(self):
        self.start_tour("/odoo/action-base.action_attachment", "dwo_listview_header_filter_tour", login="admin")


@tagged("post_install", "-at_install")
class TestStickyCompatibility(HttpCase):
    """Installed together with the list sticky header and column freeze module of DuoTEK (skipped when it is not)."""

    def test_01_with_sticky_header_and_column(self):
        sticky = self.env["ir.module.module"].search([
            ("name", "=", "listview_sticky_header_and_column"), ("state", "=", "installed")])
        if not sticky:
            self.skipTest("listview_sticky_header_and_column is not installed")
        self.env["ir.attachment"].create({"name": "dwo-hf-link", "type": "url", "url": "https://example.com/"})
        self.start_tour("/odoo/action-base.action_attachment", "dwo_listview_header_filter_sticky_tour", login="admin")
