# -*- coding: utf-8 -*-
{
    'name': "Demo: SLA & Escalation",
    'summary': "Demo data: generates realistic project.task SLA scenarios for screenshots/review.",
    'description': """
Demo module (lives in .demo, never published to the Apps store). Generates ~10 sla.definition records attached
to project.task (plus one deliberately on an untracked model, to show the
retroactive_pause config-time warning) and progresses a batch of fake
project.task records through realistic timelines (start / pause / resume /
stop / breach) by driving the real SLA engine with patched `fields.Datetime.now`
-- the same mechanism dwo_sla_core's own test suite uses -- so the resulting
sla.task rows are produced by the real engine code path, not hand-crafted.

Everything this module creates (projects, tasks, tags, sla.definition,
res.partner.category demo row) is removed on uninstall.
    """,
    'author': "DuoTEK",
    'license': 'OPL-1',
    'category': 'Hidden/Tools',
    'version': '19.0.1.0.0',
    'depends': ['dwo_sla_core', 'project'],
    'data': [
        'views/project_task_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
}
