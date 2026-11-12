from odoo.tests import HttpCase, tagged

PARTNER_LIST = '/web#action=base.action_partner_form&view_type=list'
TOUR = "odoo.__DEBUG__.services['web_tour.tour']"


@tagged('post_install', '-at_install')
class TestStickyTour(HttpCase):
    """Real browser checks (getComputedStyle / getBoundingClientRect) on res.partner demo lists."""

    browser_size = "1366,768"

    def _run_tour(self, url, name):
        # Odoo 12 has no start_tour: the tour is started by hand and waited for
        self.browser_js(url, "%s.run('%s')" % (TOUR, name), "%s.tours.%s.ready" % (TOUR, name), login='admin')

    def test_header_sticky_without_pinned_column(self):
        self._run_tour(PARTNER_LIST, 'lshc_header_sticky')

    def test_header_sticky_when_column_pinned(self):
        self._run_tour(PARTNER_LIST, 'lshc_header_sticky_pinned')

    def test_pin_buttons_added_once(self):
        self._run_tour(PARTNER_LIST, 'lshc_pin_buttons')

    def test_pin_column_sticky_on_horizontal_scroll(self):
        self._run_tour(PARTNER_LIST, 'lshc_pin_column')

    def test_unpin_column(self):
        self._run_tour(PARTNER_LIST, 'lshc_unpin_column')

    def test_pin_persists_after_navigation(self):
        self._run_tour(PARTNER_LIST, 'lshc_pin_persist')

    def test_checkbox_and_optional_columns(self):
        self._run_tour(PARTNER_LIST, 'lshc_checkbox_optional')

    def test_one2many_list_in_form(self):
        group = self.env.ref('base.group_user')
        self._run_tour('/web#action=base.action_res_groups&view_type=form&id=%d' % group.id, 'lshc_o2m_form')

    def test_list_in_dialog(self):
        self._run_tour('/web#action=base.action_partner_form&view_type=form&id=', 'lshc_dialog')

    def test_pin_first_column(self):
        group = self.env.ref('base.group_user')
        self._run_tour('/web#action=base.action_res_groups&view_type=form&id=%d' % group.id, 'lshc_pin_first_column')

    def test_unpin_then_reopen_list(self):
        self._run_tour(PARTNER_LIST, 'lshc_unpin_remount')
