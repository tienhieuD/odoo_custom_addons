# -*- coding: utf-8 -*-
"""v1.1 of the flow model: the own-state guard, entries in the Action menu, several flows per model."""
import inspect

from markupsafe import Markup

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools.safe_eval import safe_eval

from . import guard

HISTORY_LABEL = "__history__"


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
    # the own-state field cannot be written directly
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
        return set()  # nothing is patched on the registry classes: the own-state guard lives in base.write

    @api.model
    def _guard_sync(self):
        """Patch exactly the pairs the active flows need; tell the other workers to do the same."""
        registry = self.env.registry
        guard.sync(registry, self._guard_pairs())
        if self.pool.ready:
            registry.registry_invalidated = True

    @api.model
    def _guard_write_refused(self):
        raise UserError(_("The approval state can only be changed with the approval buttons."))

    @api.model
    def model_methods(self, model_name):
        """Public methods of a model with their docstring, for the autocomplete of the designer."""
        if not self.env.user.has_group("dwo_approval_flow.group_approval_manager"):
            raise AccessError(_("Only flow administrators can list the methods of a model."))
        if model_name not in self.env:
            return []
        orm = set(dir(models.Model)) | set(dir(models.BaseModel))
        cls = type(self.env[model_name])
        found = []
        for name in dir(cls):
            if name.startswith("_") or name in orm:
                continue
            func = getattr(cls, name, None)
            if not callable(func) or isinstance(func, type):
                continue
            found.append({"name": name, "doc": inspect.getdoc(func) or ""})
        # the methods behind buttons first
        found.sort(key=lambda m: (not m["name"].startswith(("action_", "button_")), m["name"]))
        return found

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
            if flow.active and flow.history_action:
                vals = {
                    "name": _("Approval history"), "model_id": flow.model_id.id, "state": "code",
                    "code": "action = env['dwo.approval.flow'].action_history(%r, records.ids)" % flow.model_name,
                    "binding_model_id": flow.model_id.id, "binding_type": "action",
                    "binding_view_types": "form", "dwo_approval_flow_id": flow.id, "dwo_label": HISTORY_LABEL}
                action = existing.filtered(lambda a: a.dwo_label == HISTORY_LABEL)[:1]
                if action:
                    action.write(vals)
                else:
                    action = Action.create(vals)
                kept |= action
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
        self.env.registry.clear_caches()

    @api.model
    def action_history(self, model, ids):
        """Open the approval history of one document (also usable as a server action or a button)."""
        if not model or not ids:
            raise UserError(_("Select a document first."))
        record = self.env[model].browse(ids[0]).exists()
        if not record:
            raise UserError(_("The document no longer exists."))
        record.check_access_rights("read")
        record.check_access_rule("read")
        return self.env["dwo.approval.history"].open_for(record)

    @api.model
    def press_label(self, flow_id, label, ids):
        """Press the arrow called ``label`` on every selected document where it is available."""
        flow = self.sudo().browse(flow_id).exists()
        if not flow or not flow.active:
            raise UserError(_("This approval is not active."))
        records = self.env[flow.model_name].browse(ids).exists()
        records.check_access_rights("read")
        records.check_access_rule("read")
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
        message = _("%(label)s: %(done)s done.", label=label, done=done)
        if skipped:
            message += " " + _("Skipped: %s", ", ".join(skipped[:10]))
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
            "target": "new", "name": _("Test the flow"),
            "context": {"default_flow_id": self.id}}


    # ------------------------------------------------------------------
    # Odoo 15: the legacy domain widget cannot be shown read only in the designer, so the server describes the rules
    # ------------------------------------------------------------------
    @api.model
    def describe_domains(self, model_name, domains):
        """Readable text of each domain, such as "Total greater than 1000"."""
        names = {"=": _("is"), "!=": _("is not"), ">": _("greater than"), ">=": _("greater or equal to"),
                 "<": _("lower than"), "<=": _("lower or equal to"), "in": _("is in"), "not in": _("is not in"),
                 "like": _("contains"), "ilike": _("contains"), "not like": _("does not contain"),
                 "not ilike": _("does not contain"), "=like": _("matches"), "=ilike": _("matches"), "=?": _("is")}
        Model = self.env[model_name] if model_name in self.env else None
        out = []
        for text in domains or []:
            try:
                domain = safe_eval(text or "[]", self.env["ir.rule"]._eval_context())
            except Exception:  # not a domain we can read: show the text as it is
                out.append(text)
                continue
            parts = []
            for leaf in domain:
                if isinstance(leaf, str) or len(leaf) != 3:
                    continue
                name, op, value = leaf
                field = Model._fields.get(name.split(".")[0]) if Model is not None else None
                label = field.string if field else name
                if value is False and op in ("=", "!="):
                    parts.append("%s %s" % (label, _("is not set") if op == "=" else _("is set")))
                else:
                    parts.append("%s %s %s" % (label, names.get(op, op), value))
            out.append((" %s " % _("and")).join(parts) or _("all records"))
        return out


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
            return Markup("<p class='text-muted'>%s</p>") % _("Pick a document and a user.")
        out = Markup("")
        routed = self.env["dwo.approval.flow"]._flow_of(record)
        if routed != flow:
            out += Markup("<p class='text-warning'>%s</p>") % _(
                "This document is handled by another flow (%s), or by none: this flow does not apply to it.",
                routed.name or "-")
        current = flow._current_state(record)
        out += Markup("<p>%s <b>%s</b></p>") % (_("Current state:"), current.name or "?")
        rows = Markup("")
        for tr in flow.transition_ids.sorted("sequence"):
            ok, why = tr._check_available(record, user)
            if tr._needed() > 1:
                why = why or _("%(count)s of %(needed)s approvals so far.",
                                        count=len(tr._vote_logs(record).user_id), needed=tr._needed())
            rows += Markup("<tr><td>%s</td><td>%s → %s</td><td class='%s'>%s</td></tr>") % (
                tr.name, tr.from_state_id.name or _("Any state"), tr.to_state_id.name,
                "text-success" if ok else "text-muted",
                _("Shown") if ok else why)
        return out + Markup("<table class='table table-sm'><tbody>%s</tbody></table>") % rows
