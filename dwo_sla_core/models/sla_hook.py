# -*- coding: utf-8 -*-
import logging

from odoo import api, models

from .sla_definition import EXCLUDED_MODEL_PREFIXES

_logger = logging.getLogger(__name__)


class SlaDefinitionHook(models.Model):
    """Hook toàn cục: patch `create`/`write`/`_compute_field_value` của các
    model có định nghĩa SLA để gọi Engine ngay sau khi ORM ghi xong.

    Logic: giống cơ chế `base_automation` (R6, AD-01) — chỉ patch model có
    định nghĩa đang bật HOẶC định nghĩa đã archive nhưng còn task đang hoạt
    động (để task cũ vẫn được Engine xử lý dù không còn attach mới,
    REQ-FUNC-007/§7.2); model khác không bị đụng tới (REQ-PERF-001). Patch
    được cài lại (gỡ rồi cài lại toàn bộ) mỗi khi `_register_sla_hook` được
    gọi (tạo/sửa model_id hoặc active/xóa định nghĩa). `_register_hook`
    được framework Odoo tự gọi một lần lúc nạp registry (STEP 9).
    Refs: REQ-FUNC-001, 004, 005, 007, 013, AD-01, R-01
    """
    _inherit = 'sla.definition'

    def _get_hook_models(self):
        """Tập model (tên) cần patch: định nghĩa bật, hoặc archive còn task hoạt động.

        Refs: AD-01, TAD §7.2
        """
        active_models = set(
            self.env['sla.definition'].sudo().search([('active', '=', True)])
            .mapped('model_name'))
        # Một truy vấn cho mọi định nghĩa tắt còn task hoạt động, không search_count
        # theo từng định nghĩa (đường nóng: gọi ở đầu mỗi lượt đánh giá).
        archived_with_task = {
            definition.model_name
            for (definition,) in self.env['sla.task'].sudo()._read_group(
                [('stage', 'in', ('in_progress', 'paused')),
                 ('sla_id.active', '=', False)],
                ['sla_id'])}
        # Không bao giờ patch model bị cấm (ir.*, sla.*, mail.*, transient...), kể cả khi
        # có định nghĩa lọt qua (ví dụ ghi thẳng SQL) — REQ-FUNC-002.
        return {
            name for name in (active_models | archived_with_task) - {False}
            if not name.startswith(EXCLUDED_MODEL_PREFIXES)
            and name in self.env and not (
                self.env[name]._transient or self.env[name]._abstract
                or not self.env[name]._auto)}

    def _get_watched_field_names(self, model_name):
        """Tên field của `model_name` mà mọi định nghĩa (kể cả archive) có dùng.

        Logic: gộp field đầu mỗi đường dẫn trong 6 domain, field reset, field
        retroactive và `company_id` (khi định nghĩa gán công ty); domain không đọc
        được thì bỏ qua (Engine sẽ báo lỗi riêng). Có dấu '*' khi có định nghĩa
        reset theo điều kiện thuần (không field theo dõi) nên mọi lần ghi đều
        phải đánh giá (REQ-FUNC-013).
        Refs: REQ-FUNC-005, REQ-PERF-001
        """
        names = set()
        definitions = self.env['sla.definition'].sudo().with_context(
            active_test=False).search([('model_name', '=', model_name)])
        for definition in definitions:
            for cond in ('start', 'cancel', 'pause', 'resume', 'stop', 'reset'):
                try:
                    domain = definition._get_domain(cond)
                except Exception:  # noqa: BLE001 -- domain hỏng: Engine ghi event error riêng
                    continue
                for leaf in domain or []:
                    if isinstance(leaf, (list, tuple)) and len(leaf) == 3:
                        names.add(str(leaf[0]).split('.')[0])
            names.update(definition.reset_field_ids.mapped('name'))
            try:
                has_reset = definition._get_domain('reset') is not None
            except Exception:  # noqa: BLE001 -- domain hỏng: Engine ghi event error riêng
                has_reset = False
            if has_reset and not definition.reset_field_ids:
                names.add('*')  # reset theo điều kiện thuần: mọi lần ghi đều cần đánh giá
            if definition.company_id:
                names.add('company_id')
            if definition.start_field_id:
                names.add(definition.start_field_id.name)
        # Field điều kiện không lưu (compute/related) đổi khi field nguồn đổi: thêm các
        # field nguồn (đệ quy) để ghi field nguồn vẫn kích hoạt đánh giá như trước.
        model = self.env[model_name]
        pending, seen = list(names - {'*'}), set()
        while pending:
            name = pending.pop()
            if name in seen:
                continue
            seen.add(name)
            field = model._fields.get(name)
            if field is None or field.store:
                continue
            for dependency in field.get_depends(model)[0]:
                head = dependency.split('.')[0]
                names.add(head)
                pending.append(head)
        return names

    def _register_hook(self):
        """Patch `create`, `write`, `_compute_field_value` trên từng model có SLA.

        Logic: các hàm patch được định nghĩa bên trong (không phải method
        của class) để closure đúng theo từng lời gọi, giống
        `base_automation._register_hook` (xem TAD AD-01, đối chiếu source
        `base_automation.py` dòng ~846-1062). Patch gọi
        `Engine.evaluate(records, now, changed)` SAU khi ORM gốc đã ghi
        xong, lỗi của Engine không được lan ra ngoài (REQ-FUNC-030): Engine
        tự cô lập theo record/định nghĩa, nhưng bọc thêm một lớp phòng thủ ở
        đây cho chắc chắn.
        Refs: REQ-FUNC-004, 005, 030, AD-01
        """
        def make_create():
            @api.model_create_multi
            def create(self, vals_list, **kw):
                records = create.origin(self, vals_list, **kw)  # pyright: ignore[reportFunctionMemberAccess]
                created = self.env.cr.__dict__.setdefault('_sla_created', set())
                keys = {(record._name, record.id) for record in records}
                added = keys - created
                created |= added
                try:
                    self.env['sla.engine']._safe_evaluate(records, changed=set())
                finally:
                    created -= added
                return records
            return create

        def make_write():
            def write(self, vals, **kw):
                tracked_fnames = [
                    name for name in vals
                    if name in self._fields and self._fields[name].store]
                old_values = {
                    record.id: {name: record[name] for name in tracked_fnames}
                    for record in self.filtered('id')
                }
                result = write.origin(self, vals, **kw)  # pyright: ignore[reportFunctionMemberAccess]
                changed_by_id = {}
                for record in self.filtered('id'):
                    old = old_values.get(record.id, {})
                    changed_by_id[record.id] = {
                        name for name in tracked_fnames if old.get(name) != record[name]}
                # Gom record có cùng tập field đổi để đánh giá theo lô, không từng
                # record một (AD-03, REQ-PERF-002).
                groups = {}
                for record in self.filtered('id'):
                    key = frozenset(changed_by_id.get(record.id, set()))
                    groups[key] = groups.get(key, self.browse()) | record
                watched = self.env['sla.definition']._get_watched_field_names(self._name)
                for key, group in groups.items():
                    # Thoát sớm: không field nào định nghĩa dùng vừa đổi -> kết quả điều
                    # kiện không đổi, bỏ qua đánh giá (REQ-FUNC-005, REQ-PERF-001).
                    if '*' in watched or key & watched:
                        self.env['sla.engine']._safe_evaluate(group, changed=set(key))
                return result
            return write

        def make_compute_field_value():
            def _compute_field_value(self, field):
                # Chỉ field compute CÓ LƯU mới quan sát được qua đường này;
                # field compute KHÔNG LƯU tính lại lúc đọc, không đi qua
                # `_compute_field_value` kèm ghi DB nên hook không biết để
                # đánh giá lại — đây là giới hạn đã biết của REQ-FUNC-042,
                # bù bằng hành động "Đánh giá lại" thủ công (REQ-INT-020).
                stored_fnames = [f.name for f in self.pool.field_computed[field] if f.store]
                result = _compute_field_value.origin(self, field)  # pyright: ignore[reportFunctionMemberAccess]
                # Thoát sớm: chỉ đánh giá khi field vừa tính lại được định nghĩa dùng
                # (điều kiện, field reset, field retroactive) — tránh đánh giá thừa
                # mỗi khi ORM tính lại field không liên quan (REQ-FUNC-005, REQ-PERF-001).
                if stored_fnames and set(stored_fnames) & self.env[
                        'sla.definition']._get_watched_field_names(self._name) - {'*'}:
                    changed = set(stored_fnames)
                    for record in self.filtered('id'):
                        self.env['sla.engine']._safe_evaluate(record, changed=changed)
                return result
            return _compute_field_value

        patched = set()

        def patch(model_class, name, method):
            key = (model_class._name, name)
            if key in patched:
                return
            patched.add(key)
            method.origin = getattr(model_class, name)
            method.sla_patch = True  # dấu đánh dấu cho _ensure_hook_registered (D9/R-01)
            setattr(model_class, name, method)

        for model_name in self._get_hook_models():
            Model = self.env.get(model_name)
            if Model is None:
                _logger.warning(
                    "Định nghĩa SLA trỏ tới model '%s' không tồn tại trong registry; "
                    "bỏ qua patch.", model_name)
                continue
            ModelClass = self.env.registry[model_name]
            patch(ModelClass, 'create', make_create())
            patch(ModelClass, 'write', make_write())
            patch(ModelClass, '_compute_field_value', make_compute_field_value())

    def _ensure_hook_registered(self):
        """Tự phát hiện và phục hồi patch bị mất (giảm thiểu R-01, D9).

        Logic: module khác (vd `base_automation`) có thể gọi `delattr` xóa
        đúng 3 tên hàm ta đã patch trên MỌI model trong registry khi đăng
        ký lại automation rule của chính nó (xem Consequences AD-01) — chỉ
        worker đang xử lý request đó bị mất patch ngay lập tức, các worker
        khác chỉ nạp lại registry khi có tín hiệu `registry_invalidated`
        (có độ trễ). Thay vì chờ tín hiệu, hàm này kiểm tra trực tiếp dấu
        `sla_patch` trên `create` của từng model đang cần patch (đủ đại
        diện, không cần kiểm cả 3 tên) ngay tại thời điểm dùng (đầu
        `process_due` và đầu `evaluate`) — thiếu dấu thì đăng ký lại ngay
        trên chính worker này và ghi log cảnh báo, không chờ tín hiệu toàn
        cục.
        Refs: AD-01 (Consequences, mitigation D9), R-01
        """
        missing = []
        for model_name in self._get_hook_models():
            Model = self.env.get(model_name)
            if Model is None:
                continue
            ModelClass = self.env.registry[model_name]
            if not getattr(ModelClass.create, 'sla_patch', False):
                missing.append(model_name)
        if missing:
            _logger.warning(
                "Hook SLA bị mất patch trên model %s (có thể do module khác "
                "đăng ký lại hook của chính nó); đăng ký lại ngay.", missing)
            self._register_sla_hook()

    def _unregister_hook(self):
        """Gỡ patch đã cài (giống `base_automation._unregister_hook`).

        Logic: chỉ gỡ đúng 3 tên hàm trên TẤT CẢ model trong registry (có
        patch hay không không quan trọng, `delattr` bỏ qua lỗi) — rủi ro mất
        patch do module khác (`base_automation`) gọi `_unregister_hook` của
        chính nó cũng xóa 3 tên này trên model của ta là rủi ro đã biết, ghi
        nhận ở R-01 (TASKS.md/TAD), tự phục hồi bằng cách `_register_sla_hook`
        được gọi lại mỗi khi định nghĩa SLA đổi; nếu patch mất giữa hai lần
        đổi định nghĩa thì cần "Đánh giá lại" thủ công để bù (REQ-FUNC-032).
        Refs: R-01, REQ-FUNC-032
        """
        for ModelClass in self.env.registry.values():
            for name in ('create', 'write', '_compute_field_value'):
                try:
                    delattr(ModelClass, name)
                except AttributeError:
                    pass

    def _register_sla_action_binding(self):
        """Tạo/xóa action "SLA" trong menu Action của record theo tập model đang cần.

        Logic: dùng lại đúng tập model của `_get_hook_models()` (định nghĩa
        bật, hoặc archive còn task hoạt động) để action cũng còn tới khi task
        còn chạy dù định nghĩa cuối đã archive (AC2), và biến mất khi không
        còn gì (AC3); mỗi model có một `ir.actions.act_window` riêng
        (`binding_model_id` trỏ tới model đó) vì domain phải nêu đích danh
        tên model dưới dạng chuỗi literal — không thể dùng chung một action
        cho nhiều model. Action lọc đúng record đang chọn bằng `active_id`
        (biến có sẵn trong domain khi action được gọi từ menu Action của
        record, giống mẫu `base.act_view_currency_rates`). Action chỉ hiện
        cho nhóm SLA qua `group_ids` (AC4). Action do module tự quản lý
        (tạo/xóa động), không phải dữ liệu người dùng nên xóa thẳng, không
        cần `noupdate`.

        Giới hạn đã biết: hàm chỉ được gọi lại khi CHÍNH `sla.definition`
        thay đổi (tạo/sửa/xóa, qua `_register_sla_hook`); nếu task hoạt
        động CUỐI CÙNG của một định nghĩa đã archive hoàn tất mà không có
        định nghĩa nào khác thay đổi sau đó, action "SLA" trên model đó có
        thể còn sót lại tới lần đổi định nghĩa kế tiếp (AC3 edge case ít gặp
        — chấp nhận đánh đổi để tránh chi phí kiểm tra lại trên mọi chuyển
        trạng thái task, tương tự tinh thần R-01 của AD-01).
        Refs: REQ-INT-006
        """
        ActWindow = self.env['ir.actions.act_window'].sudo()
        existing = ActWindow.search([
            ('res_model', '=', 'sla.task'),
            ('binding_type', '=', 'action'),
            ('binding_model_id', '!=', False),
        ])
        existing_by_model = {a.binding_model_id.model: a for a in existing}
        wanted_models = self._get_hook_models()

        for model_name in wanted_models - set(existing_by_model):
            ir_model = self.env['ir.model'].sudo().search(
                [('model', '=', model_name)], limit=1)
            if not ir_model:
                continue
            ActWindow.create({
                'name': "SLA",
                'res_model': 'sla.task',
                'view_mode': 'list,form',
                'binding_model_id': ir_model.id,
                'binding_type': 'action',
                'binding_view_types': 'form',
                'domain': "[('res_model', '=', '%s'), ('res_id', '=', active_id)]"
                          % model_name,
                'group_ids': [(6, 0, self.env.ref('dwo_sla_core.group_sla_user').ids)],
            })

        for model_name, action in existing_by_model.items():
            if model_name not in wanted_models:
                action.unlink()
