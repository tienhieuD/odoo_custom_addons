from unittest.mock import patch

from odoo.tests import TransactionCase, tagged
from odoo.addons.dwo_record_concurrency.models.dwo_record_presence import dwo_channel_allowed
from odoo.tests.common import new_test_user


@tagged('post_install', '-at_install')
class TestConcurrency(TransactionCase):

    def setUp(self):
        super().setUp()
        self.model = self.env['ir.model']._get('res.partner')
        fields_ = self.env['ir.model.fields'].search([
            ('model', '=', 'res.partner'), ('name', 'in', ['name', 'parent_id', 'category_id'])])
        self.config = self.env['dwo.model.concurrency'].create({'model_id': self.model.id, 'field_ids': [(6, 0, fields_.ids)]})
        self.partner = self.env['res.partner'].create({'name': 'Original'})
        self.concurrency = self.env['dwo.model.concurrency']

    def _capture_bus(self):
        sent = []
        bus_cls = type(self.env['bus.bus'])
        if hasattr(bus_cls, '_sendone'):
            def _sendone(this, target, notification_type, message):
                sent.append((target, notification_type, message))
            return sent, patch.object(bus_cls, '_sendone', _sendone)

        def sendone(this, channel, message):    # 12 .. 14: the type travels inside the message
            sent.append((channel, message.get('type'), message.get('payload')))
        return sent, patch.object(bus_cls, 'sendone', sendone)

    def test_ping_has_names_only(self):
        sent, patcher = self._capture_bus()
        with patcher:
            self.partner.with_context(current_tab_id='tab-1').write({'name': 'Secret value'})
        pings = [msg for target, kind, msg in sent if kind == 'dwo_record_presence']
        self.assertEqual(len(pings), 1)
        self.assertEqual(pings[0]['fields'], ['name'])
        self.assertEqual(pings[0]['current_tab_id'], 'tab-1')
        self.assertNotIn('data', pings[0])
        self.assertNotIn('Secret value', str(pings[0]))

    def test_no_ping_for_unwatched_field_or_model(self):
        sent, patcher = self._capture_bus()
        with patcher:
            self.partner.write({'website': 'https://example.com'})
            self.env['res.partner.category'].create({'name': 'x'}).write({'name': 'y'})
        self.assertFalse([1 for _t, kind, _m in sent if kind == 'dwo_record_presence'])

    def test_watched_fields_are_cached_and_invalidated(self):
        self.assertEqual(self.concurrency._get_watched_field_names('res.partner'), ('category_id', 'name', 'parent_id'))
        with self.assertQueryCount(0):
            self.concurrency._get_watched_field_names('res.partner')
        self.config.field_ids = [(6, 0, self.config.field_ids.filtered(lambda f: f.name == 'name').ids)]
        self.assertEqual(self.concurrency._get_watched_field_names('res.partner'), ('name',))
        self.config.active = False
        self.assertEqual(self.concurrency._get_watched_field_names('res.partner'), ())

    def test_conflict_only_on_fields_the_user_edits(self):
        snapshot = self.concurrency.dwo_snapshot('res.partner', self.partner.id)
        self.assertEqual(snapshot['name'], 'Original')
        # another user changes the name
        self.partner.write({'name': 'Theirs'})
        conflicts = self.concurrency.dwo_check_conflict('res.partner', self.partner.id, snapshot, ['name'])
        self.assertEqual([c['name'] for c in conflicts], ['name'])
        self.assertEqual(conflicts[0]['server'], 'Theirs')
        # the user edits another field only: nothing to report
        self.assertEqual(self.concurrency.dwo_check_conflict('res.partner', self.partner.id, snapshot, ['parent_id']), [])
        # an unwatched field is never reported
        self.assertEqual(self.concurrency.dwo_check_conflict('res.partner', self.partner.id, snapshot, ['website']), [])

    def test_conflict_relational_values_are_normalized(self):
        company = self.env['res.partner'].create({'name': 'ACME'})
        tags = self.env['res.partner.category'].create([{'name': 'a'}, {'name': 'b'}])
        snapshot = self.concurrency.dwo_snapshot('res.partner', self.partner.id)
        # same ids, other order -> no conflict
        self.partner.write({'category_id': [(6, 0, tags.ids)]})
        snapshot_after = self.concurrency.dwo_snapshot('res.partner', self.partner.id)
        self.partner.write({'category_id': [(6, 0, list(reversed(tags.ids)))]})
        self.assertEqual(self.concurrency.dwo_check_conflict(
            'res.partner', self.partner.id, snapshot_after, ['category_id']), [])
        # really different -> conflict
        self.assertTrue(self.concurrency.dwo_check_conflict(
            'res.partner', self.partner.id, snapshot, ['category_id']))
        self.partner.write({'parent_id': company.id})
        conflicts = self.concurrency.dwo_check_conflict('res.partner', self.partner.id, snapshot, ['parent_id'])
        self.assertEqual(conflicts[0]['server'], 'ACME')

    def test_check_never_raises_for_missing_record(self):
        self.assertEqual(self.concurrency.dwo_check_conflict('res.partner', 0, {}, ['name']), [])
        self.assertEqual(self.concurrency.dwo_check_conflict('does.not.exist', 1, {'x': 1}, ['x']), [])

    def test_presence_channel_follows_read_access(self):
        env = self.env
        channel = 'dwo_record_presence:res.partner:%s' % self.partner.id
        self.assertTrue(dwo_channel_allowed(env, channel))
        self.assertTrue(dwo_channel_allowed(env, 'some_other_channel'))
        portal = new_test_user(env, login='dwo_portal', groups='base.group_portal')
        # a portal user cannot read the records of an internal model
        self.assertFalse(dwo_channel_allowed(env(user=portal.id), 'dwo_record_presence:ir.cron:1'))
        self.assertFalse(dwo_channel_allowed(env, 'dwo_record_presence:garbage'))

    def test_only_administrators_edit_the_configuration(self):
        user = new_test_user(self.env, login='dwo_user', groups='base.group_user')
        self.assertTrue(self.concurrency.with_user(user).search([]))
        self.assertTrue(self.concurrency.with_user(user).dwo_snapshot('res.partner', self.partner.id))
        with self.assertRaises(Exception):
            self.concurrency.with_user(user).create({'model_id': self.model.id})

    # ------------------------------------------------------------------ more coverage
    def test_write_on_several_records_pings_each_record_once(self):
        other = self.env['res.partner'].create({'name': 'Other'})
        sent, patcher = self._capture_bus()
        with patcher:
            (self.partner | other).write({'name': 'Same'})
        pings = [msg for _t, kind, msg in sent if kind == 'dwo_record_presence']
        self.assertEqual(sorted(p['res_id'] for p in pings), sorted([self.partner.id, other.id]))

    def test_archiving_or_deleting_the_configuration_stops_pings(self):
        sent, patcher = self._capture_bus()
        with patcher:
            self.config.active = False
            self.partner.write({'name': 'archived config'})
            self.config.active = True
            self.partner.write({'name': 'active config'})
            self.config.unlink()
            self.partner.write({'name': 'deleted config'})
        pings = [msg for _t, kind, msg in sent if kind == 'dwo_record_presence']
        self.assertEqual(len(pings), 1)

    def test_deleting_the_model_deletes_the_configuration(self):
        model = self.env['ir.model'].create({'name': 'Dwo tmp', 'model': 'x_dwo_tmp', 'state': 'manual'})
        config = self.concurrency.create({'model_id': model.id})
        model.unlink()
        self.assertFalse(config.exists())

    def test_skip_context_disables_the_ping(self):
        sent, patcher = self._capture_bus()
        with patcher:
            self.partner.with_context(dwo_skip_concurrency=True).write({'name': 'silent'})
        self.assertFalse([1 for _t, kind, _m in sent if kind == 'dwo_record_presence'])

    def test_normalization_of_every_field_type(self):
        Normalize = self.concurrency._normalize_value
        tag = self.env['res.partner.category'].create({'name': 'tag'})
        self.partner.write({'category_id': [(6, 0, tag.ids)]})
        self.assertEqual(Normalize(self.partner, 'name'), ('Original', 'Original'))
        self.assertEqual(Normalize(self.partner, 'category_id'), ([tag.id], 'tag'))
        self.assertEqual(Normalize(self.partner, 'active'), (True, 'Yes'))
        self.assertEqual(Normalize(self.partner, 'parent_id'), (False, ''))
        self.assertEqual(Normalize(self.partner, 'type'), ('contact', 'Contact'))      # selection and its label
        self.assertEqual(Normalize(self.partner, 'comment'), (False, ''))              # empty html

    def test_normalization_of_date_float_and_binary(self):
        Normalize = self.concurrency._normalize_value
        rate = self.env['res.currency.rate'].create({
            'name': '2026-01-31', 'currency_id': self.env.ref('base.EUR').id, 'rate': 1.23456789,
        })
        self.assertEqual(Normalize(rate, 'name'), ('2026-01-31', '2026-01-31'))                 # date
        self.assertIsInstance(Normalize(rate, 'rate')[0], float)                                # float
        self.assertTrue(Normalize(self.env.user, 'create_date')[0])                            # datetime
        png = ('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==')
        self.assertFalse(Normalize(self.partner, 'image_1920')[0])                              # empty binary
        self.partner.image_1920 = png
        digest = Normalize(self.partner, 'image_1920')[0]
        self.assertEqual(len(digest), 40)                                                       # sha1 of the content
        self.assertEqual(digest, Normalize(self.partner, 'image_1920')[0])                      # stable

    def test_conflict_ignores_fields_missing_from_the_snapshot(self):
        self.partner.write({'name': 'changed'})
        self.assertEqual(self.concurrency.dwo_check_conflict('res.partner', self.partner.id, {}, ['name']), [])
        self.assertEqual(self.concurrency.dwo_check_conflict('res.partner', self.partner.id, {'name': 'Original'}, []), [])

    def test_conflict_reports_the_last_writer(self):
        snapshot = self.concurrency.dwo_snapshot('res.partner', self.partner.id)
        writer = new_test_user(self.env, login='dwo_writer', name='Walter Writer', groups='base.group_partner_manager,base.group_user')
        self.partner.with_user(writer).write({'name': 'by writer'})
        conflicts = self.concurrency.dwo_check_conflict('res.partner', self.partner.id, snapshot, ['name'])
        self.assertEqual(conflicts[0]['write_uid_name'], 'Walter Writer')
        self.assertEqual(conflicts[0]['label'], 'Name')

    def test_snapshot_of_a_deleted_or_unknown_record_is_empty(self):
        self.assertEqual(self.concurrency.dwo_snapshot('res.partner', 0), {})
        self.assertEqual(self.concurrency.dwo_snapshot('res.partner', 987654321), {})
        self.assertEqual(self.concurrency.dwo_snapshot('does.not.exist', 1), {})
        self.assertEqual(self.concurrency.dwo_snapshot('res.partner.category', 1), {})   # not watched

    def test_get_watched_fields_for_the_client(self):
        self.assertEqual(sorted(self.concurrency.get_watched_fields('res.partner')), ['category_id', 'name', 'parent_id'])
        self.assertEqual(self.concurrency.get_watched_fields('res.users'), [])

    def test_presence_ping_never_contains_values_even_for_binary_fields(self):
        sent, patcher = self._capture_bus()
        with patcher:
            self.env['dwo.record.presence'].publish_presence('res.partner', self.partner.id, fields=['name'])
        message = [m for _t, kind, m in sent if kind == 'dwo_record_presence'][0]
        self.assertEqual(set(message), {'model', 'res_id', 'user_id', 'user_name', 'current_tab_id', 'state', 'fields'})
