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

    def test_pin_every_column_of_sale_order_lines(self):
        """Order Lines columns (Description, Quantity, Unit Price) have no data-name: they must be pinnable too."""
        if 'sale.order' not in self.env:
            self.skipTest('needs the sale module (run with listview_sticky_header_and_column,sale)')
        partner = self.env['res.partner'].create({'name': 'Lshc customer'})
        products = self.env['product.product'].search([('sale_ok', '=', True)], limit=6)
        self.assertGreaterEqual(len(products), 3, 'sale demo products needed')
        order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {'product_id': p.id, 'product_uom_qty': 2}) for p in products],
        })
        self.start_tour('/odoo/action-sale.action_quotations_with_onboarding/%d' % order.id, 'lshc_order_lines', login='admin')
