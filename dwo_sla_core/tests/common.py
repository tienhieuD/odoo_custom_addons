# -*- coding: utf-8 -*-
"""Fixture và helper dùng chung cho test `dwo_sla_core`.

Quy ước (Refs: docs/060_Test-Case-Specification.md "Ký hiệu chung"):
- `T0` = 2026-03-02 09:00 giờ Asia/Ho_Chi_Minh (thứ Hai) = 02:00 UTC; mọi
  datetime trong test là naive, biểu diễn UTC (CLAUDE.md "Datetime luôn UTC").
- Model thử là `res.partner`, trường `ref` làm "dấu trạng thái" (FX-PARTNER-MARK).
- FX-DEF-STD: start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK;
  stop ref=DONE; cancel ref=CANCEL; mục tiêu 4 giờ; lịch 24x7;
  cancel_mode=start_unmatched; resume_mode=condition; không escalation.
- Điều khiển thời gian bằng `at(now)` (patch `fields.Datetime.now`) hoặc truyền
  `now` thẳng vào `evaluate` / `_process_task`; không dùng sleep.
"""
from datetime import datetime, timedelta
from unittest.mock import patch

from odoo import fields
from odoo.tests.common import TransactionCase, new_test_user

T0 = datetime(2026, 3, 2, 2, 0)  # 09:00 ICT, thứ Hai


def hours(n):
    """Khoảng `n` giờ."""
    return timedelta(hours=n)


STD_DOMAINS = {
    'start_domain': "[('ref', 'in', ['NEW', 'WORK', 'HOLD'])]",
    'pause_domain': "[('ref', '=', 'HOLD')]",
    'resume_domain': "[('ref', '=', 'WORK')]",
    'stop_domain': "[('ref', '=', 'DONE')]",
    'cancel_domain': "[('ref', '=', 'CANCEL')]",
}


