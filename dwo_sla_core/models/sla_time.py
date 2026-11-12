# -*- coding: utf-8 -*-
from datetime import timedelta, timezone
from zoneinfo import ZoneInfo

from odoo import fields, models

from ..constants.message import MessageCode, get_message


class SlaTime(models.AbstractModel):
    """Time Service: xác định lịch, tính hạn chót, thời gian đã trôi, mốc kế tiếp.

    Logic: các hàm ở đây PHẢI thuần (không đọc/ghi task ngoài tham số, nhận
    `now`/`record` làm tham số) để Engine và Background Processor gọi lại
    được nhiều lần với kết quả ổn định, và dễ test sau này.
    Refs: TAD §4 (building block Time Service), CLAUDE.md "Quy ước kiến trúc"
    """
    _name = 'sla.time'
    _description = "Time Service SLA"

    def resolve_calendar(self, definition, record):
        """Xác định lịch áp dụng cho `record` theo định nghĩa, có dự phòng.

        Logic: lấy lịch thô qua điểm mở rộng `definition._get_calendar(record)`
        (REQ-INT-007: nguồn `none`/`definition`/`record`, đọc bằng `sudo()` để
        không phụ thuộc quyền người dùng, REQ-SEC-005); nếu nguồn là `record`
        và lịch không dùng được (trống, loại `flexible`, hoặc không có giờ
        làm) thì dự phòng sang lịch mặc định của công ty record, rồi 24x7 nếu
        công ty cũng không dùng được (REQ-FUNC-020). Nguồn `definition` không
        dự phòng (đã bị từ chối lúc lưu nếu không dùng được, REQ-FUNC-039).
        Trả về tuple (calendar hoặc False, ghi chú dự phòng hoặc False).

        `calendar_tz_override` (scope-add) được áp dụng Ở ĐÂY, sau khi lịch
        gốc (có dự phòng) đã xác định: nếu override khác `tz` của lịch đó,
        thay bằng bản sao cùng mẫu giờ làm nhưng đổi `tz`
        (`_get_tz_override_calendar`, tìm-hoặc-tạo). Không có lịch gốc (24x7,
        `calendar = False`) thì override không có ý nghĩa (không có mẫu giờ
        làm nào để sao) -- bỏ qua, giữ 24x7.
        Refs: REQ-FUNC-019, REQ-FUNC-020, REQ-SEC-005, REQ-INT-007
        """
        if definition.schedule_source == 'none':
            return False, False
        calendar = definition._get_calendar(record)
        if definition.schedule_source == 'definition':
            calendar = self._apply_tz_override(definition, calendar)
            return calendar, False
        if self._calendar_usable(calendar):
            calendar = self._apply_tz_override(definition, calendar)
            return calendar, False

        # FUNC-020: lịch qua record không dùng được → dự phòng công ty.
        note = (
            get_message(MessageCode.NOTE_CALENDAR_PATH_UNUSABLE,
                        definition.schedule_path) if not calendar else
            get_message(MessageCode.NOTE_CALENDAR_NOT_USABLE, calendar.name))
        company = record.sudo().company_id if 'company_id' in record._fields else False
        company = company or self.env.company
        if self._calendar_usable(company.resource_calendar_id):
            note += get_message(
                MessageCode.NOTE_CALENDAR_FALLBACK_COMPANY, company.name)
            return self._apply_tz_override(definition, company.resource_calendar_id), note

        note += get_message(MessageCode.NOTE_CALENDAR_FALLBACK_24X7)
        return False, note

    def _apply_tz_override(self, definition, calendar):
        """Trả `calendar`, hoặc bản sao đổi tz nếu `calendar_tz_override` khác tz gốc.

        Logic: scope-add "calendar_tz_override" (Cách A đã chốt). Timezone của
        định nghĩa luôn thắng tz của calendar và là field bắt buộc; nhánh
        `not calendar_tz_override` chỉ còn là phòng thủ cho dữ liệu ghi thẳng
        SQL. Override bằng đúng tz hiện tại của `calendar` thì trả thẳng
        `calendar` (không tạo bản sao, không tốn query thêm).
        Refs: plan-improvement-sla-01-review §6.5
        """
        if not calendar or not definition.calendar_tz_override \
                or definition.calendar_tz_override == calendar.tz:
            return calendar
        return self.env['resource.calendar'].sudo()._sla_get_tz_variant(
            calendar, definition.calendar_tz_override)

    def _calendar_usable(self, calendar):
        """Lịch dùng được khi tồn tại, cố định (không `flexible`) và có giờ làm.

        Refs: REQ-FUNC-020
        """
        return bool(calendar) and calendar._sla_is_fully_fixed() \
            and bool(calendar.attendance_ids)

    def plan(self, calendar, start_dt, hours):
        """Tính thời điểm sau khi cộng `hours` giờ làm việc từ `start_dt`.

        Logic: có lịch → `plan_hours` với `compute_leaves=True` (trừ ngày
        nghỉ); không lịch → cộng thẳng 24x7. `plan_hours` trả `False` khi
        không xếp được lịch trong 1400 ngày (lịch nghỉ phủ kín) — giữ
        nguyên `False` để gọi nơi khác ghi event `error` (REQ-FUNC-018 AC6).
        Refs: REQ-FUNC-018
        """
        if not calendar:
            return start_dt + timedelta(hours=hours)
        # Odoo 20: `plan_hours` tính theo múi giờ công ty, không theo `calendar.tz`; tự duyệt
        # khoảng làm việc (cửa sổ 14 ngày như core) trong múi giờ của calendar.
        tz = ZoneInfo(calendar.tz or 'UTC')
        day_dt = start_dt.replace(tzinfo=timezone.utc).astimezone(tz)
        window = timedelta(days=14)
        for n in range(100):
            low = day_dt + window * n
            for start, stop, _meta in calendar._work_intervals_batch(low, low + window)[False]:
                interval_hours = (stop - start).total_seconds() / 3600
                if hours <= interval_hours:
                    return (start + timedelta(hours=hours)).astimezone(timezone.utc).replace(tzinfo=None)
                hours -= interval_hours
        return False

    def settle(self, calendar, start_dt, end_dt):
        """Tính số giờ làm việc đã trôi giữa `start_dt` và `end_dt`.

        Logic: có lịch → `get_work_hours_count` với `compute_leaves=True`
        (trừ ngày nghỉ); không lịch → chênh lệch giờ thường (24x7). Thời
        gian ở `paused` không được cộng vào vì hàm chỉ nhận đúng khoảng thời
        gian đang chạy (gọi nơi khác không truyền khoảng paused).
        Refs: REQ-FUNC-043
        """
        if not start_dt or end_dt <= start_dt:
            return 0.0
        if not calendar:
            return (end_dt - start_dt).total_seconds() / 3600.0
        tz = ZoneInfo(calendar.tz or 'UTC')
        return calendar.get_work_hours_count(
            start_dt.replace(tzinfo=timezone.utc).astimezone(tz),
            end_dt.replace(tzinfo=timezone.utc).astimezone(tz), compute_leaves=True)

    def settle_batch(self, calendar, start_dts, end_dt):
        """Tính số giờ làm việc từ từng `start_dt` tới `end_dt` cho nhiều task cùng lịch.

        Logic: lấy khoảng làm việc của lịch MỘT lần cho cả đoạn từ start sớm
        nhất tới `end_dt` (một lượt đọc lịch và ngày nghỉ), rồi với mỗi
        `start_dt` cộng phần giao của các khoảng đó với [start_dt, end_dt].
        Kết quả bằng `settle` gọi riêng từng task nhưng không đọc lịch lặp.
        Trả list giờ theo đúng thứ tự `start_dts`.
        Refs: REQ-FUNC-043, REQ-INT-023
        """
        result = [0.0] * len(start_dts)
        live = [i for i, start in enumerate(start_dts) if end_dt > start]
        if not live:
            return result
        if not calendar:
            for i in live:
                result[i] = (end_dt - start_dts[i]).total_seconds() / 3600.0
            return result
        earliest = min(start_dts[i] for i in live)
        tz = ZoneInfo(calendar.tz or 'UTC')
        intervals = calendar._work_intervals_batch(
            earliest.replace(tzinfo=timezone.utc).astimezone(tz),
            end_dt.replace(tzinfo=timezone.utc).astimezone(tz))[False]
        spans = [(start.astimezone(timezone.utc).replace(tzinfo=None),
                  stop.astimezone(timezone.utc).replace(tzinfo=None))
                 for start, stop, _meta in intervals]
        for i in live:
            start_dt = start_dts[i]
            result[i] = sum(
                (min(stop, end_dt) - max(start, start_dt)).total_seconds() / 3600.0
                for start, stop in spans if stop > start_dt and start < end_dt)
        return result

    def next_due_at(self, task, now=None):
        """Tính mốc sớm nhất xử lý nền phải xử lý cho task đang chạy.

        Logic: chỉ có nghĩa với task `in_progress`; ứng viên gồm
        `planned_end_time` (nếu chưa bật dấu vi phạm) và thời điểm mỗi mốc
        escalation chưa xử lý xong sẽ đạt phần trăm của nó (quy đổi phần
        trăm sang số giờ mục tiêu rồi `plan` phần còn lại kể từ `now`). Trả
        mốc nhỏ nhất, hoặc `False` nếu không có ứng viên nào (ví dụ mọi mốc
        đã xử lý xong và đã vi phạm).
        Refs: TAD §4 Time Service, REQ-FUNC-022, REQ-FUNC-023, REQ-FUNC-046
        """
        now = now or fields.Datetime.now()
        if task.stage != 'in_progress':
            return False

        candidates = []
        if not task.has_breached and task.planned_end_time:
            candidates.append(task.planned_end_time)

        calendar = task.schedule_id
        # Thời gian đã trôi tới `now`: phần đã đóng băng (business_duration)
        # cộng phần của đoạn đang chạy hiện tại (REQ-FUNC-043).
        elapsed_now = task.business_duration + self.settle(
            calendar, task.running_since, now)

        pending = task.sla_id.escalation_ids - task.done_escalation_ids
        for esc in pending:
            milestone_hours = task.target_duration * esc.percent / 100.0
            remaining = milestone_hours - elapsed_now
            if remaining <= 0:
                # Đã tới hoặc vượt mức phần trăm ngay lúc này (REQ-FUNC-046).
                candidates.append(now)
            else:
                due = self.plan(calendar, now, remaining)
                if due:
                    candidates.append(due)

        return min(candidates) if candidates else False
