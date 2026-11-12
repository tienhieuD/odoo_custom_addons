# -*- coding: utf-8 -*-
"""TG-08 bổ sung: validate mốc escalation, bắn mốc, thử lại, quyền/công ty, tiến độ xử lý nền
(docs/060 TC-ESC-*). Số lần gọi server action đếm bằng wrapper trên `ir.actions.server.run`
theo (action, record id); lỗi giả lập bằng `fail_plan` (số lần gọi đầu bị lỗi).
Refs: REQ-FUNC-023..028, 053..059, REQ-INT-008, 019, REQ-SEC-004, REQ-REL-001, 002
"""
from collections import defaultdict
from datetime import datetime
from unittest.mock import patch

from psycopg2 import IntegrityError

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
SA_CODE = "record.write({'comment': (record.comment or '') + 'N'})"


def ict(hour, minute=0, second=0, day=2):
    """Datetime UTC của (ngày tháng 3 năm 2026, giờ ICT)."""
    return datetime(2026, 3, day, hour, minute, second) - hours(7)


class EscCase(SlaCase):

    def setUp(self):
        super().setUp()
        self.calls = defaultdict(int)       # (action_id, record_id) -> số lần gọi
        self.fail_plan = {}                 # action_id -> số lần gọi đầu bị lỗi (inf = luôn lỗi)
        self.run_times = []
        model_class = type(self.env['ir.actions.server'])
        original = model_class.run
        case = self

        def run(actions, *args, **kwargs):
            for action in actions:
                key = (action.id, actions.env.context.get('active_id'))
                case.calls[key] += 1
                if case.calls[key] <= case.fail_plan.get(action.id, 0):
                    raise UserError('SA-FAIL: boom')
            return original(actions, *args, **kwargs)

        patcher = patch.object(model_class, 'run', run)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.progress = []
        self.time_left = float('inf')

        def commit_progress(_cron, processed=0, remaining=None, *args, **kwargs):
            self.progress.append((processed, remaining))
            if isinstance(self.time_left, Exception):
                raise self.time_left
            return self.time_left

        patcher = patch.object(type(self.env['ir.cron']), '_commit_progress', commit_progress)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.d = self.make_definition()

    def action(self, code=SA_CODE, fail=0, name=None):
        action = self.make_server_action(code, name=name or "SA %s" % len(self.fail_plan))
        self.fail_plan[action.id] = fail
        return action

    def count(self, action, partner=None):
        if partner is not None:
            return self.calls[(action.id, partner.id)]
        return sum(n for (action_id, _rid), n in self.calls.items() if action_id == action.id)

    def process(self, now):
        with self.at(now):
            self.Processor.process_due()

    def esc_events(self, task, name):
        return self.events(task).count(name)

    def attach(self, ref='NEW', now=T0):
        p = self.make_partner(ref, now)
        return p, self.task_of(p, self.d)


@tagged(*TAGS, 'tg_08')
class TestEscalationValidation(EscCase):

    def create(self, action=None, **vals):
        action = action or self.action()
        base = {'definition_id': self.d.id, 'percent': 75, 'action_type': 'server_action',
                'action_id': action.id}
        base.update(vals)
        return self.Escalation.create(base)

    def rejected(self, exc, **vals):
        with self.assertRaises(exc) as ctx, mute_logger('odoo.sql_db'), self.env.cr.savepoint():
            self.create(**vals)
        self.assertFalse(self.d.escalation_ids)
        return ctx.exception

    def test_esc_002_003_percent_not_positive(self):
        """TC-ESC-002/003: percent 0 hoặc âm bị CSDL từ chối."""
        for percent in (0, -10):
            self.rejected(IntegrityError, percent=percent)

    def test_esc_004_percent_not_integer(self):
        """TC-ESC-004: percent 75.5 bị từ chối, thông báo 'is not an integer'."""
        self.assertIn('is not an integer', str(self.rejected(ValidationError, percent=75.5)))

    def test_esc_005_percent_one(self):
        """TC-ESC-005: percent = 1 hợp lệ."""
        esc = self.create(percent=1)
        self.assertEqual((esc.percent, len(self.d.escalation_ids)), (1, 1))

    def test_esc_044_045_action_model(self):
        """TC-ESC-044/045: server action khác model bị từ chối; cùng model lưu được."""
        user_action = self.env['ir.actions.server'].create({
            'name': "SA-USER", 'model_id': self.env['ir.model']._get('res.users').id,
            'state': 'code', 'code': 'pass'})
        error = self.rejected(ValidationError, action=user_action)
        self.assertIn('res.partner', str(error))
        self.assertIn('res.users', str(error))
        self.create()
        self.assertEqual(len(self.d.escalation_ids), 1)


