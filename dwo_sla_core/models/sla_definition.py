# -*- coding: utf-8 -*-
import ast
import pytz

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression

from ..constants.message import MessageCode, get_message

# REQ-FUNC-002: model bị loại trừ vì gây đệ quy (sla.*) hoặc đụng hệ thống nền (ir.*, mail.*)
EXCLUDED_MODEL_PREFIXES = ('sla.', 'ir.', 'mail.')

# 6 điều kiện của một định nghĩa SLA (REQ-FUNC-003)
CONDITION_FIELDS = (
    'start_domain', 'cancel_domain', 'pause_domain',
    'resume_domain', 'stop_domain', 'reset_domain',
)


class SlaDefinition(models.Model):
    """Luật SLA, mỗi dòng áp dụng cho một model.

    Logic: cấu hình SLA cho model bất kỳ chỉ bằng dữ liệu (REQ-FUNC-001); các
    điều kiện là domain literal kiểm tra khi lưu (AD-11); snapshot vào task lúc
    attach để sửa cấu hình không ảnh hưởng task đang chạy (REQ-FUNC-021).
    Tên field theo quyết định "đồng bộ ServiceNow" (lịch sử trao đổi dự án):
    field có tương đương bên `contract_sla` dùng đúng từ SN (`duration`,
    `schedule_*`, `retroactive`, `type`, `target`, `vendor_id`,
    `service_commitment`); field không có tương đương (6 domain,
    `cancel_mode`/`resume_mode`) giữ tên gốc vì đây là cú pháp Odoo domain
    thật, không phải script condition của SN.
    Refs: REQ-FUNC-001, 030, DB Design §3 bảng sla_definition
    """
    _name = 'sla.definition'
    _inherit = ['mail.thread']
    _description = "SLA Definition"
    _order = 'sequence, id'

    name = fields.Char(required=True,
        help=('Name of the SLA rule, shown in lists and on every task it '
              'creates. Use something that tells users what is measured. '
              'Example: "Ticket Response - Priority 1".'))
    # Refs: plan-improvement-sla-01-review §6.3 -- mặc định tắt: định nghĩa mới
    # là bản nháp cho tới khi người dùng bấm Enable.
    active = fields.Boolean(default=False, tracking=True,
        help=('Whether this SLA is enabled. A new definition starts disabled '
              'so you can finish configuring it; press Enable when ready. '
              'Disabling stops attaching this SLA to new records, while tasks '
              'that are already running keep being tracked until they '
              'finish. Example: disable an old SLA after replacing it with a '
              'new one instead of deleting it.'))
    sequence = fields.Integer(default=10,
        help=('Display order of definitions in lists; lower numbers come '
              'first. It does not change how SLAs are evaluated. Example: 10 '
              'for the response SLA, 20 for the resolution SLA.'))
    # Refs: REQ-SEC-003
    company_id = fields.Many2one(
        'res.company', string="Company", ondelete='restrict',
        help=('Restricts the SLA to records of one company. Leave empty to '
              'apply to records of every company. Example: set "Sojitz '
              'Vietnam" so tickets of other companies never get this SLA.'))
    model_id = fields.Many2one(
        'ir.model', string="Model", required=True, ondelete='cascade',
        tracking=True,
        help=('The business model whose records are measured by this SLA. '
              'Every record of that model that meets the Start Condition gets '
              'its own SLA task. Example: "Helpdesk Ticket" or "Contact".'))
    # Refs: AD-01, AD-10
    model_name = fields.Char(
        related='model_id.model', store=True, readonly=True, index=True,
        string="Model Technical Name",
        help=('Technical name of the selected model, filled in automatically '
              'from Model. Used internally for fast lookups; do not edit. '
              'Example: res.partner.'))
    # Refs: REQ-FUNC-018 -- "target_hours" -> "duration" để khớp thẳng
    # `contract_sla.duration` của ServiceNow (tên và label); đơn vị vẫn là
    # giờ (Float), chỉ đổi tên/nhãn.
    duration = fields.Float(
        string="Duration", required=True, default=0, tracking=True,
        help=('Time allowed to finish, in hours. With a working calendar it '
              'counts working hours only, otherwise clock hours (24x7). 0 is '
              'accepted and means the deadline is the start time. Example: 4 '
              'means the SLA is breached 4 working hours after it starts.'))
    # Refs: REQ-FUNC-019, REQ-INT-007 -- "calendar_*" -> "schedule_*" (khớp
    # `contract_sla.schedule`/`schedule_source`/`schedule_source_field`).
    schedule_source = fields.Selection(
        [
            ('none', "No calendar (24x7)"),
            ('definition', "Fixed calendar on the definition"),
            ('record', "Calendar read from the record"),
        ],
        string="Calendar Source", default='none', required=True,
        tracking=True,
        help=('Where the working calendar comes from. No calendar: time runs '
              '24x7. Fixed calendar on the definition: always use the '
              'calendar selected below. Calendar read from the record: follow '
              'a calendar found on the record itself. Example: choose '
              '"Calendar read from the record" when each customer has its own '
              'support hours.'))
    schedule_id = fields.Many2one(
        'resource.calendar', string="Fixed Calendar", ondelete='restrict',
        tracking=True,
        help=('Working calendar used when Calendar Source is "Fixed calendar '
              'on the definition". It must be a fixed-hours calendar with at '
              'least one working period. Example: "Standard 40 hours/week '
              '(Mon-Fri 08:00-17:00)".'))
    schedule_path = fields.Char(
        string="Calendar Path on Record",
        help=('Field on the record that leads to a calendar, picked with the '
              'same field chooser used in Automation Rules and Mail '
              'Templates -- click it, then navigate through relations (for '
              'example Customer) to the calendar field at the end. If any '
              'step is empty or the calendar is unusable, the company '
              'calendar (then 24x7) is used instead. Example: '
              'partner_id.resource_calendar_id.'))
    # Refs: scope-add "calendar_tz_override" -- override tz độc lập với tz
    # gốc của calendar đã resolve. `resource.calendar.plan_hours()` diễn
    # giải giờ làm theo `tz` lưu sẵn trên chính bản ghi calendar, không nhận
    # tham số override tz từ ngoài, nên làm đúng cần một BẢN SAO calendar
    # cùng mẫu giờ làm nhưng đổi tz -- áp dụng ở
    # `sla.time._apply_tz_override()`/`resource.calendar._sla_get_tz_variant()`
    # (tìm-hoặc-tạo, cache qua field kỹ thuật `sla_tz_override_source_id`).
    # Refs: plan-improvement-sla-01-review §6.5 -- bắt buộc, có default (tz
    # người dùng hoặc UTC) để form mới không bị ô trống; onchange/create đổi
    # sang tz của calendar cố định khi có.
    calendar_tz_override = fields.Selection(
        selection='_get_tz_selection', string="Timezone", required=True,
        default=lambda self: self.env.user.tz or 'UTC', tracking=True,
        help=('Timezone in which the working hours of the calendar are '
              'read and the SLA clock runs; it always wins over the '
              'calendar\'s own timezone. Filled in for you. Example: '
              '"America/New_York". See the Note tab for how calendar copies '
              'work.'))
    start_domain = fields.Text(string="Start Condition", default='[]', tracking=True,
        help=('Condition that makes a record start being measured. Written as '
              'a domain list. An empty rule list [] means "not configured" '
              "and never matches; to match every record write "
              "[('id', '!=', 0)]. Example: [('priority', '=', "
              "'3')] starts the SLA for urgent tickets."
              ' See the Note tab for limits and common mistakes.'))
    cancel_domain = fields.Text(string="Cancel Condition", default='[]', tracking=True,
        help=('Condition that cancels the running SLA when Cancel Mode is '
              '"When the cancel condition matches". A cancelled SLA is '
              'discarded and not counted as achieved or breached. Example: '
              "[('stage_id.name', '=', 'Cancelled')]."
              ' See the Note tab for limits and common mistakes.'))
    pause_domain = fields.Text(string="Pause Condition", default='[]', tracking=True,
        help=('Condition that pauses the clock while it matches, for example '
              'while waiting for the customer. The paused time is not counted '
              "against the target. Example: [('state', '=', "
              "'waiting_customer')]."
              ' See the Note tab for limits and common mistakes.'))
    resume_domain = fields.Text(string="Resume Condition", default='[]', tracking=True,
        help=('Condition that restarts a paused clock when Resume Mode is '
              '"When the resume condition matches". Example: [(\'state\', \'=\', '
              "'in_progress')]."
              ' See the Note tab for limits and common mistakes.'))
    stop_domain = fields.Text(string="Stop Condition", default='[]', tracking=True,
        help=('Condition that completes the SLA. The task becomes Achieved, '
              'or Breached if the deadline had already passed. Example: '
              "[('state', 'in', ['resolved', 'closed'])]."
              ' See the Note tab for limits and common mistakes.'))
    reset_domain = fields.Text(string="Reset Condition", default='[]', tracking=True,
        help=('Condition that, together with the Start Condition, ends the '
              'current SLA and starts a fresh one, for example when a ticket '
              'is reopened. Combine with Reset-Trigger Fields to react only '
              "to real changes. Example: [('state', '=', 'reopened')]."
              ' See the Note tab for limits and common mistakes.'))
    cancel_mode = fields.Selection(
        [
            ('start_unmatched', "When start no longer matches"),
            ('condition', "When the cancel condition matches"),
            ('never', "Never cancel"),
        ],
        string="Cancel Mode", default='start_unmatched', required=True,
        tracking=True,
        help=('How cancellation is decided. When start no longer matches: '
              'cancel as soon as the record leaves the Start Condition. When '
              'the cancel condition matches: use the Cancel Condition. Never '
              'cancel: running tasks are never cancelled. Example: pick '
              '"Never cancel" to keep measuring even if the ticket is edited.'))
    resume_mode = fields.Selection(
        [
            ('condition', "When the resume condition matches"),
            ('pause_unmatched', "When pause no longer matches"),
        ],
        string="Resume Mode", default='condition', required=True,
        tracking=True,
        help=('How a paused task restarts. When the resume condition matches: '
              'use the Resume Condition. When pause no longer matches: resume '
              'as soon as the Pause Condition stops matching. Example: choose '
              'the second option so you only maintain a Pause Condition.'))
    reset_action = fields.Selection(
        [
            ('cancel', "Cancel the previous task"),
            ('complete', "Complete the previous task"),
        ],
        string="Reset Action", default='cancel', required=True,
        tracking=True,
        help=('What happens to the previous task when a reset occurs. Cancel: '
              'it is discarded. Complete: it is closed as Achieved or '
              'Breached according to the deadline. Example: use "Complete" to '
              'keep a result for each time a ticket was reopened.'))
    # Refs: REQ-FUNC-017 -- "retroactive_start" -> "retroactive" (khớp SN).
    retroactive = fields.Boolean(
        string="Retroactive Start",
        help=('Tick to take the SLA start time from a date field on the '
              'record instead of the moment the SLA is attached. A start in '
              'the past can make the task breached immediately. Example: '
              "start counting from the ticket's creation time rather than "
              'when the rule was applied.'))
    # "retroactive_field_id" -> "start_field_id" (SN gọi field này
    # "setStartTo"; giữ hậu tố _id vì vẫn là Many2one).
    start_field_id = fields.Many2one(
        'ir.model.fields', string="Start-Marker Field",
        help=('Datetime field of the model used as the SLA start time when '
              'Retroactive Start is on. If the field is empty, the current '
              'time is used and a note is logged. Example: "Created on".'))
    # Refs: REQ-FUNC-013
    reset_field_ids = fields.Many2many(
        'ir.model.fields', relation='sla_definition_reset_field_rel',
        column1='definition_id', column2='field_id',
        string="Reset-Trigger Fields",
        help=('Reset only happens when one of these fields has just changed '
              'value. Leave empty to reset every time the Reset Condition is '
              'met. Example: select "Priority" so a reset occurs only when '
              'the priority is edited.'))
    # Refs: plan-improvement-sla-01-review §6.10
    due_soon_hours = fields.Float(
        string="Due Soon (hours)", tracking=True,
        help=('Hours before the deadline when a running task counts as "Due '
              'Soon" for this SLA. Leave empty or 0 to use the global value '
              'in Settings. Must not be negative. Example: 2 on a 4-hour SLA '
              'flags tasks in their last 2 hours; 24 on a 3-day SLA flags '
              'the last day.'))
    # Refs: plan-improvement-sla-01-review §6.7
    running_task_count = fields.Integer(
        string="Running Tasks", compute='_compute_running_task_count',
        help=('Number of tasks of this SLA that are in progress or paused. '
              'Shown on the smart button and used to warn before saving '
              'changes that affect running tasks. Example: 12 means 12 '
              'records are being measured right now.'))
    # Refs: plan-improvement-sla-01-review §6.16
    apply_job_ids = fields.One2many(
        'sla.apply.job', 'definition_id', string="Manual Apply Runs", readonly=True,
        help=('History of "Apply to Existing Records" runs for this SLA, '
              'newest first. Example: a run that created 112 tasks.'))
    apply_retention_days = fields.Integer(
        string="Run History Retention", compute='_compute_apply_retention_days',
        help=('Days after which finished manual apply runs are removed '
              'automatically; it follows the event log retention in Settings. '
              'Example: 365.'))
    escalation_ids = fields.One2many(
        'sla.escalation', 'definition_id', string="Escalations",
        help=('Actions fired automatically when a task reaches a percentage '
              'of its target time (above 100% means already breached). '
              'Example: 75% notify the assignee, 100% notify the manager.'))

    # --- Metadata thêm theo scope-add, mirror ServiceNow contract_sla
    # (KHÔNG đổi hành vi engine; chỉ label để lọc/báo cáo) ---
    # Không `required=True`: Selection không có DEFAULT ở tầng DB (khác Boolean,
    # Odoo tự đặt NOT NULL DEFAULT false), nên bắt buộc sẽ vỡ các INSERT SQL
    # thô không biết tới field mới này (TC-INF-009). `default='sla'` vẫn áp
    # dụng cho mọi record tạo qua ORM như bình thường.
    type = fields.Selection(
        [('sla', "SLA"), ('ola', "OLA")], default='sla',
        help=('SLA: commitment measured directly with an external customer. '
              'OLA: internal commitment between teams supporting a larger '
              'SLA, not shown to the customer directly. Label only -- the '
              '6 conditions behave identically for both. Example: a '
              '"ticket response" definition is usually SLA; a "warehouse '
              'prep step" definition feeding into it is usually OLA.'))
    vendor_id = fields.Many2one(
        'res.partner', string="Vendor",
        help=('External vendor this commitment is measured against, when '
              'this SLA/OLA is tied to an Underpinning Contract. Label only, '
              'for reporting -- does not change engine behaviour. Example: '
              'the ISP whose uptime commitment this OLA tracks.'))
    service_commitment = fields.Boolean(
        string="Service Commitment", default=False,
        help=('Tick when this is an officially published commitment reported '
              'on a service contract, as opposed to an internal-only measure. '
              'Label only, for reporting -- does not change engine behaviour.'))
    target = fields.Selection(
        [('response', "Response"), ('resolution', "Resolution")],
        help=('Optional classification of what this SLA measures, for '
              'filtering and grouping reports. Leave empty if not '
              'classified. Does not change how the 6 conditions behave -- '
              'a "Response" and a "Resolution" SLA on the same record are '
              'still two separate definitions. Example: tag the definition '
              'that stops on first reply as "Response".'))

    # --- Retroactive pause (ServiceNow Fluent SLA API: retroactive.pause,
    # default true, only meaningful when retroactive.start is on). Scope
    # decision: only usable when the model is trackable (mail.thread) and
    # every field in pause_domain has tracking=True -- warn, never block
    # saving. ---
    retroactive_pause = fields.Boolean(
        string="Retroactive Pause", default=True,
        help=('When Retroactive Start is on and the SLA start time is backdated, '
              'subtract from the elapsed time any period in that backdated '
              'window where the Pause Condition was already true, instead of '
              'counting the whole backdated window as running time. Only has '
              'an effect when the model and the fields used in the Pause '
              'Condition are change-tracked (see the warning below if not); '
              'otherwise the backdated window is always counted as running, '
              'same as when this is off.'))
    retroactive_pause_warning = fields.Char(
        string="Retroactive Pause Warning", compute='_compute_retroactive_pause_warning',
        help=('Shown when Retroactive Pause cannot have any effect for this '
              'definition: the model is not change-tracked, or some field '
              'used in the Pause Condition is not tracked.'))

    _sql_constraints = [
        ('target_hours_check', 'CHECK(duration >= 0)', "Duration cannot be negative."),
        ('cancel_mode_check', "CHECK(cancel_mode IN ('start_unmatched','condition','never'))", "Invalid Cancel Mode."),
        ('resume_mode_check', "CHECK(resume_mode IN ('condition','pause_unmatched'))", "Invalid Resume Mode."),
        ('reset_action_check', "CHECK(reset_action IN ('cancel','complete'))", "Invalid Reset Action."),
        ('calendar_definition_check', "CHECK(schedule_source <> 'definition' OR schedule_id IS NOT NULL)", "Calendar source 'definition' requires a fixed calendar to be "
        "selected."),
        ('calendar_record_check', "CHECK(schedule_source <> 'record' OR schedule_path IS NOT NULL)", "Calendar source 'record' requires a path to be entered."),
        ('due_soon_hours_check', 'CHECK(due_soon_hours IS NULL OR due_soon_hours >= 0)', "The \"due soon\" hours cannot be negative."),
        ('type_check', "CHECK(type IN ('sla','ola'))", "Invalid Type."),
    ]

    def init(self):
        super().init()
        # Odoo 17/18 have no models.Index: the (partial) indexes are created here
        self._cr.execute(f'CREATE INDEX IF NOT EXISTS {self._table}_model_name_active_idx ON {self._table} ' + "(model_name) WHERE active IS TRUE")


    @api.model
    def _get_tz_selection(self):
        """Danh sách timezone cho `calendar_tz_override`, giống field `tz` chuẩn.

        Logic: dùng `pytz` (Python 3.8 của Odoo 15 chưa có `zoneinfo`; `pytz` là phụ thuộc của Odoo) vì
        mã nguồn module chỉ được phép import thư viện chuẩn, `pytz` hoặc `odoo.*`
        (TC-INF-034, REQ-INST không external_dependencies).
        """
        return [(tz, tz) for tz in pytz.all_timezones]

    @api.onchange('schedule_source', 'schedule_id')
    def _onchange_schedule_suggest_tz(self):
        """Điền timezone của calendar cố định khi người dùng chọn nguồn lịch.

        Logic: chỉ áp cho nguồn 'definition' có calendar. Bản ghi chưa lưu thì
        luôn lấy tz calendar (người dùng đang dựng form); bản ghi đã lưu chỉ
        điền khi ô đang trống, không ghi đè lựa chọn đã có.
        Refs: plan-improvement-sla-01-review §6.5
        """
        if (self.schedule_source == 'definition' and self.schedule_id
                and (not self.calendar_tz_override or not self._origin)):
            self.calendar_tz_override = self.schedule_id.tz

    @api.model_create_multi
    def create(self, vals_list):
        """Tạo định nghĩa, điền timezone nếu thiếu, rồi đăng ký lại hook.

        Logic: model_name là related stored (tự đồng bộ từ ir_model.model, AD-01).
        Timezone là bắt buộc: create qua ORM/import thiếu giá trị mà nguồn là
        'definition' có calendar thì lấy tz calendar, còn lại để `default` của
        field (tz người dùng hoặc UTC) lo. Sau khi tạo, tập model có định nghĩa có thể đổi nên
        phải đăng ký lại patch.
        Refs: REQ-FUNC-001, AD-01, plan-improvement-sla-01-review §6.5
        """
        for vals in vals_list:
            if (not vals.get('calendar_tz_override')
                    and vals.get('schedule_source') == 'definition'
                    and vals.get('schedule_id')):
                vals['calendar_tz_override'] = self.env['resource.calendar'].browse(
                    vals['schedule_id']).tz
        definitions = super().create(vals_list)
        self._register_sla_hook()
        return definitions

    def write(self, vals):
        """Sửa định nghĩa; đăng ký lại hook nếu đổi model hoặc bật/tắt.

        Logic: các field ảnh hưởng tới tập model cần patch là model_id,
        active; đổi các field này phải đăng ký lại hook (AD-01). Đổi model
        thật sự khi định nghĩa đã có task bị chặn: task giữ `res_model` cũ
        nên engine sẽ đánh giá nó bằng domain của model khác.
        Refs: AD-01, plan-improvement-sla-01-review §6.14
        """
        if 'model_id' in vals:
            changed = self.filtered(lambda d: d.model_id.id != vals['model_id'])
            if changed and self.env['sla.task'].sudo().search(
                    [('sla_id', 'in', changed.ids)], limit=1):
                raise ValidationError(get_message(
                    MessageCode.VAL_MODEL_LOCKED_HAS_TASKS))
        res = super().write(vals)
        if {'model_id', 'active'} & set(vals):
            self._register_sla_hook()
        return res

    def _compute_running_task_count(self):
        """Đếm task đang chạy hoặc tạm dừng của từng định nghĩa.

        Logic: một `_read_group` theo `sla_id` (sudo giống `sla.mixin`).
        Refs: plan-improvement-sla-01-review §6.7
        """
        counts = dict(self.env['sla.task'].sudo()._sla_read_group(
            [('sla_id', 'in', self.ids), ('stage', 'in', ('in_progress', 'paused'))],
            ['sla_id'], ['__count']))
        for definition in self:
            definition.running_task_count = counts.get(definition, 0)

    def _compute_apply_retention_days(self):
        """Số ngày giữ lịch sử apply thủ công, đọc từ cấu hình (cùng `event_retention_days`).

        Refs: plan-improvement-sla-01-review §6.16
        """
        days = int(self.env['ir.config_parameter'].sudo().get_param(
            'dwo_sla_core.event_retention_days', 365))
        for definition in self:
            definition.apply_retention_days = days

    def action_open_apply_wizard(self):
        """Mở wizard "Apply to Existing Records" cho định nghĩa này.

        Refs: plan-improvement-sla-01-review §6.16
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Apply to Existing Records",
            'res_model': 'sla.apply.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_definition_id': self.id},
        }

    def action_view_tasks(self):
        """Mở danh sách mọi task của định nghĩa này (smart button).

        Refs: plan-improvement-sla-01-review §6.7
        """
        self.ensure_one()
        action = self.env.ref(
            'dwo_sla_core.action_sla_task').sudo().read()[0]  # Odoo 13: no `_for_xml_id`
        action['domain'] = [('sla_id', '=', self.id)]
        action['context'] = {}
        return action

    def action_enable(self):
        """Bật định nghĩa; cảnh báo (không chặn) nếu Start Condition chưa cấu hình.

        Logic: bật xong tải lại form bằng `reload` (Odoo 15: no `soft_reload`, the page reloads). Start `[]` là "chưa cấu
        hình" nên bật mà không có rule thì sẽ không bao giờ attach task.
        Refs: plan-improvement-sla-01-review §6.3
        """
        self.write({'active': True})
        reload_action = {'type': 'ir.actions.client', 'tag': 'reload'}
        if any(definition._get_domain('start') is None for definition in self):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': get_message(MessageCode.INF_ENABLE_WITHOUT_START_TITLE),
                    'message': get_message(MessageCode.INF_ENABLE_WITHOUT_START_BODY),
                    'type': 'warning',
                    'sticky': False,
                    'next': reload_action,
                },
            }
        return reload_action

    def action_disable(self):
        """Tắt định nghĩa (task đang chạy vẫn được theo dõi), rồi tải lại form.

        Refs: plan-improvement-sla-01-review §6.3, REQ-FUNC-060
        """
        self.write({'active': False})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def unlink(self):
        """Xóa định nghĩa rồi đăng ký lại hook (tập model có thể đổi)."""
        # Odoo 14 has no `@api.ondelete(at_uninstall=False)` (15+): same check, skipped while the module is uninstalled
        if not self.env.context.get('_force_unlink'):
            self._unlink_except_has_task()
        res = super().unlink()
        self._register_sla_hook()
        return res

    def _unlink_except_has_task(self):
        """Chặn xóa định nghĩa còn task tham chiếu; gợi ý archive.

        Logic: giữ lịch sử đo, không xóa định nghĩa đã từng sinh task.
        Refs: REQ-FUNC-061
        """
        # Odoo 15: `search_count` has no `limit`
        has_task = self.env['sla.task'].sudo().search(
            [('sla_id', 'in', self.ids)], limit=1)
        if has_task:
            raise ValidationError(get_message(
                MessageCode.VAL_DEFINITION_HAS_TASKS))

    @api.constrains('model_id')
    def _check_model(self):
        """Từ chối model transient, abstract, _auto=False hoặc sla./ir./mail.*.

        Logic: tránh đệ quy (SLA gắn vào chính dữ liệu SLA) và ảnh hưởng hệ
        thống nền.
        Refs: REQ-FUNC-002
        """
        for definition in self:
            model_name = definition.model_id.model
            if model_name.startswith(EXCLUDED_MODEL_PREFIXES):
                raise ValidationError(get_message(
                    MessageCode.VAL_MODEL_EXCLUDED_GROUP, model_name))
            model = self.env.get(model_name)
            if model is None:
                continue
            if model._transient or model._abstract or not model._auto:
                raise ValidationError(get_message(
                    MessageCode.VAL_MODEL_NOT_STORABLE, model_name))

    @api.constrains(*CONDITION_FIELDS)
    def _check_domains(self):
        """Kiểm tra 6 điều kiện là domain literal hợp lệ với model đã chọn.

        Logic: điều kiện rỗng nghĩa là chưa cấu hình (FUNC-003); nếu có giá
        trị thì parse bằng ast.literal_eval (an toàn, không thực thi mã) rồi
        kiểm tra bằng expression.expression(...) (Odoo 19: Domain(...).validate, AD-11); giá trị không phải
        literal (gọi hàm, biến) bị ast.literal_eval từ chối.
        Refs: REQ-FUNC-003, AD-11
        """
        for definition in self:
            model = self.env.get(definition.model_id.model)
            if model is None:
                continue
            for field_name in CONDITION_FIELDS:
                value = definition[field_name]
                if not value:
                    continue
                try:
                    domain_literal = ast.literal_eval(value)
                except (ValueError, SyntaxError) as exc:
                    raise ValidationError(get_message(
                        MessageCode.VAL_CONDITION_DOMAIN_LITERAL_INVALID,
                        field_name, exc)) from exc
                try:
                    # Odoo 18 has no Domain(...).validate(): build the query, which checks the fields,
                    # the operators and that the fields can be searched (as Domain.validate does in 19)
                    expression.expression(expression.normalize_domain(domain_literal), model.sudo().with_context(active_test=False))
                except Exception as exc:
                    raise ValidationError(get_message(
                        MessageCode.VAL_CONDITION_DOMAIN_MODEL_INVALID,
                        field_name, definition.model_id.model, exc)) from exc

    @api.constrains('schedule_source', 'schedule_id', 'schedule_path')
    def _check_calendar(self):
        """Kiểm tra nguồn lịch: 'definition' phải có lịch fully_fixed có giờ làm.

        Logic: schedule_source='definition' từ chối lịch không có giờ làm
        trong tuần ngay khi lưu, thay vì lỗi lúc attach (REQ-FUNC-030).
        schedule_source='record' kiểm tra đường dẫn gồm các bước Many2one,
        bước cuối trỏ tới resource.calendar (không từ chối khi không dùng
        được lịch thực tế lúc runtime, vì có lịch dự phòng REQ-FUNC-020).
        Refs: REQ-FUNC-039, REQ-FUNC-019, REQ-INT-009
        """
        for definition in self:
            if definition.schedule_source == 'definition' and definition.schedule_id:
                calendar = definition.schedule_id
                if not calendar._sla_is_fully_fixed():
                    raise ValidationError(get_message(
                        MessageCode.VAL_CALENDAR_NOT_FULLY_FIXED))
                if not calendar.attendance_ids:
                    raise ValidationError(get_message(
                        MessageCode.VAL_CALENDAR_NO_ATTENDANCE, calendar.name))
            elif definition.schedule_source == 'record' and definition.schedule_path:
                model = self.env.get(definition.model_id.model)
                if model is None:
                    continue
                steps = definition.schedule_path.split('.')
                current_model = model
                for step in steps:
                    field = current_model._fields.get(step)
                    if field is None or field.type != 'many2one':
                        raise ValidationError(get_message(
                            MessageCode.VAL_CALENDAR_PATH_NOT_MANY2ONE,
                            definition.schedule_path, step, current_model._name))
                    current_model = self.env[field.comodel_name]  # pyright: ignore[reportArgumentType]
                if current_model._name != 'resource.calendar':
                    raise ValidationError(get_message(
                        MessageCode.VAL_CALENDAR_PATH_WRONG_TARGET,
                        definition.schedule_path, current_model._name))

    @api.constrains('start_field_id', 'reset_field_ids')
    def _check_fields(self):
        """Kiểm tra field retroactive và field kích hoạt reset thuộc model.

        Logic: field retroactive phải kiểu Datetime và thuộc model của định
        nghĩa; field kích hoạt reset phải thuộc model của định nghĩa.
        Refs: REQ-FUNC-041
        """
        for definition in self:
            model_name = definition.model_id.model
            if definition.start_field_id:
                field = definition.start_field_id
                if field.model != model_name:
                    raise ValidationError(get_message(
                        MessageCode.VAL_START_FIELD_WRONG_MODEL, model_name))
                if field.ttype != 'datetime':
                    raise ValidationError(get_message(
                        MessageCode.VAL_START_FIELD_NOT_DATETIME))
            for field in definition.reset_field_ids:
                if field.model != model_name:
                    raise ValidationError(get_message(
                        MessageCode.VAL_RESET_FIELD_WRONG_MODEL,
                        field.name, model_name))

    @api.depends('retroactive_pause', 'pause_domain', 'model_id')
    def _compute_retroactive_pause_warning(self):
        """Cảnh báo (không chặn lưu) khi retroactive_pause không có dữ liệu để dùng.

        Logic: retroactive_pause chỉ hoạt động khi model có mail.thread
        (duck-type hasattr(model, 'message_post'), không ép phụ thuộc cứng
        vào module `mail`) VÀ mọi field trong pause_domain có tracking=True.
        Model/field không đạt không phải lỗi cấu hình -- chỉ là tính năng im
        lặng không có lịch sử để dùng (cùng tinh thần ServiceNow: field chưa
        tick Audit cũng không chặn lưu, chỉ không có gì để tính).
        Refs: scope-add "retroactive_pause giới hạn model/field có tracking"
        """
        for definition in self:
            definition.retroactive_pause_warning = False
            if not definition.retroactive_pause or not definition.model_id:
                continue
            model = self.env.get(definition.model_id.model)
            if model is None:
                continue
            if not hasattr(model, 'message_post'):
                definition.retroactive_pause_warning = (
                    "Model '%s' is not change-tracked (no mail.thread): "
                    "Retroactive Pause will have no effect." % model._name)
                continue
            field_names = definition._pause_domain_field_names(model)
            untracked = sorted(
                name for name in field_names
                if name in model._fields and not getattr(model._fields[name], 'tracking', False))
            if untracked:
                definition.retroactive_pause_warning = (
                    "Retroactive Pause will have no effect for field(s) not "
                    "tracked on '%s': %s. Enable tracking on them, or "
                    "Retroactive Pause stays a no-op for this definition."
                    % (model._name, ", ".join(untracked)))

    def _pause_domain_field_names(self, model=None):
        """Tên field (gốc, bỏ phần quan hệ) xuất hiện trong `pause_domain`.

        Logic: dùng lại đúng cách bóc field từ domain đã có ở
        `sla_hook.py::_get_watched_field_names` (chỉ lấy leaf 3-phần tử,
        field quan hệ `a.b.c` chỉ lấy `a` -- hạn chế đã biết, không mới).
        Refs: scope-add "retroactive_pause"
        """
        self.ensure_one()
        names = set()
        try:
            domain = self._get_domain('pause')
        except Exception:  # noqa: BLE001 -- domain hỏng: constraint khác đã báo
            domain = None
        for leaf in domain or []:
            if isinstance(leaf, (list, tuple)) and len(leaf) == 3:
                names.add(str(leaf[0]).split('.')[0])
        return names

    def _retroactive_pause_eligible(self, model):
        """(đạt hay không, field không đạt) cho model đã cho -- dùng chung cho
        warning và cho Engine (REQ liên quan: scope-add "retroactive_pause").
        """
        self.ensure_one()
        if not hasattr(model, 'message_post'):
            return False, set()
        field_names = self._pause_domain_field_names(model)
        untracked = {
            name for name in field_names
            if name in model._fields and not getattr(model._fields[name], 'tracking', False)}
        return not untracked and bool(field_names), field_names

    def _retroactive_pause_segments(self, record, start_dt, end_dt):
        """Các đoạn `[seg_start, seg_end]` trong `[start_dt, end_dt]` mà `pause_domain`
        của `self` đã khớp trong quá khứ, dựng lại từ `mail.tracking.value`.

        Logic (ServiceNow Fluent SLA API `retroactive.pause`, xem scope-add
        "retroactive_pause"): chỉ áp dụng khi model trackable và mọi field
        trong `pause_domain` có `tracking=True` (REQ liên quan); nếu không,
        trả `[]` (không trừ gì -- hành vi hiện tại, không raise lỗi). Chỉ hỗ
        trợ `pause_domain` dạng list phẳng (AND ngầm định) các leaf
        `(field, operator, value)` với `operator` thuộc {'=', '!=', 'in',
        'not in'} trên field trực tiếp của model (không qua quan hệ) -- gặp
        cú pháp khác (có '&'/'|'/'!' tiền tố, hoặc operator không hỗ trợ) thì
        trả `[]` để an toàn (không trừ sai) thay vì cố đánh giá nhầm.

        Dựng lại: lấy mọi `mail.tracking.value` của `record` cho đúng các
        field cần, trong khoảng [start_dt, end_dt], giải mã giá trị theo
        `ttype` (Selection lưu LABEL hiển thị, phải map ngược lại key qua
        `fields_get`; Many2one lưu id ở cột `_integer`); dựng lại giá trị
        từng field TẠI `start_dt` bằng `old_value` của thay đổi sớm nhất tìm
        được (hoặc giá trị hiện tại của record nếu field đó không có thay
        đổi nào trong khoảng -- coi như không đổi suốt khoảng, hạn chế đã
        biết khi không có đủ lịch sử); gộp mọi mốc thay đổi thành 1 dãy mốc
        chung, đánh giá domain tại từng đoạn giữa 2 mốc liên tiếp.
        Refs: scope-add "retroactive_pause", Fluent SLA API `retroactive.pause`
        """
        self.ensure_one()
        if end_dt <= start_dt:
            return []
        model = self.env.get(self.model_id.model)
        if model is None:
            return []
        eligible, field_names = self._retroactive_pause_eligible(model)
        if not eligible:
            return []
        try:
            domain = self._get_domain('pause')
        except Exception:  # noqa: BLE001 -- domain hỏng: constraint khác đã báo
            return []
        if not self._is_flat_simple_domain(domain, field_names):
            return []

        field_ids = self.env['ir.model.fields'].sudo().search([
            ('model', '=', model._name), ('name', 'in', sorted(field_names))])
        if not field_ids:
            return []
        trackings = self.env['mail.tracking.value'].sudo().search([
            # Odoo 13: `field` of a tracking value is the field NAME (Char); 14-16: many2one `field`; 17+: `field_id`
            ('field', 'in', field_ids.mapped('name')),
            ('mail_message_id.model', '=', model._name),
            ('mail_message_id.res_id', '=', record.id),
            ('mail_message_id.date', '>=', start_dt),
            ('mail_message_id.date', '<=', end_dt),
        ]).sorted(lambda t: t.mail_message_id.date)

        selections = {
            name: dict(model.fields_get([name])[name].get('selection') or [])
            for name in field_names if model._fields[name].type == 'selection'}
        decoded = [
            (t.mail_message_id.date, t.field,
             self._decode_tracking_value(t, 'old_value', selections),
             self._decode_tracking_value(t, 'new_value', selections))
            for t in trackings]

        # Giá trị từng field tại start_dt: old_value của thay đổi sớm nhất tìm
        # được trong khoảng, hoặc giá trị hiện tại nếu không có thay đổi nào.
        # Many2one giải mã về id (int) để so khớp cùng kiểu với giá trị dựng
        # lại từ mail.tracking.value (cũng là id, xem _decode_tracking_value).
        state = {
            name: (record[name].id if model._fields[name].type == 'many2one'
                   else record[name])
            for name in field_names}
        first_old = {}
        for _dt, name, old, _new in decoded:
            first_old.setdefault(name, old)
        state.update(first_old)

        marks = sorted({start_dt, end_dt} | {dt for dt, *_ in decoded})
        segments = []
        idx = 0
        for seg_start, seg_end in zip(marks[:-1], marks[1:]):
            # Áp mọi thay đổi xảy ra TẠI seg_start trước khi đánh giá đoạn này
            # (seg_start là mốc chung, có thể trùng nhiều thay đổi cùng lúc).
            while idx < len(decoded) and decoded[idx][0] <= seg_start:
                _dt, name, _old, new = decoded[idx]
                state[name] = new
                idx += 1
            if self._domain_matches_state(domain, state):
                segments.append((seg_start, seg_end))
        return segments

    @staticmethod
    def _is_flat_simple_domain(domain, field_names):
        """True nếu `domain` là list phẳng (AND ngầm) các leaf 3-phần tử, mỗi
        leaf trên field trong `field_names` (không qua quan hệ), operator
        thuộc {'=', '!=', 'in', 'not in'} -- đủ an toàn để đánh giá thủ công.
        """
        if not domain:
            return False
        for leaf in domain:
            if not (isinstance(leaf, (list, tuple)) and len(leaf) == 3):
                return False  # '&'/'|'/'!' hoặc dạng khác -- không hỗ trợ
            field, operator, _value = leaf
            if '.' in str(field) or field not in field_names:
                return False
            if operator not in ('=', '!=', 'in', 'not in'):
                return False
        return True

    @staticmethod
    def _domain_matches_state(domain, state):
        """Đánh giá domain phẳng (AND ngầm, đã qua `_is_flat_simple_domain`) với `state`."""
        for field, operator, value in domain:
            current = state.get(field)
            if operator == '=' and current != value:
                return False
            if operator == '!=' and current == value:
                return False
            if operator == 'in' and current not in value:
                return False
            if operator == 'not in' and current in value:
                return False
        return True

    @staticmethod
    def _decode_tracking_value(tracking, prefix, selections):
        """Giải mã `old_value`/`new_value` của `tracking` theo `ttype` của field.

        Logic: Selection được `mail.tracking.value` lưu dưới dạng LABEL hiển
        thị (xem `mail_tracking_value._create_tracking_values`), phải map
        ngược lại key qua `selections[field_name]` (dict label -> key) để so
        khớp đúng domain (vốn dùng key, không dùng label). Many2one lưu id ở
        cột `_integer`.
        """
        # Odoo 13: `tracking.field` is the field name, the type is in `field_type`
        ttype = tracking.field_type
        if ttype in ('char', 'text'):
            return tracking['%s_char' % prefix]
        if ttype == 'integer':
            return tracking['%s_integer' % prefix]
        if ttype == 'float':
            return tracking['%s_float' % prefix]
        if ttype == 'datetime':
            return tracking['%s_datetime' % prefix]
        if ttype == 'boolean':
            return bool(tracking['%s_integer' % prefix])
        if ttype == 'many2one':
            return tracking['%s_integer' % prefix] or False
        if ttype == 'selection':
            label = tracking['%s_char' % prefix]
            by_label = {v: k for k, v in selections.get(tracking.field, {}).items()}
            return by_label.get(label, label)
        return tracking['%s_char' % prefix]

    def _get_domain(self, cond):
        """Trả domain literal (dạng list) đã lưu cho một điều kiện.

        Logic: điểm mở rộng để module khác trả domain động thay vì chuỗi đã
        lưu; mặc định parse chuỗi đã lưu bằng ast.literal_eval. Rỗng hoặc `[]`
        = chưa cấu hình (trả None, không bao giờ khớp).
        Refs: REQ-INT-017
        """
        self.ensure_one()
        value = self['%s_domain' % cond]
        if not value:
            return None
        domain = ast.literal_eval(value)  # pyright: ignore[reportArgumentType]
        return domain or None

    def _get_target_hours(self, record):
        """Trả thời lượng mục tiêu (giờ) áp dụng cho record.

        Logic: điểm mở rộng để module khác tính mục tiêu theo record (ví dụ
        theo hợp đồng); mặc định là `duration` của định nghĩa. Tên hàm giữ
        nguyên "_get_target_hours" (điểm mở rộng công khai; đổi tên sẽ phá
        override của module khác), chỉ nội dung đổi sang field `duration`.
        Refs: REQ-INT-015
        """
        self.ensure_one()
        return self.duration

    def _get_start_dt(self, record, now):
        """Trả mốc bắt đầu (start_dt) của task khi attach.

        Logic: điểm mở rộng để module khác tính mốc bắt đầu phức tạp hơn một
        field; mặc định dùng field retroactive nếu bật và có giá trị, ngược
        lại dùng thời điểm hiện tại.
        Refs: REQ-INT-016, REQ-FUNC-017
        """
        self.ensure_one()
        if self.retroactive and self.start_field_id:
            value = record[self.start_field_id.name]
            if value:
                return value
        return now

    def _get_calendar(self, record):
        """Trả lịch (resource.calendar) định nghĩa muốn dùng cho record.

        Logic: điểm mở rộng nguồn lịch; mặc định theo schedule_source: 'none'
        trả recordset rỗng (24x7), 'definition' trả schedule_id, 'record' đọc
        theo schedule_path trên record bằng sudo (không phụ thuộc quyền
        người dùng, REQ-SEC-005), từng bước Many2one trống thì dừng và trả
        rỗng (Time Service sẽ áp dụng lịch dự phòng, REQ-FUNC-020).

        `calendar_tz_override` KHÔNG được áp dụng ở hàm này (điểm mở rộng
        này chỉ chọn CALENDAR GỐC) -- việc đổi tz (tìm-hoặc-tạo bản sao) nằm
        ở `sla.time._apply_tz_override()`, gọi sau khi hàm này trả về, để
        module override hàm này không cần biết gì về cơ chế tz override.
        Refs: REQ-INT-007, REQ-FUNC-019
        """
        self.ensure_one()
        calendar_model = self.env['resource.calendar']
        if self.schedule_source == 'definition':
            return self.schedule_id
        if self.schedule_source == 'record' and self.schedule_path:
            current = record.sudo()
            for step in self.schedule_path.split('.'):
                if not current:
                    return calendar_model
                current = current[step]
            return current if current._name == 'resource.calendar' else calendar_model
        return calendar_model

    def _after_transition(self, task, old_stage, new_stage, event):
        """Điểm mở rộng gọi sau mỗi chuyển trạng thái của task.

        Logic: Engine gọi hàm này ngay sau khi ghi `stage` mới, truyền trạng
        thái cũ/mới và loại event vừa ghi; mặc định không làm gì. Module
        khác override để đồng bộ ra ngoài mà không phải sửa Engine. KHÔNG
        được gọi khi đánh giá không đổi trạng thái (ví dụ re-evaluate
        idempotent hoặc attach không đổi gì).
        Refs: REQ-INT-018
        """
        return None

    def _register_sla_hook(self):
        """Gỡ patch cũ rồi đăng ký lại theo tập model đang có định nghĩa SLA.

        Logic: `_register_hook()` được framework Odoo tự gọi một lần lúc nạp
        registry cho model này (odoo/modules/loading.py STEP 9); phải gọi lại
        thủ công mỗi khi tập định nghĩa có thể đã đổi (tạo, sửa model_id hay
        active, xóa) vì framework không tự biết. Gỡ trước khi cài lại để
        không patch chồng patch khi tập model thay đổi (ví dụ định nghĩa đổi
        từ model A sang model B thì A không còn cần patch nữa); đặt
        `registry_invalidated` để worker khác nạp lại registry, giống cách
        `base_automation._update_registry` làm (AD-01). Cài đặt thật của
        `_register_hook`/`_unregister_hook` nằm ở `models/sla_hook.py` (T8,
        `_inherit = 'sla.definition'`), hàm này chỉ điều phối.
        Refs: TAD AD-01
        """
        self.env['sla.definition']._unregister_hook()
        self.env['sla.definition']._register_hook()
        self.env['sla.definition']._register_sla_action_binding()
        self.env.registry.registry_invalidated = True
