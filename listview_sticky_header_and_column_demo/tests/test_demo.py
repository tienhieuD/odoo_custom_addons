# -*- coding: utf-8 -*-
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStickyDemo(TransactionCase):
    def test_demo_data(self):
        self.assertEqual(self.env["res.users"].search_count([("login", "in", ["demo_alice", "demo_bob", "demo_carol"])]), 3)
        self.assertGreaterEqual(self.env["res.partner"].search_count([("comment", "like", "list view demo")]), 400)
