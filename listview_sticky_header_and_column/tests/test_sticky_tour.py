from odoo.tests import HttpCase, tagged

PARTNER_LIST = '/web#action=base.action_partner_form&view_type=list'


@tagged('post_install', '-at_install')
class TestStickyTour(HttpCase):
    """Real browser checks (getComputedStyle / getBoundingClientRect) on res.partner demo lists."""

    browser_size = "1366,768"

    def test_header_sticky_without_pinned_column(self):
        self.start_tour(PARTNER_LIST, 'lshc_header_sticky', login='admin')

    def test_header_sticky_when_column_pinned(self):
        self.start_tour(PARTNER_LIST, 'lshc_header_sticky_pinned', login='admin')

    def test_pin_buttons_added_once(self):
        self.start_tour(PARTNER_LIST, 'lshc_pin_buttons', login='admin')

    def test_pin_column_sticky_on_horizontal_scroll(self):
        self.start_tour(PARTNER_LIST, 'lshc_pin_column', login='admin')

    def test_unpin_column(self):
        self.start_tour(PARTNER_LIST, 'lshc_unpin_column', login='admin')

    def test_pin_persists_after_navigation(self):
        self.start_tour(PARTNER_LIST, 'lshc_pin_persist', login='admin')

    def test_checkbox_and_optional_columns(self):
        self.start_tour(PARTNER_LIST, 'lshc_checkbox_optional', login='admin')

    def test_one2many_list_in_form(self):
        group = self.env.ref('base.group_user')
        self.start_tour('/web#action=base.action_res_groups&view_type=form&id=%d' % group.id, 'lshc_o2m_form', login='admin')

    def test_list_in_dialog(self):
        self.start_tour('/web#action=base.action_partner_form&view_type=form&id=', 'lshc_dialog', login='admin')

    def test_pin_first_column(self):
        group = self.env.ref('base.group_user')
        self.start_tour('/web#action=base.action_res_groups&view_type=form&id=%d' % group.id, 'lshc_pin_first_column', login='admin')

    def test_unpin_then_reopen_list(self):
        self.start_tour(PARTNER_LIST, 'lshc_unpin_remount', login='admin')
