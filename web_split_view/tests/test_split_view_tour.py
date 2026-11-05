from odoo.tests import HttpCase, tagged

URL = '/web#action=base.action_partner_form&view_type=split'


@tagged('post_install', '-at_install')
class TestSplitViewTour(HttpCase):

    def test_split_view_auto_tour(self):
        self.start_tour(URL, 'web_split_view_auto_tour', login='admin')

    def test_split_view_expand_tour(self):
        self.start_tour(URL, 'web_split_view_expand_tour', login='admin')

    def test_split_view_state_tour(self):
        self.start_tour(URL, 'web_split_view_state_tour', login='admin')

    def test_split_view_search_tour(self):
        self.start_tour(URL, 'web_split_view_search_tour', login='admin')
