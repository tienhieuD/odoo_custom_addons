from odoo.tests import HttpCase, tagged

URL = '/web#action=listview_sticky_test_lab.action_lshc_test_'
RUN = "odoo.__DEBUG__.services['web_tour.tour'].run('%s')"
READY = "odoo.__DEBUG__.services['web_tour.tour'].tours.%s.ready"


@tagged('post_install', '-at_install', 'lshc_lab')
class TestLabTours(HttpCase):
    """Drive the sticky module on the fake wide lists (pin, scroll, check the CSS really sticks)."""

    def _tour(self, action, name):
        self.browser_js(URL + action, RUN % name, READY % name, login='admin', timeout=180)

    def test_wide_list(self):
        self._tour('wide', 'lshc_lab_wide_list')

    def test_editable_list(self):
        self._tour('editable', 'lshc_lab_editable_list')

    def test_form_lists(self):
        self._tour('wide', 'lshc_lab_form_lists')
