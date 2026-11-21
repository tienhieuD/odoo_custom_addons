from odoo.tests import HttpCase, tagged

URL = '/odoo/action-demo_listview_sticky_header_and_column.action_lshc_test_'


@tagged('post_install', '-at_install', 'lshc_lab')
class TestLabTours(HttpCase):
    """Drive the sticky module on the fake wide lists (pin, scroll, check the CSS really sticks)."""

    def test_wide_list(self):
        self.start_tour(URL + 'wide', 'lshc_lab_wide_list', login='admin')

    def test_editable_list(self):
        self.start_tour(URL + 'editable', 'lshc_lab_editable_list', login='admin')

    def test_form_lists(self):
        self.start_tour(URL + 'wide', 'lshc_lab_form_lists', login='admin')
