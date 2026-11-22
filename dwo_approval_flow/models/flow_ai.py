# -*- coding: utf-8 -*-
"""The "AI" button of the designer: describe a flow in words, get a JSON suggestion.

The model call itself is ``_ai_complete``. For now it is a MOCK that returns a random flow;
replace its body with the real API call (it gets the system prompt and the user message and
must return the text the AI answered). Everything around it (the prompt, the checks, the retry
when the JSON is rejected) stays the same.
"""
import json
import logging
import random
import re

from odoo import api, models
from odoo.tools import file_open

_logger = logging.getLogger(__name__)

PROMPT_FILE = "dwo_approval_flow/docs/AI_PROMPT.md"
PROMPT_START, PROMPT_END = "=== SYSTEM PROMPT START ===", "=== SYSTEM PROMPT END ==="
MAX_TRIES = 3
MAX_FIELDS, MAX_GROUPS, MAX_USERS, MAX_OTHERS = 80, 60, 100, 40
RULE_TYPES = ("selection", "many2one", "boolean", "date", "datetime", "integer", "float", "monetary", "char")


class DwoApprovalFlow(models.Model):
    _inherit = "dwo.approval.flow"

    # ------------------------------------------------------------------
    # the prompt
    # ------------------------------------------------------------------
    @api.model
    def _ai_system_prompt(self):
        """The fixed part of the prompt: the text between the markers of docs/AI_PROMPT.md."""
        with file_open(PROMPT_FILE, "r") as handle:
            text = handle.read()
        # the markers sit alone on their line (the intro of the file also mentions them in the middle of a sentence)
        start, end = text.find("\n" + PROMPT_START + "\n"), text.find("\n" + PROMPT_END + "\n")
        if start < 0 or end < 0:
            return text
        return text[start + len(PROMPT_START) + 2:end].strip()

    def _ai_context(self, current=None):
        """The CONTEXT block: what this database offers for the model of the flow."""
        self.ensure_one()
        env, model = self.env, self.model_name
        lines = ["CONTEXT", "flow_name: %s" % (self.name or ""),
                 "model: %s (%s)" % (model, self.model_id.name),
                 "state_mode: %s" % self.state_mode,
                 "state_field: %s" % (self.state_field_id.name or "")]
        if self.state_mode == "field" and self.state_field_id:
            lines.append("field_states: " + ", ".join(
                "%s=%s" % (self._state_key(value, label), label) for value, label in self._field_values()))
        lines.append("existing_flow: %s" % (current or "none"))

        Model = env[model]
        info = Model.fields_get()
        lines += ["", "fields usable in rules (name | type | detail):"]
        count = 0
        for name, field in Model._fields.items():
            if count >= MAX_FIELDS:
                break
            if not field.store or field.type not in RULE_TYPES or name in ("id", "create_uid", "write_uid"):
                continue
            detail = ""
            if field.type == "selection":
                detail = ", ".join("'%s'=%s" % (key, label) for key, label in info[name].get("selection") or [])
            elif field.type == "many2one":
                detail = field.comodel_name
            lines.append("  %s | %s | %s" % (name, field.type, detail))
            count += 1

        lines += ["", "user fields on the model (usable in approver type \"field\" and in expressions):"]
        lines.append("  " + ", ".join(
            name for name, field in Model._fields.items()
            if field.type in ("many2one", "many2many") and field.comodel_name == "res.users") or "  none")

        Groups = env["res.groups"].sudo()
        lines += ["", "groups (xml_id | name):"]
        for group in Groups.search([("users", "!=", False)], limit=MAX_GROUPS):
            xml_id = group.get_external_id().get(group.id)
            if xml_id:
                lines.append("  %s | %s" % (xml_id, group.full_name))
        lines += ["", "users (login | name):"]
        for user in env["res.users"].sudo().search([("share", "=", False)], limit=MAX_USERS):
            lines.append("  %s | %s" % (user.login, user.name))

        for title, comodel in (("mail templates for this model (xml_id | name):", "mail.template"),
                               ("server actions for this model (xml_id | name):", "ir.actions.server")):
            lines += ["", title]
            for rec in env[comodel].sudo().search([("model_id", "=", self.model_id.id)], limit=MAX_OTHERS):
                lines.append("  %s | %s" % (rec.get_external_id().get(rec.id) or rec.id, rec.name))
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # the model call (MOCK)
    # ------------------------------------------------------------------
    @api.model
    def _ai_complete(self, system, messages, flow=None):
        """Send ``system`` and ``messages`` (``[{"role": ..., "content": ...}]``) to the AI, return its text.

        MOCK: ignores the prompt and answers with a random valid flow. Replace the body with the real call.
        """
        _logger.info("AI mock: system prompt %d chars, %d message(s)", len(system), len(messages))
        match = re.search(r"^existing_flow: (\{.*?\n\})\s*$", system, re.S | re.M)
        try:
            current = json.loads(match.group(1)) if match else None
        except ValueError:
            current = None
        return json.dumps(self._ai_mock_flow(flow, current), indent=1)

    def _ai_mock_edit(self, flow, data, rnd):
        """MOCK of an edit: keep the flow, add one state (or recolor one in field mode)."""
        states, transitions = data["states"], data["transitions"]
        if flow.state_mode == "field" or not states:
            rnd.choice(states)["color"] = rnd.randint(1, 11)
        else:
            last = states[-1]
            key = "extra_review_%d" % rnd.randint(10, 99)
            states.append({"key": key, "name": "Extra review", "x": last.get("x", 0) + 220, "y": 170,
                           "color": 2, "visible": True})
            transitions.append({"name": "Send to extra review", "from": last["key"], "to": key, "color": 0,
                                "who": None, "rules": [], "actions": []})
        data["notes"] = ["Mock answer: your flow with a small random change, not built from your description."]
        return data

    def _ai_mock_flow(self, flow, current=None):
        rnd = random.Random()
        if current:
            return self._ai_mock_edit(flow, current, rnd)
        data = {"schema": "dwo_approval_flow/1", "name": flow.name or "AI suggested flow",
                "model": flow.model_name, "state_mode": flow.state_mode,
                "state_field": flow.state_field_id.name or "", "statusbar": "replace"}
        if flow.state_mode == "field" and flow.state_field_id:
            values = flow._field_values()
            states = [{"key": flow._state_key(v, label), "name": label} for v, label in values]
        else:
            pool = ["Draft", "Submitted", "In review", "Approved by leader", "Approved by manager",
                    "Waiting for finance", "Approved", "Rejected", "Cancelled"]
            names = ["Draft"] + sorted(rnd.sample(pool[1:7], rnd.randint(2, 4)), key=pool.index) + ["Rejected"]
            states = [{"key": re.sub(r"\W+", "_", n.lower()), "name": n} for n in names]
        colors = [0, 4, 2, 10, 10, 8, 1]
        for index, st in enumerate(states):
            st.update(x=10 + 220 * index, y=170, color=colors[min(index, len(colors) - 1)], visible=True)
        if states and states[-1]["name"] == "Rejected":
            states[-1].update(color=1, visible=False)
        transitions = []
        main = [s for s in states if s["name"] != "Rejected"]
        rejected = next((s for s in states if s["name"] == "Rejected"), None)
        for a, b in zip(main, main[1:]):
            who = None
            if a is not main[0]:
                who = {"approvers": [{"type": "group", "value": rnd.choice(["base.group_user", "base.group_system"])}],
                       "approvals": {"mode": "any", "n": 1}}
            transitions.append({"name": "Submit" if a is main[0] else "Approve", "from": a["key"], "to": b["key"],
                                "color": 0 if a is main[0] else 10, "who": who, "rules": [], "actions": []})
            if rejected and a is not main[0]:
                transitions.append({"name": "Reject", "from": a["key"], "to": rejected["key"], "color": 1,
                                    "ask_reason": True, "who": who, "rules": [], "actions": []})
        if rejected and main:
            transitions.append({"name": "Reopen", "from": rejected["key"], "to": main[0]["key"], "color": 0,
                                "who": None, "rules": [], "actions": []})
        data.update(states=states, transitions=transitions,
                    notes=["Mock answer: a random flow, not built from your description."])
        return data

    # ------------------------------------------------------------------
    # called by the designer
    # ------------------------------------------------------------------
    @api.model
    def ai_suggest(self, model_id, state_mode, state_field_id, request, current=None, flow_id=False):
        """Ask the AI for a flow. Returns ``{"errors": [...]}`` or ``{"graph": ..., "json": ..., "notes": [...]}``."""
        request = (request or "").strip()
        if not request:
            return {"errors": [self.env._("Describe the flow you want first.")]}
        flow = self.browse(flow_id) if flow_id else self.new({
            "model_id": model_id, "state_mode": state_mode, "state_field_id": state_field_id})
        if not flow.model_id:
            return {"errors": [self.env._("Pick the model of the flow first.")]}
        if flow.state_mode == "field" and not flow.state_field_id:
            return {"errors": [self.env._("Pick the State field first.")]}
        if current:
            try:
                current = self.graph_to_share(current)
            except (ValueError, KeyError):
                current = None
        system = self._ai_system_prompt() + "\n\n" + flow._ai_context(current)
        if current:
            request = ("Modify the existing flow (existing_flow in CONTEXT) according to this description. Keep the keys "
                       "of the states that remain and return the full JSON.\n\n" + request)
        messages = [{"role": "user", "content": request}]
        errors = []
        for _attempt in range(MAX_TRIES):
            answer = self._ai_complete(system, messages, flow)
            messages.append({"role": "assistant", "content": answer})
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", (answer or "").strip())
            result = self.share_to_graph(flow.model_id.id, flow.state_mode, flow.state_field_id.id or False,
                                         text, flow.id if flow_id else False)
            if "graph" in result:
                try:
                    notes = json.loads(text).get("notes") or []
                except ValueError:
                    notes = []
                return {"graph": result["graph"], "json": text, "notes": notes}
            errors = result["errors"]
            messages.append({"role": "user", "content": (
                "The JSON was rejected. Fix it and return the full JSON again. Errors:\n" + "\n".join(errors))})
        return {"errors": errors}