@tagged(*TAGS, 'tg_08')
class TestEscalationFiring(EscCase):

    def setUp(self):
        super().setUp()
        self.n75 = self.action()
        self.esc75 = self.make_escalation(self.d, 75, action=self.n75)

    def test_esc_006_007_threshold(self):
        """TC-ESC-006/007: không bắn khi 2h59, bắn khi đúng 3h."""
        p, t = self.attach()
        self.assertEqual(t.next_due_at, ict(12))
        self.process(ict(11, 59))
        self.assertEqual((self.count(self.n75), self.esc_events(t, 'escalate'), t.next_due_at),
                         (0, 0, ict(12)))
        self.process(ict(12))
        self.assertEqual((self.count(self.n75), self.esc_events(t, 'escalate')), (1, 1))

    def test_esc_010_save_does_not_run_action(self):
        """TC-ESC-010: lưu record không chạy server action; chỉ xử lý nền mới chạy."""
        p, t = self.attach()
        self.write(p, {'ref': 'WORK'}, ict(12))
        self.assertEqual((p.ref, t.stage, self.count(self.n75), self.esc_events(t, 'escalate')),
                         ('WORK', 'in_progress', 0, 0))
        self.process(ict(12))
        self.assertEqual((self.count(self.n75), self.esc_events(t, 'escalate')), (1, 1))

    def test_esc_011_to_014_no_fire_when_not_running(self):
        """TC-ESC-011..014: paused/achieved/breached/cancelled không bắn mốc, next_due_at rỗng."""
        n100 = self.action()
        self.make_escalation(self.d, 100, action=n100)
        cases = (('HOLD', ict(10), 'paused', ict(19)), ('DONE', ict(10), 'achieved', ict(13)),
                 ('DONE', ict(14), 'breached', ict(14, 30)), ('CANCEL', ict(10), 'cancelled', ict(13)))
        for ref, when, stage, process_at in cases:
            p, t = self.attach()
            self.write(p, {'ref': ref}, when)
            self.assertEqual(t.stage, stage)
            self.process(process_at)
            self.assertEqual((self.count(self.n75, p), self.count(n100, p),
                              self.esc_events(t, 'escalate'), bool(t.next_due_at)),
                             (0, 0, 0, False), stage)

    def test_esc_015_resume_recomputes_due(self):
        """TC-ESC-015: attach 07:00, pause 08:00, resume 14:00 -> mốc 75% đến hạn 16:00."""
        p, t = self.attach(now=ict(7))
        self.write(p, {'ref': 'HOLD'}, ict(8))
        self.assertAlmostEqual(t.business_duration, 1.0, places=3)
        self.write(p, {'ref': 'WORK'}, ict(14))
        self.assertEqual((t.stage, t.next_due_at), ('in_progress', ict(16)))
        self.process(ict(15, 59))
        self.assertEqual(self.count(self.n75), 0)
        self.process(ict(16))
        self.assertEqual((self.count(self.n75), self.esc_events(t, 'escalate')), (1, 1))

    def test_esc_017_paused_not_recomputed(self):
        """TC-ESC-017: task vẫn paused -> không tính lại, không bắn mốc."""
        p, t = self.attach(now=ict(7))
        self.write(p, {'ref': 'HOLD'}, ict(8))
        self.assertFalse(t.next_due_at)
        self.process(ict(9, day=3))
        self.assertEqual((self.count(self.n75), self.esc_events(t, 'escalate'), bool(t.next_due_at),
                          self.esc75 in t.done_escalation_ids), (0, 0, False, False))

    def test_esc_024_failed_action_marks_done_no_retry(self):
        """TC-ESC-024: action lỗi -> escalate_failed, mốc coi là xong ngay, không thử lại (D12)."""
        self.fail_plan[self.n75.id] = float('inf')
        p, t = self.attach()
        with self.assertLogs('odoo.addons.dwo_sla_core', 'ERROR'):
            self.process(ict(12))
        self.assertEqual((self.count(self.n75), self.esc_events(t, 'escalate_failed'),
                          self.esc75 in t.done_escalation_ids), (1, 1, True))

    def test_esc_046_late_escalation_not_caught_up(self):
        """TC-ESC-046: thêm mốc 75% khi task đã ở 80% -> không bắn bù."""
        d2 = self.make_definition(name="Only100", start_domain="[('ref', '=', 'ZZ')]")
        self.esc75.unlink()
        n100 = self.action()
        self.make_escalation(self.d, 100, action=n100)
        p, t = self.attach()
        with self.at(ict(12, 12)):
            self.make_escalation(self.d, 75, action=self.n75)
        self.assertTrue(self.Escalation.search([('definition_id', '=', self.d.id), ('percent', '=', 75)])
                        <= t.done_escalation_ids)
        self.assertFalse(t.event_ids.filtered(lambda e: e.event == 'escalate'))
        self.process(ict(12, 12))
        self.assertEqual((self.count(self.n75), self.esc_events(t, 'escalate')), (0, 0))
        self.process(ict(13))
        self.assertEqual((self.count(n100), self.count(self.n75)), (1, 0))
        self.process(ict(14))
        self.assertEqual(self.count(self.n75), 0)
        self.assertTrue(d2)

    def test_esc_047_late_escalation_fires_at_threshold(self):
        """TC-ESC-047: thêm mốc 90% lúc 12:12 -> next_due_at = 12:36, bắn đúng lúc."""
        self.esc75.unlink()
        self.make_escalation(self.d, 100, action=self.action())
        p, t = self.attach()
        n90 = self.action()
        with self.at(ict(12, 12)):
            esc90 = self.make_escalation(self.d, 90, action=n90)
        self.assertNotIn(esc90, t.done_escalation_ids)
        self.assertEqual(t.next_due_at, ict(12, 36))
        self.process(ict(12, 35))
        self.assertEqual(self.count(n90), 0)
        self.process(ict(12, 36))
        self.assertEqual((self.count(n90), self.esc_events(t, 'escalate')), (1, 1))


