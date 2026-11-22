# -*- coding: utf-8 -*-
import json
import logging
import re

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from .expression import check_expression

_logger = logging.getLogger(__name__)

SCHEMA = "dwo_approval_flow/1"
STATE_FIELD = "x_dwo_approval_state_id"
APPROVER_TYPES = ("users", "group", "dept", "field", "expr")
ACTION_TYPES = ("notify", "email", "update", "server")
MAX_M2O_STATES = 50
CHANNELS = ("bus", "activity", "email")


class DwoApprovalFlow(models.Model):
    _name = "dwo.approval.flow"
    _description = "Approval Flow"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one("res.company", help="Leave empty to apply to every company.")
    model_id = fields.Many2one(
        "ir.model", string="Model", required=True, ondelete="cascade", index=True,
        domain="[('transient', '=', False)]")
    model_name = fields.Char(related="model_id.model", store=True, index=True)
    state_mode = fields.Selection(
        [("custom", "My own states"), ("field", "A field of the model")],
        string="States come from", default="custom", required=True)
    state_field_id = fields.Many2one(
        "ir.model.fields", string="State field", ondelete="cascade",
        domain="[('model_id', '=', model_id), ('ttype', 'in', ('selection', 'many2one')), ('store', '=', True)]")
    domain = fields.Char(string="Applies to", default="[]", help="Only documents matching this domain use the flow.")
    replace_statusbar = fields.Boolean(
        string="Replace the form's status bar",
        help="Hide the status bar the form already has and show the approval one instead.")
    history_action = fields.Boolean(
        string="Approval history action", default=True,
        help="Adds \"Approval history\" to the Action menu of the form. It opens every vote and move of the document.")
    state_ids = fields.One2many("dwo.approval.state", "flow_id")
    transition_ids = fields.One2many("dwo.approval.transition", "flow_id")
    state_count = fields.Integer(compute="_compute_counts")
    transition_count = fields.Integer(compute="_compute_counts")
    graph = fields.Text(compute="_compute_graph", inverse="_inverse_graph")

    @api.depends("state_ids", "transition_ids")
    def _compute_counts(self):
        for flow in self:
            flow.state_count = len(flow.state_ids)
            flow.transition_count = len(flow.transition_ids)

    # ------------------------------------------------------------------
    # constraints
    # ------------------------------------------------------------------
    @api.constrains("state_mode", "state_field_id", "model_id")
    def _check_state_source(self):
        for flow in self:
            if flow.state_mode == "field":
                if not flow.state_field_id or flow.state_field_id.model_id != flow.model_id:
                    raise ValidationError(_("Pick a selection or many2one field of the model."))

    @api.constrains("domain")
    def _check_domain(self):
        for flow in self:
            try:
                value = safe_eval(flow.domain or "[]", self.env["ir.rule"]._eval_context())
            except Exception as error:
                raise ValidationError(_("Invalid domain: %s", error)) from error
            if not isinstance(value, (list, tuple)):
                raise ValidationError(_("A domain must be a list."))

    # ------------------------------------------------------------------
    # life cycle
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        flows = super().create(vals_list)
        flows._after_change()
        return flows

    def write(self, vals):
        result = super().write(vals)
        if {"active", "model_id", "state_mode", "state_field_id", "replace_statusbar",
                "domain", "company_id", "history_action"} & set(vals):
            self._after_change()
        return result

    def unlink(self):
        self._clear_view_cache()
        return super().unlink()

    def _clear_view_cache(self):
        self.env.registry.clear_cache("templates")
        self.env.registry.clear_cache()

    def _after_change(self):
        for flow in self:
            if flow.state_mode == "custom":
                flow._ensure_state_field()
                if not flow.state_ids:
                    flow.env["dwo.approval.state"].create({
                        "flow_id": flow.id, "name": _("Draft"), "key": "draft", "sequence": 1})
            elif flow.state_field_id:
                flow._sync_field_states()
        self._clear_view_cache()

    def _state_field_name(self):
        self.ensure_one()
        return STATE_FIELD if self.state_mode == "custom" else self.state_field_id.name

    def _ensure_state_field(self):
        """Create the many2one that holds the state of documents (own-states mode)."""
        self.ensure_one()
        Field = self.env["ir.model.fields"].sudo()
        if Field.search_count([("model_id", "=", self.model_id.id), ("name", "=", STATE_FIELD)]):
            return
        Field.create({
            "name": STATE_FIELD, "model_id": self.model_id.id, "field_description": "Approval State",
            "ttype": "many2one", "relation": "dwo.approval.state", "state": "manual",
            "on_delete": "set null", "copied": False, "index": True,
        })

    def action_refresh_states(self):
        self._sync_field_states()
        self._clear_view_cache()
        return True

    def _field_values(self):
        """``[(value, label)]`` of the model field a flow mirrors."""
        self.ensure_one()
        name = self.state_field_id.name
        field = self.env[self.model_name]._fields[name]
        if field.type == "selection":
            info = self.env[self.model_name].fields_get([name])[name]
            return [(key, label) for key, label in info["selection"]]
        records = self.env[field.comodel_name].sudo().search([], limit=MAX_M2O_STATES + 1)
        if len(records) > MAX_M2O_STATES:
            raise UserError(_(
                "%(model)s has more than %(max)s records, too many to draw as states.",
                model=field.comodel_name, max=MAX_M2O_STATES))
        return [(str(rec.id), rec.display_name) for rec in records]

    def _state_key(self, value, label):
        self.ensure_one()
        if self.state_field_id.ttype == "selection":
            return value
        return self.env["dwo.approval.state"].slugify(label) + "_" + value

    @api.model
    def field_states(self, model_id, state_field_id):
        """States a model field would give (for the designer, before the flow is saved)."""
        flow = self.new({"model_id": model_id, "state_mode": "field", "state_field_id": state_field_id})
        return [{"key": flow._state_key(value, label), "name": label, "value": value}
                for value, label in flow._field_values()]

    def _sync_field_states(self):
        """Mirror the values of the model field as state records (own-states flows are untouched)."""
        State = self.env["dwo.approval.state"]
        for flow in self.filtered(lambda f: f.state_mode == "field" and f.state_field_id):
            existing = {s.value: s for s in flow.state_ids}
            seen = set()
            used = set(flow.state_ids.mapped("key"))
            for index, (value, label) in enumerate(flow._field_values()):
                seen.add(value)
                state = existing.get(value)
                if state:
                    state.write({"name": label, "missing": False})
                    continue
                key = flow._state_key(value, label)
                while key in used:
                    key += "_"
                used.add(key)
                State.create({
                    "flow_id": flow.id, "name": label, "key": key, "value": value, "sequence": index + 1,
                    "pos_x": 10 + (index % 4) * 230, "pos_y": 20 + (index // 4) * 110})
            for value, state in existing.items():
                if value not in seen and not state.missing:
                    state.missing = True

    # ------------------------------------------------------------------
    # which flow, which state
    # ------------------------------------------------------------------
    def _applies(self, record):
        self.ensure_one()
        if self.company_id and "company_id" in record._fields and record.company_id \
                and record.company_id != self.company_id:
            return False
        domain = safe_eval(self.domain or "[]", self.env["ir.rule"]._eval_context())
        return not domain or bool(record.sudo().filtered_domain(domain))

    @api.model
    def _flow_of(self, record):
        flows = self.sudo().search([("model_name", "=", record._name), ("active", "=", True)])
        return next((flow for flow in flows if flow._applies(record)), self.browse())

    def _start_state(self):
        self.ensure_one()
        return self.state_ids.filtered(lambda s: not s.missing).sorted("sequence")[:1]

    def _current_state(self, record):
        """The ``dwo.approval.state`` a document is in, or an empty recordset."""
        self.ensure_one()
        rec = record.sudo()
        raw = rec[self._state_field_name()]
        if self.state_mode == "custom":
            return raw if raw and raw.flow_id == self else self._start_state()
        value = str(raw.id) if hasattr(raw, "ids") else (raw or "")
        return self.state_ids.filtered(lambda s: s.value == value and not s.missing)[:1]

    def _write_state(self, record, state):
        self.ensure_one()
        field = self.env[self.model_name]._fields[self._state_field_name()]
        value = state.id if self.state_mode == "custom" else (
            int(state.value) if field.type == "many2one" else state.value)
        record.sudo().write({field.name: value})

    def _after_move(self, record, transition, user):
        """Hook for later versions (e.g. lock the document)."""
        return None

    # ------------------------------------------------------------------
    # form header
    # ------------------------------------------------------------------
    def _inject_form(self, arch):
        """Add the approval widgets to the header of a form arch (an lxml element, edited in place)."""
        if arch.tag != "form":
            return
        header = arch.find("header")
        if header is None:
            header = etree.Element("header")
            arch.insert(0, header)
        replace = any(flow.replace_statusbar for flow in self)
        has_bar = False
        for node in header.findall("field"):
            if node.get("widget") == "statusbar":
                has_bar = True
                if replace:
                    node.set("invisible", "1")
        for flow in self:
            fname = flow._state_field_name()
            if not arch.xpath('.//field[@name="%s"]' % fname):
                etree.SubElement(header, "field", name=fname, invisible="1")
            if len(self) == 1:
                flow._hide_native_buttons(header, fname)
        fname = self[0]._state_field_name()
        index = max([i for i, n in enumerate(header) if n.tag != "field"] + [-1]) + 1
        header.insert(index, etree.Element("widget", name="dwo_approval_buttons", state_field=fname))
        if replace or not has_bar:
            header.append(etree.Element(
                "widget", name="dwo_approval_panel", state_field=fname, show_waiting="0", show_history="0"))

    def _hide_native_buttons(self, header, fname):
        """Hide the form's own button when a flow calls that method from the same state."""
        self.ensure_one()
        if (self.domain or "[]").replace(" ", "") != "[]":
            return
        for tr in self.transition_ids.filtered(lambda t: t.move_mode == "call_method" and t.method_name):
            for button in header.findall("button"):
                if button.get("name") != tr.method_name or button.get("type") != "object":
                    continue
                if not tr.from_state_id:
                    condition = "1"
                else:
                    value = tr.from_state_id._doc_value()
                    is_text = self.state_mode == "field" and self.state_field_id.ttype == "selection"
                    shown = repr(value) if is_text else value
                    condition = "%s == %s" % (fname, shown)
                    if self.state_mode == "custom" and tr.from_state_id == self._start_state():
                        condition = "(not %s or %s)" % (fname, condition)
                old = button.get("invisible")
                button.set("invisible", "(%s) or (%s)" % (old, condition) if old else condition)

    # ------------------------------------------------------------------
    # RPC used by the widgets
    # ------------------------------------------------------------------
    @api.model
    def _record_for(self, model, res_id):
        record = self.env[model].browse(res_id).exists()
        if not record:
            raise UserError(_("The document no longer exists."))
        record.check_access_rights("read")
        record.check_access_rule("read")
        return record

    @api.model
    def get_buttons(self, model, res_id):
        record = self._record_for(model, res_id)
        flow = self._flow_of(record)
        if not flow:
            return {"flow": False, "buttons": []}
        user = self.env.user
        buttons = []
        for tr in flow.transition_ids.sorted("sequence"):
            ok, _why = tr._check_available(record, user)
            if ok:
                needed = tr._needed()
                buttons.append({
                    "id": tr.id, "name": tr.name, "color": tr.color, "ask_reason": tr.ask_reason,
                    "needed": needed, "count": len(tr._vote_logs(record).user_id) if needed > 1 else 0})
        return {"flow": flow.id, "buttons": buttons}

    @api.model
    def press(self, model, res_id, transition_id, reason=None):
        record = self._record_for(model, res_id)
        transition = self.env["dwo.approval.transition"].sudo().browse(transition_id).exists()
        if not transition:
            raise UserError(_("The button no longer exists."))
        return transition._press(record, self.env.user, reason)

    @api.model
    def get_panel_data(self, model, res_id, limit=20, offset=0):
        record = self._record_for(model, res_id)
        flow = self._flow_of(record)
        if not flow:
            return {"flow": False}
        current = flow._current_state(record)
        waiting = []
        for tr in flow.transition_ids:
            if tr._needed() > 1 and (not tr.from_state_id or tr.from_state_id == current):
                voters = tr._vote_logs(record).user_id
                if voters:
                    waiting.append({"id": tr.id, "name": tr.name, "count": len(voters),
                                    "needed": tr._needed(), "voters": voters.mapped("name")})
        Log = self.env["dwo.approval.log"].sudo()
        domain = [("res_model", "=", model), ("res_id", "=", res_id)]
        logs = Log.search(domain, limit=limit + 1, offset=offset)
        return {
            "flow": {"id": flow.id, "name": flow.name},
            "states": [{"id": s.id, "key": s.key, "name": s.name, "color": s.color, "visible": s.always_visible}
                       for s in flow.state_ids.sorted("sequence") if not s.missing],
            "current": current.id,
            "waiting": waiting,
            "history": [{
                "id": log.id, "kind": log.kind, "button": log.button, "from": log.from_name,
                "to": log.to_name, "reason": log.reason, "votes": log.votes,
                "user": {"id": log.user_id.id, "name": log.user_id.name} if log.user_id else False,
                "date": fields.Datetime.to_string(log.date)} for log in logs[:limit]],
            "has_more": len(logs) > limit,
        }

    # ------------------------------------------------------------------
    # graph: JSON <-> records
    # ------------------------------------------------------------------
    @api.depends("state_ids", "transition_ids")
    def _compute_graph(self):
        for flow in self:
            flow.graph = json.dumps(flow._graph_dict(), indent=1) if flow.id else json.dumps(
                {"schema": SCHEMA, "states": [], "transitions": []})

    def _inverse_graph(self):
        for flow in self:
            if not flow.graph:
                continue
            try:
                data = json.loads(flow.graph)
            except ValueError as error:
                raise ValidationError(_("The flow is not valid JSON: %s", error)) from error
            if flow.state_mode == "field" and flow.state_field_id:
                flow._sync_field_states()  # the states of a new flow do not exist yet
                if not data.get("states") and not data.get("transitions"):
                    continue  # nothing drawn yet: the states just came from the field
            clean, errors = flow._normalize(data)
            if errors:
                raise ValidationError("\n".join(errors))
            flow._write_graph(clean)

    def _graph_dict(self):
        self.ensure_one()
        key_of = {s.id: s.key for s in self.state_ids}
        states = [{
            "id": s.id, "key": s.key, "name": s.name, "x": s.pos_x, "y": s.pos_y, "color": s.color,
            "visible": s.always_visible, "missing": s.missing} for s in self.state_ids.sorted("sequence")]
        transitions = []
        for tr in self.transition_ids.sorted("sequence"):
            who = None
            if tr.approver_ids:
                who = {
                    "approvers": [{
                        "type": a.kind, "user_ids": a.user_ids.ids, "group_id": a.group_id.id or False,
                        "value": a.value or "", "notify": {c: bool(a["notify_" + c]) for c in CHANNELS},
                        "label": a._label()} for a in tr.approver_ids],
                    "approvals": {"mode": tr.vote_mode, "n": tr.vote_n}}
            transitions.append({
                "id": tr.id, "name": tr.name, "from": key_of.get(tr.from_state_id.id),
                "to": key_of.get(tr.to_state_id.id), "color": tr.color, "ask_reason": tr.ask_reason, "list_action": tr.list_action,
                "notify": {"followers": {c: bool(tr["notify_followers_" + c]) for c in CHANNELS},
                           "creator": tr.notify_creator},
                "who": who, "rules": [r.domain for r in tr.rule_ids],
                "main_step": {
                    "mode": tr.move_mode, "method": tr.method_name or "",
                    "server_action_id": tr.server_action_id.id or False, "verify": tr.verify,
                    "run_as": tr.run_as, "guard": tr.guard_scope},
                "actions": [{
                    "type": a.kind, "user_ids": a.recipient_user_ids.ids, "expr": a.recipient_expr or "",
                    "message": a.message or "", "field": a.field_name or "", "value": a.value or "",
                    "server_action_id": a.server_action_id.id or False,
                    "template_id": a.template_id.id or False} for a in tr.action_ids]})
        return {
            "schema": SCHEMA, "name": self.name, "model": self.model_name, "state_mode": self.state_mode,
            "state_field": self.state_field_id.name or "", "statusbar": "replace" if self.replace_statusbar else "keep",
            "states": states, "transitions": transitions}

    # --- resolving names found in shared JSON ---
    def _resolve_users(self, token, errors, where):
        logins = [x.strip() for x in (token or "").split(",") if x.strip()]
        users = self.env["res.users"].sudo().search([("login", "in", logins)])
        for login in set(logins) - set(users.mapped("login")):
            errors.append("%s: no user with login “%s”." % (where, login))
        return users.ids

    def _resolve_ref(self, model, token, errors, where):
        token = (token or "").strip()
        if not token:
            return False
        record = self.env.ref(token, raise_if_not_found=False) if "." in token else None
        if record is None or record._name != model:
            record = self.env[model].sudo().search([("name", "=", token)], limit=2)
            if len(record) != 1:
                errors.append("%s: cannot find a unique %s “%s”." % (where, model, token))
                return False
        return record.id

    def _normalize(self, data):
        """Validate a graph (internal or shared format) and return ``(clean, errors)``.

        Names (logins, xml ids) are resolved to ids. Nothing is written.
        """
        self.ensure_one()
        errors = []
        if not isinstance(data, dict) or data.get("schema") != SCHEMA:
            return None, [_('The schema must be "%s".', SCHEMA)]
        states_in, trans_in = data.get("states"), data.get("transitions")
        if not isinstance(states_in, list) or not states_in:
            errors.append("states: at least one state is required.")
        if not isinstance(trans_in, list):
            errors.append("transitions: must be a list.")
        if errors:
            return None, errors
        keys = set()
        states = []
        for i, st in enumerate(states_in):
            where = "states[%d]" % i
            key, name = st.get("key"), st.get("name")
            if not key or not name:
                errors.append("%s: key and name are required." % where)
                continue
            if key in keys:
                errors.append('%s: duplicate key "%s".' % (where, key))
            keys.add(key)
            color = st.get("color", 0)
            if not isinstance(color, int) or not 0 <= color <= 11:
                errors.append("%s: color must be 0 to 11." % where)
            states.append({
                "key": key, "name": name, "x": int(st.get("x", 10 + i * 220)), "y": int(st.get("y", 170)),
                "color": color if isinstance(color, int) else 0, "visible": bool(st.get("visible", True))})
        if self.state_mode == "field":
            known = set(self.state_ids.mapped("key"))
            if self.state_field_id:
                known |= {self._state_key(value, label) for value, label in self._field_values()}
            for st in states:
                if st["key"] not in known:
                    errors.append('states: in "field" mode the states come from the field; "%s" is not one of them.'
                                  % st["key"])
        transitions = []
        model = self.model_name
        for i, tr in enumerate(trans_in):
            where = "transitions[%d]" % i
            if not tr.get("name"):
                errors.append("%s: name is required." % where)
            if tr.get("from") not in keys and tr.get("from") is not None:
                errors.append('%s: unknown state "%s" in from.' % (where, tr.get("from")))
            if tr.get("to") not in keys:
                errors.append('%s: unknown state "%s" in to.' % (where, tr.get("to")))
            color = tr.get("color", 0)
            if not isinstance(color, int) or not 0 <= color <= 11:
                errors.append("%s: color must be 0 to 11." % where)
            clean = {
                "id": tr.get("id") if isinstance(tr.get("id"), int) else False, "name": tr.get("name") or "",
                "from": tr.get("from"), "to": tr.get("to"), "color": color if isinstance(color, int) else 0,
                "ask_reason": bool(tr.get("ask_reason")), "list_action": bool(tr.get("list_action")),
                "notify": {
                    "followers": {c: bool(((tr.get("notify") or {}).get("followers") or {}).get(c)) for c in CHANNELS},
                    "creator": bool((tr.get("notify") or {}).get("creator"))},
                "approvers": [], "mode": "any", "n": 2,
                "rules": [], "actions": []}
            who = tr.get("who")
            if who:
                approvals = who.get("approvals") or {}
                clean["mode"] = approvals.get("mode", "any")
                clean["n"] = approvals.get("n", 2)
                if clean["mode"] not in ("any", "all", "n"):
                    errors.append("%s.who.approvals.mode must be any, all or n." % where)
                if not who.get("approvers"):
                    errors.append("%s.who: approvers is empty (use null for no restriction)." % where)
                for j, ap in enumerate(who.get("approvers") or []):
                    w = "%s.who.approvers[%d]" % (where, j)
                    kind = ap.get("type")
                    if kind not in APPROVER_TYPES:
                        errors.append("%s: type must be one of %s." % (w, ", ".join(APPROVER_TYPES)))
                        continue
                    line = {"kind": kind, "user_ids": [], "group_id": False, "value": "",
                            "notify": {c: bool((ap.get("notify") or {}).get(c)) for c in CHANNELS}}
                    if kind == "users":
                        line["user_ids"] = ap.get("user_ids") or self._resolve_users(ap.get("value"), errors, w)
                        if not line["user_ids"]:
                            errors.append("%s: pick at least one user." % w)
                    elif kind == "group":
                        line["group_id"] = ap.get("group_id") or self._resolve_ref(
                            "res.groups", ap.get("value"), errors, w)
                        if not line["group_id"]:
                            errors.append("%s: pick a group." % w)
                    elif kind == "field":
                        value = ap.get("value") or ""
                        match = re.search(r"\((\w+)\)\s*$", value)
                        line["value"] = match.group(1) if match else value
                        field = self.env[model]._fields.get(line["value"])
                        if not field or field.comodel_name != "res.users":
                            errors.append("%s: “%s” is not a user field of %s." % (w, line["value"], model))
                    elif kind == "expr":
                        line["value"] = ap.get("value") or ""
                        message = check_expression(self.env, model, line["value"])
                        if message:
                            errors.append("%s: %s" % (w, message))
                    clean["approvers"].append(line)
            for j, text in enumerate(tr.get("rules") or []):
                try:
                    value = safe_eval(text, self.env["ir.rule"]._eval_context())
                    if not isinstance(value, (list, tuple)):
                        raise ValueError("not a list")
                except Exception as error:
                    errors.append("%s.rules[%d]: invalid domain (%s)." % (where, j, error))
                clean["rules"].append(text)
            step = tr.get("main_step") or {"mode": "set_state"}
            clean["step"] = {
                "move_mode": step.get("mode", "set_state"), "method_name": step.get("method") or False,
                "server_action_id": step.get("server_action_id") or self._resolve_ref(
                    "ir.actions.server", step.get("server_action"), errors, where + ".main_step"),
                "verify": step.get("verify", True), "run_as": step.get("run_as", "user"),
                "guard_scope": "none" if step.get("guard") == "none" else "direct"}
            if clean["step"]["move_mode"] not in ("set_state", "call_method"):
                errors.append("%s.main_step.mode must be set_state or call_method." % where)
            if clean["step"]["move_mode"] == "call_method":
                if not clean["step"]["method_name"] and not clean["step"]["server_action_id"]:
                    errors.append("%s.main_step: a method or a server action is required." % where)
            for j, act in enumerate(tr.get("actions") or []):
                w = "%s.actions[%d]" % (where, j)
                kind = act.get("type")
                if kind not in ACTION_TYPES:
                    errors.append("%s: type must be one of %s." % (w, ", ".join(ACTION_TYPES)))
                    continue
                users = act.get("user_ids") or self._resolve_users(act.get("to"), errors, w)
                item = {
                    "kind": kind, "recipient_user_ids": users, "recipient_expr": act.get("expr") or False,
                    "message": act.get("message") or False, "field_name": act.get("field") or False,
                    "value": act.get("value") or False,
                    "server_action_id": act.get("server_action_id") or self._resolve_ref(
                        "ir.actions.server", act.get("server_action"), errors, w),
                    "template_id": act.get("template_id") or self._resolve_ref(
                        "mail.template", act.get("template"), errors, w)}
                if item["recipient_expr"]:
                    message = check_expression(self.env, model, item["recipient_expr"])
                    if message:
                        errors.append("%s: %s" % (w, message))
                if kind == "update" and item["field_name"] not in self.env[model]._fields:
                    errors.append("%s: field “%s” does not exist." % (w, item["field_name"]))
                clean["actions"].append(item)
            transitions.append(clean)
        if errors:
            return None, errors
        return {"states": states, "transitions": transitions}, []

    def _write_graph(self, clean):
        """Create/update/delete the records so they match ``clean``. One transaction."""
        self.ensure_one()
        State, Transition = self.env["dwo.approval.state"], self.env["dwo.approval.transition"]
        by_key = {s.key: s for s in self.state_ids}
        kept = self.env["dwo.approval.state"]
        for index, st in enumerate(clean["states"]):
            vals = {"name": st["name"], "sequence": index + 1, "pos_x": st["x"], "pos_y": st["y"],
                    "color": st["color"], "always_visible": st["visible"]}
            state = by_key.get(st["key"])
            if state:
                if self.state_mode == "field":
                    vals.pop("name")
                state.write(vals)
            else:
                state = State.create(dict(vals, flow_id=self.id, key=st["key"]))
                by_key[st["key"]] = state
            kept |= state
        existing = {t.id: t for t in self.transition_ids}
        used = self.env["dwo.approval.transition"]
        for index, tr in enumerate(clean["transitions"]):
            step = tr["step"]
            vals = {
                "name": tr["name"], "sequence": index + 1, "color": tr["color"], "ask_reason": tr["ask_reason"],
                "list_action": tr["list_action"], "notify_creator": tr["notify"]["creator"],
                **{"notify_followers_" + c: tr["notify"]["followers"][c] for c in CHANNELS},
                "from_state_id": by_key[tr["from"]].id if tr["from"] else False,
                "to_state_id": by_key[tr["to"]].id,
                "vote_mode": tr["mode"], "vote_n": tr["n"], **step}
            record = existing.get(tr["id"])
            if record:
                record.write(vals)
                record.approver_ids.unlink()
                record.rule_ids.unlink()
                record.action_ids.unlink()
            else:
                record = Transition.create(dict(vals, flow_id=self.id))
            used |= record
            for seq, ap in enumerate(tr["approvers"]):
                self.env["dwo.approval.approver"].create({
                    "transition_id": record.id, "sequence": seq + 1, "kind": ap["kind"],
                    "user_ids": [(6, 0, ap["user_ids"])], "group_id": ap["group_id"] or False,
                    "value": ap["value"] or False, **{"notify_" + c: ap["notify"][c] for c in CHANNELS}})
            for seq, text in enumerate(tr["rules"]):
                self.env["dwo.approval.rule"].create({"transition_id": record.id, "sequence": seq + 1, "domain": text})
            for seq, act in enumerate(tr["actions"]):
                act = dict(act, recipient_user_ids=[(6, 0, act["recipient_user_ids"])])
                self.env["dwo.approval.action"].create(dict(act, transition_id=record.id, sequence=seq + 1))
        (self.transition_ids - used).unlink()
        if self.state_mode == "custom":
            (self.state_ids - kept).unlink()
        self._clear_view_cache()
        self.invalidate_recordset(["graph", "state_ids", "transition_ids"])

    # --- shared JSON (no ids; logins and xml ids instead) ---
    @api.model
    def graph_to_share(self, graph_text):
        """Turn the designer's JSON into JSON that can be sent to another database."""
        data = json.loads(graph_text)
        users, groups = self.env["res.users"].sudo(), self.env["res.groups"].sudo()
        for state in data.get("states", []):
            state.pop("id", None)
            state.pop("missing", None)
        for tr in data.get("transitions", []):
            tr.pop("id", None)
            who = tr.get("who")
            if who:
                for ap in who["approvers"]:
                    if ap["type"] == "users":
                        ap["value"] = ",".join(users.browse(ap.pop("user_ids", [])).mapped("login"))
                    elif ap["type"] == "group" and ap.get("group_id"):
                        group = groups.browse(ap["group_id"])
                        ap["value"] = group.get_external_id().get(group.id) or group.name
                    ap.pop("user_ids", None)
                    ap.pop("group_id", None)
                    ap.pop("label", None)
            step = tr.get("main_step") or {}
            sa = step.pop("server_action_id", False)
            if sa:
                action = self.env["ir.actions.server"].sudo().browse(sa)
                step["server_action"] = action.get_external_id().get(action.id) or action.name
            for act in tr.get("actions", []):
                act["to"] = ",".join(users.browse(act.pop("user_ids", [])).mapped("login"))
                for key, model in (("server_action_id", "ir.actions.server"), ("template_id", "mail.template")):
                    rec_id = act.pop(key, False)
                    if rec_id:
                        rec = self.env[model].sudo().browse(rec_id)
                        act[key[:-3]] = rec.get_external_id().get(rec.id) or rec.display_name
        return json.dumps(data, indent=1)

    @api.model
    def share_to_graph(self, model_id, state_mode, state_field_id, text, flow_id=False):
        """Check a pasted JSON. Returns ``{"errors": [...]}`` or ``{"graph": "..."}`` for the designer."""
        try:
            data = json.loads(text)
        except ValueError as error:
            return {"errors": [_("Not valid JSON: %s", error)]}
        flow = self.browse(flow_id) if flow_id else self.new({
            "model_id": model_id, "state_mode": state_mode, "state_field_id": state_field_id})
        clean, errors = flow._normalize(data)
        if errors:
            return {"errors": errors}
        return {"graph": json.dumps(_as_graph(clean, data, flow.env), indent=1)}


def _approver_label(env, line):
    """Text shown in the designer for an approver line that is not saved yet."""
    if env is None:
        return ""
    if line["kind"] == "users":
        return ", ".join(env["res.users"].browse(line["user_ids"]).mapped("name"))
    if line["kind"] == "group":
        return env["res.groups"].browse(line["group_id"]).display_name or ""
    if line["kind"] == "dept":
        return _("Same department as the document")
    return line["value"] or ""


def _as_graph(clean, data, env=None):
    """Build the designer JSON from a validated graph (resolved ids, no db ids)."""
    out = {"schema": SCHEMA, "states": [], "transitions": []}
    for st in clean["states"]:
        out["states"].append(dict(st, **{"id": False, "missing": False}))
    for tr in clean["transitions"]:
        out["transitions"].append({
            "id": False, "name": tr["name"], "from": tr["from"], "to": tr["to"], "color": tr["color"],
            "ask_reason": tr["ask_reason"], "list_action": tr["list_action"],
            "notify": {"followers": dict(tr["notify"]["followers"]), "creator": tr["notify"]["creator"]},
            "who": {"approvers": [{"type": a["kind"], "user_ids": a["user_ids"], "group_id": a["group_id"],
                                   "value": a["value"], "notify": dict(a["notify"]),
                                   "label": _approver_label(env, a)} for a in tr["approvers"]],
                    "approvals": {"mode": tr["mode"], "n": tr["n"]}} if tr["approvers"] else None,
            "rules": tr["rules"],
            "main_step": {"mode": tr["step"]["move_mode"], "method": tr["step"]["method_name"] or "",
                          "server_action_id": tr["step"]["server_action_id"] or False,
                          "verify": tr["step"]["verify"], "run_as": tr["step"]["run_as"],
                          "guard": tr["step"]["guard_scope"]},
            "actions": [{"type": a["kind"], "user_ids": a["recipient_user_ids"], "expr": a["recipient_expr"] or "",
                         "message": a["message"] or "", "field": a["field_name"] or "", "value": a["value"] or "",
                         "server_action_id": a["server_action_id"] or False,
                         "template_id": a["template_id"] or False} for a in tr["actions"]]})
    return out
