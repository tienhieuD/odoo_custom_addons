# -*- coding: utf-8 -*-
"""TG-14: hạ tầng — model bị cấm, dọn dẹp, tham số, kiểm tra mã nguồn (docs/060 TC-INF-*, TC-INS-*).

Các ca cài/nâng cấp/gỡ trên database riêng, docker và CI (INF-023..026, 028, 030..033, 035;
INS-003, 011, 013, 014) không thuộc TransactionCase; xem báo cáo độ phủ ở TASKS.md.
Refs: REQ-FUNC-002, 034, 035, 061, REQ-INT-010, REQ-INST-001..004, REQ-SEC-001
"""
import ast
import os
import re
import sys
from datetime import timedelta

from odoo.exceptions import AccessError, ValidationError
from odoo.modules import get_module_path
from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
MODULE_PATH = get_module_path('dwo_sla_core')
PARAM = 'dwo_sla_core.event_retention_days'


@tagged(*TAGS, 'tg_14')
class TestModelRestrictions(SlaCase):

    def rejected(self, model):
        n0 = self.Definition.search_count([('model_name', '=', model)])
        with self.assertRaises(ValidationError) as ctx, self.env.cr.savepoint():
            self.Definition.create({
                'name': "D %s" % model, 'model_id': self.env['ir.model']._get(model).id,
                'duration': 4, 'start_domain': "[]"})
        self.assertTrue(str(ctx.exception))
        self.assertEqual(self.Definition.search_count([('model_name', '=', model)]), n0)

    def test_inf_001_to_006_forbidden_models(self):
        """TC-INF-001..006: model ir.*, sla.*, transient, abstract, _auto=False, mail.* bị từ chối."""
        for model in ('ir.attachment', 'sla.task', 'base.language.install', 'image.mixin', 'mail.message'):
            self.rejected(model)
        auto_false = [name for name, cls in self.env.registry.items()
                      if not cls._auto and not cls._abstract and not cls._transient
                      and not name.startswith(('ir.', 'sla.', 'mail.'))]
        if auto_false:
            self.rejected(auto_false[0])

    def test_inf_007_partner_accepted(self):
        """TC-INF-007: res.partner được chấp nhận."""
        d = self.make_definition(start_domain="[('ref', '=', 'NEW')]")
        self.assertEqual((bool(d.id), d.model_name), (True, 'res.partner'))
        self.assertEqual(self.Definition.search_count([('model_name', '=', 'res.partner')]), 1)

    def test_inf_009_ir_model_not_observed(self):
        """TC-INF-009: model ir.attachment không bị quan sát dù có định nghĩa lọt qua (SQL)."""
        self.env.cr.execute(
            "INSERT INTO sla_definition (name, model_id, model_name, duration, start_domain, "
            "schedule_source, calendar_tz_override, cancel_mode, resume_mode, reset_action, "
            "active, sequence) "
            "SELECT 'SQL', id, 'ir.attachment', 4, '[(''id'', ''!='', 0)]', 'none', 'UTC', "
            "'start_unmatched', 'condition', 'cancel', true, 10 FROM ir_model WHERE model='ir.attachment'")
        self.Definition.invalidate_model()
        self.Definition._register_sla_hook()
        n_task, n_event = self.Task.sudo().search_count([]), self.Event.sudo().search_count([])
        self.env['ir.attachment'].create({'name': 'a.txt', 'res_model': 'res.partner', 'raw': b'x'})
        self.assertEqual((self.Task.sudo().search_count([]), self.Event.sudo().search_count([])),
                         (n_task, n_event))


