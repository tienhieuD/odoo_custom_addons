# -*- coding: utf-8 -*-
"""Message registry tập trung cho dwo_sla_core.

Quy ước (xem thêm CLAUDE.md, mục "Ngôn ngữ hiển thị cho user"): MỌI chuỗi
hiển thị cho người dùng (lỗi validate, hộp thoại xác nhận, thông báo
info/success) phải viết bằng TIẾNG ANH và định nghĩa DUY NHẤT một lần ở
đây, gọi ra bằng mã (`MessageCode.*`) thay vì viết literal string rải rác
tại nơi raise/thông báo. Mục đích: (1) tránh lặp/lệch nội dung, (2) 1 chỗ
để sửa, (3) `_lt(...)` (LazyTranslate) giữ cho trình export i18n của Odoo
quét ra `.pot/.po` (yêu cầu đối số là chuỗi literal ngay trong lời gọi
`_lt(...)`, không phải biến).

Khác với `astra_mail/constants/message.py` (bản tham khảo, được đánh giá
là thiết kế chưa tốt) ở 3 điểm:

1. MỌI entry đều được bọc qua `_ltparams(...)` — kể cả message KHÔNG có
   tham số `%s` — nên `get_message(code, *args)` luôn gọi theo một kiểu
   DUY NHẤT (callable). Bản tham khảo có entry là `_lt(...)` trần (không
   gọi được) xen lẫn entry đã bọc callable; nơi gọi phải tự biết/đoán
   đúng kiểu, dễ lỗi (gọi nhầm chuỗi thành hàm, hoặc quên gọi hàm nên
   hiển thị `%s` thô cho user).
2. Mã được khai báo thành hằng số (`MessageCode.VAL_...`) thay vì chuỗi
   rời rạc (`"COM_067"`) để tránh gõ sai và có gợi ý IDE; mã được đánh số
   RIÊNG theo từng nhóm (VAL/ACC/CONF/INF) thay vì 1 dãy số chung xuyên
   suốt (bản tham khảo dùng `ERR_002`...`ERR_093` rải rác không theo thứ
   tự nào), để dễ thêm message mới mà không phải rà toàn bộ danh sách.
3. `get_message()` báo lỗi RÕ bằng `KeyError` khi mã không tồn tại, thay
   vì âm thầm trả `''`/`None` (bản tham khảo) khiến lỗi gõ sai mã code
   chỉ lộ ra khi user thấy hộp thoại trống, rất khó debug.
"""
from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)


def _ltparams(message):
    """Bọc một `_lt(...)` đã tạo (literal, để trình export quét được)
    thành hàm có thể gọi lại với tham số runtime.

    Logic: `message._source` là chuỗi GỐC (chưa dịch) của lần gọi
    `_lt("...")` literal ngay tại `MESSAGE_IDS` bên dưới. Lambda trả về
    gọi lại `_lt(msg, *arg)` MỚI mỗi lần `get_message()` được dùng, để
    dịch + thế tham số đúng theo locale hiện hành TẠI THỜI ĐIỂM GỌI
    (không cache cứng theo tham số của lần định nghĩa dict).
    """
    msg = message._source if hasattr(message, '_source') else message
    return lambda *arg: _lt(msg, *arg)


