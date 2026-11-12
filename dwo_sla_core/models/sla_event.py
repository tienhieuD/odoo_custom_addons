# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.tools import html2plaintext

from ..constants.message import MessageCode, get_message

_logger = logging.getLogger(__name__)


class SlaEvent(models.Model):
    """Nhật ký sự kiện SLA: giải thích vì sao SLA ra kết quả như vậy.

    Logic: một dòng cho mỗi thay đổi trạng thái của task và mỗi hành động
    escalation (REQ-FUNC-029); cũng là nơi ghi lỗi của engine (event `error`,
    REQ-FUNC-030). Không chứa giá trị field của record gốc, chỉ định danh
    (REQ-OBS-003). Chỉ hệ thống ghi; ngoại lệ duy nhất người dùng được đổi là
    trạng thái xử lý (`is_resolved`) của event `error` (REQ-SEC-006).
    Refs: REQ-FUNC-029, 030, 040, DB Design §3 bảng sla_event
    """
    _name = 'sla.event'
    _description = "SLA Event Log"
    _order = 'event_dt desc, id desc'

    task_id = fields.Many2one(
        'sla.task', string="Task", ondelete='cascade',
        help=('SLA task the event belongs to. Empty for error events that '
             'could not be linked to a task. Example: the task of a ticket '
             'that was paused.'))
    event = fields.Selection(
        [
            ('attach', "Attach"),
            ('pause', "Pause"),
            ('resume', "Resume"),
            ('complete', "Complete"),
            ('reset', "Reset"),
            ('cancel', "Cancel"),
            ('breach', "Breach"),
            ('escalate', "Escalate"),
            ('escalate_failed', "Escalate Failed"),
            ('error', "Error"),
            ('recalculate', "Settings Applied"),
            ('reevaluate', "Conditions Re-checked"),
        ],
        string="Event Type", required=True,
        help=('Type of event: Attach (SLA started), Pause, Resume, Complete, '
              'Reset, Cancel, Breach (deadline passed), Escalate, Escalate '
              'Failed, Error, Settings Applied (a manager pushed the current '
              'settings onto the task), Conditions Re-checked (a manager '
              'ran the conditions again). Example: filter on Error to find '
              'problems.'))
    event_dt = fields.Datetime(string="Timestamp", required=True, index=True,
        help='When the event happened (UTC). Example: 2026-03-02 05:00:00.')
    note = fields.Text(
        string="Note",
        help=('Extra detail about the event, such as why a fallback calendar '
             'was used, which fields triggered a reset or the error message. '
             "It never contains values of the record's fields. Example: "
             '"Calendar path unusable, company calendar used".'))
    res_model = fields.Char(
        string="Related Record Model",
        help=('Technical name of the model of the related record, used for '
             'error events that have no task. Example: res.partner.'))
    res_id = fields.Many2oneReference(
        string="Related Record Id", model_field='res_model',
        help=('Id of the related record, used together with the model for '
              'error events that have no task. Example: 42.'))
    definition_id = fields.Many2one(
        'sla.definition', string="Definition", ondelete='set null', index=True,
        help=('SLA definition involved in the event, if any. Example: "Ticket '
              'Response - Priority 1".'))
    company_id = fields.Many2one(
        'res.company', string="Company", ondelete='restrict', index=True,
        help=('Company of the task or record concerned; used for company '
              'access rules. Example: "Sojitz Vietnam".'))
    # Refs: REQ-FUNC-040
    is_resolved = fields.Boolean(
        string="Resolved", default=False,
        help=('Only meaningful for error events. An SLA Manager ticks it once '
             'the problem has been looked at, so unresolved errors stay easy '
             'to find. Example: tick after fixing a broken condition and '
             're-evaluating.'))

    _event_check = models.Constraint(
        "CHECK(event IN ('attach','pause','resume','complete','reset','cancel',"
        "'breach','escalate','escalate_failed','error','recalculate','reevaluate'))",
        "Invalid event type.")
    _task_dt_idx = models.Index("(task_id, event_dt)")
    _error_unresolved_idx = models.Index(
        "(company_id) WHERE event = 'error' AND is_resolved IS NOT TRUE")

    def action_mark_resolved(self):
        """Đánh dấu các event error đã chọn là đã xử lý.

        Logic: ngoại lệ duy nhất người dùng (SLA Manager) được phép ghi trực
        tiếp lên sla.event; dùng sudo vì model chỉ cho hệ thống ghi
        (REQ-SEC-006, AD-13 sudo hẹp ở điểm ghi). Chỉ áp dụng cho event
        `error`, bỏ qua loại khác.
        Refs: REQ-FUNC-040 AC2, REQ-SEC-006
        """
        if not self.env.user.has_group('dwo_sla_core.group_sla_manager'):
            raise AccessError(get_message(
                MessageCode.ACC_MARK_RESOLVED_SLA_MANAGER_ONLY))
        self.filtered(lambda e: e.event == 'error').sudo().write(
            {'is_resolved': True})

    def action_reevaluate_batch(self):
        """"Đánh giá lại" hàng loạt từ danh sách event lỗi đã chọn (REQ-FUNC-031).

        Logic: chỉ SLA Manager được gọi (AC4); chỉ xét event `error`, event
        loại khác bị bỏ qua (AC3); đánh giá lại record liên quan bằng thời
        điểm hiện tại, không kích hoạt reset theo field (REQ-FUNC-032, dùng
        `changed=set()`); task đã kết thúc (`achieved/breached/cancelled`)
        không bị ảnh hưởng vì `evaluate()` tự tôn trọng bất biến đó
        (REQ-FUNC-007, AC2). Một event được đánh dấu "đã xử lý" khi lần đánh
        giá lại này KHÔNG sinh thêm event `error` mới cho đúng record đó
        (REQ-FUNC-040 AC3); nếu vẫn còn lỗi thì event cũ giữ nguyên "chưa xử
        lý" và event lỗi mới (do `evaluate()` tự ghi) tồn tại song song
        (AC4).
        Refs: REQ-FUNC-031, REQ-FUNC-032, REQ-FUNC-040
        """
        if not self.env.user.has_group('dwo_sla_core.group_sla_manager'):
            raise AccessError(get_message(
                MessageCode.ACC_REEVALUATE_EVENTS_SLA_MANAGER_ONLY))
        now = fields.Datetime.now()
        SlaEvent = self.env['sla.event'].sudo()
        last_event = SlaEvent.search([], order='id desc', limit=1)
        last_id_before = last_event.id if last_event else 0
        for event in self.sudo().filtered(lambda e: e.event == 'error'):
            if not event.res_model or not event.res_id:
                continue
            record = self.env[event.res_model].sudo().browse(event.res_id).exists()
            if not record:
                continue
            self.env['sla.engine'].evaluate(record, now=now, changed=set())
            new_errors = SlaEvent.search_count([
                ('id', '>', last_id_before), ('event', '=', 'error'),
                ('res_model', '=', event.res_model), ('res_id', '=', event.res_id),
            ])
            if not new_errors:
                event.write({'is_resolved': True})

    @api.autovacuum
    def _gc_old_events(self):
        """Dọn event cũ hơn số ngày cấu hình (REQ-FUNC-035, gọi hằng ngày).

        Logic: ngưỡng lấy từ `ir.config_parameter`
        `dwo_sla_core.event_retention_days` (REQ-INT-010), mặc định 365;
        so sánh biên đúng bằng ngày (event đúng N ngày tuổi KHÔNG bị xóa,
        chỉ xóa khi cũ HƠN N ngày, AC2 boundary).
        Refs: REQ-FUNC-035
        """
        retention_days = int(
            self.env['ir.config_parameter'].sudo().get_str(
                'dwo_sla_core.event_retention_days', 365))
        threshold = fields.Datetime.now() - timedelta(days=retention_days)
        self.sudo().search([('event_dt', '<', threshold)]).unlink()

    @api.model
    def _scrub_values(self, res_model, res_id, text):
        """Thay giá trị field chuỗi của record gốc xuất hiện trong `text` bằng `<redacted>`.

        Logic: thông báo lỗi gốc (ví dụ "invalid literal 'SECRET-123'") có thể trích
        nguyên giá trị field; đọc các field `char`/`text`/`html` đã lưu của record, thay
        mọi giá trị từ 3 ký tự trở lên (field `html` cả bản gốc và bản văn bản thuần) (giá trị dài thay trước) rồi mới ghi note
        hoặc log. Chỉ chạy ở đường lỗi nên không ảnh hưởng hiệu năng bình thường.
        Refs: REQ-OBS-003
        """
        text = str(text or '')
        if not text or not res_id or res_model not in self.env:
            return text
        record = self.env[res_model].sudo().browse(res_id).exists()
        values = set()
        for name, field in record._fields.items():
            value = record[name] if field.store and field.type in ('char', 'text', 'html') else None
            if isinstance(value, str):
                values.add(str(value))
                if field.type == 'html':
                    values.add(html2plaintext(value).strip())
        values = {value for value in values if len(value) >= 3}
        for value in sorted(values, key=len, reverse=True):
            text = text.replace(value, '<redacted>')
        return text

    @api.model
    def _log_error(self, *, definition=None, res_model, res_id, message, task=None):
        """Ghi event `error` kèm ngữ cảnh đủ để điều tra, và log mức ERROR.

        Logic: event error PHẢI có model, id record, tên định nghĩa (nếu có)
        và thông báo lỗi không rỗng; log log server ERROR cùng ngữ cảnh,
        không ghi giá trị field của record (REQ-OBS-001, 002, 003).
        Refs: REQ-FUNC-030, REQ-OBS-001, REQ-OBS-002, REQ-OBS-003
        """
        message = self._scrub_values(res_model, res_id, message)
        company = False
        if task is not None:
            company = task.company_id.id
        elif res_id and res_model in self.env:
            # Không có task: lấy công ty từ record gốc để quy tắc đa công ty áp
            # dụng cho event lỗi (REQ-SEC-003).
            record = self.env[res_model].sudo().browse(res_id).exists()
            if 'company_id' in record._fields:
                company = record.company_id.id  # type: ignore
        self.sudo().create({
            'task_id': task.id if task else False,
            'event': 'error',
            'event_dt': fields.Datetime.now(),
            'note': message,
            'res_model': res_model,
            'res_id': res_id,
            'definition_id': definition.id if definition else False,
            'company_id': company,
        })
        _logger.error(
            "SLA engine error: model=%s id=%s definition=%s message=%s",
            res_model, res_id, definition.name if definition else None, message)
