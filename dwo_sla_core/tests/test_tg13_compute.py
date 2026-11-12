# -*- coding: utf-8 -*-
"""TG-13: field compute có lưu / không lưu, đánh giá lại thủ công (docs/060 TC-CMP-*).

Model thử FX-CMP dựng bằng model manual `x_sla_cmp_ticket` (tên phải có tiền tố `x_`; 060 ghi
`x.sla.cmp.ticket` — xem ghi chú lệch trong TASKS.md). Field manual có compute bằng code Python.
Refs: REQ-FUNC-005, 015, 031, 032, 042, 050, REQ-INT-020
"""
from unittest.mock import patch

from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
MODEL = 'x_sla_cmp_ticket'


class CmpCase(SlaCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cmp_model = cls.env['ir.model'].create({
            'name': "SLA CMP Ticket", 'model': MODEL, 'state': 'manual'})
        cls._add_fields()
        cls.env['sla.definition']._register_sla_hook()

    @classmethod
    def _add_fields(cls):
        def field(name, ttype, **vals):
            return cls.env['ir.model.fields'].create({
                'name': name, 'model_id': cls.cmp_model.id, 'ttype': ttype,
                'state': 'manual', 'field_description': name, **vals})

        # Odoo 12: the options of a manual selection field are a text (13+: `selection_ids`)
        field('x_stage', 'selection', selection="[('new', 'new'), ('work', 'work'), ('resolved', 'resolved')]")
        field('x_weight', 'integer')
        field('x_partner_id', 'many2one', relation='res.partner')
        field('x_parent_id', 'many2one', relation=MODEL)
        field('x_child_ids', 'one2many', relation=MODEL, relation_field='x_parent_id')
        field('x_is_resolved', 'boolean', store=True, depends='x_stage', compute=(
            "for rec in self:\n    rec['x_is_resolved'] = rec.x_stage == 'resolved'"))
        field('x_lvl', 'integer', store=True, depends='x_weight', compute=(
            "for rec in self:\n    rec['x_lvl'] = (rec.x_weight or 0) // 10"))
        field('x_is_big', 'boolean', store=False, depends='x_weight', compute=(
            "for rec in self:\n    rec['x_is_big'] = (rec.x_weight or 0) >= 100"))
        field('x_children_done', 'boolean', store=True, depends='x_child_ids.x_stage', compute=(
            "for rec in self:\n"
            "    rec['x_children_done'] = bool(rec.x_child_ids) and "
            "all(c.x_stage == 'resolved' for c in rec.x_child_ids)"))

    @property
    def Ticket(self):
        return self.env[MODEL]

    def cmp_definition(self, **vals):
        base = {'name': "DEF-CMP", 'model_id': self.cmp_model.id, 'duration': 4,
                'schedule_source': 'none', 'start_domain': "[('x_stage', 'in', ['new', 'work'])]",
                'stop_domain': "[('x_is_resolved', '=', True)]", 'active': True}
        base.update(vals)
        return self.Definition.create(base)

    def ticket(self, now=T0, **vals):
        with self.at(now):
            return self.Ticket.create({'x_stage': 'new', **vals})

    def put(self, record, vals, now):
        with self.at(now):
            record.write(vals)
            self.env['base'].flush()

    def task_events(self, record, definition=None):
        tasks = self.Task.sudo().search([('res_model', '=', MODEL), ('res_id', '=', record.id)] + (
            [('sla_id', '=', definition.id)] if definition else []))
        return tasks, tasks.mapped('event_ids').sorted('id').mapped('event')


@tagged(*TAGS, 'tg_13')
class TestStoredCompute(CmpCase):

    def test_cmp_001_stage_drives_stored_compute(self):
        """TC-CMP-001: đổi stage làm is_resolved đổi -> task kết thúc đúng 1 lần."""
        d = self.cmp_definition()
        k = self.ticket()
        tasks, events = self.task_events(k, d)
        self.assertEqual((len(tasks), tasks.stage, events), (1, 'in_progress', ['attach']))
        self.put(k, {'x_stage': 'resolved'}, T0 + hours(1))
        self.assertTrue(k.x_is_resolved)
        tasks, events = self.task_events(k, d)
        self.assertEqual((tasks.stage, tasks.end_time, events), ('achieved', T0 + hours(1), ['attach', 'complete']))

    def test_cmp_002_three_writes_no_extra_events(self):
        """TC-CMP-002: 3 lần ghi trong một giao dịch không sinh event dư thừa."""
        d = self.cmp_definition()
        k = self.ticket()
        task = self.task_events(k, d)[0]
        with self.at(T0 + hours(1)):
            for stage in ('work', 'new', 'work'):
                k.write({'x_stage': stage})
        self.env['base'].flush()
        tasks, events = self.task_events(k, d)
        self.assertEqual((tasks, events), (task, ['attach']))
        self.assertEqual(tasks.stage, 'in_progress')

    def test_cmp_003_compute_change_same_condition_result(self):
        """TC-CMP-003: lvl đổi 1 -> 2 nhưng vẫn thỏa `lvl >= 1` -> không event mới."""
        d = self.cmp_definition(name="DEF-CMP2", start_domain="[('x_lvl', '>=', 1)]", stop_domain=False)
        k = self.ticket(x_weight=10)
        before = self.task_events(k, d)
        self.assertEqual(len(before[0]), 1)
        self.put(k, {'x_weight': 20}, T0 + hours(1))
        self.assertEqual(k.x_lvl, 2)
        self.assertEqual(self.task_events(k, d), before)

    def test_cmp_004_child_change_drives_parent_stop(self):
        """TC-CMP-004: con đổi làm children_done của cha đổi -> task của cha kết thúc."""
        d = self.cmp_definition(name="DEF-CMP3", start_domain="[('x_stage', '=', 'new')]",
                                stop_domain="[('x_children_done', '=', True)]")
        parent = self.ticket()
        child = self.ticket(x_parent_id=parent.id)
        self.assertEqual(self.task_events(parent, d)[0].stage, 'in_progress')
        self.put(child, {'x_stage': 'resolved'}, T0 + hours(1))
        self.assertTrue(parent.x_children_done)
        tasks, events = self.task_events(parent, d)
        self.assertEqual((tasks.stage, events.count('complete')), ('achieved', 1))

    def test_cmp_005_unwatched_recompute_skipped(self):
        """TC-CMP-005: ghi weight (không nằm trong domain nào) không gọi evaluate, không event error."""
        self.cmp_definition()
        k = self.ticket(x_weight=10)
        calls = []
        original = type(self.Engine).evaluate

        def spy(engine, *args, **kwargs):
            calls.append(args)
            return original(engine, *args, **kwargs)

        with patch.object(type(self.Engine), 'evaluate', spy):
            self.put(k, {'x_weight': 50}, T0 + hours(1))
        self.assertEqual((k.x_lvl, len(calls)), (5, 0))
        self.assertEqual(self.task_events(k)[1], ['attach'])
        self.assertFalse(self.Event.sudo().search([('event', '=', 'error')]))


@tagged(*TAGS, 'tg_13')
class TestManualReevaluate(CmpCase):

    def setUp(self):
        super().setUp()
        self.manager = self.make_user('sla_mgr_cmp', 'manager')
        self.viewer = self.make_user('sla_usr_cmp', 'user')
        self.france = self.env.ref('base.fr')
        self.vn = self.env.ref('base.vn')

    def reevaluate(self, records, now=T0 + hours(1)):
        with self.at(now):
            self.Engine.with_user(self.manager).evaluate(records, now=None, changed=set())

    def test_cmp_006_010_relation_condition_needs_reevaluate(self):
        """TC-CMP-006/010: điều kiện qua quan hệ không tự đánh giá; Đánh giá lại gắn task, start = now."""
        d = self.cmp_definition(name="DEF-REL", start_domain="[('x_partner_id.country_id', '=', %d)]" % self.vn.id,
                                stop_domain=False)
        partner = self.make_partner(False, country_id=self.france.id)
        k = self.ticket(x_partner_id=partner.id)
        self.assertFalse(self.task_events(k, d)[0])
        self.put(partner, {'country_id': self.vn.id}, T0 + hours(1))
        self.reevaluate(k)
        tasks, events = self.task_events(k, d)
        self.assertEqual((tasks.stage, tasks.start_time, events), ('in_progress', T0 + hours(1), ['attach']))
        self.assertFalse(self.Event.sudo().search([('event', '=', 'error'), ('res_id', '=', k.id)]))

    def test_cmp_007_008_unstored_compute_no_error(self):
        """TC-CMP-007/008: điều kiện dùng compute không lưu: không event error; Đánh giá lại gắn đúng 1 task, idempotent."""
        d = self.cmp_definition(name="DEF-NS", start_domain="[('x_is_big', '=', True)]", stop_domain=False)
        k = self.ticket(x_weight=50)
        self.put(k, {'x_weight': 500}, T0 + hours(1))
        self.assertFalse(self.Event.sudo().search([('event', '=', 'error'), ('definition_id', '=', d.id)]))
        self.reevaluate(k)
        snapshot = self.task_events(k, d)
        self.assertEqual((len(snapshot[0]), snapshot[0].stage), (1, 'in_progress'))
        self.reevaluate(k)
        self.assertEqual(self.task_events(k, d), snapshot)

    def test_cmp_011_batch_attaches_only_matching(self):
        """TC-CMP-011: đánh giá lại lô 2 record chỉ gắn task cho record có start khớp."""
        d = self.cmp_definition(name="DEF-REL2", start_domain="[('x_weight', '>=', 50)]", stop_domain=False)
        k1, k2 = self.ticket(x_weight=1), self.ticket(x_weight=1)
        self.env.cr.execute("UPDATE %s SET x_weight=50 WHERE id=%%s" % MODEL, (k1.id,))
        k1.invalidate_cache(None, ids=k1.ids)
        self.reevaluate(k1 | k2)
        self.assertEqual((self.task_events(k1, d)[1], self.task_events(k2, d)[1]), (['attach'], []))

    def test_cmp_012_015_reevaluate_idempotent_and_now(self):
        """TC-CMP-012/015: đánh giá lại lần 2 không đổi gì; start = thời điểm đánh giá lại."""
        d = self.cmp_definition(name="DEF-W", start_domain="[('x_weight', '>=', 50)]", stop_domain=False)
        k = self.ticket(x_weight=1)
        self.env.cr.execute("UPDATE %s SET x_weight=50 WHERE id=%%s" % MODEL, (k.id,))
        k.invalidate_cache(None, ids=k.ids)
        self.reevaluate(k, T0 + hours(5))
        tasks, events = self.task_events(k, d)
        self.assertEqual((tasks.start_time, tasks.planned_end_time), (T0 + hours(5), T0 + hours(9)))
        snap = (tasks.id, tasks.stage, tasks.start_time, tasks.planned_end_time, tasks.business_duration, events)
        self.reevaluate(k, T0 + hours(5))
        tasks, events = self.task_events(k, d)
        self.assertEqual((tasks.id, tasks.stage, tasks.start_time, tasks.planned_end_time,
                          tasks.business_duration, events), snap)

    def test_cmp_013_viewer_denied(self):
        """TC-CMP-013: group_sla_user không đánh giá lại hàng loạt được."""
        d = self.cmp_definition()
        self.Event._log_error(definition=d, res_model=MODEL, res_id=1, message="m")
        event = self.Event.sudo().search([('event', '=', 'error')], limit=1)
        with self.assertRaisesRegex(AccessError, 'SLA Manager'):
            event.with_user(self.viewer).action_reevaluate_batch()

    def test_cmp_014_no_reset_on_manual_reevaluate(self):
        """TC-CMP-014: Đánh giá lại thủ công không reset dù field theo dõi đã khác."""
        weight = self.env['ir.model.fields']._get(MODEL, 'x_weight')
        d = self.cmp_definition(name="DEF-R", reset_domain="[('id', '!=', 0)]", reset_field_ids=[(6, 0, weight.ids)])
        k = self.ticket(x_weight=10)
        task = self.task_events(k, d)[0]
        self.env.cr.execute("UPDATE %s SET x_weight=99 WHERE id=%%s" % MODEL, (k.id,))
        k.invalidate_cache(None, ids=k.ids)
        self.reevaluate(k)
        tasks, events = self.task_events(k, d)
        self.assertEqual((tasks, tasks.stage), (task, 'in_progress'))
        self.assertEqual((events.count('reset'), events.count('cancel')), (0, 0))

    def test_cmp_016_stop_beats_cancel(self):
        """TC-CMP-016: stop và cancel cùng khớp khi đánh giá lại -> achieved, không cancel."""
        d = self.cmp_definition(name="DEF-PRI", stop_domain="[('x_weight', '>=', 50)]",
                                cancel_mode='condition', cancel_domain="[('x_weight', '>=', 50)]")
        k = self.ticket(x_weight=10)
        task = self.task_events(k, d)[0]
        self.env.cr.execute("UPDATE %s SET x_weight=60 WHERE id=%%s" % MODEL, (k.id,))
        k.invalidate_cache(None, ids=k.ids)
        with self.at(T0 + hours(1)):
            task.with_user(self.manager).action_reevaluate()
        tasks, events = self.task_events(k, d)
        self.assertEqual((tasks.stage, tasks.end_time, events.count('complete'), events.count('cancel')),
                         ('achieved', T0 + hours(1), 1, 0))


@tagged(*TAGS, 'tg_13')
class TestDerivedConditionFields(SlaCase):

    def test_start_on_unstored_related_field_still_attaches(self):
        """Hồi quy: điều kiện start dùng field related KHÔNG lưu (country_code); ghi field nguồn (country_id) vẫn gắn task."""
        # Odoo 14: res.partner has no `country_code`; a manual related field that is not stored does the same
        self.make_x_field('x_country_code', 'char', related='country_id.code', store=False)
        d = self.make_definition(start_domain="[('x_country_code', '=', 'VN')]", stop_domain=False,
                                 pause_domain=False, resume_domain=False, cancel_domain=False)
        p = self.make_partner(False)
        self.assertFalse(self.tasks(p, d))
        self.write(p, {'country_id': self.env.ref('base.vn').id}, T0 + hours(1))
        self.assertEqual(len(self.tasks(p, d)), 1)