@tagged(*TAGS, 'tg_08')
class TestEmailEscalation(EscCase):
    """D12 (TASKS.md): mốc kiểu email -- 3 cách resolve người nhận."""

    def test_esc_060_fixed_email(self):
        """Mốc 'fixed' gửi đúng tới địa chỉ cố định, mốc coi là xong."""
        esc = self.make_email_escalation(self.d, 75, recipient_type='fixed',
                                         email_fixed_address='oncall@example.com')
        p, t = self.attach()
        self.process(ict(12))
        mail = self.env['mail.mail'].sudo().search([('email_to', '=', 'oncall@example.com')])
        self.assertEqual(len(mail), 1)
        self.assertIn(self.d.name, mail.subject)
        self.assertIn(esc, t.done_escalation_ids)

    def test_esc_061_field_email(self):
        """Mốc 'field' đọc thẳng 1 field email (Char) trên record gốc."""
        self.make_email_escalation(self.d, 75, recipient_type='field',
                                   email_field_id=self.env['ir.model.fields']._get(
                                       'res.partner', 'email').id)
        p, t = self.attach()
        p.email = 'customer@example.com'
        self.process(ict(12))
        mail = self.env['mail.mail'].sudo().search([('email_to', '=', 'customer@example.com')])
        self.assertEqual(len(mail), 1)

    def test_esc_062_responsible_email(self):
        """Mốc 'responsible' đọc Many2one user/partner rồi lấy `.email` của record đó."""
        self.make_email_escalation(self.d, 75, recipient_type='responsible',
                                   email_field_id=self.env['ir.model.fields']._get(
                                       'res.partner', 'user_id').id)
        p, t = self.attach()
        p.user_id = self.env.ref('base.user_admin')
        self.process(ict(12))
        mail = self.env['mail.mail'].sudo().search(
            [('email_to', '=', self.env.ref('base.user_admin').email)])
        self.assertEqual(len(mail), 1)

    def test_esc_064_responsible_x2many_multiple_to(self):
        """'responsible' trên field One2many/Many2many -- 1 mail, nhiều 'To'.

        Refs: scope-add "responsible x2many" (user: 2026-11-07)
        """
        self.make_email_escalation(self.d, 75, recipient_type='responsible',
                                   email_field_id=self.env['ir.model.fields']._get(
                                       'res.partner', 'child_ids').id)
        p, t = self.attach()
        c1 = self.env['res.partner'].create({'name': 'Contact A', 'email': 'a@example.com'})
        c2 = self.env['res.partner'].create({'name': 'Contact B', 'email': 'b@example.com'})
        p.child_ids = [(6, 0, (c1 + c2).ids)]
        self.process(ict(12))
        mail = self.env['mail.mail'].sudo().search(
            [('email_to', '=', 'a@example.com,b@example.com')])
        self.assertEqual(len(mail), 1)

    def test_esc_063_no_recipient_marks_failed(self):
        """Không resolve được người nhận (field rỗng) -> escalate_failed, không raise ra ngoài."""
        self.make_email_escalation(self.d, 75, recipient_type='field',
                                   email_field_id=self.env['ir.model.fields']._get(
                                       'res.partner', 'email').id)
        p, t = self.attach()
        with self.assertLogs('odoo.addons.dwo_sla_core', 'ERROR'):
            self.process(ict(12))
        self.assertEqual(self.esc_events(t, 'escalate_failed'), 1)

    def test_esc_065_no_template_falls_back_to_plain_body(self):
        """Xóa `email_template_id` -> dùng nội dung mặc định đơn giản (NOTE_ESCALATION_EMAIL_BODY)."""
        esc = self.make_email_escalation(self.d, 75, recipient_type='fixed',
                                         email_fixed_address='oncall@example.com',
                                         email_template_id=False)
        self.assertFalse(esc.email_template_id)
        p, t = self.attach()
        self.process(ict(12))
        mail = self.env['mail.mail'].sudo().search([('email_to', '=', 'oncall@example.com')])
        self.assertEqual(len(mail), 1)
        self.assertIn(self.d.name, mail.subject)
        self.assertIn('%', mail.body_html)

    def test_esc_066_template_wrong_model_rejected(self):
        """`email_template_id` không phải model sla.task bị từ chối khi lưu."""
        other_template = self.env['mail.template'].create({
            'name': 'Wrong Model Template',
            'model_id': self.env['ir.model']._get('res.partner').id,
            'subject': 'x',
        })
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.make_email_escalation(self.d, 75, recipient_type='fixed',
                                       email_fixed_address='oncall@example.com',
                                       email_template_id=other_template.id)


