# -*- coding: utf-8 -*-
"""v1.1 of the flow model: guards, entries in the Action menu, several flows per model."""
from markupsafe import Markup

from odoo import api, fields, models
from odoo.exceptions import UserError

from . import guard
from .flow import STATE_FIELD


class DwoApprovalFlow(models.Model):
    _inherit = "dwo.approval.flow"

    # ------------------------------------------------------------------
    # life cycle
    # ------------------------------------------------------------------
    def write(self, vals):
        result = super().write(vals)
        if "name" in vals:
            self._sync_list_actions()
        return result

    def unlink(self):
        result = super().unlink()
        self._guard_sync()
        return result

    def _after_change(self):
        super()._after_change()
        self._guard_sync()
        self._sync_list_actions()

    def _write_graph(self, clean):
        super()._write_graph(clean)
        self._guard_sync()
        self._sync_list_actions()

    def _write_state(self, record, state):
        with guard.bypass():
            return super()._write_state(record, state)

    # ------------------------------------------------------------------
    # guards
    # ------------------------------------------------------------------
    @api.model
    def _register_hook(self):
        super()._register_hook()
        self._guard_sync()

    def _unregister_hook(self):
        guard.sync(self.env.registry, set())
        super()._unregister_hook()

    @api.model
    def _guard_pairs(self):
        pairs = set()
        for flow in self.sudo().search([]):
            if flow.model_name not in self.env.registry:
                continue
            if flow.state_mode == "custom":
                pairs.add((flow.model_name, "write"))
            for tr in flow.transition_ids:
                if tr.move_mode == "call_method" and tr.method_name and tr.guard_scope != "none":
                    pairs.add((flow.model_name, tr.method_name))
        return pairs

    @api.model
    def _guard_sync(self):
        """Patch exactly the pairs the active flows need; tell the other workers to do the same."""
        registry = self.env.registry
        guard.sync(registry, self._guard_pairs())
        if self.pool.ready:
            registry.registry_invalidated = True

    @api.model
    def _guard_write_refused(self):
        raise UserError(self.env._("The approval state can only be changed with the approval buttons."))

    @api.model
    def _guard_call(self, records, name, original, args, kwargs):
        """A guarded method was called: send governed documents through their arrow instead."""
        direct = guard.called_from_rpc(name)
        free, held = records.browse(), []
        for record in records:
            flow = self._flow_of(record)
            arrows = flow.transition_ids.filtered(
                lambda t: t.move_mode == "call_method" and t.method_name == name
                and (t.guard_scope == "all" or (t.guard_scope == "direct" and direct))
            ).sorted("sequence") if flow else self.env["dwo.approval.transition"]
            if arrows:
                held.append((record, arrows))
            else:
                free |= record
        result = original(free, *args, **kwargs) if free else True
        user = self.env.user
        for record, arrows in held:
            arrow = next((t for t in arrows if t._check_available(record, user)[0]), None)
            if not arrow:
                why = arrows[0]._check_available(record, user)[1]
                raise UserError(self.env._(
                    "“%(doc)s” goes through an approval and you cannot do this now. %(why)s",
                    doc=record.display_name, why=why))
            if arrow.ask_reason:
                raise UserError(self.env._("Use the approval button of the document: a reason is required."))
            outcome = arrow._press(record, user)
            if outcome.get("action"):
                result = outcome["action"]
            elif outcome["status"] == "waiting" and len(records) == 1:
                result = {"type": "ir.actions.client", "tag": "display_notification", "params": {
                    "title": self.env._("Approval"), "type": "info", "sticky": False,
                    "message": self.env._("Approved. %(count)s of %(needed)s approvals.",
                                          count=outcome["count"], needed=outcome["needed"]),
                    "next": {"type": "ir.actions.client", "tag": "reload"}}}
        return result

    # ------------------------------------------------------------------
    # Action menu of the list view
    # ------------------------------------------------------------------
    def _sync_list_actions(self):
        Action = self.env["ir.actions.server"].sudo()
        for flow in self.exists():
            labels = []
            if flow.active:
                for tr in flow.transition_ids.sorted("sequence"):
                    if tr.list_action and tr.name not in labels:
                        labels.append(tr.name)
            existing = Action.search([("dwo_approval_flow_id", "=", flow.id)])
            kept = Action
            for label in labels:
                vals = {
                    "name": "%s: %s" % (flow.name, label), "model_id": flow.model_id.id, "state": "code",
                    "code": "action = env['dwo.approval.flow'].press_label(%d, %r, records.ids)" % (flow.id, label),
                    "binding_model_id": flow.model_id.id, "binding_type": "action",
                    "binding_view_types": "list,form", "dwo_approval_flow_id": flow.id, "dwo_label": label}
                action = existing.filtered(lambda a: a.dwo_label == label)[:1]
                if action:
                    action.write(vals)
                else:
                    action = Action.create(vals)
                kept |= action
            (existing - kept).unlink()
        self.env.registry.clear_cache()

    @api.model
    def press_label(self, flow_id, label, ids):
        """Press the arrow called ``label`` on every selected document where it is available."""
        flow = self.sudo().browse(flow_id).exists()
        if not flow or not flow.active:
            raise UserError(self.env._("This approval is not active."))
        records = self.env[flow.model_name].browse(ids).exists()
        records.check_access("read")
        user = self.env.user
        done, skipped = 0, []
        arrows = flow.transition_ids.filtered(lambda t: t.name == label and t.list_action).sorted("sequence")
        for record in records:
            arrow = next((t for t in arrows if flow._flow_of(record) == flow
                          and t._check_available(record, user)[0]), None)
            if not arrow or arrow.ask_reason:
                skipped.append(record.display_name)
                continue
            try:
                with self.env.cr.savepoint():
                    arrow._press(record, user)
                done += 1
            except UserError as error:
                skipped.append("%s (%s)" % (record.display_name, error.args[0]))
        message = self.env._("%(label)s: %(done)s done.", label=label, done=done)
        if skipped:
            message += " " + self.env._("Skipped: %s", ", ".join(skipped[:10]))
        return {"type": "ir.actions.client", "tag": "display_notification", "params": {
            "title": flow.name, "message": message, "type": "warning" if skipped else "success",
            "sticky": bool(skipped), "next": {"type": "ir.actions.client", "tag": "reload"}}}

    # ------------------------------------------------------------------
    # Test
    # ------------------------------------------------------------------
    def action_test(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window", "res_model": "dwo.approval.test", "view_mode": "form",
            "target": "new", "name": self.env._("Test the flow"),
            "context": {"default_flow_id": self.id}}


