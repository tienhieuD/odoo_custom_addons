from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAutoSplit(TransactionCase):
    """The split mode is offered automatically on window actions that have a list and a form view."""

    def setUp(self):
        super().setUp()
        self.action = self.env.ref('base.action_partner_form')

    def _types(self, action=None):
        return [view_type for _view_id, view_type in (action or self.action).views]

    def test_split_added_after_list(self):
        types = self._types()
        self.assertIn('split', types)
        self.assertEqual(types.index('split'), types.index('list') + 1, "split comes right after the list view")

    def test_default_view_unchanged(self):
        # kanban stays the first view of the partner action: the split mode never becomes the default
        self.assertNotEqual(self._types()[0], 'split')

    def test_opt_out_on_action(self):
        self.action.no_split_view = True
        self.assertNotIn('split', self._types())

    def test_global_setting(self):
        self.env['ir.config_parameter'].set_bool('web_split_view.auto_split', False)
        self.assertNotIn('split', self._types(self.env.ref('base.action_partner_form')))

    def test_no_split_without_form_or_in_dialog(self):
        action = self.env['ir.actions.act_window'].create({
            'name': 'Only list', 'res_model': 'res.partner', 'view_mode': 'list'})
        self.assertNotIn('split', self._types(action))
        dialog = self.env['ir.actions.act_window'].create({
            'name': 'Dialog', 'res_model': 'res.partner', 'view_mode': 'list,form', 'target': 'new'})
        self.assertNotIn('split', self._types(dialog))

    def test_default_split_view_loads(self):
        views = self.env['res.partner'].get_views([(False, 'split')])
        self.assertEqual(views['views']['split']['arch'].strip()[:6], '<split')
