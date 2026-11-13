# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.orm.domains import Domain
from odoo.tools import SQL, format_datetime

from ..constants.message import MessageCode, get_message


class SlaTask(models.Model):
    """Một SLA đang hoặc đã chạy trên một record.

    Logic: liên kết record gốc bằng res_model/res_id (tham chiếu mềm, không
    FK) để không thêm cột vào model gốc (REQ-INST-003, AD-02). Lưu thời gian
    đã trôi (business_duration) thay vì thời gian còn lại, để giữ đúng mức vượt
    qua các lần pause/resume (AD-04, REQ-FUNC-046). Chỉ hệ thống (Engine,
    Background Processor, Maintenance) được ghi (REQ-SEC-006); không có form
    sửa/xóa cho người dùng.

    Tên field theo quyết định "đồng bộ ServiceNow" (lịch sử trao đổi dự án):
    `sla_id` (link + hậu tố `_id`, giống `task_sla.sla`), `schedule_id`
    (giống `task_sla.schedule`), `start_time`/`planned_end_time`/`end_time`
    (giống `task_sla.start_time`/`planned_end_time`/`end_time`),
    `business_duration`/`business_pause_duration` (giống
    `task_sla.business_duration`/`business_pause_duration`),
    `business_percent_used` (rõ nghĩa "theo giờ làm", phân biệt với
    `percentage`/`percent` bản giờ đồng hồ). `target_duration` KHÔNG tồn tại
    ở ServiceNow (SN không snapshot mục tiêu vào task, chỉ qua link `sla`) --
    đổi tên chỉ để không đụng field `duration` mới (giờ đồng hồ đã trôi).
    `original_breach_time`, `duration`, `pause_duration` (bản giờ đồng hồ) là
    field MỚI, thêm để khớp `task_sla.original_breach_time`/`duration`/
    `pause_duration` (xem ghi chú tại từng field).
    Refs: REQ-FUNC-006 đến 016, 018, 021, 022, 043, 044, 046, DB Design §3
    """
    _name = 'sla.task'
    _description = "SLA Task"
    _order = 'id desc'
    _rec_name = 'display_name'

    sla_id = fields.Many2one(
        'sla.definition', string="SLA", required=True,
        ondelete='cascade', index=True,
        help=('The SLA definition that created this task. Example: "Ticket '
              'Response - Priority 1".'))
    res_model = fields.Char(string="Source Record Model", required=True,
        help=('Technical name of the model of the record this task measures. '
              'Example: res.partner.'))
    res_id = fields.Many2oneReference(
        string="Source Record Id", required=True, model_field='res_model',
        help=('Id of the record this task measures; together with the model '
              'it identifies the source record. Example: 42.'))
    # Refs: REQ-SEC-003
    company_id = fields.Many2one(
        'res.company', string="Company", index=True, ondelete='restrict',
        help=('Company of the source record when the task was created; used '
              'for company access rules. Example: "Sojitz Vietnam".'))
    # Refs: REQ-FUNC-021, REQ-INT-005 -- field tự thêm (không có ở SN, xem
    # docstring class); đổi tên để không đụng field `duration` mới dưới đây.
    target_duration = fields.Float(
        string="Target Duration", required=True,
        help=('Time allowed for this task, copied from the definition when it '
              'started. Changing the definition later does not change running '
              'tasks unless Apply Current Settings is used. Example: 4.0.'))
    schedule_id = fields.Many2one(
        'resource.calendar', string="Calendar", index=True, ondelete='restrict',
        help=('Working calendar used to count time for this task, copied at '
              'start; empty means 24x7. Example: "Standard 40 hours/week".'))
    stage = fields.Selection(
        [
            ('in_progress', "In Progress"),
            ('paused', "Paused"),
            ('achieved', "Achieved"),
            ('breached', "Breached"),
            ('cancelled', "Cancelled"),
        ],
        string="Stage", required=True, default='in_progress',
        help=('Where the task is in its life. In Progress: clock running. '
              'Paused: clock stopped. Achieved: finished on time. Breached: '
              'finished or still running after the deadline. Cancelled: '
              'discarded. Example: use the Breached filter to find late '
              'tickets.'))
    start_time = fields.Datetime(string="Start", required=True,
        help=('Moment the SLA clock started (UTC); may be in the past with a '
              'retroactive start. Example: 2026-03-02 02:00:00.'))
    planned_end_time = fields.Datetime(string="Planned End",
        help=('Deadline (UTC) computed from the start, the target time and '
              'the calendar; recomputed when the task resumes from a pause. '
              'Example: start 09:00 with 4 working hours gives 13:00.'))
    # Refs: scope-add "original_breach_time" -- deadline GỐC, set đúng 1 lần
    # lúc attach (= planned_end_time lúc đó), KHÔNG bao giờ ghi lại ở
    # resume/recalculate (khác planned_end_time, vẫn bị tính lại). Mất
    # trường này sẽ không còn cách biết SLA ban đầu hứa xong lúc nào sau vài
    # lần pause/resume -- khớp `task_sla.original_breach_time` của SN.
    original_breach_time = fields.Datetime(
        string="Original Breach Time",
        help=('Deadline as first computed when the task attached, before any '
              'pause/resume recalculation. Set once and never changed '
              'afterwards, unlike Planned End. Example: a task resumed twice '
              'still shows the deadline promised at the very start here.'))
    end_time = fields.Datetime(string="End",
        help=('Moment the task finished or was cancelled; empty while it is '
              'still active. Example: 2026-03-02 05:30:00.'))
    # Refs: REQ-FUNC-043, REQ-FUNC-046
    business_duration = fields.Float(
        string="Business Duration", default=0,
        help=('Working hours consumed so far, accumulated across pauses; may '
              'exceed the target when late. It is updated when the task '
              'pauses, resumes or completes. Example: 4.4 hours on a 4-hour '
              'target.'))
    running_since = fields.Datetime(string="Running Since",
        help=('Start of the current running period (UTC); only set while the '
              'task is In Progress. Used to add the time since this moment to '
              'the elapsed time. Example: 2026-03-02 03:00:00.'))
    pause_time = fields.Datetime(string="Paused Since",
        help=('Moment the task was paused (UTC); only set while it is Paused. '
              'Example: 2026-03-02 03:00:00.'))
    business_pause_duration = fields.Float(
        string="Total Paused Hours (Business)", default=0,
        help=('Total WORKING hours this task has spent paused; for '
              'information and reporting only. Example: 2.5.'))
    # Refs: scope-add "duration/pause_duration bản giờ đồng hồ" -- khớp
    # `task_sla.duration`/`pause_duration` của SN (bản giờ đồng hồ thật,
    # KHÔNG trừ ngoài giờ làm/ngày nghỉ, khác với business_duration/
    # business_pause_duration ở trên). Khi schedule_id trống (24x7), giá trị
    # 2 cặp field trùng nhau; chỉ khác khi task CÓ dùng calendar.
    duration = fields.Float(
        string="Duration", default=0,
        help=('Total real (wall-clock) hours elapsed since Start, NOT '
              'excluding non-working time/holidays -- unlike Business '
              'Duration. Equal to Business Duration when this task runs '
              '24x7 (no calendar). Example: a task paused for a full '
              'weekend shows +48h here but +0h on Business Duration.'))
    pause_duration = fields.Float(
        string="Total Paused Hours (Clock)", default=0,
        help=('Total real (wall-clock) hours this task has spent paused, '
              'NOT excluding non-working time -- unlike Total Paused Hours '
              '(Business). Equal to it when this task runs 24x7 (no '
              'calendar). For information and reporting only.'))
    # Refs: REQ-FUNC-046
    has_breached = fields.Boolean(
        string="Breached", default=False,
        help=('Set when the deadline passes while the task is active and '
              'never cleared afterwards, even after pauses. Example: a task '
              'paused after being late is still marked breached.'))
    # Refs: REQ-PERF-003, AD-05
    next_due_at = fields.Datetime(
        string="Next Background Processing Due",
        help=('Earliest moment (UTC) the background process must look at this '
              'task: the deadline or the next escalation threshold. Empty '
              'when the task is not running. Example: 2026-03-02 05:00:00.'))
    done_escalation_ids = fields.Many2many(
        'sla.escalation', relation='sla_task_escalation_done_rel',
        column1='task_id', column2='escalation_id',
        string="Escalations Done",
        help=('Escalations already processed for this task, so each one runs '
              'only once. Example: the 75% and 100% rules after both have '
              'fired.'))
    event_ids = fields.One2many('sla.event', 'task_id', string="Event Log",
        help=('History of what happened to this task: attach, pause, resume, '
              'breach, escalations and errors, each with its time. Example: '
              'attach, pause, resume, complete.'))
    # Refs: plan-improvement-sla-01-review §6.12 -- cùng bảng sla.event, chỉ lọc loại event.
    escalation_event_ids = fields.One2many(
        'sla.event', 'task_id', string="Escalation History", readonly=True,
        domain=[('event', 'in', ('escalate', 'escalate_failed'))],
        help=('Times this task ran an escalation, including failed attempts, '
              'newest first. It does not say which rule ran; see Escalations '
              'Done for that. Example: one "Escalated" line at 75% and one '
              '"Escalation failed" line when the email could not be sent.'))
    # Refs: REQ-INT-023
    business_percent_used = fields.Integer(
        string="% Duration Used (Business)", compute='_compute_percent_used',
        help=('Share of the target time already consumed, counted in WORKING '
              'hours (elapsed divided by target, rounded down); can exceed '
              '100. Example: 110 means 10% over the target.'))
    # Bản "live" của business_duration/duration: giá trị đã chốt cộng đoạn đang
    # chạy tới lúc đọc. Chỉ để HIỂN THỊ (không lưu nên không sort/filter/group
    # được); báo cáo vẫn dùng hai cột lưu, vốn chỉ được chốt lúc pause/complete.
    business_duration_live = fields.Float(
        string="Business Duration (live)", compute='_compute_duration_live',
        help=('Working hours consumed up to now: Business Duration plus the '
              'period currently running. Computed when the view is loaded, so '
              'it cannot be sorted, filtered or grouped; reports use Business '
              'Duration. Example: 2.5 on a running task whose stored Business '
              'Duration is still 1.0.'))
    duration_live = fields.Float(
        string="Duration (live)", compute='_compute_duration_live',
        help=('Real (wall-clock) hours elapsed up to now: Duration plus the '
              'period currently running. Computed when the view is loaded, so '
              'it cannot be sorted, filtered or grouped; reports use Duration. '
              'Example: 50.0 on a task running over a weekend.'))
    display_name = fields.Char(compute='_compute_display_name',
        help=('Readable name of the task made of the definition name and the '
              'source record. Example: "Ticket Response - res.partner#42".'))
    # Refs: REQ-INT-012
    is_due_soon = fields.Boolean(
        string="Due Soon", compute='_compute_is_due_soon',
        search='_search_is_due_soon',
        help="in_progress, not breached, planned_end_time within the next X "
             "hours; X is read from the dwo_sla_core.due_soon_hours "
             "setting.")

    # Refs: REQ-FUNC-036, REQ-FUNC-062
    achieved_rate = fields.Float(
        string="Achieved Rate", compute='_compute_report_measures', store=True,
        aggregator='avg', digits=(16, 4),
        help=('Report measure: 1 when the task ended on time, 0 when it ended '
              'breached, empty for tasks still running or cancelled. Its average '
              'over a group is the share of tasks achieved, e.g. 0.8 means 80%; '
              'a group without ended tasks has no value.'))
    breaching_count = fields.Integer(
        string="Currently Breaching", compute='_compute_report_measures', store=True,
        aggregator='sum',
        help=('Report measure: 1 while the task is running or paused and already past '
              'its deadline, otherwise 0. Its sum over a group is the number of SLAs '
              'currently in breach (ended breached tasks are not counted).'))

    # Refs: task 006 C1 (báo cáo) -- field lưu để nhóm/lọc/pivot; tính lại tự động
    # khi Engine đổi stage / has_breached / business_duration (mọi chỗ ghi stage
    # đều đi qua task.write nên các @api.depends bên dưới đủ, không cần hook riêng).
    outcome = fields.Selection(
        [
            ('on_time', "On Time"),
            ('late', "Late"),
            ('breached_open', "Breached (Open)"),
            ('running', "Running"),
            ('paused', "Paused"),
            ('cancelled', "Cancelled"),
        ],
        string="Outcome", compute='_compute_outcome', store=True, index=True,
        help=('One-word result for reports. On Time: achieved within the '
              'target. Late: finished after the deadline had passed. Breached '
              '(Open): still running or paused and already past the deadline. '
              'Running / Paused: active and not yet breached. Cancelled: '
              'discarded. Example: group by Outcome to see the share of late '
              'tasks.'))
    final_percent_used = fields.Float(
        string="% Used (Final)", compute='_compute_usage', store=True,
        aggregator='avg', digits=(16, 2),
        help=('Share of the target time consumed in working hours, as of the '
              'last stored value (at completion for finished tasks; for active '
              'tasks the value saved at the last pause or breach). Never below '
              '100 once the task has breached. The average over a group counts '
              'finished tasks only. Example: 112.5 means 12.5% over target.'))
    usage_bucket = fields.Selection(
        [
            ('0_50', "0-50%"),
            ('50_75', "50-75%"),
            ('75_100', "75-100%"),
            ('100_150', "100-150%"),
            ('150_plus', ">150%"),
        ],
        string="Usage Range", compute='_compute_usage_bucket', store=True,
        help=('Range of % Used (Final): below 50, 50 to below 75, 75 to below '
              '100, 100 to 150 included, above 150. Used to chart how close to '
              'the deadline tasks are handled. Example: a task that used 100% '
              'of its target is in 100-150%.'))
    overdue_duration = fields.Float(
        string="Overdue Hours", compute='_compute_usage', store=True,
        aggregator='avg',
        help=('Working hours beyond the target for a task that has breached; '
              '0 when it has not. For active tasks this is the last stored '
              'value. The average over a group counts finished tasks only. '
              'Example: 1.5 for a task that used 5.5 hours on a 4-hour '
              'target.'))
    source_name = fields.Char(
        string="Source Name", compute='_compute_source_name', store=True,
        groups='dwo_sla_core.group_sla_manager',
        help=('Display name of the source record when the task was attached, '
              'kept so lists and pivots stay readable. It is not renamed '
              'automatically when the record is renamed; Apply Current '
              'Settings refreshes it. Example: "Azure Interior".'))
    sla_type = fields.Selection(
        related='sla_id.type', string="SLA Type", store=True, index=True,
        help=('Copy of the definition Type (SLA or OLA) kept on the task so '
              'reports can group by it. Example: OLA.'))
    sla_target = fields.Selection(
        related='sla_id.target', string="SLA Target", store=True, index=True,
        help=('Copy of the definition Target (Response or Resolution) kept on '
              'the task so reports can group by it. Example: Response.'))

    _target_hours_check = models.Constraint(
        'CHECK(target_duration >= 0)', "Target duration cannot be negative.")
    _business_elapsed_check = models.Constraint(
        'CHECK(business_duration >= 0)', "Elapsed time cannot be negative.")
    _pause_duration_check = models.Constraint(
        'CHECK(business_pause_duration >= 0)', "Total paused hours (business) "
        "cannot be negative.")
    _duration_check = models.Constraint(
        'CHECK(duration >= 0)', "Duration (clock) cannot be negative.")
    _pause_duration_clock_check = models.Constraint(
        'CHECK(pause_duration >= 0)', "Total paused hours (clock) cannot be "
        "negative.")
    _stage_check = models.Constraint(
        "CHECK(stage IN ('in_progress','paused','achieved','breached','cancelled'))",
        "Invalid task stage.")
    _end_dt_check = models.Constraint(
        "CHECK((stage IN ('achieved','breached','cancelled')) = (end_time IS NOT NULL))",
        "end_time only has a value once the task has ended.")
    _paused_since_check = models.Constraint(
        "CHECK((stage = 'paused') = (pause_time IS NOT NULL))",
        "pause_time only has a value when stage = paused.")
    _next_due_at_check = models.Constraint(
        "CHECK(next_due_at IS NULL OR stage = 'in_progress')",
        "Only a running task can have a next background-processing due "
        "date.")
    _planned_end_check = models.Constraint(
        "CHECK(planned_end_time IS NULL OR planned_end_time >= start_time)",
        "Planned end cannot be before the start date.")
    _breached_check = models.Constraint(
        "CHECK(stage <> 'breached' OR has_breached)",
        "A breached task must have the breach flag set.")
    _achieved_check = models.Constraint(
        "CHECK(stage <> 'achieved' OR NOT has_breached)",
        "An achieved task cannot have the breach flag set.")
    _running_since_check = models.Constraint(
        "CHECK((stage = 'in_progress') = (running_since IS NOT NULL))",
        "running_since only has a value when stage = in_progress.")
    _res_idx = models.Index("(res_model, res_id)")
    _due_idx = models.Index("(next_due_at) WHERE stage = 'in_progress'")
    _definition_end_idx = models.Index(
        "(sla_id, end_time) WHERE stage IN ('achieved','breached')")
    _breached_active_idx = models.Index(
        "(has_breached) WHERE stage IN ('in_progress','paused')")
    # Một task hoạt động duy nhất cho mỗi (định nghĩa, record), kể cả hai giao
    # dịch đồng thời cùng cố gắng gắn (REQ-FUNC-014, AD-08); vi phạm là lỗi cô
    # lập được Engine bắt trong savepoint (AD-07).
    _one_active_uniq = models.UniqueIndex(
        "(sla_id, res_model, res_id) WHERE stage IN ('in_progress','paused')",
        "This record already has an active SLA for this definition.")

    def _read_group_select(self, aggregate_spec, query):
        """Trung bình `achieved_rate` chỉ tính task đã kết thúc achieved/breached.

        Logic: cột lưu 0.0 cho task cancelled/đang chạy (Float không có giá trị rỗng),
        nên phải lọc theo stage; nhóm không có task kết thúc cho kết quả rỗng
        ("không xác định") thay vì 0% (REQ-FUNC-036).
        Refs: REQ-FUNC-036
        """
        if aggregate_spec == 'achieved_rate:avg':
            return SQL(
                "AVG(%s) FILTER (WHERE %s IN ('achieved', 'breached'))",
                self._field_to_sql(self._table, 'achieved_rate', query),
                self._field_to_sql(self._table, 'stage', query))
        if aggregate_spec in ('final_percent_used:avg', 'overdue_duration:avg'):
            # Chỉ task đã kết thúc (achieved/breached); task đang chạy giữ giá trị cũ,
            # cancelled không có ý nghĩa, nên không được kéo trung bình.
            field_name = aggregate_spec.split(':')[0]
            return SQL(
                "AVG(%s) FILTER (WHERE %s IN ('achieved', 'breached'))",
                self._field_to_sql(self._table, field_name, query),
                self._field_to_sql(self._table, 'stage', query))
        return super()._read_group_select(aggregate_spec, query)

    def init(self):
        """Xóa index đầy đủ `next_due_at` còn sót trên DB đã cài từ bản cũ.

        Logic: bản cũ khai báo `index=True` tạo index đầy đủ, trùng việc với
        `sla_task_due_idx` (từng phần) nhưng phải cập nhật mỗi lần `next_due_at`
        đổi; Odoo không tự xóa index khi bỏ `index=True`.
        Refs: REQ-PERF-003, 030 §6
        """
        super().init()
        self.env.cr.execute("DROP INDEX IF EXISTS sla_task__next_due_at_index")

    @api.depends('stage', 'has_breached')
    def _compute_report_measures(self):
        """Tính hai chỉ số báo cáo: tỷ lệ đạt và số đang vi phạm.

        Logic: tỷ lệ đạt chỉ xét task đã kết thúc không phải cancelled (achieved = 1,
        breached = 0; còn lại rỗng để trung bình bỏ qua, nhóm không có task kết thúc
        thì không xác định); đang vi phạm là task in_progress/paused đã bật dấu vi phạm.
        Refs: REQ-FUNC-036, REQ-FUNC-062
        """
        for task in self:
            task.achieved_rate = 1.0 if task.stage == 'achieved' else 0.0
            task.breaching_count = int(
                task.stage in ('in_progress', 'paused') and task.has_breached)

    @api.depends('stage', 'has_breached')
    def _compute_outcome(self):
        """Gộp stage và dấu vi phạm thành một kết quả cho báo cáo.

        Logic: dấu vi phạm của task còn mở (in_progress/paused) thắng stage để
        "đang vi phạm" khớp `breaching_count`; achieved -> on_time, breached
        (đã kết thúc sau hạn) -> late.
        Refs: task 006 C1
        """
        for task in self:
            stage = task.stage
            if stage == 'achieved':
                task.outcome = 'on_time'
            elif stage == 'breached':
                task.outcome = 'late'
            elif stage == 'cancelled':
                task.outcome = 'cancelled'
            elif task.has_breached:
                task.outcome = 'breached_open'
            else:
                task.outcome = 'paused' if stage == 'paused' else 'running'

    @api.depends('business_duration', 'target_duration', 'has_breached')
    def _compute_usage(self):
        """% thời hạn đã dùng và số giờ trễ, từ `business_duration` đã lưu.

        Logic: cùng quy ước `_compute_percent_used` (target 0 -> 100% nếu có
        thời gian trôi) nhưng KHÔNG làm tròn và không cộng đoạn đang chạy (field
        lưu). Task đã vi phạm không bao giờ dưới 100% (giá trị lưu có thể cũ
        trước khi pause/complete chốt lại). Giờ trễ = phần vượt mục tiêu, 0 nếu
        chưa vi phạm.
        Refs: task 006 C1
        """
        for task in self:
            elapsed, target = task.business_duration, task.target_duration
            if target:
                percent = elapsed / target * 100.0
            else:
                percent = 100.0 if elapsed else 0.0
            if task.has_breached:
                percent = max(percent, 100.0)
                task.overdue_duration = max(elapsed - target, 0.0)
            else:
                task.overdue_duration = 0.0
            task.final_percent_used = percent

    @api.depends('final_percent_used')
    def _compute_usage_bucket(self):
        """Xếp `final_percent_used` vào nhóm: <50, <75, <100, <=150, >150."""
        for task in self:
            percent = task.final_percent_used
            if percent < 50:
                task.usage_bucket = '0_50'
            elif percent < 75:
                task.usage_bucket = '50_75'
            elif percent < 100:
                task.usage_bucket = '75_100'
            elif percent <= 150:
                task.usage_bucket = '100_150'
            else:
                task.usage_bucket = '150_plus'

    @api.depends('res_model', 'res_id')
    def _compute_source_name(self):
        """Tên hiển thị của record nguồn, đọc theo lô cho mỗi model.

        Logic: sudo vì người đọc báo cáo có thể không có quyền đọc record nguồn
        (đánh đổi đã ghi ở CHANGELOG); model đã gỡ hoặc record đã xoá thì dùng
        "model#id". Lỗi khi đọc tên không được làm hỏng việc tạo task.
        Refs: task 006 C1
        """
        by_model = {}
        for task in self:
            by_model.setdefault(task.res_model, set()).add(task.res_id)
        names = {}
        for model, ids in by_model.items():
            if model in self.env:
                try:
                    with self.env.cr.savepoint():
                        for rec in self.env[model].sudo().browse(sorted(ids)).exists():
                            names[(model, rec.id)] = rec.display_name
                except Exception:  # noqa: BLE001 -- model lạ, không được chặn engine
                    pass
        for task in self:
            task.source_name = (names.get((task.res_model, task.res_id))
                                or "%s#%s" % (task.res_model, task.res_id))

    def _refresh_source_names(self):
        """Tính lại `source_name` ngay (sau khi record nguồn đổi tên)."""
        self.sudo()._compute_source_name()

    @api.depends('business_duration', 'target_duration', 'stage', 'running_since',
                 'schedule_id')
    def _compute_percent_used(self):
        """Tính % thời lượng mục tiêu đã dùng (theo giờ làm), làm tròn xuống, có thể vượt 100%.

        Logic: task `in_progress` cộng thêm đoạn đang chạy từ `running_since`
        tới thời điểm xem (field không lưu nên mỗi lần đọc view được tính lại);
        các stage khác chỉ dùng `business_duration` đã chốt. target_duration = 0
        thì coi như đã dùng hết ngay (100%) để tránh chia cho 0.
        Refs: REQ-INT-023
        """
        extra = self._running_business_hours(fields.Datetime.now())
        for task in self:
            elapsed = task.business_duration + extra.get(task.id, 0.0)
            if task.target_duration:
                task.business_percent_used = int((elapsed / task.target_duration) * 100)
            else:
                task.business_percent_used = 100 if elapsed else 0

    def _running_business_hours(self, now):
        """Giờ làm của đoạn đang chạy (`running_since` tới `now`) theo id task.

        Logic: chỉ task `in_progress` có đoạn đang chạy; gom theo lịch để chỉ
        đọc lịch/ngày nghỉ một lần mỗi lịch. Task khác không có trong kết quả.
        Refs: REQ-FUNC-043, REQ-INT-023
        """
        running = self.filtered(lambda t: t.stage == 'in_progress' and t.running_since)
        extra = {}
        for calendar in list(running.schedule_id) + [self.env['resource.calendar']]:
            group = running.filtered(lambda t, c=calendar: t.schedule_id == c)
            hours = self.env['sla.time'].settle_batch(
                calendar, [t.running_since for t in group], now)
            extra.update(zip(group.ids, hours))
        return extra

    @api.depends('business_duration', 'duration', 'stage', 'running_since', 'schedule_id')
    def _compute_duration_live(self):
        """Thời gian đã trôi tính tới lúc đọc: giá trị đã chốt + đoạn đang chạy.

        Logic: hai cột lưu chỉ được cộng dồn khi task pause/complete nên đứng
        yên trong lúc `in_progress`; ở đây cộng thêm đoạn từ `running_since`
        tới hiện tại (giờ làm qua lịch, và giờ đồng hồ). Task không chạy thì
        bằng đúng giá trị đã lưu.
        Refs: REQ-FUNC-043
        """
        now = fields.Datetime.now()
        extra = self._running_business_hours(now)
        for task in self:
            task.business_duration_live = task.business_duration + extra.get(task.id, 0.0)
            clock = 0.0
            if task.stage == 'in_progress' and task.running_since and now > task.running_since:
                clock = (now - task.running_since).total_seconds() / 3600.0
            task.duration_live = task.duration + clock

    @api.depends('res_model', 'res_id', 'sla_id.name')
    def _compute_display_name(self):
        """Tên hiển thị gồm định nghĩa và record gốc, tránh lộ giá trị field."""
        for task in self:
            task.display_name = "%s - %s#%s" % (
                task.sla_id.name, task.res_model, task.res_id)

    def _due_soon_hours_global(self):
        """Đọc ngưỡng X giờ toàn hệ thống của "Sắp đến hạn" từ cấu hình (REQ-INT-012)."""
        return float(self.env['ir.config_parameter'].sudo().get_param(
            'dwo_sla_core.due_soon_hours', 4))

    @api.depends('stage', 'has_breached', 'planned_end_time', 'sla_id.due_soon_hours')
    def _compute_is_due_soon(self):
        """Tính "Sắp đến hạn" không lưu trữ; ngưỡng theo definition, trống thì theo Settings.

        Refs: REQ-INT-012, plan-improvement-sla-01-review §6.10
        """
        now = fields.Datetime.now()
        default_hours = self._due_soon_hours_global()
        for task in self:
            hours = task.sla_id.due_soon_hours or default_hours
            task.is_due_soon = (
                task.stage == 'in_progress' and not task.has_breached
                and bool(task.planned_end_time)
                and task.planned_end_time <= now + timedelta(hours=hours))

    def _search_is_due_soon(self, operator, value):
        """Domain tương đương cho bộ lọc "Sắp đến hạn" (REQ-INT-012 AC1/AC2).

        Logic: mỗi giá trị giờ khác nhau trên definition là một nhánh với mốc
        thời gian riêng; definition để trống dùng ngưỡng toàn hệ thống. Phần
        phủ định lấy bằng `~` của domain dương, không phải tải id task.
        Refs: plan-improvement-sla-01-review §6.10
        """
        # Odoo có thể chuẩn hóa ('=', True) thành ('in', [True]); xử lý cả hai dạng để
        # không đảo ngược kết quả bộ lọc (REQ-INT-012).
        if operator in ('in', 'not in'):
            wanted = {bool(v) for v in value}
            if len(wanted) != 1:
                return [(1, '=', 1)] if (operator == 'in') == (len(wanted) > 1) else [(0, '=', 1)]
            positive = wanted.pop() == (operator == 'in')
        else:
            positive = (operator == '=' and bool(value)) or (operator == '!=' and not value)
        now = fields.Datetime.now()
        default_hours = self._due_soon_hours_global()
        groups = self.env['sla.definition'].sudo().with_context(active_test=False)._read_group(
            [], ['due_soon_hours'], ['id:array_agg'])
        by_hours = {}
        for hours, ids in groups:
            by_hours.setdefault(hours or default_hours, []).extend(ids)
        branches = [
            Domain('sla_id', 'in', ids)
            & Domain('planned_end_time', '<=', now + timedelta(hours=hours))
            for hours, ids in by_hours.items()]
        domain = (Domain('stage', '=', 'in_progress') & Domain('has_breached', '=', False)
                  & Domain.OR(branches))
        return domain if positive else ~domain

    @api.model
    def get_record_sla_summary(self, res_model, res_id):
        """Tóm tắt SLA của một record cho chip trạng thái trên form.

        Logic: không `sudo()` (nhóm SLA đã có quyền đọc và rule theo công ty).
        Có task đang chạy/tạm dừng thì `state` là của task "gấp nhất" theo thứ
        tự `breached` > `due_soon` > `paused` > `running`, đồng hạng thì lấy
        task có `business_percent_used` cao nhất; không có thì `met` (có task
        đúng hạn), `missed` (có task trễ) hoặc `None` (không có gì để hiện).
        `percent` luôn <= 100: client không bao giờ phải hiện % vượt hạn.
        Refs: plan-improvement-sla-01-review §6.9, REQ-INT-024
        """
        if not res_model or not res_id:
            return {'state': None}
        key = [('res_model', '=', res_model), ('res_id', '=', res_id)]
        tasks = self.search(key + [('stage', 'in', ('in_progress', 'paused'))])
        if not tasks:
            counts = dict(self._read_group(
                key + [('stage', 'in', ('achieved', 'breached'))], ['stage'], ['__count']))
            late, ok = counts.get('breached', 0), counts.get('achieved', 0)
            state = 'missed' if late else 'met' if ok else None
            return {'state': state, 'count': late + ok, 'late_count': late}

        rank = {'breached': 3, 'due_soon': 2, 'paused': 1, 'running': 0}

        def task_state(task):
            if task.has_breached:
                return 'breached'
            if task.is_due_soon:
                return 'due_soon'
            return 'paused' if task.stage == 'paused' else 'running'

        lines = [{
            'name': task.sla_id.name,
            'state': task_state(task),
            'percent': min(task.business_percent_used, 100),
            'planned_end_time': fields.Datetime.to_string(task.planned_end_time) or False,
        } for task in tasks]
        main = max(lines, key=lambda line: (rank[line['state']], line['percent']))
        return {
            'state': main['state'],
            'count': len(lines),
            'late_count': sum(1 for line in lines if line['state'] == 'breached'),
            'percent': main['percent'],
            'planned_end_time': main['planned_end_time'],
            'lines': lines,
        }

    def action_open_source_record(self):
        """Mở form của record gốc; không sudo nên thiếu quyền thì Odoo tự báo lỗi.

        Logic: record gốc là tham chiếu mềm (không FK) nên có thể đã bị xoá,
        hoặc model đã gỡ; khi đó báo thân thiện thay vì lỗi kỹ thuật.
        Refs: plan-improvement-sla-01-review §6.13
        """
        self.ensure_one()
        if (self.res_model not in self.env
                or not self.env[self.res_model].browse(self.res_id).exists()):
            raise UserError(get_message(MessageCode.VAL_SOURCE_RECORD_MISSING))
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_recalculate(self):
        """"Apply Current Settings": áp cấu hình hiện hành của định nghĩa/record lên task.

        Logic: chỉ SLA Manager được gọi (AC4, kiểm tra cứng chứ không chỉ ẩn
        nút); chỉ tác dụng trên task `in_progress`/`paused`, task khác hoặc
        record gốc đã mất thì bỏ qua và được đếm vào "skipped" (AC3); giữ
        nguyên `business_duration` đã trôi, lấy lại `target_duration` và lịch
        hiện hành (REQ-FUNC-021, 052); với task `in_progress` chưa vi phạm thì
        xếp lại `planned_end_time` = hiện tại + phần giờ còn lại theo lịch mới
        (AC1, AC2); task đã vi phạm giữ nguyên `planned_end_time` (nhất quán
        với REQ-FUNC-044 AC2); task `paused` chỉ cập nhật `target_duration`/lịch,
        `planned_end_time` được xếp lại khi resume (theo đúng lời văn
        REQ-INT-005, không tính lại ở đây). KHÔNG đụng `original_breach_time`
        (deadline gốc, bất biến sau attach). Task nào thực sự đổi (mục tiêu,
        lịch hoặc deadline) được ghi một event `recalculate` (người bấm, cũ →
        mới); mọi event tạo bằng MỘT lệnh create sau vòng lặp. Trả thông báo
        "N updated, M skipped" rồi tải lại view.
        Refs: REQ-INT-005, plan-improvement-sla-01-review §6.17
        """
        if not self.env.user.has_group('dwo_sla_core.group_sla_manager'):
            raise AccessError(get_message(
                MessageCode.ACC_RECALCULATE_SLA_MANAGER_ONLY))
        now = fields.Datetime.now()
        time_srv = self.env['sla.time']
        user_name = self.env.user.name
        events = []
        updated = skipped = 0
        for task in self.sudo():
            record = self.env[task.res_model].browse(task.res_id).exists() \
                if task.stage in ('in_progress', 'paused') else None
            if not record:
                skipped += 1
                continue
            old = (task.target_duration, task.schedule_id, task.planned_end_time)
            target_duration = task.sla_id._get_target_hours(record)
            calendar, _note = time_srv.resolve_calendar(task.sla_id, record)
            vals = {
                'target_duration': target_duration,
                'schedule_id': calendar.id if calendar else False,
            }
            if task.stage == 'in_progress' and not task.has_breached:
                remaining = max(target_duration - task.business_duration, 0.0)
                planned_end_time = time_srv.plan(calendar, now, remaining)
                if planned_end_time is not False:
                    vals['planned_end_time'] = planned_end_time
            task.write(vals)
            if task.stage == 'in_progress':
                task.next_due_at = time_srv.next_due_at(task, now)
            updated += 1
            new = (task.target_duration, task.schedule_id, task.planned_end_time)
            if new != old:
                events.append({
                    'task_id': task.id,
                    'event': 'recalculate',
                    'event_dt': now,
                    'note': get_message(
                        MessageCode.NOTE_RECALCULATE_APPLIED, user_name,
                        "%.2f h" % old[0], "%.2f h" % new[0],
                        old[1].display_name or "-", new[1].display_name or "-",
                        format_datetime(self.env, old[2]) if old[2] else "-",
                        format_datetime(self.env, new[2]) if new[2] else "-"),
                    'definition_id': task.sla_id.id,
                    'company_id': task.company_id.id,
                })
        self._refresh_source_names()
        if events:
            self.env['sla.event'].sudo().create(events)
        return self._result_notification(
            MessageCode.INF_RECALCULATE_RESULT_TITLE,
            get_message(MessageCode.INF_RECALCULATE_RESULT_BODY, updated, skipped))

    def action_reevaluate(self):
        """"Re-check Conditions": chạy lại 6 điều kiện của ĐÚNG định nghĩa của từng task (REQ-INT-020).

        Logic: chỉ SLA Manager được gọi (AC2); dùng thời điểm hiện tại,
        không coi field nào là "vừa đổi" nên không kích hoạt reset theo
        field (REQ-FUNC-032, REQ-FUNC-050 AC3); task đã kết thúc không đổi
        vì `evaluate()` tự tôn trọng bất biến REQ-FUNC-007 (AC3); gom task theo
        `(res_model, sla_id)` để gọi `evaluate()` theo lô (AD-03) và chỉ với
        định nghĩa đó, nên task của định nghĩa khác trên cùng record không bị
        chạm. Mỗi task được ghi một event `reevaluate` (người bấm, stage cũ →
        mới hoặc "không đổi") bằng MỘT lệnh create. Nếu điều kiện Reset khớp,
        task hiện tại đóng và task mới được tạo; task mới không nằm trong số đếm.
        Refs: REQ-INT-020, REQ-FUNC-032, plan-improvement-sla-01-review §6.18
        """
        if not self.env.user.has_group('dwo_sla_core.group_sla_manager'):
            raise AccessError(get_message(
                MessageCode.ACC_REEVALUATE_SLA_MANAGER_ONLY))
        now = fields.Datetime.now()
        tasks = self.sudo()
        before = {task.id: task.stage for task in tasks}
        groups = {}
        for task in tasks:
            groups.setdefault((task.res_model, task.sla_id.id), []).append(task.res_id)
        for (res_model, sla_id), res_ids in groups.items():
            records = self.env[res_model].sudo().browse(res_ids).exists()
            self.env['sla.engine'].evaluate(
                records, now=now, changed=set(),
                definitions=self.env['sla.definition'].sudo().browse(sla_id))
        tasks.invalidate_recordset(['stage'])
        labels = dict(self._fields['stage']._description_selection(self.env))
        user_name = self.env.user.name
        events = []
        changed = 0
        for task in tasks:
            old_stage, new_stage = before[task.id], task.stage
            if old_stage != new_stage:
                changed += 1
                note = get_message(
                    MessageCode.NOTE_REEVALUATE_CHANGED, user_name,
                    labels[old_stage], labels[new_stage])
            else:
                note = get_message(
                    MessageCode.NOTE_REEVALUATE_UNCHANGED, user_name,
                    labels[old_stage])
            events.append({
                'task_id': task.id,
                'event': 'reevaluate',
                'event_dt': now,
                'note': note,
                'definition_id': task.sla_id.id,
                'company_id': task.company_id.id,
            })
        if events:
            self.env['sla.event'].sudo().create(events)
        return self._result_notification(
            MessageCode.INF_REEVALUATE_RESULT_TITLE,
            get_message(MessageCode.INF_REEVALUATE_RESULT_BODY, len(tasks), changed))

    @staticmethod
    def _result_notification(title_code, message):
        """Thông báo kết quả của nút hàng loạt, rồi tải lại view hiện tại.

        Refs: plan-improvement-sla-01-review §6.17, §6.18
        """
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': get_message(title_code),
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.client', 'tag': 'soft_reload'},
            },
        }

    def _mark_passed_escalations_done(self, escalations=None):
        """Đánh dấu mốc escalation đã vượt phần trăm của task là đã xử lý, không bắn bù.

        Logic: với mỗi task đang hoạt động (`in_progress`/`paused`), mốc nào
        có `percent` không cao hơn phần trăm hiện tại của task được thêm vào
        `done_escalation_ids` NGAY (không chạy action, không ghi event) để xử
        lý nền không bao giờ bắn bù (REQ-FUNC-053 AC1). `escalations` None =
        mọi mốc của định nghĩa của task; truyền recordset thì chỉ xét các mốc
        đó (đúng định nghĩa của từng task). Sau đó task `in_progress` được tính
        lại `next_due_at` vì tập mốc chờ đã đổi (AC2, 024). Dùng bởi
        `sla.escalation.create` và backfill của `sla.apply.job`.
        Refs: REQ-FUNC-053, plan-improvement-sla-01-review §2.3, §6.16
        """
        now = fields.Datetime.now()
        processor = self.env['sla.processor']
        time_srv = self.env['sla.time']
        for task in self.sudo().filtered(lambda t: t.stage in ('in_progress', 'paused')):
            candidates = task.sla_id.escalation_ids if escalations is None \
                else escalations.filtered(lambda e: e.definition_id == task.sla_id)
            if task.stage == 'in_progress':
                current_percent = processor._current_percent(task, now)
            elif task.target_duration > 0:
                current_percent = task.business_duration / task.target_duration * 100.0
            else:
                current_percent = 100.0
            passed = candidates.filtered(lambda e: current_percent >= e.percent)
            if passed:
                task.write({'done_escalation_ids': [(4, e.id) for e in passed]})
            if task.stage == 'in_progress':
                # Mốc mới có thể đến hạn sớm hơn mốc đang chờ: tính lại để
                # xử lý nền không bắn muộn (REQ-FUNC-053 AC2, 024).
                task.next_due_at = time_srv.next_due_at(task, now)

    @api.autovacuum
    def _gc_orphan_tasks(self):
        """Dọn task mồ côi khi record gốc đã bị xóa (gọi bởi autovacuum hằng ngày).

        Logic: `res_model`/`res_id` là tham chiếu mềm, không có khóa ngoại
        (AD-02), nên record gốc bị xóa không tự động dọn task; duyệt theo
        từng `res_model` có mặt trong bảng, kiểm tra record nào còn tồn tại
        bằng `exists()`, rồi xóa các task còn lại — event/lượt thử lại tự
        xóa theo (`ondelete='cascade'`). Không cần đồng bộ với thao tác xóa
        record gốc, miễn trong vòng 24 giờ (REQ-FUNC-034, AD-09).
        Refs: REQ-FUNC-034, AD-09
        """
        SlaTask = self.sudo()
        for (res_model,) in SlaTask._read_group([], ['res_model']):
            if not res_model or res_model not in self.env:
                continue
            tasks = SlaTask.search([('res_model', '=', res_model)])
            existing_ids = set(
                self.env[res_model].sudo().browse(tasks.mapped('res_id')).exists().ids)
            orphans = tasks.filtered(lambda t: t.res_id not in existing_ids)
            orphans.unlink()
        # Event lỗi không gắn task còn tham chiếu record đã bị xóa cũng được dọn.
        events = self.env['sla.event'].sudo().search([
            ('task_id', '=', False), ('res_id', '!=', 0), ('res_model', '!=', False)])
        for res_model in set(events.mapped('res_model')):
            if res_model not in self.env:
                continue
            of_model = events.filtered(lambda e, m=res_model: e.res_model == m)
            existing_ids = set(self.env[res_model].sudo().browse(of_model.mapped('res_id')).exists().ids)
            of_model.filtered(lambda e: e.res_id not in existing_ids).unlink()
