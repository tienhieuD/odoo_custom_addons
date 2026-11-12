# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError

from ..constants.message import MessageCode, get_message


class SlaEscalation(models.Model):
    """Mốc escalation của một định nghĩa: tại phần trăm nào báo cho ai/chạy gì.

    Logic: khi task chạm phần trăm, engine gửi email thông báo (mặc định,
    dễ dùng) hoặc chạy server action (nâng cao) trên record gốc, rồi đánh
    dấu mốc đã xử lý xong (FUNC-023). Lỗi (ví dụ không resolve được email)
    chỉ được ghi lại, KHÔNG thử lại -- D12 (TASKS.md): bỏ cơ chế retry vì
    lỗi action/email gần như luôn deterministic (bug, thiếu quyền, thiếu
    field), thử lại sau vài phút không tự sửa được lỗi đó; email qua
    `mail.mail` đã có hàng chờ gửi lại riêng của Odoo.
    Refs: REQ-FUNC-023, 038
    """
    _name = 'sla.escalation'
    _description = "SLA Escalation Rule"
    _order = 'sequence, percent, id'

    definition_id = fields.Many2one(
        'sla.definition', string="Definition", required=True,
        ondelete='cascade', index=True,
        help=('The SLA definition this escalation belongs to. Example: '
              '"Ticket Response - Priority 1".'))
    sequence = fields.Integer(default=10,
        help=('Order used when several escalations are due at the same '
              'moment; lower numbers run first. Example: 10 for the warning, '
              '20 for the manager alert.'))
    # D6 (ĐÃ CHỐT, xem TASKS.md): FLOAT8 thay vì INT4 gốc của 030 để từ chối
    # rõ số không nguyên theo AC2, thay vì ORM Integer làm tròn âm thầm.
    # Refs: REQ-FUNC-023
    percent = fields.Float(
        string="Percent", required=True,
        help=('Percentage of the target time at which the action runs. Must '
              'be a whole number greater than 0; values above 100 fire after '
              'the deadline. Example: 75 fires after 3 of 4 hours; 120 fires '
              '48 minutes after the deadline.'))
    # Refs: D12 (TASKS.md) -- email là mặc định để người dùng phổ thông dùng
    # được ngay, không cần tạo Server Action; server_action vẫn có cho nhu
    # cầu nâng cao (gọi webhook, ghi field khác, v.v).
    action_type = fields.Selection(
        [('email', "Send Email"), ('server_action', "Run Server Action")],
        string="Action Type", required=True, default='email',
        help=('Send Email: notify someone directly, no setup beyond this '
              'rule. Run Server Action: execute a custom automation rule '
              '(Settings > Technical > Server Actions) for advanced cases.'))
    # Refs: REQ-FUNC-038 -- required chỉ khi action_type=server_action (xem
    # _check_action_type), không required=True ở field để không ép mọi mốc
    # kiểu email phải chọn 1 server action vô nghĩa.
    action_id = fields.Many2one(
        'ir.actions.server', string="Server Action",
        ondelete='restrict',
        help=("Server action executed on the SLA's source record when the "
              'percentage is reached, on the same model as the definition. '
              'Example: an action that posts a note or emails the team '
              'leader.'))
    # Refs: D12 (TASKS.md)
    email_recipient_type = fields.Selection(
        [
            ('responsible', "Responsible User/Partner on Record"),
            ('field', "Email Field on Record"),
            ('fixed', "Fixed Email Address"),
        ],
        string="Notify", default='responsible',
        help=('Responsible: read a user or partner field on the source '
              "record and use that person's email, e.g. Assignee or "
              'Customer. Email Field: read a plain email address field on '
              'the record. Fixed: always the same address, e.g. a team '
              'distribution list.'))
    email_field_id = fields.Many2one(
        'ir.model.fields', string="Record Field",
        help=('Field on the SLA\'s model read to find the recipient: a '
              'User/Partner field (Many2one, or One2many/Many2many for '
              'several people, e.g. Followers) for "Responsible", or a '
              'text field holding an email address for "Email Field". '
              'Example: "Assigned to" or "Customer Email".'))
    email_fixed_address = fields.Char(
        string="Fixed Email Address",
        help='Email address always notified by this rule. Example: '
             '"support-team@example.com".')
    # Refs: scope-add "email template" -- mặc định trỏ template dựng sẵn
    # (data/mail_templates.xml), người dùng có thể đổi sang template khác
    # cùng model sla.task hoặc xóa để dùng nội dung mặc định đơn giản
    # (NOTE_ESCALATION_EMAIL_BODY, xem _send_escalation_email).
    email_template_id = fields.Many2one(
        'mail.template', string="Email Template",
        domain="[('model', '=', 'sla.task')]",
        default=lambda self: self.env.ref(
            'dwo_sla_core.mail_template_escalation_default', raise_if_not_found=False),
        help=('Email template used for the subject and body, rendered on '
              'the SLA Task (so it can reference the SLA name, percentage, '
              'deadline, etc.). The "To" address is always the one resolved '
              'by Notify above, regardless of what the template itself '
              'specifies. Leave empty to send a short built-in message '
              'instead of using a template.'))
    # Refs: scope-add "escalation list UX" -- list view chỉ hiện 2 cột gọn
    # (percent_display, display_name), form đầy đủ mở qua dialog khi bấm
    # dòng/Add a line (xem views/sla_definition_views.xml). Cả 2 field dùng
    # get_message() nên tự dịch lại theo ngôn ngữ của người xem tại thời
    # điểm đọc (không lưu cứng theo ngôn ngữ lúc tạo).
    percent_display = fields.Char(
        string="Percent (display)", compute='_compute_percent_display',
        help='Percent formatted with a % sign for the list view.')
    display_name = fields.Char(
        string="Action", compute='_compute_display_name',
        help=('Human-readable summary of this rule: who gets emailed, or '
              'which Server Action runs. Example: "Send Email to the '
              '\'Assigned to\' of Project Task".'))

    @api.depends('percent')
    def _compute_percent_display(self):
        """"75" -> "75%"; percent đã bị ràng buộc là số nguyên (D6, VAL_016)."""
        for escalation in self:
            escalation.percent_display = "%d%%" % round(escalation.percent)

    @api.depends('action_type', 'action_id.name', 'email_recipient_type',
                 'email_fixed_address', 'email_field_id.field_description',
                 'definition_id.model_id.name')
    def _compute_display_name(self):
        """Tóm tắt 1 dòng: ai được báo bằng gì, dùng cho list + form title.

        Logic: 4 nhánh theo `action_type`/`email_recipient_type`, khớp
        validate ở `_check_action_type`; dòng mới chưa đủ cấu hình (field
        bắt buộc còn trống) trả về nhãn trung tính thay vì chuỗi rỗng/lỗi.
        Refs: scope-add "escalation list UX"
        """
        for escalation in self:
            escalation.display_name = escalation._build_action_summary()

    def _build_action_summary(self):
        self.ensure_one()
        model_name = self.definition_id.model_id.name or ''
        if self.action_type == 'server_action':
            if not self.action_id:
                return get_message(MessageCode.DISP_ESCALATION_NOT_CONFIGURED)
            return get_message(
                MessageCode.DISP_ESCALATION_SERVER_ACTION, self.action_id.name)

        if self.email_recipient_type == 'fixed':
            if not self.email_fixed_address:
                return get_message(MessageCode.DISP_ESCALATION_NOT_CONFIGURED)
            return get_message(
                MessageCode.DISP_ESCALATION_EMAIL_FIXED, self.email_fixed_address)

        if not self.email_field_id:
            return get_message(MessageCode.DISP_ESCALATION_NOT_CONFIGURED)
        field_label = self.email_field_id.field_description
        if self.email_recipient_type == 'responsible':
            return get_message(
                MessageCode.DISP_ESCALATION_EMAIL_RESPONSIBLE, field_label, model_name)
        return get_message(
            MessageCode.DISP_ESCALATION_EMAIL_FIELD, field_label, model_name)

    _percent_check = models.Constraint(
        'CHECK(percent > 0)', "Percent must be greater than 0.")

    @api.constrains('percent')
    def _check_percent(self):
        """Từ chối percent không phải số nguyên dương (D6: field là FLOAT8).

        Logic: CHECK `percent > 0` chỉ bắt được giá trị <= 0; phần "không
        nguyên" (REQ-FUNC-023 AC2, ví dụ 75,5) phải kiểm ở Python vì FLOAT8
        không có CHECK số nguyên ở database. Dùng float_is_zero để so sánh an
        toàn, không so sánh `==` trực tiếp trên số thực.
        Refs: REQ-FUNC-023 AC2, D6 (TASKS.md)
        """
        for escalation in self:
            rounded = round(escalation.percent)
            if not tools.float_is_zero(escalation.percent - rounded, precision_digits=6):
                raise ValidationError(get_message(
                    MessageCode.VAL_ESCALATION_PERCENT_NOT_INTEGER,
                    escalation.percent))

    @api.constrains('definition_id', 'action_type', 'action_id',
                     'email_recipient_type', 'email_field_id',
                     'email_fixed_address', 'email_template_id')
    def _check_action_type(self):
        """Kiểm tra cấu hình của mốc khớp với `action_type` đã chọn.

        Logic: `server_action` cần `action_id` cùng model với định nghĩa
        (REQ-FUNC-038, giữ nguyên hành vi cũ). `email` cần đủ thông tin theo
        `email_recipient_type`: field thuộc đúng model cho 'responsible'/
        'field', hoặc địa chỉ cố định cho 'fixed'. 'responsible' chấp nhận
        Many2one/One2many/Many2many trỏ tới res.users/res.partner (scope-add:
        X2many gửi 1 email cho TẤT CẢ người trong danh sách, nhiều địa chỉ
        trong cùng `email_to`, xem `_resolve_email_recipient`); 'field' chỉ
        nhận Char (email trực tiếp trên record, không có khái niệm "nhiều
        người nhận" cho kiểu này). Field sai kiểu/sai model bị từ chối ở đây
        thay vì chỉ lộ ra lúc chạy nền (D12, TASKS.md).
        Refs: REQ-FUNC-038, D12
        """
        for escalation in self:
            model_name = escalation.definition_id.model_id.model
            if escalation.action_type == 'server_action':
                if not escalation.action_id:
                    raise ValidationError(get_message(
                        MessageCode.VAL_ESCALATION_EMAIL_FIELD_REQUIRED,
                        "Server Action"))
                action_model = escalation.action_id.model_id.model
                if model_name and action_model and action_model != model_name:
                    raise ValidationError(get_message(
                        MessageCode.VAL_ESCALATION_ACTION_MODEL_MISMATCH,
                        action_model, model_name))
                continue

            if escalation.email_template_id and escalation.email_template_id.model != 'sla.task':
                raise ValidationError(get_message(
                    MessageCode.VAL_ESCALATION_EMAIL_FIELD_WRONG_MODEL,
                    escalation.email_template_id.name, "sla.task"))

            if escalation.email_recipient_type == 'fixed':
                if not escalation.email_fixed_address:
                    raise ValidationError(get_message(
                        MessageCode.VAL_ESCALATION_EMAIL_FIELD_REQUIRED,
                        "Fixed Email Address"))
                continue

            field = escalation.email_field_id
            if not field:
                raise ValidationError(get_message(
                    MessageCode.VAL_ESCALATION_EMAIL_FIELD_REQUIRED,
                    "Record Field"))
            if model_name and field.model != model_name:
                raise ValidationError(get_message(
                    MessageCode.VAL_ESCALATION_EMAIL_FIELD_WRONG_MODEL,
                    field.name, model_name))
            if escalation.email_recipient_type == 'responsible':
                if field.ttype not in ('many2one', 'one2many', 'many2many') \
                        or field.relation not in ('res.users', 'res.partner'):
                    raise ValidationError(get_message(
                        MessageCode.VAL_ESCALATION_EMAIL_FIELD_WRONG_MODEL,
                        field.name, "res.users / res.partner"))
            elif field.ttype != 'char':
                raise ValidationError(get_message(
                    MessageCode.VAL_ESCALATION_EMAIL_FIELD_WRONG_MODEL,
                    field.name, "Char"))

    def _resolve_email_recipient(self, record):
        """Trả email người nhận theo `email_recipient_type`, hoặc False.

        Logic: 'fixed' trả thẳng địa chỉ cấu hình; 'field'/'responsible' đọc
        `email_field_id` trên `record`. 'field' là chuỗi email trực tiếp.
        'responsible' là Many2one/One2many/Many2many tới res.users/
        res.partner (REQ-FUNC-065 AC2 mở rộng, scope-add): dùng `.mapped()`
        nên chạy đúng cho cả 2 trường hợp -- Many2one trả recordset 0/1 bản
        ghi, X2many trả recordset nhiều bản ghi -- rồi gộp các email khác
        rỗng thành MỘT chuỗi phân tách bằng dấu phẩy, đúng định dạng
        `mail.mail.email_to` (gửi 1 email, nhiều "To", không gửi riêng từng
        người). Trả False khi record rỗng hoặc không có email nào, để nơi
        gọi ghi lỗi thay vì gửi mail không có người nhận.
        Refs: D12 (TASKS.md), REQ-FUNC-065
        """
        self.ensure_one()
        if self.email_recipient_type == 'fixed':
            return self.email_fixed_address or False
        if not record or not self.email_field_id:
            return False
        value = record[self.email_field_id.name]
        if self.email_recipient_type == 'field':
            return value or False
        emails = [email for email in value.mapped('email') if email]
        return ','.join(emails) if emails else False

    @api.model_create_multi
    def create(self, vals_list):
        """Tạo mốc mới; task đã qua ngưỡng % của mốc này bỏ qua, không bắn bù.

        Logic: với mỗi mốc vừa tạo, tìm các task đang hoạt động
        (`in_progress`/`paused`) của cùng định nghĩa; task nào đã có phần
        trăm hiện tại >= phần trăm của mốc mới thì đánh dấu mốc đã xử lý
        xong NGAY (không chạy action, không ghi event) để Background
        Processor không bao giờ bắn bù cho task đó (REQ-FUNC-053 AC1).
        Task chưa tới ngưỡng thì không đụng tới, sẽ bắn bình thường khi tới
        mức (AC2).
        Refs: REQ-FUNC-053
        """
        escalations = super().create(vals_list)
        tasks = self.env['sla.task'].sudo().search([
            ('sla_id', 'in', escalations.definition_id.ids),
            ('stage', 'in', ('in_progress', 'paused')),
        ])
        tasks._mark_passed_escalations_done(escalations)
        return escalations