class MessageCode:
    """Hằng số mã message — dùng thay cho chuỗi "VAL_001" gõ tay.

    Nhóm theo loại: VAL (validation error), ACC (access/permission error),
    NOTE (ghi vào sla.event.note), DISP (nhãn hiển thị read-only trong
    list/kanban, ví dụ tóm tắt 1 dòng escalation -- khác NOTE vì không gắn
    với sự kiện/audit trail nào, chỉ là UI label). Thêm CONF (confirm
    dialog) / INF (info, success) khi module cần.
    """

    # --- Validation errors (ir.exceptions.ValidationError) ---
    VAL_LOG_RETENTION_DAYS_POSITIVE = "VAL_001"
    VAL_DUE_SOON_HOURS_POSITIVE = "VAL_002"
    VAL_BATCH_SIZE_POSITIVE = "VAL_003"
    VAL_DEFINITION_HAS_TASKS = "VAL_004"
    VAL_MODEL_EXCLUDED_GROUP = "VAL_005"
    VAL_MODEL_NOT_STORABLE = "VAL_006"
    VAL_CONDITION_DOMAIN_LITERAL_INVALID = "VAL_007"
    VAL_CONDITION_DOMAIN_MODEL_INVALID = "VAL_008"
    VAL_CALENDAR_NOT_FULLY_FIXED = "VAL_009"
    VAL_CALENDAR_NO_ATTENDANCE = "VAL_010"
    VAL_CALENDAR_PATH_NOT_MANY2ONE = "VAL_011"
    VAL_CALENDAR_PATH_WRONG_TARGET = "VAL_012"
    VAL_START_FIELD_WRONG_MODEL = "VAL_013"
    VAL_START_FIELD_NOT_DATETIME = "VAL_014"
    VAL_RESET_FIELD_WRONG_MODEL = "VAL_015"
    VAL_ESCALATION_PERCENT_NOT_INTEGER = "VAL_016"
    VAL_ESCALATION_ACTION_MODEL_MISMATCH = "VAL_017"
    VAL_ESCALATION_EMAIL_FIELD_REQUIRED = "VAL_018"
    VAL_ESCALATION_EMAIL_FIELD_WRONG_MODEL = "VAL_019"
    VAL_MODEL_LOCKED_HAS_TASKS = "VAL_020"
    VAL_SOURCE_RECORD_MISSING = "VAL_021"
    VAL_APPLY_JOB_ALREADY_RUNNING = "VAL_022"
    VAL_APPLY_DEFINITION_INACTIVE = "VAL_023"

    # --- Access/permission errors (ir.exceptions.AccessError) ---
    ACC_RECALCULATE_SLA_MANAGER_ONLY = "ACC_001"
    ACC_REEVALUATE_SLA_MANAGER_ONLY = "ACC_002"
    ACC_MARK_RESOLVED_SLA_MANAGER_ONLY = "ACC_003"
    ACC_REEVALUATE_EVENTS_SLA_MANAGER_ONLY = "ACC_004"

    # --- Informational notes stored on sla.event.note (shown to users in
    # the Event Log, not raised as exceptions) ---
    NOTE_CALENDAR_PATH_UNUSABLE = "NOTE_001"
    NOTE_CALENDAR_NOT_USABLE = "NOTE_002"
    NOTE_CALENDAR_FALLBACK_COMPANY = "NOTE_003"
    NOTE_CALENDAR_FALLBACK_24X7 = "NOTE_004"
    NOTE_START_FIELD_EMPTY_USE_NOW = "NOTE_005"
    NOTE_FIELDS_CHANGED = "NOTE_006"
    NOTE_TARGET_HOURS_NEGATIVE = "NOTE_007"
    NOTE_DEADLINE_OUT_OF_RANGE = "NOTE_008"
    NOTE_BATCH_EVALUATE_ERROR = "NOTE_009"
    NOTE_BACKGROUND_PROCESSING_ERROR = "NOTE_010"
    NOTE_ESCALATION_EMAIL_BODY = "NOTE_011"
    NOTE_RECALCULATE_APPLIED = "NOTE_012"
    NOTE_REEVALUATE_CHANGED = "NOTE_013"
    NOTE_REEVALUATE_UNCHANGED = "NOTE_014"
    NOTE_APPLY_JOB_FAILED = "NOTE_015"

    # --- Notifications shown to the user after an action button ---
    INF_ENABLE_WITHOUT_START_TITLE = "INF_001"
    INF_ENABLE_WITHOUT_START_BODY = "INF_002"
    INF_RECALCULATE_RESULT_TITLE = "INF_003"
    INF_RECALCULATE_RESULT_BODY = "INF_004"
    INF_REEVALUATE_RESULT_TITLE = "INF_005"
    INF_REEVALUATE_RESULT_BODY = "INF_006"
    INF_APPLY_RESULT_TITLE = "INF_007"
    INF_APPLY_RESULT_BODY = "INF_008"
    INF_APPLY_RESULT_CONTINUES = "INF_009"

    # --- Computed display labels shown read-only in list/kanban views (not
    # errors, not event notes) ---
    DISP_ESCALATION_NOT_CONFIGURED = "DISP_001"
    DISP_ESCALATION_SERVER_ACTION = "DISP_002"
    DISP_ESCALATION_EMAIL_FIXED = "DISP_003"
    DISP_ESCALATION_EMAIL_FIELD = "DISP_004"
    DISP_ESCALATION_EMAIL_RESPONSIBLE = "DISP_005"


