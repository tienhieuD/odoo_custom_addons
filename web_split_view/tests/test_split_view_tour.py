from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestSplitViewTour(HttpCase):

    def test_split_view_tour(self):
        self.start_tour('/odoo/action-web_split_view.action_customer_split_demo', 'web_split_view_tour', login='admin')