class SlaCase(TransactionCase):
    """Lớp cơ sở: tạo định nghĩa/partner, điều khiển thời gian, đọc event."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Definition = cls.env['sla.definition']
        cls.Escalation = cls.env['sla.escalation']
        cls.Task = cls.env['sla.task']
        cls.Event = cls.env['sla.event']
        cls.Engine = cls.env['sla.engine']
        cls.Processor = cls.env['sla.processor']
        cls.Partner = cls.env['res.partner']
        cls.partner_model = cls.env['ir.model']._get('res.partner')
        # Patch của hook nằm ở cấp class Python nên không bị rollback của
        # TransactionCase; phải gỡ khi xong lớp test để không rò sang test khác.
        cls.addClassCleanup(cls._remove_hook_patches, cls.registry)

    @staticmethod
    def _remove_hook_patches(registry):
        for model_class in registry.values():
            for name in ('create', 'write', '_compute_field_value'):
                try:
                    delattr(model_class, name)
                except AttributeError:
                    pass
        registry.registry_invalidated = False

    # ------------------------------------------------------------------
    # Thời gian
    # ------------------------------------------------------------------

    @staticmethod
    def at(now):
        """Context manager: `fields.Datetime.now()` trả `now` (hook dùng đồng hồ này)."""
        return patch.object(fields.Datetime, 'now', return_value=now)

    # ------------------------------------------------------------------
    # Dựng dữ liệu
    # ------------------------------------------------------------------

    def make_definition(self, **overrides):
        """Tạo FX-DEF-STD trên res.partner; `overrides` ghi đè từng field."""
        vals = {
            'active': True,
            'name': "SLA test",
            'model_id': self.partner_model.id,
            'duration': 4,
            'schedule_source': 'none',
            'cancel_mode': 'start_unmatched',
            'resume_mode': 'condition',
            **STD_DOMAINS,
        }
        vals.update(overrides)
        if vals['schedule_source'] == 'record':
            # Timezone SLA luôn thắng: lịch fixture (FX-CAL-VN) dùng tz ICT, nên đặt
            # trùng tz đó để không sinh bản sao calendar (trừ khi test chủ ý đổi).
            vals.setdefault('calendar_tz_override', 'Asia/Ho_Chi_Minh')
        return self.Definition.create(vals)

    def make_partner(self, ref=False, now=T0, **vals):
        """Tạo partner tại thời điểm `now` (hook, nếu đã bật, chạy với `now`)."""
        with self.at(now):
            return self.Partner.create({'name': "SLA P", 'ref': ref, **vals})

    def write(self, partner, vals, now):
        """Ghi `vals` lên partner tại thời điểm `now` (qua hook thật)."""
        with self.at(now):
            partner.write(vals)

    def evaluate(self, records, now, changed=None):
        """Gọi Engine trực tiếp với `now` (và `changed`) tường minh."""
        self.Engine.evaluate(records, now=now, changed=changed)

    def tasks(self, partner=None, definition=None, stage=None):
        domain = []
        if partner is not None:
            domain += [('res_model', '=', partner._name), ('res_id', '=', partner.id)]
        if definition is not None:
            domain.append(('sla_id', '=', definition.id))
        if stage:
            domain.append(('stage', '=', stage))
        return self.Task.sudo().search(domain, order='id')

    def task_of(self, partner, definition=None):
        """Task duy nhất của partner (assert đúng 1)."""
        tasks = self.tasks(partner, definition)
        self.assertEqual(len(tasks), 1, "Kỳ vọng đúng 1 task, có %s" % len(tasks))
        return tasks

    @staticmethod
    def events(task):
        """Danh sách tên event của task, theo id tăng dần."""
        return task.event_ids.sorted('id').mapped('event')

    def no_commit_progress(self):
        """Thay `ir.cron._commit_progress` (gọi cr.commit(), bị cấm trong test) bằng "không giới hạn thời gian"."""
        patcher = patch.object(
            type(self.env['ir.cron']), '_commit_progress', return_value=float('inf'))
        mocked = patcher.start()
        self.addCleanup(patcher.stop)
        return mocked

    def make_x_field(self, name, ttype, model='res.partner', **vals):
        """Tạo field manual `name` (`x_`) trên `model`, rồi đăng ký lại hook.

        Tạo field manual dựng lại class model của registry nên patch của hook mất; phải
        `_register_sla_hook()` lại (AD-01). Field và registry được Odoo khôi phục sau test.

        `clear_caches()`: `mail.thread._track_get_fields()` (dùng cho
        scope-add "retroactive_pause") có `@ormcache('self.env.uid',
        'self.env.su')` -- kết quả đã tính TRƯỚC khi field manual này tồn tại
        (ví dụ lúc cài module `mail`) vẫn còn trong cache và không tự biết
        field mới, nên field vừa tạo với `tracking=...` sẽ KHÔNG được
        `mail.thread` theo dõi (không sinh `mail.tracking.value`) nếu không
        xóa cache sau khi tạo field.
        """
        field = self.env['ir.model.fields'].create({
            'name': name, 'model_id': self.env['ir.model']._get(model).id, 'ttype': ttype,
            'state': 'manual', 'field_description': name, **vals})
        self.env['sla.definition']._register_sla_hook()
        self.env.registry.clear_all_caches()
        return field

    def make_user(self, login, sla_group=None, **vals):
        """Người dùng nội bộ; `sla_group` = 'user' | 'manager' | None (FX-USERS)."""
        groups = 'base.group_user'
        if sla_group:
            groups += ',dwo_sla_core.group_sla_%s' % sla_group
        return new_test_user(self.env, login=login, groups=groups, **vals)

    def make_server_action(self, code, name="SLA test action"):
        """Server action `code` trên res.partner."""
        return self.env['ir.actions.server'].create({
            'name': name,
            'model_id': self.partner_model.id,
            'state': 'code',
            'code': code,
        })

    def make_escalation(self, definition, percent, action=None, **vals):
        """Mốc escalation kiểu `server_action` (mặc định field là 'email', xem sla_escalation.py)."""
        action = action or self.make_server_action("record.write({'function': 'esc'})")
        vals.setdefault('action_type', 'server_action')
        return self.Escalation.create({
            'definition_id': definition.id,
            'percent': percent,
            'action_id': action.id,
            **vals,
        })

    def make_email_escalation(self, definition, percent, recipient_type='fixed', **vals):
        """Mốc escalation kiểu `email`; mặc định gửi tới địa chỉ cố định."""
        vals.setdefault('email_fixed_address', 'sla-alert@example.com')
        return self.Escalation.create({
            'definition_id': definition.id,
            'percent': percent,
            'action_type': 'email',
            'email_recipient_type': recipient_type,
            **vals,
        })

    def make_calendar(self, tz='Asia/Ho_Chi_Minh', days=range(5), hour_from=8, hour_to=17):
        """FX-CAL-VN: lịch fully_fixed, mặc định T2–T6 08:00–17:00, không nghỉ trưa."""
        return self.env['resource.calendar'].create({
            'name': "SLA test calendar",
            'tz': tz,
            'schedule_type': 'fully_fixed',
            'attendance_ids': [(5, 0, 0)] + [(0, 0, {
                'name': "Day %s" % d,
                'dayofweek': str(d),
                'hour_from': hour_from,
                'hour_to': hour_to,
                'day_period': 'morning',
            }) for d in days],
        })
