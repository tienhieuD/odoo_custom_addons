# -*- coding: utf-8 -*-
{
    'name': "SLA & Escalation",
    'summary': "Enterprise SLA & escalation engine for any Odoo model: working-calendar durations, multi-stage alerts, enable and apply to existing records",
    'description': """
Enterprise-grade Service Level Agreement (SLA) and Operational Level
Agreement (OLA) engine for Odoo, not tied to any specific model.
Configure start/stop/pause/resume/cancel/reset conditions (domain-based, no
code) on any model, track the full lifecycle, compute duration against a
working calendar (resource.calendar), run multi-stage percentage-based
escalations (built-in email notification or a custom server action),
support retroactive start/pause and a per-rule timezone, enable or disable
a definition with one button, attach a definition to records that already
exist, and show live SLA progress with the built-in SLA Progress widget, a
status chip on the form of the source record and an optional smart button.
Requires only the standard base, resource, web and mail modules.
""",
    'author': "DUO-TEK Software Vietnam",
    'website': 'https://duotek.io.vn',
    'support': 'hello@duotek.io.vn',

    'category': 'Services',
    'version': '17.0.1.2.1',
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    # Giá/ảnh dưới đây là cho listing Odoo Apps -- xem listings/dwo_sla_core.json.
    # Giá ra mắt 249 EUR (chốt với user 2026-11-07); cân nhắc tăng lên
    # 349-399 sau khi có review/rating (xem tư vấn giá trong hội thoại).
    'price': 89.00,
    'currency': 'EUR',
    'images': ['static/description/banner.png'],

    # REQ-INST-002: chỉ base + resource; 'web' thêm có duyệt và ghi lý do
    # deviation trong docs/010_Software-Requirements-Specification.md (D1,
    # TASKS.md). 'mail' thêm vì retroactive_pause đọc trực tiếp
    # mail.tracking.value (sla_definition.py) — không có 'mail' thì model đó
    # không tồn tại và tính năng sập ngay khi dùng.
    'depends': [
        'base',
        'resource',
        'web',
        'mail',
    ],

    'data': [
        'security/sla_security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/mail_templates.xml',
        'views/sla_definition_views.xml',
        'views/sla_task_views.xml',
        'views/sla_event_views.xml',
        'views/sla_apply_views.xml',
        'views/res_config_settings_views.xml',
        'views/sla_menus.xml',
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
            'dwo_sla_core/static/src/sla_progress/sla_progress_widget.js',
            'dwo_sla_core/static/src/sla_progress/sla_progress_widget.xml',
            'dwo_sla_core/static/src/sla_progress/sla_progress_widget.scss',
            'dwo_sla_core/static/src/float_time_unit/float_time_unit_field.js',
            'dwo_sla_core/static/src/float_time_unit/float_time_unit_field.xml',
            'dwo_sla_core/static/src/definition_form/definition_form_controller.js',
            'dwo_sla_core/static/src/form_sla_status/form_sla_status.js',
            'dwo_sla_core/static/src/form_sla_status/form_sla_status.xml',
            'dwo_sla_core/static/src/form_sla_status/form_sla_status.scss',
        ],
        'web.assets_tests': ['dwo_sla_core/static/tests/**/*'],
    },
}
