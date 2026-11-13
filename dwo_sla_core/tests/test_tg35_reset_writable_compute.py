# -*- coding: utf-8 -*-
"""TG-35: reset theo field lưu ghi được (stored compute, readonly=False) chỉ bắn một lần (task 021).

Mô phỏng `sale.order.validity_date`: field lưu tính từ field khác nhưng người dùng ghi tay được.
Refs: REQ-FUNC-005, 012, 013, 042
"""
from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
MODEL = 'x_sla_rst_order'


@tagged(*TAGS, 'tg_35')
class TestResetWritableCompute(SlaCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rst_model = cls.env['ir.model'].create({
            'name': "SLA RST Order", 'model': MODEL, 'state': 'manual'})

        def field(name, ttype, **vals):
            return cls.env['ir.model.fields'].create({
                'name': name, 'model_id': cls.rst_model.id, 'ttype': ttype,
                'state': 'manual', 'field_description': name, **vals})

        field('x_stage', 'selection', selection_ids=[
            (0, 0, {'value': v, 'name': v, 'sequence': i}) for i, v in enumerate(('draft', 'sent', 'done'))])
        field('x_weight', 'integer')
        field('x_due', 'integer', store=True, readonly=False, depends='x_weight', compute=(
            "for rec in self:\n    rec['x_due'] = (rec.x_weight or 0) * 2"))
        cls.due_field = cls.env['ir.model.fields']._get(MODEL, 'x_due')
        cls.env['sla.definition']._register_sla_hook()

    def flush_all_(self):
        """Odoo 13 có Model.flush(); Odoo 12 ghi ngay, không có flush."""
        if hasattr(self.env['base'], 'flush'):
            self.env['base'].flush()

    def make_def(self, **vals):
        base = {'name': "DEF-RST", 'model_id': self.rst_model.id, 'duration': 4,
                'schedule_source': 'none', 'start_domain': "[('x_stage', '=', 'sent')]",
                'stop_domain': "[('x_stage', '=', 'done')]", 'active': True,
                'reset_domain': "[('id', '!=', 0)]", 'reset_field_ids': [(6, 0, self.due_field.ids)]}
        base.update(vals)
        return self.Definition.create(base)

    def counts(self, record, definition):
        tasks = self.Task.sudo().search([('res_model', '=', MODEL), ('res_id', '=', record.id),
                                         ('sla_id', '=', definition.id)])
        events = tasks.event_ids.mapped('event')
        return len(tasks), events.count('reset')

    def run_case(self, vals, **def_vals):
        d = self.make_def(**def_vals)
        with self.at(T0):
            rec = self.env[MODEL].create({'x_stage': 'sent', 'x_weight': 5})
        self.assertEqual(self.counts(rec, d), (1, 0))
        with self.at(T0 + hours(1)):
            rec.write(vals)
            self.flush_all_()
        return self.counts(rec, d)

    def test_rst_001_write_stored_compute_field(self):
        """Ghi tay field lưu tính được: đúng một reset, đúng một task mới."""
        self.assertEqual(self.run_case({'x_due': 99}), (2, 1))

    def test_rst_002_write_with_dependency(self):
        """Ghi cả field nguồn và field lưu tính được trong một lần ghi."""
        self.assertEqual(self.run_case({'x_weight': 7, 'x_due': 99}), (2, 1))

    def test_rst_003_write_dependency_only(self):
        """Chỉ ghi field nguồn: compute đổi x_due -> một reset."""
        self.assertEqual(self.run_case({'x_weight': 7}), (2, 1))

    def test_rst_004_reset_complete(self):
        self.assertEqual(self.run_case({'x_due': 99}, reset_action='complete'), (2, 1))

    def run_two(self, first, second, flush_between=False):
        d = self.make_def()
        with self.at(T0):
            rec = self.env[MODEL].create({'x_stage': 'sent', 'x_weight': 5})
        with self.at(T0 + hours(1)):
            rec.write(first)
            if flush_between:
                self.flush_all_()
            rec.write(second)
            self.flush_all_()
        return self.counts(rec, d)

    def test_rst_005_pending_recompute_then_explicit_write(self):
        """Hồi quy 021: field nguồn đổi (x_due chờ tính lại) rồi ghi tay x_due, chưa flush: một reset, không hai."""
        self.assertEqual(self.run_two({'x_weight': 7}, {'x_due': 99}), (2, 1))

    def test_rst_006_two_real_changes_two_resets(self):
        """Hai thay đổi thật (tính lại đã flush rồi mới ghi tay): hai reset, đúng thiết kế."""
        self.assertEqual(self.run_two({'x_weight': 7}, {'x_due': 99}, flush_between=True), (3, 2))

    def test_rst_007_pending_recompute_still_resets_once(self):
        """Chỉ field nguồn đổi rồi flush: tính lại vẫn gây đúng một reset."""
        self.assertEqual(self.run_two({'x_weight': 7}, {'x_stage': 'sent'}), (2, 1))

    # --- task 027: hook cài hai lớp (framework gọi _register_hook khi lớp đã patch) ---

    def layers(self, name):
        """Số lớp patch của ta chồng lên nhau ở `name` của model thử."""
        func, count = getattr(self.registry[MODEL], name), 0
        while getattr(func, 'sla_patch', False):
            count, func = count + 1, func.origin
        return count

    def register_again(self):
        """Như STEP 9 của `load_modules` sau khi định nghĩa tạo lúc nạp module: không gỡ trước."""
        self.addCleanup(self.env['sla.definition']._register_sla_hook)
        self.env['sla.definition']._register_hook()

    def test_rst_008_register_hook_twice_keeps_one_layer(self):
        """Gọi `_register_hook` lần hai khi đã patch: mỗi hàm vẫn đúng một lớp."""
        self.make_def()
        self.env['sla.definition']._register_sla_hook()
        self.register_again()
        self.assertEqual([self.layers(n) for n in ('create', 'write', '_compute_field_value')], [1, 1, 1])

    def test_rst_009_register_hook_twice_resets_once(self):
        """Hồi quy 027: hook cài hai lớp làm một lần sửa field reset bắn 2 reset, 3 task."""
        self.make_def()
        self.env['sla.definition']._register_sla_hook()
        self.register_again()
        with self.at(T0):
            rec = self.env[MODEL].create({'x_stage': 'sent', 'x_weight': 5})
        with self.at(T0 + hours(1)):
            rec.write({'x_due': 99})
            self.flush_all_()
        self.assertEqual(self.counts(rec, self.Definition.search([('name', '=', 'DEF-RST')])), (2, 1))
