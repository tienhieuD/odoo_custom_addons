from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install', 'lshc_lab')
class TestLabTours(HttpCase):
    """Drive the sticky module on the fake wide lists (pin, scroll, check the CSS really sticks)."""

    def test_wide_list(self):
        self.start_tour('/odoo/action-listview_sticky_test_lab.action_lshc_test_wide', 'lshc_lab_wide_list', login='admin')

    def test_editable_list(self):
        self.start_tour('/odoo/action-listview_sticky_test_lab.action_lshc_test_editable', 'lshc_lab_editable_list', login='admin')

    def test_form_lists(self):
        self.start_tour('/odoo/action-listview_sticky_test_lab.action_lshc_test_wide', 'lshc_lab_form_lists', login='admin')
