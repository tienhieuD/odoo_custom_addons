# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

from ..constants.message import MessageCode, get_message

_logger = logging.getLogger(__name__)


class SlaProcessor(models.AbstractModel):
    """Xử lý nền: bắt vi phạm và chạy escalation đến hạn.

    Logic: cron gọi `process_due` mỗi phút; hàm khóa và xử lý từng task một
    (`try_lock_for_update(limit=1)`), lưu và báo tiến độ cho `ir.cron` ngay
    sau mỗi task (`_commit_progress`) để nhường tài nguyên (REQ-REL-002,
    AD-12). Mỗi task được cô lập trong savepoint riêng: lỗi của một task
    (kể cả lỗi server action) không ảnh hưởng task khác (AD-07). Chỉ xử lý
    breach và escalation — KHÔNG xử lý attach/pause/resume/reset/cancel
    (thuộc Engine, REQ-FUNC-025).
    Refs: REQ-FUNC-022 đến 027, 054 đến 059, REQ-INT-008, 019, REQ-REL-001,
      002, TAD §5.3, §6.3, AD-12
    """
    _name = 'sla.processor'
    _description = "SLA Background Processor"

    def process_due(self):
        """Xử lý các task đến hạn (breach/escalation) cho một lần cron gọi.

        Logic: lặp chọn-khóa-xử lý-báo tiến độ từng task một; dừng khi hết
        task đến hạn, chạm kích thước lô tối đa, hoặc thời gian còn lại của
        lần chạy (do `_commit_progress` trả về) bằng 0. Task bị khóa bởi
        giao dịch khác bị bỏ qua (SKIP LOCKED), xử lý ở lần gọi sau
        (REQ-REL-001, 002).
        Refs: REQ-REL-002, AD-12
        """
        self.env['sla.definition'].sudo()._ensure_hook_registered()
        SlaTask = self.env['sla.task'].sudo()
        IrCron = self.env['ir.cron']
        batch_size = int(
            self.env['ir.config_parameter'].sudo().get_param(
                'dwo_sla_core.batch_size', default=50))
        processed = 0
        drained = False
        while processed < batch_size:
            now = fields.Datetime.now()
            candidates = SlaTask.search([
                ('stage', '=', 'in_progress'),
                ('next_due_at', '<=', now),
            ], order='next_due_at', limit=max(batch_size - processed, 1) * 2)
            if not candidates:
                drained = True
                break
            locked = candidates.try_lock_for_update(limit=1)
            if not locked:
                # Mọi candidate đang bị khóa bởi giao dịch khác; dừng, xử lý
                # lần sau (REQ-REL-001 AC1).
                break
            try:
                with self.env.cr.savepoint():
                    self._process_task(locked, now)
            except Exception as exc:  # noqa: BLE001 -- cô lập lỗi theo task (AD-07)
                self.env['sla.event']._log_error(
                    definition=locked.sla_id, res_model=locked.res_model,
                    res_id=locked.res_id, task=locked,
                    message=get_message(
                        MessageCode.NOTE_BACKGROUND_PROCESSING_ERROR, exc))
            processed += 1
            remaining = SlaTask.search_count([
                ('stage', '=', 'in_progress'),
                ('next_due_at', '<=', fields.Datetime.now()),
            ])
            time_left = IrCron._commit_progress(1, remaining=remaining)
            drained = remaining == 0
            if drained or time_left <= 0:
                break

    def _process_task(self, task, now):
        """Xử lý một task: breach rồi từng mốc escalation đến hạn.

        Logic: breach được ghi trước mọi mốc >= 100% (REQ-FUNC-022 AC3); sau
        mỗi mốc xử lý, tính lại `next_due_at` vì trạng thái mốc vừa đổi.
        Refs: REQ-FUNC-022, 023, 024
        """
        self.env['sla.engine']._check_breach(task, now)
        while task.stage == 'in_progress':
            escalation = self._next_due_escalation(task, now)
            if not escalation:
                break
            self._run_escalation(task, escalation, now)
        task.next_due_at = self.env['sla.time'].next_due_at(task, now)

    def _current_percent(self, task, now):
        """% thời lượng mục tiêu đã dùng tính tới `now` (bao gồm đoạn đang chạy).

        Logic: `business_elapsed` lưu trên task chỉ chốt tại lần settle gần
        nhất (pause/resume/complete); phải cộng thêm đoạn đang chạy từ
        `running_since` tới `now` mới có số liệu tức thời (REQ-FUNC-043).
        Refs: REQ-FUNC-043, 023
        """
        elapsed = task.business_duration + self.env['sla.time'].settle(
            task.schedule_id, task.running_since, now)
        if task.target_duration <= 0:
            return 100.0
        return (elapsed / task.target_duration) * 100.0

    def _next_due_escalation(self, task, now):
        """Tìm mốc escalation đến hạn tiếp theo (chưa xử lý xong, đã tới phần trăm).

        Logic: mốc đến hạn khi phần trăm hiện tại >= phần trăm của mốc. Mốc
        đã có trong `done_escalation_ids` không bao giờ được xét lại
        (REQ-FUNC-024).
        Refs: REQ-FUNC-023, 024
        """
        done_ids = set(task.done_escalation_ids.ids)
        percent = None
        for escalation in task.sla_id.escalation_ids.sorted('sequence'):
            if escalation.id in done_ids:
                continue
            if percent is None:
                percent = self._current_percent(task, now)
            if percent >= escalation.percent:
                return escalation
        return None

    def _run_escalation(self, task, escalation, now):
        """Chạy action (email hoặc server action) của một mốc, xử lý lỗi.

        Logic: chạy trong savepoint riêng (lỗi của action không làm hỏng
        trạng thái mốc/task khác đã xử lý trước đó trong cùng task,
        REQ-FUNC-026 AC1). 'server_action' giữ nguyên hành vi cũ: ngữ cảnh
        có `active_model/active_id` (REQ-INT-008), chạy đúng công ty của
        record (REQ-INT-019). 'email' resolve người nhận rồi gửi qua
        `mail.mail`. Lỗi chỉ được ghi lại, KHÔNG thử lại (D12, TASKS.md):
        mốc luôn được đánh dấu xử lý xong dù thành công hay lỗi, để không
        bắn lại vô hạn cho một lỗi không tự sửa được.
        Refs: REQ-FUNC-023, 024, 026, INT-008, 019, D12
        """
        error_message = None
        try:
            with self.env.cr.savepoint():
                if escalation.action_type == 'server_action':
                    # Chạy theo quyền của user xử lý nền, không sudo
                    # (REQ-SEC-004): `escalation` đọc qua env sudo nên dựng
                    # lại action từ env gốc.
                    action = self.env['ir.actions.server'].browse(escalation.action_id.id)
                    if task.company_id:
                        action = action.with_company(task.company_id)
                    action = action.with_context(
                        active_model=task.res_model,
                        active_id=task.res_id,
                        active_ids=[task.res_id],
                    )
                    action.run()
                else:
                    self._send_escalation_email(task, escalation)
        except Exception as exc:  # noqa: BLE001 -- lỗi action bị cô lập (REQ-FUNC-026)
            error_message = self.env['sla.event']._scrub_values(
                task.res_model, task.res_id, str(exc))
            _logger.error(
                "SLA escalation error: task=%s escalation=%s message=%s",
                task.id, escalation.id, error_message)

        task.write({'done_escalation_ids': [(4, escalation.id)]})
        self._log_event(
            task, 'escalate' if error_message is None else 'escalate_failed',
            now, note=error_message)

    def _send_escalation_email(self, task, escalation):
        """Resolve người nhận của mốc rồi gửi 1 mail, có template hoặc không.

        Logic: dùng `mail.mail`/`mail.template` thay vì `message_post`/
        `message_notify` vì record gốc không bắt buộc kế thừa `mail.thread`
        (module vẫn generic cho mọi model, REQ-INST-003); raise lỗi bình
        thường khi không resolve được người nhận để `_run_escalation` ghi
        event lỗi, không gửi mail trống người nhận. Có `email_template_id`
        (mặc định trỏ `mail_template_escalation_default`, scope-add "email
        template"): render template trên TASK (không phải record gốc -- mọi
        placeholder của template là field của `sla.task`, dùng được với mọi
        model của định nghĩa), rồi ép `email_to` bằng người nhận đã resolve
        qua `email_values` (override bất kể template tự set gì, GHI ĐÈ sau
        khi render -- xem `mail.template.send_mail_batch`). Không có template
        (người dùng xóa): giữ nguyên nội dung mặc định đơn giản như trước.
        Refs: D12 (TASKS.md)
        """
        record = self.env[task.res_model].sudo().browse(task.res_id).exists()
        email_to = escalation._resolve_email_recipient(record)
        if not email_to:
            raise ValueError(get_message(
                MessageCode.VAL_ESCALATION_EMAIL_FIELD_REQUIRED, "Notify"))
        if escalation.email_template_id:
            escalation.email_template_id.sudo().send_mail(
                task.id, force_send=True, raise_exception=True,
                email_values={'email_to': email_to})
            return
        self.env['mail.mail'].sudo().create({
            'subject': "[%s] %s" % (escalation.definition_id.name, record.display_name),
            'body_html': get_message(
                MessageCode.NOTE_ESCALATION_EMAIL_BODY,
                escalation.definition_id.name, escalation.percent,
                record.display_name),
            'email_to': email_to,
        }).send()

    def _log_event(self, task, event, event_dt, note=False):
        """Ghi một dòng `sla.event` cho task (REQ-FUNC-029)."""
        self.env['sla.event'].sudo().create({
            'task_id': task.id,
            'event': event,
            'event_dt': event_dt,
            'note': note,
            'definition_id': task.sla_id.id,
            'company_id': task.company_id.id,
        })
