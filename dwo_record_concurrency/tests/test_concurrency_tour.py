from odoo.tests import HttpCase, tagged

RUN = "odoo.__DEBUG__.services['web_tour.tour'].run('%s')"
READY = "odoo.__DEBUG__.services['web_tour.tour'].tours.%s.ready"


@tagged('post_install', '-at_install')
class TestConcurrencyTour(HttpCase):

    def setUp(self):
        super().setUp()
        fields_ = self.env['ir.model.fields'].search([('model', '=', 'res.partner'), ('name', '=', 'name')])
        self.env['dwo.model.concurrency'].create({
            'model_id': self.env['ir.model']._get('res.partner').id, 'field_ids': [(6, 0, fields_.ids)]})
        self.env['res.partner'].create({'name': 'DWO Conflict Partner'})

    def _start(self, tour):
        # Odoo 12 has no start_tour(): run the tour from the browser
        partner = self.env['res.partner'].search([('name', '=', 'DWO Conflict Partner')])
        url = '/web#action=base.action_partner_form&id=%s&view_type=form' % partner.id
        self.browser_js(url, RUN % tour, READY % tour, login='admin', timeout=180)

    def test_conflict_dialog_tour(self):
        self._start('dwo_concurrency_conflict')

    def test_no_conflict_on_other_field_tour(self):
        self._start('dwo_concurrency_no_conflict')

    def test_discard_shows_latest_data_tour(self):
        self._start('dwo_concurrency_discard')
