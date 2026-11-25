# -*- coding: utf-8 -*-
"""The assistant: describes a page change in words, gets a new page back. It never saves anything: the answer is a proposal,
validated as the person who asked, that the editor loads as a draft (Save and Discard decide, and the revision check
protects the page).

What leaves this server, always and only: the grammar of a page, the names and kinds of the fields the caller may read in the
datasets in play, the metrics, the page as it is now and the request. No record is ever sent. The provider and its key are
set by system administrators (Dashboard > Configuration > AI assistant); the key is never returned to a browser."""
import json
import logging
import re

import psycopg2
import requests

from odoo import _, api, models
from odoo.exceptions import AccessError, UserError

from ..spec import constants as C
from ..spec.grammar import dataset_help, format_help
from ..spec.sqlscan import scan

_logger = logging.getLogger(__name__)

DEFAULT_OLG_ENDPOINT = "https://olg.api.odoo.com"  # the one the HTML editor of Odoo uses
DEFAULT_OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"
PROVIDER_TIMEOUT = 45     # seconds per call; a request makes two at most, well under the 120 s a worker is allowed
MAX_REQUEST = 1500        # characters of what the person writes
MAX_FIELDS = 70           # fields described per dataset
MAX_PAGE_JSON = 24000     # the current page, as sent
MAX_ANSWER = 200000
MAX_TABLES = 8            # tables described to the service for a SQL dataset
MAX_TABLE_COLUMNS = 60
MANAGER = "dwo_dashboard.group_dwo_dashboard_manager"
TABLE_NAME = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")
FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.I)


