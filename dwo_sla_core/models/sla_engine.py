# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

from ..constants.message import MessageCode, get_message

_logger = logging.getLogger(__name__)

ACTIVE_STAGES = ('in_progress', 'paused')
TERMINAL_STAGES = ('achieved', 'breached', 'cancelled')


class SlaEngine(models.AbstractModel):
    """Engine: đánh giá 6 điều kiện và chuyển trạng thái task SLA.

    Logic: hàm `evaluate` được hook (T8) hoặc hành động thủ công (T9) gọi
    ngay sau khi record được ghi; chỉ xử lý vòng đời (attach, pause, resume,
    complete, cancel, reset) — KHÔNG xử lý escalation (REQ-FUNC-025: chạy
    ngoài thao tác lưu, do Background Processor đảm nhiệm, T7). Mỗi điều
    kiện được tính một lần cho cả lô bằng `filtered_domain` (AD-03,
    REQ-PERF-002); mỗi record được cô lập trong savepoint riêng để lỗi của
    một record không ảnh hưởng record khác (AD-07, REQ-FUNC-030, 014 AC2).
    Refs: REQ-FUNC-004 đến 022, 037, 043, 044, 046, 048, 050, 051, 055, TAD
      §4 Engine, §5.2 Whitebox, CLAUDE.md "Quy ước kiến trúc"
    """
    _name = 'sla.engine'
    _description = "SLA Engine"

    def _safe_evaluate(self, records, now=None, changed=None):
        """Gọi `evaluate` nhưng không bao giờ để lỗi lan ra lần lưu của người dùng.

        Logic: hook (`sla_hook.py`) gọi hàm này thay vì gọi `evaluate` trực
        tiếp; `evaluate` đã tự cô lập lỗi theo record/định nghĩa, nhưng đây
        là lớp phòng thủ cuối cùng cho lỗi không lường trước (ví dụ lỗi khi
        tính `now`), để thao tác lưu gốc của người dùng luôn thành công
        (REQ-FUNC-030).
        Refs: REQ-FUNC-030, AD-01
        """
        cr = self.env.cr
        if getattr(cr, '_sla_evaluating', False):
            # Chống đệ quy: ghi `sla.task` có thể flush field compute của record
            # gốc, làm hook gọi lại Engine khi lượt ngoài chưa INSERT xong, gây
            # gắn trùng và event `error` giả (REQ-FUNC-014, AD-08). Không bỏ
            # mất thay đổi: ghi lại field đổi, lượt ngoài đánh giá bù sau khi
            # xong (REQ-FUNC-005 — field compute có lưu đổi trong lúc đánh giá).
            pending = cr.__dict__.setdefault('_sla_pending', {})
            created = cr.__dict__.get('_sla_created', ())
            for record in records.filtered('id'):
                key = (record._name, record.id)
                # Giá trị compute lần đầu của record vừa tạo không phải "thay đổi"
                # (REQ-FUNC-013); lượt bù chỉ cần cho thay đổi thật.
                if changed and key not in created:
                    pending.setdefault(key, set()).update(changed)
            return
        try:
            self.evaluate(records, now=now, changed=changed)
        except Exception:  # noqa: BLE001 -- không được chặn lưu record (REQ-FUNC-030)
            _logger.exception("SLA engine evaluate() lỗi không lường trước sau khi lưu record")

    def evaluate(self, records, now=None, changed=None, definitions=None):
        """Đánh giá SLA cho `records` theo mọi định nghĩa áp dụng.

        Logic: `changed` là tập tên field vừa đổi giá trị trong lần ghi đang
        xử lý (dùng để kiểm field kích hoạt reset, REQ-FUNC-013); không
        truyền (None) nghĩa là không có field nào được coi là "vừa đổi"
        (an toàn mặc định cho "Đánh giá lại" thủ công, REQ-FUNC-050 AC3).
        Cờ `_sla_evaluating` chặn hook lồng trong lúc đánh giá; các thay đổi
        field compute bị hoãn được đánh giá bù ngay sau lượt ngoài cùng
        (tối đa vài vòng để không lặp vô hạn), việc đánh giá lại idempotent
        (REQ-FUNC-015). `definitions` (recordset `sla.definition`) giới hạn lượt
        đánh giá đầu tiên vào đúng các định nghĩa đó, kể cả định nghĩa đã tắt;
        None = mọi định nghĩa của model (hành vi mặc định của hook/cron). Lượt
        đánh giá bù field compute KHÔNG dùng tham số này, giữ hành vi cũ.
        Refs: REQ-FUNC-004, 005, 014, 050, plan-improvement-sla-01-review §6.18
        """
        if not records:
            return
        cr = self.env.cr
        if getattr(cr, '_sla_evaluating', False):
            # Gọi lồng trực tiếp (không qua hook): chạy thẳng, lượt ngoài lo phần bù.
            self._evaluate_once(records, now, changed, definitions)
            return
        cr._sla_evaluating = True
        cr._sla_pending = {}
        try:
            self._evaluate_once(records, now, changed, definitions)
            for _round in range(5):
                pending, cr._sla_pending = cr._sla_pending, {}
                if not pending:
                    break
                for (res_model, res_id), pending_changed in pending.items():
                    record = self.env[res_model].browse(res_id).exists()
                    if record:
                        self._evaluate_once(record, now, pending_changed)
        finally:
            cr._sla_evaluating = False
            cr._sla_pending = {}

    def _evaluate_once(self, records, now, changed, definitions=None):
        """Một lượt đánh giá `records` theo mọi định nghĩa, hoặc theo `definitions` nếu có.

        Refs: REQ-FUNC-004, 005, 060, REQ-OBS-001, plan-improvement-sla-01-review §6.18
        """
        now = now or fields.Datetime.now()
        changed = changed or set()
        self.env['sla.definition'].sudo()._ensure_hook_registered()
        # Định nghĩa archive vẫn được đánh giá để task đang chạy tiếp tục
        # stop/cancel/pause/resume (REQ-FUNC-060); chỉ không gắn task mới (REQ-FUNC-033).
        if definitions is not None:
            definitions = definitions.sudo()
        else:
            definitions = self.env['sla.definition'].sudo().with_context(
                active_test=False).search([('model_name', '=', records._name)])
        for definition in definitions:
            defn_records = self._filter_company(definition, records)
            if defn_records:
                try:
                    self._evaluate_definition(definition, defn_records, now, changed)
                except Exception as exc:  # noqa: BLE001 -- lỗi 1 định nghĩa không chặn định nghĩa khác (REQ-FUNC-030)
                    # Ghi một event cho từng record để có đủ id record (REQ-OBS-001 AC1).
                    for record in defn_records:
                        self.env['sla.event']._log_error(
                            definition=definition, res_model=records._name,
                            res_id=record.id,
                            message=get_message(
                                MessageCode.NOTE_BATCH_EVALUATE_ERROR, exc))

    def _filter_company(self, definition, records):
        """Chỉ giữ record cùng công ty với định nghĩa (hoặc định nghĩa không gán công ty).

        Refs: REQ-SEC-003
        """
        if not definition.company_id or 'company_id' not in records._fields:
            return records
        return records.filtered(
            lambda r: not r.company_id or r.company_id == definition.company_id)

    def _evaluate_definition(self, definition, records, now, changed):
        """Đánh giá một định nghĩa trên cả lô record, cô lập lỗi theo record.

        Logic: tính 6 tập id khớp điều kiện một lần cho cả lô (AD-03); tìm
        task đang hoạt động bằng một search; với record chưa có task hoạt
        động, tìm task gần nhất (nếu có) để áp REQ-FUNC-007. Lỗi của một
        record được cô lập bằng savepoint, ghi event `error`, record khác
        không bị ảnh hưởng (AD-07, REQ-FUNC-030).
        Refs: REQ-FUNC-004, 007, 014, 030, AD-03, AD-07
        """
        SlaTask = self.env['sla.task'].sudo()
        active_tasks = SlaTask.search([
            ('sla_id', '=', definition.id),
            ('res_model', '=', records._name),
            ('res_id', 'in', records.ids),
            ('stage', 'in', ACTIVE_STAGES),
        ])
        # Định nghĩa tắt mà không có task đang chạy thì không có gì để làm: bỏ qua
        # trước khi tính 6 điều kiện (đường nóng, tắt là trạng thái bình thường).
        if not definition.active and not active_tasks:
            return
        match = self._match_sets(definition, records)

        active_by_res = {t.res_id: t for t in active_tasks}
        no_active_ids = [rid for rid in records.ids if rid not in active_by_res]
        last_by_res = self._last_task_by_res(definition, records._name, no_active_ids) \
            if no_active_ids else {}

        def process(record, batch):
            task = active_by_res.get(record.id)
            if task:
                self._apply_active(definition, task, record, now, changed, match)
            elif definition.active:  # REQ-FUNC-033: archive không gắn task mới
                self._maybe_attach(
                    definition, record, now, last_by_res.get(record.id), match, batch)

        # Bỏ qua record không có gì để làm (không task hoạt động và không đủ điều
        # kiện attach) để khỏi tốn savepoint/truy vấn theo record (REQ-PERF-002).
        todo = records.filtered(lambda r: r.id in active_by_res or (
            definition.active and self._can_attach(r.id, last_by_res.get(r.id), match)))
        if not todo:
            return
        # Đường nhanh: cả lô trong MỘT savepoint, task mới và event được ghi theo lô
        # (số truy vấn không tăng theo số record, REQ-PERF-002). Có lỗi thì hoàn tác
        # và chạy lại từng record trong savepoint riêng để cô lập lỗi (AD-07).
        try:
            with self.env.cr.savepoint():
                self._run_batched(definition, todo, now, lambda rec, batch: process(rec, batch))
            return
        except Exception:  # noqa: BLE001 -- chạy lại từng record để cô lập lỗi
            todo.invalidate_cache(None, ids=todo.ids)
        for record in todo:
            try:
                with self.env.cr.savepoint():
                    self._run_batched(
                        definition, record, now, lambda rec, batch: process(rec, batch))
            except Exception as exc:  # noqa: BLE001 -- cô lập lỗi theo record (AD-07)
                self.env['sla.event']._log_error(
                    definition=definition, res_model=records._name, res_id=record.id,
                    message=str(exc))

    def _run_batched(self, definition, records, now, func):
        """Chạy `func(record, batch)` cho từng record rồi ghi task mới + event theo lô.

        Logic: `_attach` chỉ gom giá trị vào `batch`; sau vòng lặp tạo mọi task bằng
        một lệnh create, tính `next_due_at` theo nhóm giá trị, rồi ghi mọi event bằng
        một lệnh create (giữ đúng thứ tự phát sinh).
        Refs: REQ-PERF-002, AD-03
        """
        cr = self.env.cr
        previous_buffer = cr.__dict__.get('_sla_event_buffer')
        cr._sla_event_buffer = []
        try:
            batch = []
            for record in records:
                func(record, batch)
            self._create_attached(definition, batch, now)
            events = cr._sla_event_buffer
            cr._sla_event_buffer = None
            if events:
                self.env['sla.event'].sudo().create(events)
        finally:
            cr._sla_event_buffer = previous_buffer

    @staticmethod
    def _can_attach(rid, last_task, match):
        """Record chưa có task hoạt động có đủ điều kiện attach không (REQ-FUNC-006, 007)."""
        if rid not in match['start'] or rid in match['stop'] or rid in match['cancel']:
            return False
        return not (last_task and last_task.stage in ('achieved', 'breached'))

    def _match_sets(self, definition, records):
        """Tính tập id khớp cho 6 điều kiện, mỗi điều kiện một `filtered_domain`.

        Logic: điều kiện rỗng hoặc `[]` (chưa cấu hình) không bao giờ khớp (tập
        rỗng); muốn khớp mọi record phải viết `[('id', '!=', 0)]` (REQ-FUNC-003).
        Refs: REQ-FUNC-003, AD-03
        """
        result = {}
        for cond in ('start', 'cancel', 'pause', 'resume', 'stop', 'reset'):
            domain = definition._get_domain(cond)
            result[cond] = frozenset(records.filtered_domain(domain).ids) \
                if domain is not None else frozenset()
        return result

    def _last_task_by_res(self, definition, res_model, res_ids):
        """Tìm task gần nhất (id lớn nhất) của mỗi record chưa có task hoạt động.

        Refs: REQ-FUNC-007
        """
        tasks = self.env['sla.task'].sudo().search([
            ('sla_id', '=', definition.id),
            ('res_model', '=', res_model),
            ('res_id', 'in', res_ids),
        ], order='id desc')
        result = {}
        for task in tasks:
            result.setdefault(task.res_id, task)
        return result

    # ------------------------------------------------------------------
    # Record đã có task đang hoạt động: bảng ưu tiên (REQ-FUNC-008)
    # ------------------------------------------------------------------

    def _apply_active(self, definition, task, record, now, changed, match):
        """Áp bảng ưu tiên stop → cancel → reset → pause → resume.

        Logic: dừng ở mục đầu tiên khớp, không xét các mục sau (REQ-FUNC-008).
        Refs: REQ-FUNC-008, 016
        """
        rid = record.id
        if rid in match['stop']:
            self._complete(task, now)
            return

        start_match = rid in match['start']
        if self._cancel_matches(definition, rid, match, start_match):
            self._cancel(task, now)
            return

        if rid in match['reset'] and start_match:
            if self._reset_field_changed(definition, changed):
                self._reset(definition, task, record, now, changed, match)
                return

        if task.stage == 'in_progress' and rid in match['pause']:
            self._pause(task, now)
            return

        if task.stage == 'paused':
            if definition.resume_mode == 'condition':
                if rid in match['resume']:
                    self._resume(task, now)
            else:  # pause_unmatched (REQ-FUNC-048)
                if rid not in match['pause']:
                    self._resume(task, now)

    def _cancel_matches(self, definition, rid, match, start_match):
        """Xác định cancel có khớp theo `cancel_mode` (REQ-FUNC-010)."""
        if definition.cancel_mode == 'condition':
            return rid in match['cancel']
        if definition.cancel_mode == 'start_unmatched':
            return not start_match
        return False  # 'never'

    def _reset_field_changed(self, definition, changed):
        """True nếu không cấu hình field theo dõi, hoặc một field vừa đổi.

        Refs: REQ-FUNC-013, 050, 051
        """
        if not definition.reset_field_ids:
            return True
        tracked = set(definition.reset_field_ids.mapped('name'))
        return bool(tracked & changed)

    # ------------------------------------------------------------------
    # Record chưa có task đang hoạt động: attach (REQ-FUNC-006, 007)
    # ------------------------------------------------------------------

    def _maybe_attach(self, definition, record, now, last_task, match, batch=None):
        """Gắn SLA mới nếu đủ điều kiện và task gần nhất không bất biến.

        Logic: task gần nhất `achieved`/`breached` là bất biến, không gắn lại
        dù start vẫn khớp (REQ-FUNC-007); task `cancelled` được gắn lại bình
        thường.
        Refs: REQ-FUNC-006, 007
        """
        if self._can_attach(record.id, last_task, match):
            self._attach(definition, record, now, match, batch)

    def _attach(self, definition, record, now, match, batch=None):
        """Tạo task mới: snapshot cấu hình, tính hạn, ghi event attach (+breach).

        Logic: snapshot `duration`/lịch lúc attach, sửa định nghĩa sau đó
        không ảnh hưởng (REQ-FUNC-021); lỗi tính mục tiêu âm hoặc không xếp
        được lịch thì KHÔNG tạo task, ghi event `error` (REQ-INT-015 AC3,
        REQ-FUNC-018 AC6); retroactive start có thể làm task breach ngay lúc
        attach (REQ-FUNC-017). `original_breach_time` được set BẰNG
        `planned_end_time` ở đây và không bao giờ ghi lại sau đó (khác
        `planned_end_time`, bị tính lại ở `_resume`/`action_recalculate`) --
        scope-add "original_breach_time".
        Refs: REQ-FUNC-006, 017, 018, 020, 021
        """
        time_srv = self.env['sla.time']
        target_duration = definition._get_target_hours(record)
        if target_duration < 0:
            # Refs: REQ-INT-015 AC3
            self.env['sla.event']._log_error(
                definition=definition, res_model=record._name, res_id=record.id,
                message=get_message(
                    MessageCode.NOTE_TARGET_HOURS_NEGATIVE, target_duration))
            return

        start_time, start_note = self._get_start_dt_with_note(definition, record, now)
        calendar, cal_note = time_srv.resolve_calendar(definition, record)
        planned_end_time = time_srv.plan(calendar, start_time, target_duration)
        if planned_end_time is False:
            # Refs: REQ-FUNC-018 AC6
            self.env['sla.event']._log_error(
                definition=definition, res_model=record._name, res_id=record.id,
                message=get_message(MessageCode.NOTE_DEADLINE_OUT_OF_RANGE))
            return

        # Retroactive start có thể lùi start_time về quá khứ: thời gian từ
        # start_time tới now (lúc attach) PHẢI được tính vào business_duration/
        # duration ngay từ đầu, trừ các đoạn khớp pause_domain trong quá khứ
        # nếu retroactive_pause bật và đủ điều kiện (mail.thread + field
        # tracking) -- nếu không có gì đặc biệt (start_time == now, attach
        # bình thường, hoặc không tìm được đoạn pause nào), các số này đơn
        # giản là 0/không đổi gì, giống hệt hành vi trước khi có tính năng
        # này (không regress test TG-07 hiện có, vốn không cấu hình tracking).
        # `running_since`/`pause_time` vẫn đặt = `now` (đúng nghĩa field
        # "đoạn ĐANG chạy/paused HIỆN TẠI", xem docstring field) -- phần quá
        # khứ đã được dồn vào business_duration/duration ở đây, không cần dời
        # running_since. Scope-add "retroactive_pause"; sửa cùng lúc một lỗi
        # liên quan: trước bản sửa này, business_duration/duration LUÔN bắt
        # đầu ở 0 bất kể start_time lùi bao xa, nên % đã dùng/báo cáo ngay sau
        # 1 attach lùi xa bị báo sai (thấp hơn thực tế) cho tới lần
        # pause/resume/complete đầu tiên -- không phải lỗi do retroactive_pause
        # gây ra, nhưng phải sửa cùng lúc vì retroactive_pause không có gì để
        # trừ nếu base vẫn luôn là 0.
        business_duration = time_srv.settle(calendar, start_time, now)
        duration = self._clock_hours(start_time, now)
        business_pause_duration = 0.0
        pause_duration = 0.0
        if definition.retroactive_pause and now > start_time:
            segments = definition._retroactive_pause_segments(record, start_time, now)
            for seg_start, seg_end in segments:
                business_pause_duration += time_srv.settle(calendar, seg_start, seg_end)
                pause_duration += self._clock_hours(seg_start, seg_end)
            business_duration = max(business_duration - business_pause_duration, 0.0)
            duration = max(duration - pause_duration, 0.0)
            if business_pause_duration > 0:
                # Hạn chót cũng phải dời ra đúng bằng số giờ làm vừa loại trừ --
                # giống cách `_resume` luôn dời `planned_end_time` khi tiếp tục
                # sau một lần pause thường (forward); không làm vậy thì hạn
                # chót vẫn tính như thể record chạy liên tục suốt khoảng quá
                # khứ, mâu thuẫn với chính mục đích của retroactive_pause.
                extended = time_srv.plan(calendar, planned_end_time, business_pause_duration)
                if extended is not False:
                    planned_end_time = extended

        has_breached = bool(planned_end_time and now >= planned_end_time)
        stage = 'paused' if record.id in match['pause'] else 'in_progress'
        vals = {
            'sla_id': definition.id,
            'res_model': record._name,
            'res_id': record.id,
            'company_id': record.company_id.id if 'company_id' in record._fields else False,
            'schedule_id': calendar.id if calendar else False,
            'target_duration': target_duration,
            'stage': stage,
            'start_time': start_time,
            'planned_end_time': planned_end_time,
            'original_breach_time': planned_end_time,
            'has_breached': has_breached,
            'business_duration': business_duration,
            'duration': duration,
            'business_pause_duration': business_pause_duration,
            'pause_duration': pause_duration,
        }
        if stage == 'in_progress':
            vals['running_since'] = now
        else:
            vals['pause_time'] = now
        note = " ".join(p for p in (start_note, cal_note) if p) or False
        entry = (vals, note)
        if batch is not None:
            batch.append(entry)
        else:
            self._create_attached(definition, [entry], now)

    def _create_attached(self, definition, entries, now):
        """Tạo các task đã chuẩn bị ở `_attach` bằng một lệnh create, ghi event attach/breach.

        Logic: `next_due_at` tính sau khi tạo (cần task) rồi ghi theo nhóm cùng giá trị
        để không tốn một UPDATE cho mỗi task; điểm mở rộng `_after_transition` vẫn được
        gọi cho từng task.
        Refs: REQ-FUNC-006, 017, REQ-PERF-002
        """
        if not entries:
            return
        time_srv = self.env['sla.time']
        tasks = self.env['sla.task'].sudo().create([vals for vals, _note in entries])
        by_due = {}
        for task in tasks.filtered(lambda t: t.stage == 'in_progress'):
            by_due.setdefault(time_srv.next_due_at(task, now), []).append(task.id)
        for due, task_ids in by_due.items():
            tasks.browse(task_ids).write({'next_due_at': due})
        for task, (vals, note) in zip(tasks, entries):
            self._log_event(task, 'attach', now, note=note)
            if vals['has_breached']:
                self._log_event(task, 'breach', now)
            definition._after_transition(task, False, vals['stage'], 'attach')

    def _get_start_dt_with_note(self, definition, record, now):
        """Trả (start_time, note) — note khi field retroactive trống (REQ-FUNC-017 AC3)."""
        start_time = definition._get_start_dt(record, now)
        if definition.retroactive and definition.start_field_id:
            value = record[definition.start_field_id.name]
            if not value:
                return start_time, get_message(
                    MessageCode.NOTE_START_FIELD_EMPTY_USE_NOW,
                    definition.start_field_id.name)
        return start_time, False

    # ------------------------------------------------------------------
    # Chuyển trạng thái (REQ-FUNC-009, 010, 011, 012, 037, 044, 046, 048)
    # ------------------------------------------------------------------

    def _check_breach(self, task, now):
        """Bật dấu vi phạm ngay nếu `now >= planned_end_time`, dù phát hiện lúc nào.

        Logic: dấu vi phạm không bao giờ tắt lại (REQ-FUNC-046); việc phát
        hiện ở đây xảy ra khi người dùng ghi record làm task chuyển trạng
        thái trước khi xử lý nền kịp chạy (REQ-FUNC-022 AC2).
        Refs: REQ-FUNC-022, 046
        """
        if task.stage == 'in_progress' and not task.has_breached \
                and task.planned_end_time and now >= task.planned_end_time:
            task.has_breached = True
            self._log_event(task, 'breach', now)

    @staticmethod
    def _clock_hours(start_dt, end_dt):
        """Số giờ đồng hồ thật giữa hai thời điểm (không qua calendar).

        Logic: cặp với `sla.time.settle()` (bản giờ làm) để tính song song
        field `duration`/`pause_duration` (bản giờ đồng hồ) -- scope-add
        "duration/pause_duration bản giờ đồng hồ".
        """
        if not start_dt or end_dt <= start_dt:
            return 0.0
        return (end_dt - start_dt).total_seconds() / 3600.0

    def _settle_running(self, task, now):
        """Cộng dồn thời gian đã trôi của đoạn đang chạy hiện tại.

        Logic: trả (business_duration, duration) -- bản giờ làm (qua
        calendar, như trước) VÀ bản giờ đồng hồ thật song song (scope-add).
        Refs: REQ-FUNC-043
        """
        business_add = self.env['sla.time'].settle(task.schedule_id, task.running_since, now)
        clock_add = self._clock_hours(task.running_since, now)
        return task.business_duration + business_add, task.duration + clock_add

    def _complete(self, task, now):
        """Hoàn thành (stop khớp): achieved hoặc breached theo dấu vi phạm.

        Logic: task `paused` chỉ xét dấu vi phạm đã có, không so lại
        `planned_end_time` (REQ-FUNC-009 "More Information"/AC3); task đã kết
        thúc rồi thì bỏ qua (AC4, vô hại khi gọi lại).
        Refs: REQ-FUNC-009
        """
        if task.stage not in ACTIVE_STAGES:
            return
        if task.stage == 'in_progress':
            self._check_breach(task, now)
            business_duration, duration = self._settle_running(task, now)
        else:
            business_duration, duration = task.business_duration, task.duration
        old_stage = task.stage
        stage = 'breached' if task.has_breached else 'achieved'
        task.write({
            'stage': stage,
            'business_duration': business_duration,
            'duration': duration,
            'running_since': False,
            'pause_time': False,  # CHECK sla_task_paused_since_check (030 §5)
            'end_time': now,
            'next_due_at': False,
        })
        self._log_event(task, 'complete', now)
        task.sla_id._after_transition(task, old_stage, stage, 'complete')

    def _cancel(self, task, now):
        """Hủy task: `cancelled`, không xét dấu vi phạm (REQ-FUNC-010)."""
        if task.stage not in ACTIVE_STAGES:
            return
        old_stage = task.stage
        task.write({
            'stage': 'cancelled',
            'running_since': False,
            'pause_time': False,  # CHECK sla_task_paused_since_check (030 §5)
            'end_time': now,
            'next_due_at': False,
        })
        self._log_event(task, 'cancel', now)
        task.sla_id._after_transition(task, old_stage, 'cancelled', 'cancel')

    def _pause(self, task, now):
        """Tạm dừng: chốt thời gian đã trôi, ghi event pause (REQ-FUNC-011)."""
        if task.stage != 'in_progress':
            return
        self._check_breach(task, now)
        business_duration, duration = self._settle_running(task, now)
        task.write({
            'stage': 'paused',
            'business_duration': business_duration,
            'duration': duration,
            'running_since': False,
            'pause_time': now,
            'next_due_at': False,
        })
        self._log_event(task, 'pause', now)
        task.sla_id._after_transition(task, 'in_progress', 'paused', 'pause')

    def _resume(self, task, now):
        """Tiếp tục: xếp lại `planned_end_time` nếu chưa vi phạm, tính lại mốc.

        Logic: dấu vi phạm đã bật thì giữ nguyên `planned_end_time`
        (REQ-FUNC-044 AC2); mốc escalation chưa xử lý xong được tính lại từ
        đầu. Cộng dồn `business_pause_duration`/
        `pause_duration` (bản giờ đồng hồ) cho đoạn vừa paused -- field này
        trước đây KHÔNG được cộng dồn ở đâu cả (field tồn tại nhưng luôn giữ
        giá trị mặc định 0); sửa cùng lúc với việc thêm bản giờ đồng hồ song
        song vì cả hai cộng dồn tại đúng một điểm (lúc resume).
        Refs: REQ-FUNC-037, 044, 046, 048, 055
        """
        if task.stage != 'paused':
            return
        time_srv = self.env['sla.time']
        business_pause_add = time_srv.settle(task.schedule_id, task.pause_time, now)
        clock_pause_add = self._clock_hours(task.pause_time, now)
        planned_end_time = task.planned_end_time
        if not task.has_breached:
            remaining = max(task.target_duration - task.business_duration, 0.0)
            new_planned_end_time = time_srv.plan(task.schedule_id, now, remaining)
            if new_planned_end_time is not False:
                planned_end_time = new_planned_end_time
        task.write({
            'stage': 'in_progress',
            'running_since': now,
            'pause_time': False,
            'planned_end_time': planned_end_time,
            'business_pause_duration': task.business_pause_duration + business_pause_add,
            'pause_duration': task.pause_duration + clock_pause_add,
        })
        # Ghi next_due_at ở lệnh write riêng vì công thức cần planned_end_time và
        # running_since đã cập nhật; cả hai write nằm trong cùng savepoint
        # của record này nên không lộ trạng thái "in_progress nhưng
        # next_due_at cũ" ra ngoài giao dịch (không vi phạm tinh thần
        # CHECK `sla_task_next_due_at_check`).
        task.next_due_at = time_srv.next_due_at(task, now)
        self._log_event(task, 'resume', now)
        task.sla_id._after_transition(task, 'paused', 'in_progress', 'resume')

    def _reset(self, definition, task, record, now, changed, match):
        """Kết thúc task cũ theo hành động reset, rồi gắn task mới nếu còn khớp.

        Logic: hành động reset `cancel`/`complete` tái dùng `_cancel`/
        `_complete` (đã ghi event tương ứng); event `reset` ghi riêng, nêu
        field đã đổi nếu có cấu hình theo dõi (REQ-FUNC-051 AC2). Vì nhánh
        này chỉ được gọi khi `start` đã khớp (điều kiện vào của bảng ưu tiên,
        REQ-FUNC-008), task mới luôn được gắn — xem ghi chú tại nơi gọi về
        REQ-FUNC-012 AC5 (giả định đã chọn theo REQ-FUNC-008).
        Refs: REQ-FUNC-012, 013, 051
        """
        if definition.reset_action == 'cancel':
            self._cancel(task, now)
        else:
            self._complete(task, now)

        changed_names = sorted(
            name for name in definition.reset_field_ids.mapped('name') if name in changed)
        note = get_message(
            MessageCode.NOTE_FIELDS_CHANGED, ", ".join(changed_names)) \
            if changed_names else False
        self._log_event(task, 'reset', now, note=note)
        # Ghi task cũ xuống DB TRƯỚC khi tạo task mới, nếu không INSERT chạm
        # unique index một-task-hoạt-động (030 §6, REQ-FUNC-012).
        task.flush()
        self._attach(definition, record, now, match)

    def _log_event(self, task, event, event_dt, note=False):
        """Ghi một dòng `sla.event` cho task (REQ-FUNC-029).

        Đang trong `_run_batched` thì gom vào bộ đệm, ghi một lần cuối lô (REQ-PERF-002).
        """
        values = {
            'task_id': task.id,
            'event': event,
            'event_dt': event_dt,
            'note': note,
            'definition_id': task.sla_id.id,
            'company_id': task.company_id.id,
        }
        buffer = self.env.cr.__dict__.get('_sla_event_buffer')
        if buffer is not None:
            buffer.append(values)
        else:
            self.env['sla.event'].sudo().create(values)
