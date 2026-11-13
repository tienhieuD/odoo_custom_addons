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

    def test_edited_row_above_pinned_cells_and_header(self):
        model = self.env['ir.model'].create({'name': 'Lshc sticky', 'model': 'x_lshc_sticky'})
        for i in range(6):
            self.env['ir.model.access'].create({
                'name': 'access %d' % i, 'model_id': model.id,
                'group_id': self.env.ref('base.group_user').id, 'perm_read': True,
            })
        self._run_tour('/web#action=base.action_model_model&view_type=form&id=%d' % model.id, 'lshc_edit_row_on_top')

    def test_pin_every_column_of_sale_order_lines(self):
        """Order Lines: every data header has one pin button (none on the handle); pinning works on each."""
        if 'sale.order' not in self.env:
            self.skipTest('needs the sale module (run with listview_sticky_header_and_column,sale)')
        partner = self.env['res.partner'].create({'name': 'Lshc customer'})
        products = self.env['product.product'].search([('sale_ok', '=', True)], limit=6)
        self.assertGreaterEqual(len(products), 3, 'sale demo products needed')
        order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {'product_id': p.id, 'product_uom_qty': 2}) for p in products],
        })
        self._run_tour('/web#action=sale.action_quotations&view_type=form&id=%d' % order.id, 'lshc_order_lines')