@tagged(*TAGS, 'tg_14')
class TestHousekeeping(SlaCase):

    def setUp(self):
        super().setUp()
        self.d = self.make_definition()

    def test_inf_010_orphans_removed(self):
        """TC-INF-010: dọn task và event của record đã xóa; giữ record còn."""
        d2 = self.make_definition(name="D2")
        p = self.make_partner('NEW')
        self.task_of(p, self.d)
        self.assertTrue(self.task_of(p, d2))
        self.Event._log_error(definition=self.d, res_model='res.partner', res_id=p.id, message="x")
        pid = p.id
        p.unlink()
        self.assertTrue(self.Task.sudo().search([('res_id', '=', pid)]))
        self.Task._gc_orphan_tasks()
        self.assertEqual(self.Task.sudo().search_count([('res_model', '=', 'res.partner'), ('res_id', '=', pid)]), 0)
        self.assertEqual(self.Event.sudo().search_count([('res_id', '=', pid)]), 0)

    def test_inf_011_012_keep_existing_records(self):
        """TC-INF-011/012: giữ task của record còn tồn tại, chỉ dọn của record đã xóa."""
        p1, p2 = self.make_partner('NEW'), self.make_partner('NEW')
        t2 = self.task_of(p2, self.d)
        p1_id = p1.id
        p1.unlink()
        self.Task._gc_orphan_tasks()
        self.assertEqual(self.Task.sudo().search_count([('res_id', '=', p1_id), ('res_model', '=', 'res.partner')]), 0)
        self.assertEqual((t2.exists().stage, len(t2.event_ids)), ('in_progress', 1))

    def event_aged(self, days, now):
        event = self.Event.sudo().create({
            'event': 'error', 'event_dt': now - timedelta(days=days), 'note': 'x',
            'res_model': 'res.partner', 'res_id': 0})
        self.env.cr.execute("UPDATE sla_event SET create_date=%s WHERE id=%s",
                            (now - timedelta(days=days), event.id))
        return event

    def gc(self, now, retention):
        self.env['ir.config_parameter'].sudo().set_param(PARAM, str(retention))
        with self.at(now):
            self.Event._gc_old_events()
        self.env.invalidate_all()

    def test_inf_013_to_016_retention(self):
        """TC-INF-013..016: xóa event quá ngưỡng, giữ event đúng ngưỡng hoặc mới hơn, ngưỡng chỉnh được."""
        now = T0 + timedelta(days=200)
        a, b = self.event_aged(100, now), self.event_aged(10, now)
        e_equal = self.event_aged(90, now)
        e_over = self.event_aged(90, now) if False else self.Event.sudo().create({
            'event': 'error', 'event_dt': now - timedelta(days=90, minutes=1), 'note': 'x',
            'res_model': 'res.partner', 'res_id': 0})
        self.gc(now, 90)
        self.assertEqual((a.exists().id, b.exists().id, e_equal.exists().id, e_over.exists().id),
                         (False, b.id, e_equal.id, False))
        e40 = self.event_aged(40, now)
        self.gc(now, 30)
        self.assertFalse(e40.exists())


@tagged(*TAGS, 'tg_14')
class TestRetentionSetting(SlaCase):

    def setUp(self):
        super().setUp()
        self.param = self.env['ir.config_parameter'].sudo()
        self.param.set_param(PARAM, '365')
        self.sysadmin = self.make_user('sla_sysadmin_set')
        self.sysadmin.group_ids += self.env.ref('base.group_system')
        self.viewer = self.make_user('sla_viewer_set', 'user')

    def save(self, value, user=None):
        Settings = self.env['res.config.settings'].with_user(user or self.sysadmin)
        return Settings.create({'sla_event_retention_days': value}).execute()

    def test_inf_017_default_365(self):
        """TC-INF-017: mặc định 365 (chưa chỉnh)."""
        self.env['ir.config_parameter'].sudo().search([('key', '=', PARAM)]).unlink()
        defaults = self.env['res.config.settings'].default_get(['sla_event_retention_days'])
        self.assertEqual(defaults.get('sla_event_retention_days'), 365)

    def test_inf_018_019_invalid_values(self):
        """TC-INF-018/019: 0 và -1 bị từ chối, giữ 365."""
        for value in (0, -1):
            with self.assertRaisesRegex(ValidationError, 'greater than 0'), self.env.cr.savepoint():
                self.save(value)
            self.assertEqual(self.param.get_param(PARAM), '365')

    def test_inf_020_021_valid_values(self):
        """TC-INF-020/021: 1 và 180 lưu được."""
        for value in (1, 180):
            self.save(value)
            self.assertEqual(self.param.get_param(PARAM), str(value))

    def test_inf_022_viewer_denied(self):
        """TC-INF-022: SLA User không lưu được tham số."""
        with self.assertRaises(AccessError):
            self.save(180, self.viewer)
        self.assertEqual(self.param.get_param(PARAM), '365')


