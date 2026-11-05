from odoo.release import version_info
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestConcurrencyTour(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fields_ = cls.env['ir.model.fields'].search([('model', '=', 'res.partner'), ('name', '=', 'name')])
        cls.env['dwo.model.concurrency'].create({
            'model_id': cls.env['ir.model']._get('res.partner').id, 'field_ids': [(6, 0, fields_.ids)]})
        cls.env['res.partner'].create({'name': 'DWO Conflict Partner'})

    def _start(self, tour):
        partner = self.env['res.partner'].search([('name', '=', 'DWO Conflict Partner')])
        if version_info[0] >= 18:
            url = f'/odoo/action-base.action_partner_form/{partner.id}'
        else:
            url = f'/web#action=base.action_partner_form&id={partner.id}&view_type=form'
        self.start_tour(url, tour, login='admin')

    def test_conflict_dialog_tour(self):
        self._start('dwo_concurrency_conflict')

    def test_no_conflict_on_other_field_tour(self):
        self._start('dwo_concurrency_no_conflict')

    def test_discard_shows_latest_data_tour(self):
        self._start('dwo_concurrency_discard')
