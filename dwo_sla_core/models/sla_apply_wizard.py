# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import AccessError, UserError

from ..constants.message import MessageCode, get_message


class SlaApplyWizard(models.TransientModel):
    """Wizard "Apply to Existing Records": chọn bộ lọc rồi tạo và chạy job.

    Logic: chỉ MỘT ô domain (bộ lọc thêm, giao với Start Condition, không thay
    thế nó); Start Condition vẫn quyết định record nào được gắn task. Wizard
    tạo `sla.apply.job`, chạy lô đầu ngay (`_run_batch`) và, nếu còn record, nhờ
    cron xử lý phần còn lại. Chỉ SLA Manager (ACL).
    Refs: plan-improvement-sla-01-review §6.16
    """
    _name = 'sla.apply.wizard'
    _description = "Apply SLA to Existing Records"

    @api.model_create_multi
    def create(self, vals_list):
        # Odoo 13 and older: a transient model has no access rights (anyone can create one): check the group here
        if self.env.uid != SUPERUSER_ID and not self.env.user.has_group('dwo_sla_core.group_sla_manager'):
            raise AccessError(_("Only an SLA Configuration Administrator can apply an SLA to existing records."))
        return super().create(vals_list)

    definition_id = fields.Many2one(
        'sla.definition', string="Definition", required=True, ondelete='cascade',
        help=('SLA definition to apply to records that already exist. Example: '
              '"Ticket Response - Priority 1".'))
    model_name = fields.Char(
        related='definition_id.model_name', readonly=True,
        help='Technical name of the measured model. Example: helpdesk.ticket.')
    filter_domain = fields.Text(
        string="Extra Filter", default='[]',
        help=('Optional rules that narrow the records considered. They are '
              'combined with the Start Condition, never replace it. Empty or '
              "no rule means no extra filter. Example: Created on before "
              '2026-01-01.'))
    match_count = fields.Integer(
        string="Records to Check", compute='_compute_match_count',
        help=('How many records match the Start Condition and the extra '
              'filter right now. Records that already have a task are counted '
              'but get no new one. Example: 120.'))

    @api.depends('definition_id', 'filter_domain')
    def _compute_match_count(self):
        """Đếm record sẽ được xét bằng đúng domain mà job sẽ dùng.

        Refs: plan-improvement-sla-01-review §6.16
        """
        Job = self.env['sla.apply.job']
        for wizard in self:
            definition = wizard.definition_id
            if not definition:
                wizard.match_count = 0
                continue
            domain = Job._build_domain(definition, wizard.filter_domain)
            wizard.match_count = self.env[definition.model_name].sudo().search_count(domain)

    def action_apply(self):
        """Tạo job, chạy lô đầu ngay, giao phần còn lại cho cron, báo kết quả.

        Logic: không cho tạo job mới khi definition còn job `queued`/`running`
        (tránh hai job tranh nhau); definition phải đang bật vì engine không
        gắn task mới cho định nghĩa tắt.
        Refs: plan-improvement-sla-01-review §6.16
        """
        self.ensure_one()
        definition = self.definition_id
        if not definition.active:
            raise UserError(get_message(MessageCode.VAL_APPLY_DEFINITION_INACTIVE))
        Job = self.env['sla.apply.job'].sudo()
        if Job.search_count([('definition_id', '=', definition.id),
                             ('state', 'in', ('queued', 'running'))]):
            raise UserError(get_message(MessageCode.VAL_APPLY_JOB_ALREADY_RUNNING))
        job = Job.create({
            'definition_id': definition.id,
            'filter_domain': self.filter_domain or '[]',
            'user_id': self.env.user.id,
            'total': self.match_count,
        })
        job._run_batch()
        more = job.state in ('queued', 'running')
        if more:
            cron = self.env.ref('dwo_sla_core.ir_cron_sla_apply').sudo()
            if hasattr(cron, '_trigger'):
                cron._trigger()
            else:
                # Odoo 14 has no `ir.cron._trigger`: bring the next call forward
                cron.nextcall = fields.Datetime.now()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': get_message(MessageCode.INF_APPLY_RESULT_TITLE),
                'message': get_message(
                    MessageCode.INF_APPLY_RESULT_BODY, job.processed, job.attached,
                    job.error_count,
                    get_message(MessageCode.INF_APPLY_RESULT_CONTINUES) if more else ''),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