@tagged(*TAGS, 'tg_14')
class TestSchemaAndSource(SlaCase):

    def columns(self, table):
        self.env.cr.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name=%s ORDER BY 1", (table,))
        return [row[0] for row in self.env.cr.fetchall()]

    def test_inf_027_029_no_columns_added(self):
        """TC-INF-027/029: module không thêm field/cột vào res.partner (kể cả sau khi có task)."""
        owned = self.env['ir.model.data'].sudo().search([
            ('module', '=', 'dwo_sla_core'), ('model', '=', 'ir.model.fields')])
        partner_fields = self.env['ir.model.fields'].sudo().search([('model', '=', 'res.partner')])
        self.assertFalse(set(owned.mapped('res_id')) & set(partner_fields.ids))
        before = self.columns('res_partner')
        d = self.make_definition()
        self.task_of(self.make_partner('NEW'), d)
        self.assertEqual(self.columns('res_partner'), before)
        self.assertFalse([c for c in before if c.startswith('sla')])

    def python_files(self):
        for root, _dirs, files in os.walk(MODULE_PATH):
            if '/tests' in root or '/docs' in root or '__pycache__' in root:
                continue
            for name in files:
                if name.endswith('.py'):
                    yield os.path.join(root, name)

    def test_inf_ondelete_company_calendar_restricted(self):
        """030 §4: không xóa được công ty/lịch đang được định nghĩa dùng (RESTRICT)."""
        company = self.env['res.company'].create({'name': "SLA Co"})
        calendar = self.make_calendar()
        self.make_definition(name="Scoped", company_id=company.id)
        self.make_definition(name="Fixed", schedule_source='definition', schedule_id=calendar.id)
        for record in (company, calendar):
            with self.assertRaises(Exception), mute_logger('odoo.sql_db'), self.env.cr.savepoint():
                record.unlink()
        self.assertTrue(company.exists() and calendar.exists())

    def test_inf_next_due_at_only_partial_index(self):
        """030 §6: next_due_at chỉ có index từng phần, không có index đầy đủ thừa."""
        self.env.cr.execute(
            "SELECT indexdef FROM pg_indexes WHERE tablename = 'sla_task' "
            "AND indexdef LIKE '%(next_due_at)%'")
        defs = [row[0] for row in self.env.cr.fetchall()]
        self.assertEqual(len(defs), 1, defs)
        self.assertIn('WHERE', defs[0])

    def test_inf_034_only_stdlib_and_odoo_imports(self):
        """TC-INF-034: mã nguồn chỉ import thư viện chuẩn và odoo; manifest không có external_dependencies."""
        allowed = set(sys.stdlib_module_names) | {'odoo'}
        for path in self.python_files():
            tree = ast.parse(open(path).read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots = {alias.name.split('.')[0] for alias in node.names}
                elif isinstance(node, ast.ImportFrom) and not node.level:
                    roots = {node.module.split('.')[0]}
                else:
                    continue
                self.assertLessEqual(roots, allowed, path)
        manifest = ast.literal_eval(open(os.path.join(MODULE_PATH, '__manifest__.py')).read())
        self.assertFalse(manifest.get('external_dependencies'))

    def test_ins_001_depends(self):
        """TC-INS-001: depends chỉ base + resource, cộng `web` (D1) và `mail` (D10) đã duyệt, ghi lý do trong SRS."""
        manifest = ast.literal_eval(open(os.path.join(MODULE_PATH, '__manifest__.py')).read())
        self.assertEqual(set(manifest['depends']), {'base', 'resource', 'web', 'mail'})
        srs = open(os.path.join(MODULE_PATH, 'docs', '010_Software-Requirements-Specification.md')).read()
        self.assertIn('Deviation (đã duyệt', srs)

    def test_ins_002_no_forbidden_references(self):
        """TC-INS-002: không phụ thuộc/tham chiếu thật tới helpdesk, nev_*, dwo_* khác, OCA."""
        pattern = re.compile(r"(sh_all_in_one_helpdesk|nev_\w+\.|dwo_(?!sla_core)\w+\.|\boca\b)", re.I)
        for root, _dirs, files in os.walk(MODULE_PATH):
            if any(part in root for part in ('/docs', '/tests', '__pycache__')):
                continue
            for name in files:
                if name.endswith(('.py', '.xml', '.csv')):
                    for lineno, line in enumerate(open(os.path.join(root, name)), 1):
                        code = line.split('#')[0] if name.endswith('.py') else line
                        self.assertFalse(pattern.search(code), "%s:%s %s" % (name, lineno, line.strip()))

    def test_ins_004_js_scoped_to_static_src(self):
        """TC-INS-004: mã JS (REQ-BUILD-001 cho phép "nếu có") chỉ giới hạn
        trong static/src/ (các widget hiển thị, Deviation D11 trong
        TASKS.md) -- không rải rác JS ở nơi khác trong module (models/,
        tests/, root, ...)."""
        found = [os.path.relpath(os.path.join(root, f), MODULE_PATH)
                 for root, _d, files in os.walk(MODULE_PATH) for f in files
                 if f.endswith('.js')]
        allowed_dir = os.path.join('static', 'src')
        # Tour kiểm thử (web.assets_tests) nằm ở static/tests theo quy ước của Odoo.
        for rel in found:
            self.assertTrue(
                rel.startswith((allowed_dir, os.path.join('static', 'tests'))), rel)
        self.assertIn(os.path.join(allowed_dir, 'sla_progress', 'sla_progress_widget.js'), found)
        self.assertIn(os.path.join(allowed_dir, 'float_time_unit', 'float_time_unit_field.js'), found)
        self.assertIn(os.path.join(allowed_dir, 'definition_form', 'definition_form_controller.js'), found)
        self.assertIn(os.path.join(allowed_dir, 'form_sla_status', 'form_sla_status.js'), found)

    def test_ins_005_pylintrc_covers_module(self):
        """TC-INS-005: .pylintrc không bỏ qua dwo_sla_core."""
        repo = os.path.abspath(os.path.join(MODULE_PATH, '..', '..'))
        path = os.path.join(repo, '.pylintrc')
        if not os.path.exists(path):
            self.skipTest("không có .pylintrc trong môi trường chạy")
        text = open(path).read()
        match = re.search(r'ignore-patterns\s*=\s*(.*)', text)
        for pattern in (match.group(1).split(',') if match else []):
            self.assertIsNone(re.match(pattern.strip(), 'dwo_sla_core'), pattern)

    def test_ins_012_suite_is_generic(self):
        """TC-INS-012: suite dùng res.partner và không tham chiếu ticket/demo."""
        tests_dir = os.path.join(MODULE_PATH, 'tests')
        sources = {name: open(os.path.join(tests_dir, name)).read()
                   for name in os.listdir(tests_dir) if name.endswith('.py')}
        self.assertTrue(any("res.partner" in text for text in sources.values()))
        for name, text in sources.items():
            code = ''.join(line for line in text.splitlines(True) if 'TC-INS-012' not in line)
            for forbidden in ('sh.helpdesk.ticket', 'dwo_sla_demo_ticket', "env['demo.ticket']"):
                if name != os.path.basename(__file__):
                    self.assertNotIn(forbidden, code, name)
