# -*- coding: utf-8 -*-
import ast
import logging
import time
from datetime import timedelta

from odoo import api, fields, models
from odoo.osv import expression

from ..constants.message import MessageCode, get_message

_logger = logging.getLogger(__name__)


class SlaApplyJob(models.Model):
    """Một lần "Apply to Existing Records": gắn SLA cho record có sẵn theo lô.

    Logic: record tạo trước khi định nghĩa được bật không có task và không có
    cách nào để có (engine chỉ chạy khi record được ghi). Mỗi lần chạy là một
    dòng, không ghi đè lần trước. Lô đầu chạy ngay trong request của wizard;
    phần còn lại do cron `_cron_run` xử lý. Cả hai dùng chung MỘT hàm lô
    `_run_batch`, con trỏ `last_id` (id tăng dần) giúp chạy lại sau khi bị ngắt
    mà không xử lý trùng. Chỉ hệ thống ghi (mọi ghi qua `sudo()`, REQ-SEC-006).
    Refs: plan-improvement-sla-01-review §6.16
    """
    _name = 'sla.apply.job'
    _description = "SLA Manual Apply Run"
    _order = 'id desc'

    definition_id = fields.Many2one(
        'sla.definition', string="Definition", required=True, ondelete='cascade',
        index=True,
        help=('SLA definition this run applies to existing records. Example: '
              '"Ticket Response - Priority 1".'))
    filter_domain = fields.Text(
        string="Extra Filter",
        help=('Optional domain that narrows the records considered, combined '
              'with the Start Condition (never replacing it). Empty or [] adds '
              "no filter. Example: [('id', '<', 1000)] to only look at the "
              'oldest records.'))
    state = fields.Selection(
        [
            ('queued', "Queued"),
            ('running', "Running"),
            ('done', "Done"),
            ('cancelled', "Cancelled"),
            ('failed', "Failed"),
        ],
        string="Status", required=True, default='queued', index=True,
        help=('Queued: waiting for the first batch. Running: more batches are '
              'left for the background job. Done: every record was looked at. '
              'Cancelled: stopped by a manager. Failed: stopped by an '
              'unexpected error (see Note). Example: Running with 120 of 500 '
              'processed.'))
    total = fields.Integer(
        string="Total",
        help=('Number of records that matched when the run was created; only '
              'a progress indicator, it can drift if data changes meanwhile. '
              'Example: 500.'))
    processed = fields.Integer(
        string="Processed",
        help='Records already looked at by the engine. Example: 120.')
    attached = fields.Integer(
        string="Tasks Created",
        help=('SLA tasks created by this run. Records that already had a task '
              'create none. Example: 112.'))
    error_count = fields.Integer(
        string="Errors",
        help=('Error events logged for the processed records; details are in '
              'the SLA Events. Example: 0.'))
    last_id = fields.Integer(
        string="Last Record Id", default=0,
        help=('Id of the last source record processed; the next batch '
              'continues after it. Example: 4210.'))
    user_id = fields.Many2one(
        'res.users', string="Started By", ondelete='set null',
        help='User who started the run. Example: "Mitchell Admin".')
    start_time = fields.Datetime(
        string="Started",
        help='When the first batch ran (UTC). Example: 2026-03-02 05:00:00.')
    end_time = fields.Datetime(
        string="Finished",
        help=('When the run reached a final status (UTC). Example: '
              '2026-03-02 05:10:00.'))
    note = fields.Text(
        string="Note",
        help=('Error detail when the run failed. Example: "Manual apply '
              'stopped by an unexpected error: ...".'))

    @api.model
    def _build_domain(self, definition, filter_domain, last_id=0):
        """Domain của các record cần xét: Start Condition & bộ lọc thêm & id > last_id.

        Logic: Start Condition chưa cấu hình thì không record nào được xét. Ở
        bộ lọc thêm, trống hoặc `[]` nghĩa là KHÔNG lọc thêm (khác với 6 điều
        kiện của định nghĩa, nơi `[]` là chưa cấu hình).
        Refs: plan-improvement-sla-01-review §6.16
        """
        start = definition._get_domain('start')
        if start is None:
            return expression.FALSE_DOMAIN
        extra = ast.literal_eval(filter_domain) if filter_domain else []
        return expression.AND([list(start), list(extra), [('id', '>', last_id)]])

    def _run_batch(self):
        """Xử lý MỘT lô record; đóng job `done` khi không còn record nào.

        Logic: tải tối đa `dwo_sla_core.batch_size` record theo id tăng dần sau
        `last_id`, gọi engine với đúng định nghĩa này (idempotent nhờ
        `_can_attach`, không tạo trùng), đánh dấu sẵn các mốc escalation đã
        vượt của task mới để không bắn hàng loạt (REQ-FUNC-053), rồi cập nhật
        bộ đếm và `last_id`; lô ngắn hơn kích thước lô nghĩa là đã hết record nên
        job `done` ngay. Engine đã tự cô lập lỗi theo record bằng
        savepoint nên không bọc thêm ở đây. Job không còn `queued`/`running`
        (ví dụ bị Cancel) thì không làm gì.
        Refs: plan-improvement-sla-01-review §6.16, REQ-FUNC-053
        """
        self.ensure_one()
        self.invalidate_cache(['state'], ids=self.ids)
        if self.state not in ('queued', 'running'):
            return
        now = fields.Datetime.now()
        definition = self.definition_id
        batch_size = int(self.env['ir.config_parameter'].sudo().get_param(
            'dwo_sla_core.batch_size', default=50))
        Model = self.env[definition.model_name].sudo()
        records = Model.search(
            self._build_domain(definition, self.filter_domain, self.last_id),
            order='id', limit=batch_size)
        if not records:
            self.write({
                'state': 'done', 'end_time': now,
                'start_time': self.start_time or now,
            })
            return
        Task = self.env['sla.task'].sudo()
        Event = self.env['sla.event'].sudo()
        key = [('sla_id', '=', definition.id), ('res_model', '=', Model._name),
               ('res_id', 'in', records.ids)]
        last_task = Task.search([], order='id desc', limit=1).id or 0
        last_event = Event.search([], order='id desc', limit=1).id or 0
        self.env['sla.engine'].evaluate(records, definitions=definition)
        new_tasks = Task.search(key + [('id', '>', last_task)])
        new_tasks._mark_passed_escalations_done()
        errors = Event.search_count([
            ('id', '>', last_event), ('event', '=', 'error'),
            ('definition_id', '=', definition.id),
            ('res_model', '=', Model._name), ('res_id', 'in', records.ids)])
        # Lô ngắn hơn kích thước lô nghĩa là đã hết record: đóng job ngay, khỏi
        # tốn thêm một lượt rỗng.
        finished = len(records) < batch_size
        self.write({
            'state': 'done' if finished else 'running',
            'end_time': now if finished else False,
            'start_time': self.start_time or now,
            'processed': self.processed + len(records),
            'attached': self.attached + len(new_tasks),
            'error_count': self.error_count + errors,
            'last_id': records[-1].id,
        })

    @api.model
    def _cron_run(self):
        """Cron: chạy tiếp các job còn lại theo lô, báo tiến độ sau mỗi lô.

        Logic: lặp `_run_batch` cho tới khi job xong/bị huỷ hoặc hết ngân sách
        thời gian của `ir.cron` (`_commit_progress` trả số giây còn lại). Mỗi lô
        nằm trong savepoint: lỗi không lường trước làm job `failed` kèm `note`,
        không kéo theo job khác.
        Refs: plan-improvement-sla-01-review §6.16, REQ-REL-002
        """
        IrCron = self.env['ir.cron'].with_context(dwo_sla_started=time.monotonic())
        jobs = self.sudo().search([('state', 'in', ('queued', 'running'))], order='id')
        for job in jobs:
            while job.state in ('queued', 'running'):
                try:
                    with self.env.cr.savepoint():
                        job._run_batch()
                except Exception as exc:  # noqa: BLE001 -- lỗi một job không chặn job khác
                    _logger.exception("SLA manual apply job %s failed", job.id)
                    job.invalidate_cache(None, ids=job.ids)
                    job.write({
                        'state': 'failed', 'end_time': fields.Datetime.now(),
                        'note': get_message(MessageCode.NOTE_APPLY_JOB_FAILED, exc),
                    })
                remaining = self.sudo().search_count([('state', 'in', ('queued', 'running'))])
                if IrCron._commit_progress(1, remaining=remaining) <= 0:
                    return

    def action_cancel(self):
        """Huỷ job đang `queued`/`running`; vòng cron dừng ở lô kế tiếp.

        Refs: plan-improvement-sla-01-review §6.16
        """
        self.filtered(lambda j: j.state in ('queued', 'running')).sudo().write({
            'state': 'cancelled', 'end_time': fields.Datetime.now()})

    @api.autovacuum
    def _gc_old_jobs(self):
        """Dọn job đã kết thúc cũ hơn `event_retention_days`; không đụng job còn chạy.

        Logic: cùng ngưỡng với `sla.event` (mặc định 365 ngày); chỉ xoá job
        `done`/`cancelled`/`failed` có `end_time` cũ hơn ngưỡng.
        Refs: plan-improvement-sla-01-review §6.16, REQ-FUNC-035
        """
        retention_days = int(self.env['ir.config_parameter'].sudo().get_param(
            'dwo_sla_core.event_retention_days', 365))
        threshold = fields.Datetime.now() - timedelta(days=retention_days)
        self.sudo().search([
            ('state', 'in', ('done', 'cancelled', 'failed')),
            ('end_time', '<', threshold)]).unlink()
