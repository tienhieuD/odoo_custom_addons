from odoo.tests import HttpCase, tagged

PARTNER_LIST = '/odoo/action-base.action_partner_form?view_type=list'


@tagged('post_install', '-at_install')
class TestStickyTour(HttpCase):
    """Real browser checks (getComputedStyle / getBoundingClientRect) on res.partner demo lists."""

    def test_header_sticky_on_vertical_scroll(self):
        self.start_tour(PARTNER_LIST, 'lshc_header_sticky', login='admin')

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
        self.start_tour('/odoo/action-base.action_res_groups/%d' % group.id, 'lshc_o2m_form', login='admin')

    def test_pin_first_column(self):
        group = self.env.ref('base.group_user')
        self.start_tour('/odoo/action-base.action_res_groups/%d' % group.id, 'lshc_pin_first_column', login='admin')

    def test_unpin_then_reopen_list(self):
        self.start_tour(PARTNER_LIST, 'lshc_unpin_remount', login='admin')

    def test_list_in_dialog(self):
        self.start_tour('/odoo/action-base.action_partner_form/new', 'lshc_dialog', login='admin')

    def test_edited_row_above_pinned_cells_and_header(self):
        model = self.env['ir.model'].create({'name': 'Lshc sticky', 'model': 'x_lshc_sticky'})
        for i in range(6):
            self.env['ir.model.access'].create({
                'name': 'access %d' % i, 'model_id': model.id,
                'group_id': self.env.ref('base.group_user').id, 'perm_read': True,
            })
        self.start_tour('/odoo/action-base.action_model_model/%d' % model.id, 'lshc_edit_row_on_top', login='admin')
