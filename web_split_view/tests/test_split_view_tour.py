from odoo.tests import HttpCase, tagged

URL = '/web#action=base.action_partner_form&view_type=split'
RUN = "odoo.__DEBUG__.services['web_tour.tour'].run('%s')"
READY = "odoo.__DEBUG__.services['web_tour.tour'].tours.%s.ready"


@tagged('post_install', '-at_install')
class TestSplitViewTour(HttpCase):

    def _tour(self, name):
        # Odoo 12 has no start_tour(): run the tour from the browser
        self.browser_js(URL, RUN % name, READY % name, login='admin', timeout=180)

    def test_split_view_auto_tour(self):
        self._tour('web_split_view_auto_tour')

    def test_split_view_expand_tour(self):
        self._tour('web_split_view_expand_tour')

    def test_split_view_state_tour(self):
        self._tour('web_split_view_state_tour')

    def test_split_view_search_tour(self):
        self._tour('web_split_view_search_tour')
