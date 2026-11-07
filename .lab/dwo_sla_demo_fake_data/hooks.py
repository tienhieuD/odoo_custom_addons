# -*- coding: utf-8 -*-
"""Generate fake-but-realistic SLA demo data for project.task.

Refs: ad-hoc request (2026-11-06) -- "chuan bi kich ban, tao module fake
data cho demo, sau do chup hinh". Not part of dwo_sla_core itself; lives
in .lab so it is never shipped.

Design: every scenario is driven through the REAL sla.definition ->
sla.task engine by writing on project.task while `fields.Datetime.now` is
patched to a chosen instant (the exact mechanism dwo_sla_core/tests/common.py
uses as `at(now)`). This way the generated sla.task rows, their
business_duration/duration, pause_time, breach flags, etc. are all produced
by the engine's real code path -- not hand-set -- so they are consistent and
trustworthy to look at.
"""
from datetime import datetime, timedelta
from unittest.mock import patch

from odoo import fields


def _at(now):
    return patch.object(fields.Datetime, 'now', return_value=now)


def post_init_hook(env):
    Project = env['project.project']
    Task = env['project.task']
    Definition = env['sla.definition']
    Escalation = env['sla.escalation']
    Calendar = env['resource.calendar']
    Category = env['res.partner.category']
    ServerAction = env['ir.actions.server']

    task_model = env['ir.model']._get('project.task')
    category_model = env['ir.model']._get('res.partner.category')
    user_ids_field = env['ir.model.fields']._get('project.task', 'user_ids')
    email_from_field = env['ir.model.fields']._get('project.task', 'email_from')

    # Server Action dùng cho mốc escalation kiểu "Run Server Action" (demo
    # case cho action_type=server_action, scope-add "escalation list UX").
    demo_server_action = ServerAction.create({
        'name': "Log SLA Escalation (Demo)",
        'model_id': task_model.id,
        'state': 'code',
        'code': "record.message_post(body='SLA escalation triggered (demo): "
                "target exceeded, see SLA Task for details.')",
    })

    # ------------------------------------------------------------------
    # 1. Working calendar (std, Mon-Fri 08:00-12:00 / 13:00-17:00 ICT)
    # ------------------------------------------------------------------
    calendar = Calendar.create({
        'name': "Support Hours 08-17 ICT (Demo)",
        'tz': 'Asia/Ho_Chi_Minh',
        'attendance_ids': [
            (0, 0, {
                'name': f'{day_name} {period}',
                'dayofweek': str(day),
                'hour_from': hour_from,
                'hour_to': hour_to,
                'day_period': period_key,
            })
            for day, day_name in enumerate(
                ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])
            for period, period_key, hour_from, hour_to in [
                ('AM', 'morning', 8, 12), ('PM', 'afternoon', 13, 17)]
        ],
    })

    # ------------------------------------------------------------------
    # 2. Projects (scope SLA definitions realistically)
    # ------------------------------------------------------------------
    support_project = Project.create({'name': "Customer Support Demo (Fake)"})
    infra_project = Project.create({'name': "Infra & Vendor Demo (Fake)"})
    retro_project = Project.create({'name': "Retroactive Scenarios Demo (Fake)"})

    vendor = env['res.partner'].create({'name': "Acme Managed Hosting (Demo Vendor)"})

    # ------------------------------------------------------------------
    # 3. 10 sla.definition -- representative configuration scenarios
    # ------------------------------------------------------------------
    common = {
        'model_id': task_model.id,
        'resume_mode': 'pause_unmatched',
        'cancel_mode': 'start_unmatched',
    }

    sp = support_project.id
    d_p0_response = Definition.create({
        **common, 'name': "P0 Urgent -- Response SLA",
        'type': 'sla', 'target': 'response', 'duration': 1.0,
        'schedule_source': 'none',
        'start_domain': f"[('project_id', '=', {sp}), ('priority', '=', '3')]",
        'pause_domain': "[('state', '=', '04_waiting_normal')]",
        'stop_domain': "[('state', 'in', ['1_done', '1_canceled'])]",
    })
    d_p0_resolution = Definition.create({
        **common, 'name': "P0 Urgent -- Resolution SLA",
        'type': 'sla', 'target': 'resolution', 'duration': 8.0,
        'schedule_source': 'definition', 'schedule_id': calendar.id,
        'start_domain': f"[('project_id', '=', {sp}), ('priority', '=', '3')]",
        'pause_domain': "[('state', '=', '04_waiting_normal')]",
        'stop_domain': "[('state', 'in', ['1_done', '1_canceled'])]",
    })
    d_p1_response = Definition.create({
        **common, 'name': "P1 High -- Response SLA",
        'type': 'sla', 'target': 'response', 'duration': 4.0,
        'schedule_source': 'definition', 'schedule_id': calendar.id,
        'start_domain': f"[('project_id', '=', {sp}), ('priority', '=', '2')]",
        'pause_domain': "[('state', '=', '04_waiting_normal')]",
        'stop_domain': "[('state', 'in', ['1_done', '1_canceled'])]",
    })
    d_p1_resolution = Definition.create({
        **common, 'name': "P1 High -- Resolution SLA",
        'type': 'sla', 'target': 'resolution', 'duration': 24.0,
        'schedule_source': 'definition', 'schedule_id': calendar.id,
        'start_domain': f"[('project_id', '=', {sp}), ('priority', '=', '2')]",
        'pause_domain': "[('state', '=', '04_waiting_normal')]",
        'stop_domain': "[('state', 'in', ['1_done', '1_canceled'])]",
    })
    d_p2_resolution = Definition.create({
        **common, 'name': "P2 Medium -- Resolution SLA",
        'type': 'sla', 'target': 'resolution', 'duration': 72.0,
        'schedule_source': 'definition', 'schedule_id': calendar.id,
        'start_domain': f"[('project_id', '=', {sp}), ('priority', '=', '1')]",
        'pause_domain': "[('state', '=', '04_waiting_normal')]",
        'stop_domain': "[('state', 'in', ['1_done', '1_canceled'])]",
    })
    d_std_resolution = Definition.create({
        **common, 'name': "Standard (Low) -- Resolution SLA",
        'type': 'sla', 'target': 'resolution', 'duration': 120.0,
        'schedule_source': 'definition', 'schedule_id': calendar.id,
        'start_domain': f"[('project_id', '=', {sp}), ('priority', '=', '0')]",
        'pause_domain': "[('state', '=', '04_waiting_normal')]",
        'stop_domain': "[('state', 'in', ['1_done', '1_canceled'])]",
    })
    d_vendor_ola = Definition.create({
        **common, 'name': "Vendor OLA -- Infra Support",
        'type': 'ola', 'target': 'resolution', 'vendor_id': vendor.id,
        'service_commitment': True, 'duration': 48.0,
        'schedule_source': 'none', 'calendar_tz_override': 'Asia/Tokyo',
        'start_domain': f"[('project_id', '=', {infra_project.id})]",
        'pause_domain': "[('state', '=', '04_waiting_normal')]",
        'stop_domain': "[('state', 'in', ['1_done', '1_canceled'])]",
    })
    rp = retro_project.id
    start_field = env['ir.model.fields'].search([
        ('model', '=', 'project.task'), ('name', '=', 'create_date')], limit=1)
    d_retro_start = Definition.create({
        **common, 'name': "Retroactive Start -- Backdated Ticket SLA",
        'type': 'sla', 'target': 'response', 'duration': 2.0,
        'schedule_source': 'none',
        'retroactive': True, 'start_field_id': start_field.id,
        'start_domain': f"[('project_id', '=', {rp}), ('priority', '=', '2')]",
        'pause_domain': "[('state', '=', '04_waiting_normal')]",
        'stop_domain': "[('state', 'in', ['1_done', '1_canceled'])]",
    })
    d_retro_pause = Definition.create({
        **common, 'name': "Retroactive Pause -- Hold Time Credit SLA",
        'type': 'sla', 'target': 'resolution', 'duration': 24.0,
        'schedule_source': 'none', 'retroactive': True,
        'start_field_id': start_field.id, 'retroactive_pause': True,
        'start_domain': f"[('project_id', '=', {rp}), ('priority', '=', '3')]",
        'pause_domain': "[('state', '=', '04_waiting_normal')]",
        'stop_domain': "[('state', 'in', ['1_done', '1_canceled'])]",
    })
    d_warning_demo = Definition.create({
        'name': "DEMO ONLY -- Untracked Model Warning Example",
        'model_id': category_model.id,
        'resume_mode': 'pause_unmatched', 'cancel_mode': 'start_unmatched',
        'type': 'sla', 'target': 'resolution', 'duration': 4.0,
        'schedule_source': 'none', 'retroactive_pause': True,
        'start_domain': "[('name', '=', 'x')]",
        'pause_domain': "[('name', '=', 'y')]",
        'stop_domain': "[('name', '=', 'z')]",
        'active': False,
    })
    Category.create({'name': "Demo Category (untracked model example)"})

    # ------------------------------------------------------------------
    # 3b. Escalation rules -- cover all 4 action/recipient combinations
    # (D12/D13, scope-add "escalation list UX" and "email template"):
    # email+responsible (Many2many `user_ids`, 1 mail to ALL assignees),
    # email+field (Char `email_from`), email+fixed, and server_action. Email
    # template left on its default (mail_template_escalation_default).
    # ------------------------------------------------------------------
    Escalation.create([
        {
            'definition_id': d_p0_response.id, 'percent': 75, 'sequence': 10,
            'action_type': 'email', 'email_recipient_type': 'responsible',
            'email_field_id': user_ids_field.id,
        },
        {
            'definition_id': d_p0_response.id, 'percent': 100, 'sequence': 20,
            'action_type': 'email', 'email_recipient_type': 'fixed',
            'email_fixed_address': 'oncall-p0@acme-demo.com',
        },
        {
            'definition_id': d_p1_resolution.id, 'percent': 60, 'sequence': 10,
            'action_type': 'email', 'email_recipient_type': 'field',
            'email_field_id': email_from_field.id,
        },
        {
            'definition_id': d_p1_resolution.id, 'percent': 100, 'sequence': 20,
            'action_type': 'server_action', 'action_id': demo_server_action.id,
        },
        {
            'definition_id': d_vendor_ola.id, 'percent': 50, 'sequence': 10,
            'action_type': 'email', 'email_recipient_type': 'fixed',
            'email_fixed_address': 'vendor-escalation@acme-hosting-demo.com',
        },
    ])

    # ------------------------------------------------------------------
    # 4. Fake tasks, progressed through realistic timelines
    # ------------------------------------------------------------------
    # T0 tính theo thời điểm cài module (KHÔNG hardcode ngày), để mọi kịch
    # bản "đang chạy, còn thời gian"/"vừa mới tạo" luôn đúng bất kể cài lúc
    # nào -- trước đây T0 cố định 2026-10-26 nên sau vài ngày mọi task
    # "trong hạn" sẽ hiện SAI thành đã trễ hạn rất xa so với thời gian thực.
    T0 = fields.Datetime.now()

    def mk(project, name, priority, **extra):
        return Task.create({
            'project_id': project.id, 'name': name, 'priority': priority,
            **extra,
        })

    def backdate_create_date(task, when):
        """`create_date` is stamped by Postgres `now()` at INSERT time, so
        patching `fields.Datetime.now` has no effect on it. The
        'retroactive'/start_field_id demo scenarios read `create_date`
        directly, so it must be rewritten in SQL and the cache invalidated
        before the engine reads it again."""
        env.cr.execute(
            'UPDATE project_task SET create_date = %s WHERE id = %s',
            (when, task.id))
        task.invalidate_recordset(['create_date'])

    def write_tracked_at(task, when, vals):
        """Like `task.write(vals)` under `_at(when)`, but also makes sure a
        `mail.tracking.value` row for this change exists with a backdated
        `mail.message.date` -- that field's `default=fields.Datetime.now`
        was captured by the `mail` module at load time, long before this
        hook's patch exists, so patching `fields.Datetime.now` here never
        reaches it. If the automatic tracking message didn't fire for some
        reason, call `_message_track` directly as a fallback."""
        field_name = next(iter(vals))
        before_ids = set(env['mail.message'].search(
            [('model', '=', 'project.task'), ('res_id', '=', task.id)]).ids)
        initial = {task.id: {field_name: task[field_name]}}
        task.write(vals)
        new_msgs = env['mail.message'].search(
            [('model', '=', 'project.task'), ('res_id', '=', task.id),
             ('id', 'not in', list(before_ids) or [0])])
        if not new_msgs:
            task._message_track([field_name], initial)
            new_msgs = env['mail.message'].search(
                [('model', '=', 'project.task'), ('res_id', '=', task.id),
                 ('id', 'not in', list(before_ids) or [0])])
        if new_msgs:
            env.cr.execute(
                'UPDATE mail_message SET date = %s WHERE id IN %s',
                (when, tuple(new_msgs.ids)))
            new_msgs.invalidate_recordset(['date'])

    # -- Scenario A: P0 urgent, in progress, well within SLA --------------
    with _at(T0):
        t_a = mk(support_project, "[DEMO] Payment gateway 500 errors", '3')

    # -- Scenario L: P0 urgent, IN PROGRESS and past both escalation
    #    thresholds -- the only scenario where escalations are actually
    #    fired (`sla.processor._process_task`, not just attached), so the
    #    Escalation tab/History/outgoing email are real, not just
    #    configured. Response SLA is schedule_source='none' (24x7), so the
    #    75%/100% timing is plain wall-clock, no calendar math to get
    #    wrong. Covers both demo rules on d_p0_response: 75% email to ALL
    #    assignees (`user_ids`, Many2many -> multiple "To"), 100% email to
    #    a fixed address. -------------------------------------------------
    with _at(T0 - timedelta(minutes=90)):
        t_l = mk(support_project, "[DEMO] Checkout service intermittent 502s", '3')
        t_l.user_ids = [(6, 0, [env.user.id])]
    sla_task_l = env['sla.task'].sudo().search([
        ('res_model', '=', 'project.task'), ('res_id', '=', t_l.id),
        ('sla_id', '=', d_p0_response.id)], limit=1)
    env['sla.processor']._process_task(sla_task_l, T0)

    # -- Scenario B: P0 urgent, BREACHED (resolution SLA blown) ------------
    with _at(T0 - timedelta(days=3)):
        t_b = mk(support_project, "[DEMO] Prod DB replica lagging", '3')
    with _at(T0 - timedelta(hours=2)):
        t_b.write({'state': '1_done'})

    # -- Scenario C: P1 high, currently PAUSED (waiting on customer) ------
    with _at(T0 - timedelta(hours=10)):
        t_c = mk(support_project, "[DEMO] SSO login intermittent failures", '2')
    with _at(T0 - timedelta(hours=3)):
        t_c.write({'state': '04_waiting_normal'})

    # -- Scenario D: P1 high, ACHIEVED within target -----------------------
    with _at(T0 - timedelta(hours=20)):
        t_d = mk(support_project, "[DEMO] Export CSV missing a column", '2')
    with _at(T0 - timedelta(hours=2)):
        t_d.write({'state': '1_done'})

    # -- Scenario E: pause then resume, still in progress ------------------
    with _at(T0 - timedelta(hours=30)):
        t_e = mk(support_project, "[DEMO] API rate-limit tuning request", '2')
    with _at(T0 - timedelta(hours=20)):
        t_e.write({'state': '04_waiting_normal'})
    with _at(T0 - timedelta(hours=15)):
        t_e.write({'state': '01_in_progress'})

    # -- Scenario F: P2 medium, in progress ---------------------------------
    with _at(T0 - timedelta(hours=5)):
        t_f = mk(support_project, "[DEMO] Monthly report formatting request", '1')

    # -- Scenario G: Standard/Low, in progress (long runway) ---------------
    with _at(T0 - timedelta(hours=1)):
        t_g = mk(support_project, "[DEMO] Minor UI copy change", '0')

    # -- Scenario H: CANCELLED task (cancel_mode start_unmatched: de-prioritised) --
    with _at(T0 - timedelta(hours=8)):
        t_h = mk(support_project, "[DEMO] Investigate slow report (deprioritised)", '2')
    with _at(T0 - timedelta(hours=4)):
        t_h.write({'priority': '0'})  # no longer matches start_domain -> cancel

    # -- Scenario I: Vendor OLA, in progress --------------------------------
    with _at(T0 - timedelta(hours=12)):
        t_i = mk(infra_project, "[DEMO] Vendor: restore staging snapshot", '2')

    # -- Scenario J: Retroactive start -- ticket created 2 days ago, only now
    #    flagged urgent; engine backdates start_time to create_date, so the
    #    task attaches ALREADY BREACHED (2h target, 2 days elapsed). -------
    with _at(T0 - timedelta(days=2)):
        t_j = mk(retro_project, "[DEMO] Backlog ticket just escalated", '0')
        backdate_create_date(t_j, T0 - timedelta(days=2))
    with _at(T0 - timedelta(hours=1)):
        t_j.write({'priority': '2'})

    # -- Scenario K: Retroactive pause -- the ticket was on hold for 5h
    #    BEFORE the SLA ever started tracking it (priority still '0' then);
    #    once escalated to Urgent, retroactive=True backdates start_time to
    #    create_date and retroactive_pause reconstructs that 5h hold from
    #    the tracked `state` field history (mail.tracking.value) and
    #    excludes/credits it -- demonstrating the actual feature's purpose. --
    with _at(T0 - timedelta(hours=40)):
        t_k = mk(retro_project, "[DEMO] Waiting on customer access (credited)", '0')
        backdate_create_date(t_k, T0 - timedelta(hours=40))
    with _at(T0 - timedelta(hours=38)):
        write_tracked_at(t_k, T0 - timedelta(hours=38), {'state': '04_waiting_normal'})
    with _at(T0 - timedelta(hours=33)):
        write_tracked_at(t_k, T0 - timedelta(hours=33), {'state': '01_in_progress'})
    with _at(T0 - timedelta(hours=10)):
        t_k.write({'priority': '3'})

    env.cr.flush()