@tagged(*TAGS, 'tg_08')
class TestEscalationCompanyAndProgress(EscCase):

    def setUp(self):
        super().setUp()
        self.co_a = self.env.company
        self.co_b = self.env['res.company'].create({'name': "CO-B"})
        self.set_company = self.action("record.write({'comment': 'CO=%s' % env.company.id})")

    def cron_user(self, name, companies):
        user = self.make_user(name, 'user', company_id=companies[0].id,
                              company_ids=[(6, 0, [c.id for c in companies])])
        user.groups_id += self.env.ref('base.group_partner_manager')
        return user

    def company_case(self):
        self.make_escalation(self.d, 75, action=self.set_company)
        p = self.make_partner('NEW', company_id=self.co_b.id)
        return p, self.task_of(p, self.d)

    def test_esc_050_runs_in_record_company(self):
        """TC-ESC-050: action chạy với env.company = công ty của record (CO-B)."""
        p, t = self.company_case()
        user = self.cron_user('sla_cron_ab', [self.co_a, self.co_b])
        with self.at(ict(12)):
            self.Processor.with_user(user).process_due()
        self.assertIn('CO=%s' % self.co_b.id, p.comment)
        self.assertEqual((self.esc_events(t, 'escalate'), self.esc_events(t, 'escalate_failed')), (1, 0))

    def test_esc_051_no_company_access_fails_once(self):
        """TC-ESC-051: user cron không có công ty của record -> đúng 1 escalate_failed (lỗi quyền)."""
        p, t = self.company_case()
        user = self.cron_user('sla_cron_a', [self.co_a])
        with self.assertLogs('odoo.addons.dwo_sla_core', 'ERROR'), self.at(ict(12)):
            self.Processor.with_user(user).process_due()
        failed = t.event_ids.filtered(lambda e: e.event == 'escalate_failed')
        self.assertEqual((len(failed), self.esc_events(t, 'escalate')), (1, 0))
        self.assertIn('access', failed.note.lower())
        self.assertFalse(p.comment)
        for when in (ict(12, 1), ict(13)):
            with self.at(when):
                self.Processor.with_user(user).process_due()
        self.assertEqual((self.esc_events(t, 'escalate_failed'), bool(p.comment)), (1, False))

    def due_tasks(self, count):
        self.make_escalation(self.d, 75, action=self.action())
        partners = self.Partner
        for _ in range(count):
            partners |= self.make_partner('NEW')
        return partners

    def test_esc_053_progress_reported_per_task(self):
        """TC-ESC-053: 120 task đến hạn, lô 50 -> 3 lần gọi báo 50, 50, 20 lần; remaining giảm 1."""
        partners = self.due_tasks(120)
        for _call in range(3):
            self.process(ict(12))
        self.assertEqual(len(self.progress), 120)
        self.assertTrue(all(processed == 1 for processed, _r in self.progress))
        self.assertEqual([r for _p, r in self.progress], list(range(119, -1, -1)))
        tasks = self.Task.sudo().search([('sla_id', '=', self.d.id)])
        self.assertTrue(all(self.esc_events(t, 'escalate') == 1 for t in tasks))
        self.assertTrue(all(n == 1 for n in self.calls.values()))
        self.assertEqual(len(partners), 120)

    def test_esc_054_resume_after_interruption(self):
        """TC-ESC-054: bị dừng sau task đầu, chạy lại: mỗi task đúng 1 lần."""
        self.due_tasks(3)
        self.time_left = InterruptedError()
        try:  # không dùng assertRaises: nó rollback savepoint, còn ở đây kết quả task đầu đã lưu
            self.process(ict(12))
        except InterruptedError:
            pass
        else:
            self.fail("process_due phải bị ngắt")
        self.assertEqual(self.progress, [(1, 2)])
        self.env.flush_all()
        self.env.invalidate_all()
        done_first = self.Task.sudo().search([('sla_id', '=', self.d.id)]).filtered(
            lambda t: self.esc_events(t, 'escalate'))
        self.assertEqual(len(done_first), 1)
        self.time_left = float('inf')
        self.process(ict(12))
        self.assertEqual(self.progress[1:], [(1, 1), (1, 0)])
        for task in self.Task.sudo().search([('sla_id', '=', self.d.id)]):
            self.assertEqual(self.esc_events(task, 'escalate'), 1)
        self.assertTrue(all(n == 1 for n in self.calls.values()))

    def test_esc_055_no_time_left(self):
        """TC-ESC-055: thời gian còn lại 0 sau task đầu -> chỉ xử lý 1 task, remaining 99."""
        self.due_tasks(100)
        self.time_left = 0
        self.process(ict(12))
        self.assertEqual(self.progress, [(1, 99)])
        tasks = self.Task.sudo().search([('sla_id', '=', self.d.id)])
        self.assertEqual(len(tasks.filtered(lambda t: self.esc_events(t, 'escalate'))), 1)

    def settings(self, value):
        return self.env['res.config.settings'].create({'sla_batch_size': value}).execute()

    def test_esc_056_058_batch_size_setting(self):
        """TC-ESC-056/057/058: batch_size 0/âm bị từ chối (giữ 50); 1 được chấp nhận."""
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('dwo_sla_core.batch_size', '50')
        for bad in (0, -5):
            with self.assertRaisesRegex(ValidationError, '(?i)batch size'), self.env.cr.savepoint():
                self.settings(bad)
            self.assertEqual(param.get_param('dwo_sla_core.batch_size'), '50')
        self.settings(1)
        self.assertEqual(param.get_param('dwo_sla_core.batch_size'), '1')
