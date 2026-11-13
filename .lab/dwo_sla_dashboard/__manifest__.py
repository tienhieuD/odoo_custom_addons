# -*- coding: utf-8 -*-
{
    'name': "SLA Overview Dashboard",
    'summary': "Overview screen for SLA & Escalation: KPI cards with trend, outcome donut, results by definition, weekly compliance line and a needs-attention list",
    'description': """
Adds the SLA Overview screen to the SLA app of dwo_sla_core: KPI cards
(running, due soon, breached, achieved rate, late) compared with the previous
period, a donut of outcomes, stacked bars per definition, a weekly compliance
line and the list of tasks that need attention. Quick filters (SLA/OLA,
Response/Resolution, definitions) apply to every card and chart; every card,
slice and bar opens the matching filtered list of SLA tasks. Read-only,
respects access rules and multi-company.
""",
    'author': "DUO-TEK Software Vietnam",
    'website': 'https://duotek.io.vn',
    'support': 'hello@duotek.io.vn',
    'category': 'Services',
    'version': '17.0.1.0.0',
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'depends': ['dwo_sla_core'],
    'data': [
        'views/sla_overview_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dwo_sla_dashboard/static/src/overview/overview.js',
            'dwo_sla_dashboard/static/src/overview/overview.xml',
            'dwo_sla_dashboard/static/src/overview/overview.scss',
        ],
        'web.assets_tests': ['dwo_sla_dashboard/static/tests/**/*'],
    },
}