MESSAGE_IDS = {
    MessageCode.VAL_LOG_RETENTION_DAYS_POSITIVE: _ltparams(_lt(
        "Event log retention (days) must be greater than 0.")),
    MessageCode.VAL_DUE_SOON_HOURS_POSITIVE: _ltparams(_lt(
        "The \"due soon\" window must be greater than 0 hours.")),
    MessageCode.VAL_BATCH_SIZE_POSITIVE: _ltparams(_lt(
        "Background processing batch size must be greater than 0.")),
    MessageCode.VAL_DEFINITION_HAS_TASKS: _ltparams(_lt(
        "Cannot delete an SLA definition that still has referenced tasks. "
        "Archive it instead of deleting.")),
    MessageCode.VAL_MODEL_EXCLUDED_GROUP: _ltparams(_lt(
        "Cannot attach SLA to model '%s': the model belongs to an excluded "
        "group (sla.*, ir.*, mail.*).")),
    MessageCode.VAL_MODEL_NOT_STORABLE: _ltparams(_lt(
        "Cannot attach SLA to model '%s': the model is transient, abstract, "
        "or has no dedicated table.")),
    MessageCode.VAL_CONDITION_DOMAIN_LITERAL_INVALID: _ltparams(_lt(
        "Condition '%s' is not a valid domain literal: %s")),
    MessageCode.VAL_CONDITION_DOMAIN_MODEL_INVALID: _ltparams(_lt(
        "Condition '%s' is not valid for model '%s': %s")),
    MessageCode.VAL_CALENDAR_NOT_FULLY_FIXED: _ltparams(_lt(
        "The definition's fixed calendar must be of type 'fully_fixed' "
        "(REQ-INT-009).")),
    MessageCode.VAL_CALENDAR_NO_ATTENDANCE: _ltparams(_lt(
        "Calendar '%s' has no working hours configured for any day of the "
        "week; it cannot be used for SLA.")),
    MessageCode.VAL_CALENDAR_PATH_NOT_MANY2ONE: _ltparams(_lt(
        "Invalid calendar path '%s': '%s' is not a Many2one field on "
        "model '%s'.")),
    MessageCode.VAL_CALENDAR_PATH_WRONG_TARGET: _ltparams(_lt(
        "Calendar path '%s' must end at model 'resource.calendar', not "
        "'%s'.")),
    MessageCode.VAL_START_FIELD_WRONG_MODEL: _ltparams(_lt(
        "The start-marker field must belong to model '%s'.")),
    MessageCode.VAL_START_FIELD_NOT_DATETIME: _ltparams(_lt(
        "The start-marker field must be of type Datetime.")),
    MessageCode.VAL_RESET_FIELD_WRONG_MODEL: _ltparams(_lt(
        "Reset-trigger field '%s' must belong to model '%s'.")),
    MessageCode.VAL_ESCALATION_PERCENT_NOT_INTEGER: _ltparams(_lt(
        "Percent '%s' is not an integer. Enter a positive integer, e.g. "
        "75 or 100.")),
    MessageCode.VAL_ESCALATION_ACTION_MODEL_MISMATCH: _ltparams(_lt(
        "The server action belongs to model '%s' but the definition "
        "belongs to model '%s'.")),
    MessageCode.VAL_ESCALATION_EMAIL_FIELD_REQUIRED: _ltparams(_lt(
        "'%s' is required for this escalation rule's action type.")),
    MessageCode.VAL_ESCALATION_EMAIL_FIELD_WRONG_MODEL: _ltparams(_lt(
        "Field '%s' is not usable here; it must be a %s field on the "
        "definition's model.")),
    MessageCode.VAL_MODEL_LOCKED_HAS_TASKS: _ltparams(_lt(
        "Cannot change the model of an SLA definition that already has "
        "tasks. Create a new definition for the other model instead.")),
    MessageCode.VAL_SOURCE_RECORD_MISSING: _ltparams(_lt(
        "Source record no longer exists.")),
    MessageCode.VAL_APPLY_JOB_ALREADY_RUNNING: _ltparams(_lt(
        "This SLA already has a manual apply run that is queued or "
        "running. Wait for it to finish or cancel it first.")),
    MessageCode.VAL_APPLY_DEFINITION_INACTIVE: _ltparams(_lt(
        "Enable the SLA definition before applying it to existing "
        "records.")),
    MessageCode.ACC_RECALCULATE_SLA_MANAGER_ONLY: _ltparams(_lt(
        "Only an SLA Manager can use the \"Apply Current Settings\" action.")),
    MessageCode.ACC_REEVALUATE_SLA_MANAGER_ONLY: _ltparams(_lt(
        "Only an SLA Manager can use the \"Re-check Conditions\" action.")),
    MessageCode.ACC_REEVALUATE_EVENTS_SLA_MANAGER_ONLY: _ltparams(_lt(
        "Only an SLA Manager can re-evaluate SLA error events.")),
    MessageCode.ACC_MARK_RESOLVED_SLA_MANAGER_ONLY: _ltparams(_lt(
        "Only an SLA Manager can mark SLA events as resolved.")),
    MessageCode.NOTE_CALENDAR_PATH_UNUSABLE: _ltparams(_lt(
        "Calendar path '%s' is empty or the calendar cannot be used.")),
    MessageCode.NOTE_CALENDAR_NOT_USABLE: _ltparams(_lt(
        "Calendar '%s' cannot be used (flexible type or no working "
        "hours).")),
    MessageCode.NOTE_CALENDAR_FALLBACK_COMPANY: _ltparams(_lt(
        " Using company '%s' default calendar because the record's "
        "calendar cannot be used.")),
    MessageCode.NOTE_CALENDAR_FALLBACK_24X7: _ltparams(_lt(
        " The company default calendar cannot be used either; the task "
        "runs 24x7.")),
    MessageCode.NOTE_START_FIELD_EMPTY_USE_NOW: _ltparams(_lt(
        "Start-marker field '%s' is empty; using the current time "
        "instead.")),
    MessageCode.NOTE_FIELDS_CHANGED: _ltparams(_lt(
        "Changed fields: %s")),
    MessageCode.NOTE_TARGET_HOURS_NEGATIVE: _ltparams(_lt(
        "Target duration is negative (%s); task was not created.")),
    MessageCode.NOTE_DEADLINE_OUT_OF_RANGE: _ltparams(_lt(
        "Could not plan a deadline within the supported range (fully "
        "covered by non-working time).")),
    MessageCode.NOTE_BATCH_EVALUATE_ERROR: _ltparams(_lt(
        "Batch evaluation error (before the per-record loop): %s")),
    MessageCode.NOTE_BACKGROUND_PROCESSING_ERROR: _ltparams(_lt(
        "Background processing error: %s")),
    MessageCode.NOTE_ESCALATION_EMAIL_BODY: _ltparams(_lt(
        "<p>SLA \"%s\" reached %s%% on %s.</p>")),
    MessageCode.NOTE_RECALCULATE_APPLIED: _ltparams(_lt(
        "Current settings applied by %s. Target: %s -> %s. Calendar: %s -> "
        "%s. Deadline: %s -> %s.")),
    MessageCode.NOTE_REEVALUATE_CHANGED: _ltparams(_lt(
        "Conditions re-checked by %s. Stage: %s -> %s.")),
    MessageCode.NOTE_REEVALUATE_UNCHANGED: _ltparams(_lt(
        "Conditions re-checked by %s. No change (stage: %s).")),
    MessageCode.NOTE_APPLY_JOB_FAILED: _ltparams(_lt(
        "Manual apply stopped by an unexpected error: %s")),
    MessageCode.INF_ENABLE_WITHOUT_START_TITLE: _ltparams(_lt(
        "Enabled, but nothing will start")),
    MessageCode.INF_ENABLE_WITHOUT_START_BODY: _ltparams(_lt(
        "The Start Condition has no rule, so no record will get an SLA "
        "task. Add a rule to the Start Condition.")),
    MessageCode.INF_RECALCULATE_RESULT_TITLE: _ltparams(_lt(
        "Current settings applied")),
    MessageCode.INF_RECALCULATE_RESULT_BODY: _ltparams(_lt(
        "%s task(s) updated, %s skipped.")),
    MessageCode.INF_REEVALUATE_RESULT_TITLE: _ltparams(_lt(
        "Conditions re-checked")),
    MessageCode.INF_REEVALUATE_RESULT_BODY: _ltparams(_lt(
        "%s task(s) checked, %s changed stage.")),
    MessageCode.INF_APPLY_RESULT_TITLE: _ltparams(_lt(
        "Applied to existing records")),
    MessageCode.INF_APPLY_RESULT_BODY: _ltparams(_lt(
        "%s record(s) processed, %s task(s) created, %s error(s). %s")),
    MessageCode.INF_APPLY_RESULT_CONTINUES: _ltparams(_lt(
        "The remaining records continue in the background.")),
    MessageCode.DISP_ESCALATION_NOT_CONFIGURED: _ltparams(_lt(
        "Not configured yet")),
    MessageCode.DISP_ESCALATION_SERVER_ACTION: _ltparams(_lt(
        "Run Server Action: %s")),
    MessageCode.DISP_ESCALATION_EMAIL_FIXED: _ltparams(_lt(
        "Send Email to %s")),
    MessageCode.DISP_ESCALATION_EMAIL_FIELD: _ltparams(_lt(
        "Send Email to the '%s' field on %s")),
    MessageCode.DISP_ESCALATION_EMAIL_RESPONSIBLE: _ltparams(_lt(
        "Send Email to the '%s' of %s")),
}


def get_message(message_code, *args):
    """Lấy message theo mã, dịch + thế tham số theo locale hiện hành.

    Raise `KeyError` nếu mã không tồn tại (cố ý THẤT BẠI RÕ thay vì trả
    chuỗi rỗng, để lỗi gõ sai mã bị phát hiện ngay khi test/chạy thay vì
    chỉ lộ ra khi user thấy thông báo trống).
    """
    if message_code not in MESSAGE_IDS:
        raise KeyError(
            "Unknown message code '%s' in dwo_sla_core.constants.message"
            % message_code)
    return str(MESSAGE_IDS[message_code](*args))