class DwoDashboardAI(models.AbstractModel):
    _name = "dwo.dashboard.ai"
    _description = "Dashboard assistant"

    # ---------------------------------------------------------------------------------------------------- providers
    @api.model
    def _dwo_ai_providers(self):
        """{name: (label, callable(prompt, history) -> text)}. A plugin adds its own with ``super()``."""
        return {"odoo_olg": (_("Odoo AI (default)"), self._complete_olg),
                "openai": (_("OpenAI-compatible API"), self._complete_openai)}

    @api.model
    def _param(self, key, default=False):
        return self.env["ir.config_parameter"].sudo().get_param("dwo_dashboard.ai_" + key, default)

    @api.model
    def _provider_name(self):
        name = self._param("provider", "odoo_olg")
        return name if name in self._dwo_ai_providers() else "odoo_olg"

    @api.model
    def _complete_olg(self, prompt, history):
        """Odoo's own gateway (the one the HTML editor uses): plain text in, plain text out, no system role, no tools."""
        from odoo.addons.iap.tools import iap_tools  # imported here: the module does not need IAP unless this provider runs
        params = self.env["ir.config_parameter"].sudo()
        endpoint = params.get_param("html_editor.olg_api_endpoint", DEFAULT_OLG_ENDPOINT)
        response = iap_tools.iap_jsonrpc(endpoint + "/api/olg/1/chat", params={
            "prompt": prompt, "conversation_history": history or [], "database_id": params.get_param("database.uuid")},
            timeout=PROVIDER_TIMEOUT)
        status = (response or {}).get("status")
        if status == "success":
            return response["content"]
        if status == "error_prompt_too_long":
            raise UserError(_("The request is too long for the AI service. Use fewer data sources or a shorter request."))
        if status == "limit_call_reached":
            raise UserError(_("The AI service refused the request: the limit of this database is reached. Try again later."))
        raise UserError(_("The AI service could not answer. Try again later."))

    @api.model
    def _complete_openai(self, prompt, history):
        key = self._param("api_key")
        if not key:
            raise UserError(_("The AI assistant is not set up: ask an administrator to add the API key."))
        endpoint = self._param("endpoint") or DEFAULT_OPENAI_ENDPOINT
        messages = [{"role": "system", "content": _("You reply with one JSON object and nothing else.")}]
        messages += [{"role": m["role"], "content": m["content"]} for m in history or []]
        messages.append({"role": "user", "content": prompt})
        try:
            reply = requests.post(endpoint, headers={"Authorization": "Bearer " + key}, timeout=PROVIDER_TIMEOUT, json={
                "model": self._param("model") or "gpt-4o-mini", "messages": messages, "temperature": 0})
            reply.raise_for_status()
            return reply.json()["choices"][0]["message"]["content"]
        except (requests.RequestException, KeyError, ValueError, IndexError):
            _logger.warning("dashboard AI: the %s provider failed", "openai")  # never the key, never the prompt
            raise UserError(_("The AI service could not answer. Check the endpoint, the model and the key."))

    # ---------------------------------------------------------------------------------------------------- prompt
    @api.model
    def _describe_datasets(self, refs):
        """The datasets in play as short lines, from what the caller can read (``describe_dataset`` is as the caller)."""
        explore = self.env["dwo.dashboard.explore"]
        lines = []
        for ref in refs:
            if not ref.startswith("orm:"):
                continue  # a blend or a SQL dataset is never described to the service (a SQL one has a query nobody should send out)
            try:
                d = explore.describe_dataset(ref)
            except AccessError:
                continue
            dims, measures = [], []
            for f in d["fields"][:MAX_FIELDS * 3]:
                kind = f["type"] if not f.get("relation") else "%s>%s" % (f["type"], f["relation"])
                if f["selection"]:
                    kind += ":" + "/".join(str(k) for k, _label in f["selection"][:8])
                if f["dimension"] and len(dims) < MAX_FIELDS:
                    dims.append("%s(%s)" % (f["name"], kind))
                if f["measure"] and f["type"] != "many2one" and len(measures) < MAX_FIELDS and f["aggs"] != ["count_distinct"]:
                    measures.append("%s(%s)" % (f["name"], "/".join(f["aggs"])))
            metrics = ["%s=%s%s" % (m["name"], m["label"], " [%s]" % m["agg"]) for m in d["metrics"]]
            lines.append("%s \"%s\"\n  group by: %s\n  measures: %s%s" % (
                ref, d["label"], ", ".join(dims) or "-", ", ".join(measures) or "-",
                "\n  metrics (use {\"metric\":name}): " + "; ".join(metrics) if metrics else ""))
        return "\n".join(lines)

    @api.model
    def _build_prompt(self, spec, request, refs):
        registry = self.env["dwo.dashboard.spec"]._dwo_registry()
        page = json.dumps(spec, separators=(",", ":"), ensure_ascii=False)
        if len(page) > MAX_PAGE_JSON:
            raise UserError(_("This page is too large for the assistant."))
        return (
            "You edit a dashboard page of Odoo. Reply with the COMPLETE new page as ONE JSON object and nothing else: "
            "no markdown, no comments, no explanation. Keep everything the request does not touch exactly as it is. "
            "Use only the data listed below.\n\nFORMAT\n%s\n\nDATA\n%s\n\nCURRENT PAGE\n%s\n\nREQUEST\n%s" % (
                format_help(registry), self._describe_datasets(refs) or "(none)", page, request.strip()))

    # ---------------------------------------------------------------------------------------------------- answers
    @staticmethod
    def _parse(text):
        text = FENCE.sub("", (text or "").strip())
        if len(text) > MAX_ANSWER:
            raise ValueError("too long")
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end < start:
            raise ValueError("no JSON object in the answer")
        value = json.loads(text[start:end + 1])
        if not isinstance(value, dict):
            raise ValueError("the answer is not an object")
        return value

    @api.model
    def _repair(self, spec, errors):
        """The two mistakes a model keeps making and that cost nothing to put right: a widget laid over another one (it goes to
        the bottom of the page) and a sort by something that is not a measure of the widget (the sort is dropped). Anything
        else goes back to the model. Returns True when something was changed."""
        changed = False
        widgets = spec.get("widgets") if isinstance(spec.get("widgets"), list) else []
        cols = spec.get("grid", {}).get("cols", C.GRID_COLS_DEFAULT) if isinstance(spec.get("grid"), dict) else C.GRID_COLS_DEFAULT
        for e in errors:
            m = re.match(r"^/widgets/(\d+)(/order.*|/[xywh])?$", e["path"])
            if not m or int(m.group(1)) >= len(widgets) or not isinstance(widgets[int(m.group(1))], dict):
                continue
            widget = widgets[int(m.group(1))]
            if m.group(2) and m.group(2).startswith("/order") and widget.pop("order", None) is not None:
                changed = True
            elif e["code"] == "layout":
                others = [w for i, w in enumerate(widgets) if i != int(m.group(1)) and isinstance(w, dict)]
                bottom = max([w.get("y", 0) + w.get("h", 0) for w in others if isinstance(w.get("y"), int) and isinstance(w.get("h"), int)] or [0])
                widget["x"], widget["y"] = 0, bottom
                if isinstance(widget.get("w"), int) and widget["w"] > cols:
                    widget["w"] = cols
                changed = True
        return changed

    @api.model
    def _diff(self, before, after):
        old = {w["id"]: w for w in (before or {}).get("widgets", []) if isinstance(w, dict) and "id" in w}
        new = {w["id"]: w for w in after.get("widgets", []) if isinstance(w, dict) and "id" in w}
        return {"added": [i for i in new if i not in old], "removed": [i for i in old if i not in new],
                "changed": [i for i in new if i in old and new[i] != old[i]],
                "page_changed": {k: v for k, v in after.items() if k != "widgets"} != {k: v for k, v in (before or {}).items() if k != "widgets"}}

    # ---------------------------------------------------------------------------------------------------- public API
    @api.model
    def get_status(self):
        """What the editor needs to know before showing the assistant."""
        providers = self._dwo_ai_providers()
        name = self._provider_name()
        return {"provider": name, "label": providers[name][0], "enabled": self._enabled(),
                "configured": name != "openai" or bool(self._param("api_key"))}

    @api.model
    def _enabled(self):
        """A switch for a database that must not call an AI service (a public demo): ``dwo_dashboard.ai_enabled`` = 0."""
        return self._param("enabled", "1") not in ("0", "False", "false")

    @api.model
    def propose(self, page_id, request, datasets=None, current=None):
        """A new page for ``page``, from words. As the caller, who must be able to edit the page. ``current`` is the page as the
        editor shows it (a draft that is not saved yet); the stored one is used without it. Returns
        ``{"ok": True, "spec", "diff", "retried"}`` or ``{"ok": False, "message", "errors"}``; never saves."""
        if not self._enabled():
            raise UserError(_("The assistant is switched off on this database."))
        page = self.env["dwo.dashboard.page"].browse(page_id)
        page.check_access("write")
        if page._level() == "view":
            raise AccessError(_("You can only look at this page."))
        request = (request or "").strip()
        if not request or len(request) > MAX_REQUEST:
            raise UserError(_("Write what you want in 1 to %d characters.") % MAX_REQUEST)
        spec = current if isinstance(current, dict) else page.spec or {"schema": C.SCHEMA_ID, "widgets": []}
        refs = list(dict.fromkeys([w["dataset"] for w in spec.get("widgets", []) if isinstance(w, dict) and w.get("dataset")]
                                  + [d for d in (datasets or []) if isinstance(d, str) and d.startswith("orm:")]))[:6]
        prompt = self._build_prompt(spec, request, refs)
        complete = self._dwo_ai_providers()[self._provider_name()][1]
        history, retried, repaired, problem = [], False, False, ""
        for attempt in (1, 2):
            text = complete(prompt, history)
            try:
                new = self._parse(text)
            except (ValueError, json.JSONDecodeError) as exc:
                problem = _("The answer was not a page (%s).", exc)
                errors = [{"path": "", "code": "json", "message": str(exc)}]
            else:
                new.setdefault("schema", C.SCHEMA_ID)
                result = self.env["dwo.dashboard.spec"]._validate(new, True)
                for _round in range(4):  # a repair can uncover the next overlap: a few rounds, then it is the model's turn
                    if result["valid"] or not self._repair(new, result["errors"]):
                        break
                    repaired = True
                    result = self.env["dwo.dashboard.spec"]._validate(new, True)
                if result["valid"]:
                    return {"ok": True, "spec": new, "diff": self._diff(spec, new), "retried": retried, "repaired": repaired}
                problem = _("The page proposed is not valid.")
                errors = result["errors"]
            if attempt == 1:  # one more try, told what was wrong
                retried = True
                history = [{"role": "user", "content": prompt}, {"role": "assistant", "content": (text or "")[:6000]}]
                prompt = ("Your page cannot be used. Problems:\n%s\nReply again with the complete corrected page as ONE JSON "
                          "object and nothing else." % "\n".join("%(path)s: %(message)s" % e for e in errors[:8]))
        return {"ok": False, "message": problem, "errors": errors[:8], "retried": retried}

    # ---------------------------------------------------------------------------------------------------- datasets
    @api.model
    def _describe_tables(self, names, request=""):
        """Tables of the database as ``table(column type, ...)`` lines: names and types, nothing else. A table of the denylist of the
        SQL engine and a column that looks like a credential are never described. ``names`` are what the manager chose; without them
        the tables whose name appears in the request are used. Returns ``(text, [table names])``."""
        from ..engine import sql as sql_engine
        denied = sql_engine.denied_tables(self.env)
        wanted = [n.strip().lower().replace(".", "_") for n in names or [] if isinstance(n, str)]
        if not wanted:
            words = [w for w in re.findall(r"[a-z0-9_]+", (request or "").lower()) if len(w) >= 3]
            words += [w[:-1] for w in words if w.endswith("s")]
            wanted = list(words) + [a + "_" + b for a, b in zip(words, words[1:])]
        wanted = [w for w in dict.fromkeys(wanted) if TABLE_NAME.match(w) and w not in denied]
        if not wanted:
            return "", []
        self.env.cr.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' "
                            "AND table_name = ANY(%s) ORDER BY table_name", [wanted])
        tables = [r[0] for r in self.env.cr.fetchall()][:MAX_TABLES]
        if not tables:
            return "", []
        self.env.cr.execute("SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema = 'public' "
                            "AND table_name = ANY(%s) ORDER BY table_name, ordinal_position", [tables])
        columns = {}
        for table, column, kind in self.env.cr.fetchall():
            if re.search(sql_engine.SECRET_COLUMN, column, re.I):
                continue
            columns.setdefault(table, []).append("%s %s" % (column, kind.replace("character varying", "varchar").replace(
                "timestamp without time zone", "timestamp")))
        return "\n".join("%s(%s)" % (t, ", ".join(columns.get(t, [])[:MAX_TABLE_COLUMNS])) for t in tables), tables

    @api.model
    def _dataset_prompt(self, kind, request, data, current):
        parts = ["You help a manager write a dataset for the dashboards of Odoo. Reply with ONE JSON object and nothing else: no markdown, "
                 "no comments, no explanation. Use only the data listed below.", "FORMAT\n" + dataset_help(kind), "DATA\n" + (data or "(none)")]
        if current:
            parts.append("CURRENT DEFINITION (change it as the request says, keep the rest)\n" + current)
        parts.append("REQUEST\n" + request)
        return "\n\n".join(parts)

    @api.model
    def _dataset_answer(self, kind, reply, model):
        """Checks one reply of the service as the caller. Returns ``(result, errors)``: ``result`` is what the manager gets."""
        Spec = self.env["dwo.dashboard.spec"]
        if kind == "blend":
            reply.setdefault("schema", C.DATASET_SCHEMA_ID)
            reply["type"] = "blend"
            reply.setdefault("code", "blend")
            reply.setdefault("label", reply["code"])
            check = Spec._validate_dataset(reply, True)
            return ({"definition": reply} if check["valid"] else None), check["errors"]
        if kind == "orm":
            metrics = reply.get("metrics")
            defn = {"schema": C.DATASET_SCHEMA_ID, "type": "orm", "model": model, "label": model, "metrics": metrics}
            check = Spec._validate_dataset(defn, True)
            return ({"metrics": metrics} if check["valid"] else None), check["errors"]
        query = reply.get("query")
        if not isinstance(query, str) or not query.strip():
            return None, [{"path": "/query", "code": "required", "message": "the answer has no query"}]
        query = query.strip().rstrip(";").strip()
        problems, names = scan(query)
        if problems:
            return None, [{"path": "/query", "code": "sql", "message": p} for p in problems[:5]]
        code = reply.get("code") if isinstance(reply.get("code"), str) and re.match(C.ID_PATTERN, reply["code"]) else "ai_query"
        result = {"code": code, "label": reply.get("label") if isinstance(reply.get("label"), str) else code,
                  "query": query, "params": [n for n in dict.fromkeys(names) if n in C.SQL_PARAMS], "tested": False}
        if Spec._sql_enabled():
            from ..engine import sql as sql_engine
            try:
                columns, _types, rows = sql_engine.sample(self.env, {"query": query, "params": result["params"]})
            except sql_engine.SqlSetupError:
                pass  # no safe login here: the manager gets the query untested
            except sql_engine.SqlRefused as exc:
                return None, [{"path": "/query", "code": "refused", "message": str(exc)}]
            except psycopg2.Error as exc:  # the database says what is wrong with the query: the model can fix it
                text = (exc.pgerror or str(exc)).strip().splitlines()
                return None, [{"path": "/query", "code": "database", "message": (text[0] if text else "the query failed")[:300]}]
            else:
                result.update(tested=True, columns=columns, rows=len(rows))
        return result, []

    @api.model
    def propose_dataset(self, kind, request, refs=None, current=None):
        """A definition for a dataset, from words. Dashboard managers only; never saves. ``kind``: ``blend`` (``refs`` are the Odoo
        models, ``orm:model``), ``orm`` (the metrics of the model in ``refs[0]``) or ``sql`` (``refs`` are table names, or the ones in the
        request are used). ``current`` is the definition now (a blend as a JSON text, a query for SQL), sent only when given.
        Returns ``{"ok": True, "kind", ...}`` or ``{"ok": False, "message", "errors"}``."""
        if not self._enabled():
            raise UserError(_("The assistant is switched off on this database."))
        if not self.env.user.has_group(MANAGER):
            raise AccessError(_("Only dashboard managers can ask the assistant for a dataset."))
        if kind not in ("blend", "orm", "sql"):
            raise UserError(_("Choose what to write: a blend, the metrics of a model or a SQL query."))
        request = (request or "").strip()
        if not request or len(request) > MAX_REQUEST:
            raise UserError(_("Write what you want in 1 to %d characters.") % MAX_REQUEST)
        refs = [r if r.startswith("orm:") else "orm:" + r for r in (refs or []) if isinstance(r, str) and r.strip()][:6] \
            if kind != "sql" else [r for r in (refs or []) if isinstance(r, str) and r.strip()][:MAX_TABLES]
        current = (current or "").strip()[:MAX_PAGE_JSON] if isinstance(current, str) else ""
        model, tables = None, []
        if kind == "sql":
            data, tables = self._describe_tables(refs, request)
            if not tables:
                raise UserError(_("Name the tables the query reads (for example sale_order, res_partner): none was found."))
        else:
            if kind == "orm":
                if len(refs) != 1:
                    raise UserError(_("Choose the model the metrics are about."))
                refs = refs[:1]
            elif len(refs) < 2:
                raise UserError(_("Choose two or three models to blend."))
            data = self._describe_datasets(refs)
            described = [r for r in refs if ('%s "' % r) in data]
            if len(described) < len(refs):
                raise UserError(_("You cannot read one of these models."))
            model = refs[0][4:] if kind == "orm" else None
        prompt = self._dataset_prompt(kind, request, data, current)
        complete = self._dwo_ai_providers()[self._provider_name()][1]
        history, retried, problem, errors = [], False, "", []
        for attempt in (1, 2):
            text = complete(prompt, history)
            try:
                reply = self._parse(text)
            except (ValueError, json.JSONDecodeError) as exc:
                problem = _("The answer was not a definition (%s).", exc)
                errors = [{"path": "", "code": "json", "message": str(exc)}]
            else:
                result, errors = self._dataset_answer(kind, reply, model)
                if result is not None:
                    return dict(result, ok=True, kind=kind, retried=retried)
                problem = _("The definition proposed is not valid.")
            if attempt == 1:
                retried = True
                history = [{"role": "user", "content": prompt}, {"role": "assistant", "content": (text or "")[:6000]}]
                prompt = ("Your answer cannot be used. Problems:\n%s\nReply again with the complete corrected answer as ONE JSON object "
                          "and nothing else." % "\n".join("%(path)s: %(message)s" % e for e in errors[:8]))
        return {"ok": False, "message": problem, "errors": errors[:8], "retried": retried}
