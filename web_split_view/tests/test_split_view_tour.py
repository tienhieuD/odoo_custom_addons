from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestSplitViewTour(HttpCase):

    def test_split_view_tour(self):
        self.start_tour('/web#action=web_split_view.action_customer_split_demo', 'web_split_view_tour', login='admin')

    def test_split_view_auto_tour(self):
        self.start_tour('/web#action=base.action_partner_form&view_type=split', 'web_split_view_auto_tour', login='admin')

    def test_split_view_state_tour(self):
        self.start_tour('/web#action=base.action_partner_form&view_type=split', 'web_split_view_state_tour', login='admin')

    def test_split_view_expand_tour(self):
        self.start_tour('/web#action=base.action_partner_form&view_type=split', 'web_split_view_expand_tour', login='admin')

    def test_split_view_back_tour(self):
        self.start_tour('/web#action=base.action_partner_form&view_type=split', 'web_split_view_back_tour', login='admin')