class DwoApprovalTest(models.TransientModel):
    _name = "dwo.approval.test"
    _description = "Try an approval flow on a document"

    flow_id = fields.Many2one("dwo.approval.flow", required=True, ondelete="cascade")
    res_model = fields.Char(related="flow_id.model_name")
    res_id = fields.Many2oneReference(string="Document", model_field="res_model")
    user_id = fields.Many2one("res.users", string="As user", default=lambda self: self.env.user, required=True)
    result = fields.Html(compute="_compute_result", sanitize=False)

    @api.depends("flow_id", "res_id", "user_id")
    def _compute_result(self):
        for wizard in self:
            wizard.result = wizard._build_result()

    def _build_result(self):
        self.ensure_one()
        flow, user = self.flow_id, self.user_id
        record = self.env[flow.model_name].sudo().browse(self.res_id or 0).exists() if self.res_id else None
        if not record:
            return Markup("<p class='text-muted'>%s</p>") % self.env._("Pick a document and a user.")
        out = Markup("")
        routed = self.env["dwo.approval.flow"]._flow_of(record)
        if routed != flow:
            out += Markup("<p class='text-warning'>%s</p>") % self.env._(
                "This document is handled by another flow (%s), or by none: this flow does not apply to it.",
                routed.name or "-")
        current = flow._current_state(record)
        out += Markup("<p>%s <b>%s</b></p>") % (self.env._("Current state:"), current.name or "?")
        rows = Markup("")
        for tr in flow.transition_ids.sorted("sequence"):
            ok, why = tr._check_available(record, user)
            if tr._needed() > 1:
                why = why or self.env._("%(count)s of %(needed)s approvals so far.",
                                        count=len(tr._vote_logs(record).user_id), needed=tr._needed())
            rows += Markup("<tr><td>%s</td><td>%s → %s</td><td class='%s'>%s</td></tr>") % (
                tr.name, tr.from_state_id.name or self.env._("Any state"), tr.to_state_id.name,
                "text-success" if ok else "text-muted",
                self.env._("Shown") if ok else why)
        return out + Markup("<table class='table table-sm'><tbody>%s</tbody></table>") % rows
