# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.tools import SQL

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
              'tasks unless Recalculate is used. Example: 4.0.'))
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
    # Refs: REQ-INT-023
    business_percent_used = fields.Integer(
        string="% Duration Used (Business)", compute='_compute_percent_used',
        help=('Share of the target time already consumed, counted in WORKING '
              'hours (elapsed divided by target, rounded down); can exceed '
              '100. Example: 110 means 10% over the target.'))
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
        now = fields.Datetime.now()
        # Gom task đang chạy theo lịch để chỉ đọc lịch/ngày nghỉ một lần mỗi lịch
        running = self.filtered(lambda t: t.stage == 'in_progress' and t.running_since)
        extra = {}
        for calendar in list(running.schedule_id) + [self.env['resource.calendar']]:
            group = running.filtered(lambda t, c=calendar: t.schedule_id == c)
            hours = self.env['sla.time'].settle_batch(
                calendar, [t.running_since for t in group], now)
            extra.update(zip(group.ids, hours))
        for task in self:
            elapsed = task.business_duration + extra.get(task.id, 0.0)
            if task.target_duration:
                task.business_percent_used = int((elapsed / task.target_duration) * 100)
            else:
                task.business_percent_used = 100 if elapsed else 0

    @api.depends('res_model', 'res_id', 'sla_id.name')
    def _compute_display_name(self):
        """Tên hiển thị gồm định nghĩa và record gốc, tránh lộ giá trị field."""
        for task in self:
            task.display_name = "%s - %s#%s" % (
                task.sla_id.name, task.res_model, task.res_id)

    def _due_soon_threshold(self):
        """Đọc ngưỡng X giờ của bộ lọc "Sắp đến hạn" từ cấu hình (REQ-INT-012)."""
        hours = int(self.env['ir.config_parameter'].sudo().get_param(
            'dwo_sla_core.due_soon_hours', 4))
        return fields.Datetime.now() + timedelta(hours=hours)

    @api.depends('stage', 'has_breached', 'planned_end_time')
    def _compute_is_due_soon(self):
        """Tính "Sắp đến hạn" không lưu trữ, phụ thuộc ngưỡng cấu hình hiện hành.

        Refs: REQ-INT-012
        """
        threshold = self._due_soon_threshold()
        for task in self:
            task.is_due_soon = (
                task.stage == 'in_progress' and not task.has_breached
                and bool(task.planned_end_time) and task.planned_end_time <= threshold)

    def _search_is_due_soon(self, operator, value):
        """Domain tương đương cho bộ lọc "Sắp đến hạn" (REQ-INT-012 AC1/AC2)."""
        threshold = self._due_soon_threshold()
        # Odoo có thể chuẩn hóa ('=', True) thành ('in', [True]); xử lý cả hai dạng để
        # không đảo ngược kết quả bộ lọc (REQ-INT-012).
        if operator in ('in', 'not in'):
            wanted = {bool(v) for v in value}
            if len(wanted) != 1:
                return [(1, '=', 1)] if (operator == 'in') == (len(wanted) > 1) else [(0, '=', 1)]
            positive = wanted.pop() == (operator == 'in')
        else:
            positive = (operator == '=' and bool(value)) or (operator == '!=' and not value)
        if positive:
            return [
                ('stage', '=', 'in_progress'), ('has_breached', '=', False),
                ('planned_end_time', '<=', threshold),
            ]
        # Phủ định De Morgan của domain dương ở trên.
        return [
            '|', '|',
            ('stage', '!=', 'in_progress'), ('has_breached', '=', True),
            ('planned_end_time', '>', threshold),
        ]

    def action_recalculate(self):
        """"Tính lại": áp cấu hình hiện hành của định nghĩa/record lên task.

        Logic: chỉ SLA Manager được gọi (AC4, kiểm tra cứng chứ không chỉ ẩn
        nút); chỉ tác dụng trên task `in_progress`/`paused`, task khác bỏ qua
        (AC3); giữ nguyên `business_duration` đã trôi, lấy lại `target_duration`
        và lịch hiện hành (REQ-FUNC-021, 052); với task `in_progress` chưa vi
        phạm thì xếp lại `planned_end_time` = hiện tại + phần giờ còn lại theo
        lịch mới (AC1, AC2); task đã vi phạm giữ nguyên `planned_end_time`
        (nhất quán với REQ-FUNC-044 AC2); task `paused` chỉ cập nhật
        `target_duration`/lịch, `planned_end_time` được xếp lại khi resume (theo
        đúng lời văn REQ-INT-005, không tính lại ở đây). KHÔNG đụng
        `original_breach_time` (deadline gốc, bất biến sau attach).
        Refs: REQ-INT-005
        """
        if not self.env.user.has_group('dwo_sla_core.group_sla_manager'):
            raise AccessError(get_message(
                MessageCode.ACC_RECALCULATE_SLA_MANAGER_ONLY))
        now = fields.Datetime.now()
        time_srv = self.env['sla.time']
        for task in self.sudo().filtered(lambda t: t.stage in ('in_progress', 'paused')):
            record = self.env[task.res_model].browse(task.res_id).exists()
            if not record:
                continue
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

    def action_reevaluate(self):
        """"Đánh giá lại": chạy lại 6 điều kiện cho record gốc (REQ-INT-020).

        Logic: chỉ SLA Manager được gọi (AC2); dùng thời điểm hiện tại,
        không coi field nào là "vừa đổi" nên không kích hoạt reset theo
        field (REQ-FUNC-032, REQ-FUNC-050 AC3); task đã kết thúc không đổi
        vì `evaluate()` tự tôn trọng bất biến REQ-FUNC-007 (AC3); gom các
        task theo `res_model` để gọi `evaluate()` theo lô thay vì từng
        record (AD-03).
        Refs: REQ-INT-020, REQ-FUNC-032
        """
        if not self.env.user.has_group('dwo_sla_core.group_sla_manager'):
            raise AccessError(get_message(
                MessageCode.ACC_REEVALUATE_SLA_MANAGER_ONLY))
        now = fields.Datetime.now()
        by_model = {}
        for task in self.sudo():
            by_model.setdefault(task.res_model, []).append(task.res_id)
        for res_model, res_ids in by_model.items():
            records = self.env[res_model].sudo().browse(res_ids).exists()
            if records:
                self.env['sla.engine'].evaluate(records, now=now, changed=set())

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
