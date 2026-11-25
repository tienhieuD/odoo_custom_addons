# -*- coding: utf-8 -*-
import json
import logging

import psycopg2.errors

from odoo import _, api, models
from odoo.exceptions import AccessError, MissingError

from ..engine import blend, dates, interact, measures, sql as sql_engine, domain as dom, grouped, guard, records
from ..spec import validate_semantics, validate_structure

_logger = logging.getLogger(__name__)
MAX_IDS = 1000
_TZ_KNOWN = {}  # time zone name -> does this PostgreSQL know it (aliases such as "Asia/Saigon" may be missing)


class DwoDashboardEngine(models.AbstractModel):
    """Runs one widget at a time with the permissions of the caller (never ``sudo``): access rights, record rules,
    field groups and companies apply, so two people see different numbers on the same page.

    One RPC per widget: a widget that fails (no access, a field deleted since, a cancelled query) answers
    ``{"ok": false, "error": {"code": ...}}`` and its neighbours are not affected. Nothing the client sends is trusted: the
    widget is validated again here, as the caller, before a query is built, and filter values are re-checked."""
    _name = "dwo.dashboard.engine"
    _description = "Dashboard query engine"

    @api.model
    def run_widget(self, page_id, widget_id, filter_values=None, interactions=None):
        """Run a widget of a stored page. ``filter_values``: {filter id: value} chosen in the page's filter bar.
        ``interactions``: what was clicked, {"select": {"widget", "key"}, "drills": {widget id: [keys]}} (see engine/interact.py)."""
        try:
            page = self.env["dwo.dashboard.page"].browse(page_id)
            page.check_access("read")
            spec = page.spec or {}
        except AccessError:
            return self._error("access")
        widget = next((w for w in spec.get("widgets", []) if w.get("id") == widget_id), None)
        if widget is None:
            return self._error("not_found")
        return self._run(spec, widget, filter_values, interactions)

    @api.model
    def drill_records(self, page_id, widget_id, key, filter_values=None, interactions=None):
        """The records behind one bar, slice or row (drill-through): ``{"model", "ids", "total"}`` for the client to open
        as a list. The same filters and clicks as the widget, as the viewer, and the ids are capped (``MAX_IDS``)."""
        try:
            page = self.env["dwo.dashboard.page"].browse(page_id)
            page.check_access("read")
            spec = page.spec or {}
        except AccessError:
            return self._error("access")
        widget = next((w for w in spec.get("widgets", []) if w.get("id") == widget_id), None)
        if widget is None or not self._well_formed(spec, widget) or not widget["dataset"].startswith("orm:"):
            return self._error("not_found")
        item = interact.primary(widget)
        if item is None:
            return self._error("unsupported")
        env = self._viewer().env
        try:
            chain = interact.drill_chain(item)
            interval = chain[interact.depth(interactions or {}, widget_id, item)] if chain else None
            applied = interact.apply(env, spec, widget, interactions) if interactions else widget
            applied = dict(applied, where=list(applied.get("where", [])) + interact.key_leaves(
                env, env[widget["dataset"][4:]], item, interval, key))
            error = self._check_widget(spec, applied)  # the widget as saved, with the click: what the author could have written
            if error:
                return error
            applied, mixed = self._with_metric_where(applied)
            model = env[widget["dataset"][4:]]
            with guard.guarded(env):
                domain = dom.widget_domain(env, model, self._mini_page(spec, applied), applied, filter_values)
                ids = model.search(domain, limit=MAX_IDS, order="id desc").ids
                total = model.search_count(domain, limit=MAX_IDS * 50)
        except (ValueError, KeyError, TypeError):
            return self._error("invalid")
        except AccessError:
            return self._error("access")
        except Exception:
            _logger.exception("drill-through of widget %s failed", widget_id)
            return self._error("failed")
        return {"ok": True, "result": {"model": model._name, "ids": ids, "total": total, "mixed": mixed}}

    def _with_metric_where(self, widget):
        """The records behind a bar are those its measures count: when every measure carries the same ``where`` (a widget of one
        metric, or of several that share it) it is added to the domain. With different ones, or a mix of metrics and plain
        measures, no single list of records is "the" answer: the whole group is listed and ``mixed`` tells the client."""
        if any("metric" in i for w in widget["wells"].values() for i in (w if isinstance(w, list) else [w])):
            defn = self.env["dwo.dashboard.spec"]._dwo_resolve_dataset(widget["dataset"])
            widget = measures.resolve_metrics(widget, defn)
        items = [i for v in widget["wells"].values() for i in (v if isinstance(v, list) else [v])
                 if isinstance(i, dict) and "agg" in i]
        wheres = {json.dumps(i.get("where") or None, sort_keys=True) for i in items}
        if len(wheres) == 1 and wheres != {"null"}:
            where = next(i["where"] for i in items if i.get("where"))
            return dict(widget, where=list(widget.get("where", [])) + list(where)), False
        return widget, len(wheres) > 1

    def _check_widget(self, spec, widget):
        """The error to answer for a widget that is not valid for the caller, else None."""
        Spec = self.env["dwo.dashboard.spec"]
        mini = self._mini_page(spec, widget)
        errors = validate_structure(mini, Spec._dwo_registry())
        if not errors:
            errors = validate_semantics(self.env, mini, Spec._dwo_registry(), Spec._dwo_resolve_dataset, True,
                                        Spec._dwo_dataset_checkers())
        if errors:
            code = "access" if any(e["code"] == "access" for e in errors) else "invalid"
            return self._error(code, errors[0]["message"] if code == "invalid" else None)
        return None

    @api.model
    def run_preview(self, widget, filters=None, filter_values=None, page_id=None):
        """Run a widget that is not saved yet (Explore). The same checks as for a stored widget; a widget on a SQL dataset also
        needs the page it is being written on, and the right to change that page (nobody tries a query on nothing)."""
        if not isinstance(widget, dict):
            return self._error("invalid")
        if str(widget.get("dataset", "")).startswith("sql:"):
            try:
                page = self.env["dwo.dashboard.page"].browse(page_id if isinstance(page_id, int) else 0)
                if not page.exists():
                    raise AccessError("no page")
                page.check_access("write")
                if page._level() == "view":
                    raise AccessError("view only")
            except (AccessError, MissingError):
                return self._error("access")
        widget = dict(widget, id=widget.get("id") or "preview")
        for key, default in (("x", 0), ("y", 0), ("w", 6), ("h", 4)):
            widget.setdefault(key, default)
        spec = {"schema": "dwo-dashboard/1", "filters": filters or [], "widgets": [widget]}
        return self._run(spec, widget, filter_values)

    # ---------------------------------------------------------------------------------------------------- internals
    def _viewer(self):
        """This model with a time zone PostgreSQL can use. Legacy names (a browser on macOS reports "Asia/Saigon", which a
        minimal tzdata no longer has) are mapped to their current name first, so day, week and month buckets stay right
        for the viewer; a name that is still unknown falls back to UTC, and the result says so (``notes``)."""
        requested = self.env.context.get("tz") or self.env.user.tz or "UTC"
        tz = dates.canonical_tz(requested)
        if tz not in _TZ_KNOWN:
            self.env.cr.execute("SELECT 1 FROM pg_timezone_names WHERE name = %s", [tz])
            _TZ_KNOWN[tz] = bool(self.env.cr.fetchone())
        return self.with_context(tz=tz if _TZ_KNOWN[tz] else "UTC", dwo_tz_fallback=not _TZ_KNOWN[tz])

    def _run(self, spec, widget, filter_values, interactions=None):
        try:
            if not self._well_formed(spec, widget):
                return self._error("invalid")
            return self._viewer()._run_checked(spec, widget, filter_values, interactions)
        except Exception:  # whatever the payload was, the client never gets a traceback
            _logger.exception("dashboard widget %s failed", widget.get("id") if isinstance(widget, dict) else "?")
            return self._error("failed")

    @staticmethod
    def _well_formed(spec, widget):
        """The shape the engine itself relies on, checked before anything reads it (the full validation comes next)."""
        if not isinstance(spec, dict) or not isinstance(widget, dict) or not isinstance(widget.get("dataset"), str):
            return False
        filters = spec.get("filters", [])
        if not isinstance(filters, list):
            return False
        for flt in filters:
            binds = flt.get("bind") if isinstance(flt, dict) else None
            if not isinstance(flt.get("id") if isinstance(flt, dict) else None, str) or not isinstance(binds, list) \
                    or not all(isinstance(b, dict) and isinstance(b.get("dataset"), str) for b in binds):
                return False
        return True

    def _run_checked(self, spec, widget, filter_values, interactions=None):
        if interactions:
            widget = interact.apply(self.env, spec, widget, interactions)
        Spec = self.env["dwo.dashboard.spec"]
        registry = Spec._dwo_registry()
        # validate this widget, as the caller, with the filters that apply to its dataset only
        mini = self._mini_page(spec, widget)
        errors = validate_structure(mini, registry)
        if not errors:
            errors = validate_semantics(self.env, mini, registry, Spec._dwo_resolve_dataset, True,
                                        Spec._dwo_dataset_checkers())
        if errors:
            code = "access" if any(e["code"] == "access" for e in errors) else "invalid"
            return self._error(code, errors[0]["message"] if code == "invalid" else None)
        prefix, name = widget["dataset"].split(":", 1)
        if prefix == "blend":
            return self._run_blend(mini, widget, filter_values, registry.visuals[widget["type"]])
        if prefix == "sql":
            return self._run_sql(mini, widget, filter_values, registry.visuals[widget["type"]])
        if prefix != "orm":
            return self._error("unsupported")  # SQL and plugin datasets arrive in later phases
        vdef = registry.visuals[widget["type"]]
        model = self.env[name]
        if any("metric" in i for w in widget["wells"].values() for i in (w if isinstance(w, list) else [w])):
            widget = measures.resolve_metrics(widget, Spec._dwo_resolve_dataset(widget["dataset"]))
        try:
            with guard.guarded(self.env):
                extra = {}
                setup = dom.compare_setup(self.env, model, mini, widget, filter_values) if widget.get("compare") else None
                if setup:
                    domain, extra = setup["domain"], {"compare": setup}
                else:
                    domain = dom.widget_domain(self.env, model, mini, widget, filter_values)
                if widget.get("trend"):
                    extra["trend"] = dom.trend_setup(self.env, model, mini, widget, filter_values)
                engine = records if vdef["query"] == "records" else grouped
                result = engine.run(self.env, model, vdef, widget, domain, **extra)
        except psycopg2.errors.QueryCanceled:
            return self._error("timeout")
        except AccessError:
            return self._error("access")
        except Exception:  # never leak SQL or a traceback to the client
            _logger.exception("dashboard widget %s failed", widget.get("id"))
            return self._error("failed")
        if self.env.context.get("dwo_tz_fallback"):
            result["notes"] = ["timezone"]  # the time zone of the viewer is unknown to the database: buckets are in UTC
        return {"ok": True, "result": result}

    def _run_sql(self, mini, widget, filter_values, vdef):
        if not self.env["dwo.dashboard.spec"]._sql_enabled():
            return self._error("sql_setup")
        defn = self.env["dwo.dashboard.spec"]._dwo_resolve_dataset(widget["dataset"])
        try:
            result = sql_engine.run(self.env, mini, widget, defn, vdef, filter_values)
        except sql_engine.SqlSetupError:
            _logger.warning("dashboard sql: no safe database login for SQL datasets")
            return self._error("sql_setup")
        except sql_engine.SqlRefused as exc:
            return self._error("invalid", str(exc))
        except psycopg2.errors.QueryCanceled:
            return self._error("timeout")
        except psycopg2.errors.InsufficientPrivilege:
            return self._error("access")
        except psycopg2.Error:
            _logger.warning("dashboard sql: dataset %s failed in the database", widget["dataset"])  # never the text or the message
            return self._error("failed")
        except Exception:
            _logger.exception("dashboard sql %s failed", widget.get("id"))
            return self._error("failed")
        if self.env.context.get("dwo_tz_fallback"):
            result["notes"] = ["timezone"]
        return {"ok": True, "result": result}

    def _run_blend(self, mini, widget, filter_values, vdef):
        defn = self.env["dwo.dashboard.spec"]._dwo_resolve_dataset(widget["dataset"])
        try:
            result = blend.run(self.env, mini, widget, defn, vdef, filter_values)
        except (psycopg2.errors.QueryCanceled, TimeoutError):
            return self._error("timeout")
        except AccessError:
            return self._error("access")
        except Exception:  # never leak SQL or a traceback to the client
            _logger.exception("dashboard blend %s failed", widget.get("id"))
            return self._error("failed")
        if self.env.context.get("dwo_tz_fallback"):
            result["notes"] = ["timezone"]
        return {"ok": True, "result": result}

    @staticmethod
    def _mini_page(spec, widget):
        """The page reduced to one widget; filters keep only the binds of that widget's dataset."""
        filters = []
        for flt in spec.get("filters", []):
            binds = [b for b in flt["bind"] if b["dataset"] == widget["dataset"]]
            if binds:
                filters.append(dict(flt, bind=binds))
        return {"schema": "dwo-dashboard/1", "grid": spec.get("grid", {"cols": 12}), "filters": filters,
                "widgets": [widget]}

    @staticmethod
    def _error(code, detail=None):
        messages = {
            "access": _("You do not have access to this data."),
            "invalid": detail or _("This widget is not valid any more."),
            "timeout": _("The query took too long and was stopped."),
            "not_found": _("This widget does not exist."),
            "unsupported": _("This kind of data is not available yet."),
            "failed": _("This widget could not be computed."),
            "sql_setup": _("SQL datasets are not set up on this server: an administrator has to configure the read-only database login."),
        }
        return {"ok": False, "error": {"code": code, "message": messages[code]}}
