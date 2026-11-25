# -*- coding: utf-8 -*-
import copy
import json
import os
import unittest
from unittest.mock import patch

import psycopg2

from odoo import sql_db
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests.common import TransactionCase

from ..engine import sql as sql_engine
from ..spec.sqlscan import scan

ROLE, PASSWORD = "dwo_t_reader", "dwo_t_pw_9x"
QUERY = ("SELECT code AS code, name->>'en_US' AS name, phone_code AS phone, (code IN ('BE', 'FR', 'DE')) AS big "
         "FROM res_country WHERE code IS NOT NULL")
DAYS = ("SELECT d::date AS day, d AS moment, 1 AS n FROM generate_series('2025-12-31 20:00'::timestamp, "
        "'2026-03-31 20:00'::timestamp, '1 day') AS d")


def definition(**block):
    sql = {"query": QUERY, "groups": ["dwo_dashboard.group_dwo_dashboard_user"], "columns": [
        {"name": "code", "type": "text", "role": "dimension", "label": "Code"},
        {"name": "name", "type": "text", "role": "dimension", "label": "Country"},
        {"name": "phone", "type": "integer", "role": "measure", "label": "Phone code"},
        {"name": "big", "type": "boolean", "role": "dimension", "label": "Big"}]}
    sql.update(block)
    return {"schema": "dwo-dataset/1", "type": "sql", "code": "countries", "label": "Countries", "sql": sql,
            "metrics": [{"name": "phones", "agg": "sum", "field": "phone", "label": "Phone codes"}]}


class SqlCase(TransactionCase):
    """A real read-only login (created for the test class, committed because it lives in another connection)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        dbname = cls.env.cr.dbname
        info = dict(sql_db.connection_info_for(dbname)[1])
        cls.admin_conn = psycopg2.connect(**info)
        cls.admin_conn.autocommit = True
        cr = cls.admin_conn.cursor()
        cr.execute("SELECT rolsuper OR rolcreaterole FROM pg_roles WHERE rolname = current_user")
        if not cr.fetchone()[0]:
            cls.admin_conn.close()
            raise unittest.SkipTest("the SQL tests create a database login: the connecting role needs CREATEROLE (a development database does)")
        cr.execute("DROP OWNED BY %s" % ROLE) if _role_exists(cr) else None
        cr.execute("DROP ROLE IF EXISTS %s" % ROLE)
        cr.execute("CREATE ROLE %s LOGIN PASSWORD '%s' NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS" % (ROLE, PASSWORD))
        cr.execute('GRANT CONNECT ON DATABASE "%s" TO %s' % (dbname, ROLE))
        cr.execute("GRANT USAGE ON SCHEMA public TO %s" % ROLE)
        cr.execute("GRANT SELECT ON res_country, res_lang TO %s" % ROLE)
        cr.execute("DROP TABLE IF EXISTS dwo_t_tokens")
        cr.execute("CREATE TABLE dwo_t_tokens (id int, name text, access_token text)")
        cr.execute("INSERT INTO dwo_t_tokens VALUES (1, 'a', 'secret-a')")
        cr.execute("GRANT SELECT (id, name) ON dwo_t_tokens TO %s" % ROLE)
        cr.execute("DROP VIEW IF EXISTS dwo_t_secret_view")
        cr.execute("CREATE VIEW dwo_t_secret_view AS SELECT id, login FROM res_users")
        cr.execute("GRANT SELECT ON dwo_t_secret_view TO %s" % ROLE)
        cls.addClassCleanup(cls._drop_role)

    @classmethod
    def _drop_role(cls):
        cr = cls.admin_conn.cursor()
        cr.execute("DROP VIEW IF EXISTS dwo_t_secret_view")
        cr.execute("DROP TABLE IF EXISTS dwo_t_tokens")
        cr.execute("DROP OWNED BY %s" % ROLE)
        cr.execute("DROP ROLE %s" % ROLE)
        cls.admin_conn.close()

    def setUp(self):
        super().setUp()
        env = patch.dict(os.environ, {"DWO_SQL_USER": ROLE, "DWO_SQL_PASSWORD": PASSWORD})
        env.start()
        self.addCleanup(env.stop)
        self.admin = self.env.ref("base.user_admin")
        internal = self.env.ref("base.group_user")
        self.manager = self.env["res.users"].create({"name": "Sq Manager", "login": "sq_manager", "group_ids": [
            (6, 0, [internal.id, self.env.ref("dwo_dashboard.group_dwo_dashboard_manager").id])]})
        self.user = self.env["res.users"].create({"name": "Sq User", "login": "sq_user", "group_ids": [(6, 0, [internal.id])]})
        self.dataset = self.make(definition())

    def make(self, defn, code="countries"):
        defn = dict(defn, code=code)
        return self.env["dwo.dataset"].create({"kind": "sql", "code": code, "label": defn["label"],
                                               "definition_text": json.dumps(defn)})

    def widget(self, kind="bar", **extra):
        wells = {"axis": {"field": "big"}, "values": [{"agg": "count"}]}
        if kind == "kpi":
            wells = {"value": {"metric": "phones"}}
        if kind == "table":
            wells = {"columns": [{"field": "code"}, {"field": "name"}, {"field": "phone"}]}
        if kind in ("pie", "doughnut"):
            wells = {"category": {"field": "big"}, "value": {"agg": "count"}}
        return dict({"id": "s", "type": kind, "dataset": "sql:countries", "wells": wells}, **extra)

    def page_of(self, user, *widgets):
        dashboard = self.env["dwo.dashboard"].with_user(user).get_my_dashboard()
        page = self.env["dwo.dashboard.page"].browse(dashboard["pages"][0]["id"]).with_user(user)
        spec = {"schema": "dwo-dashboard/1", "grid": {"cols": 12},
                "widgets": [dict(w, x=0, y=4 * i, w=6, h=3) for i, w in enumerate(widgets)]}
        page.write({"spec": spec})
        return page

    def stored(self, user, widget, **kw):
        page = self.page_of(user, widget)
        return self.env["dwo.dashboard.engine"].with_user(user).run_widget(page.id, widget["id"], kw.get("values"))

    def ok(self, answer):
        self.assertTrue(answer["ok"], answer)
        return answer["result"]


def _role_exists(cr):
    cr.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [ROLE])
    return bool(cr.fetchone())


class TestScanner(TransactionCase):

    def errs(self, query):
        return scan(query)[0]

    def test_what_is_one_statement(self):
        for good in ("SELECT 1", "select a, 'x;y' from t -- ; )", "WITH a AS (SELECT 1) SELECT * FROM a", "SELECT $$ ; ) $$",
                     "SELECT E'it\\'s ; fine'", "SELECT 'a%%' WHERE x = %(uid)s", "SELECT /* a /* b */ ; */ 1"):
            self.assertEqual(self.errs(good), [], good)

    def test_what_is_refused(self):
        bad = ["SELECT 1; DROP TABLE x", "SELECT 1) AS q; DROP TABLE x --", "DELETE FROM t", "UPDATE t SET a = 1", "", "   -- nothing",
               "SELECT 'open", 'SELECT "open', "SELECT /* open", "SELECT $$ open", "SELECT (1", "SELECT 'a%' ", "SELECT %s",
               "SELECT pg_read_file('/etc/passwd')", "SELECT set_config('role', 'none', true)", "SELECT current_setting('x')",
               "SELECT lo_get(1)", "SELECT * FROM dblink('x', 'y') AS t(a int)", "SELECT query_to_xml('select 1', true, true, '')",
               "SELECT PG_SLEEP (70)", "SELECT 1 /* ) */ ) "]
        for query in bad:
            self.assertTrue(self.errs(query), query)

    def test_placeholders_are_found(self):
        self.assertEqual(scan("SELECT 1 WHERE a = %(uid)s AND b = ANY(%(company_ids)s) AND c LIKE 'x%%'")[1], ["uid", "company_ids"])


class TestSqlEngine(SqlCase):

    def test_it_needs_a_login_that_is_set_up(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DWO_SQL_USER", None)
            answer = self.stored(self.admin, self.widget())
        self.assertEqual((answer["ok"], answer["error"]["code"]), (False, "sql_setup"))
        with patch.dict(os.environ, {"DWO_SQL_USER": "odoo", "DWO_SQL_PASSWORD": "odoo"}):   # a login that is a superuser
            answer = self.stored(self.admin, self.widget())
        self.assertEqual((answer["ok"], answer["error"]["code"]), (False, "sql_setup"))
        self.env["ir.config_parameter"].sudo().set_param("dwo_dashboard.sql_enabled", "0")   # the switch
        self.assertEqual(self.stored(self.admin, self.widget())["error"]["code"], "sql_setup")

    def test_a_grouped_widget_ground_truth(self):
        result = self.ok(self.stored(self.admin, self.widget(order=[{"measure": "__count", "dir": "desc"}])))
        countries = self.env["res.country"].search([("code", "!=", False)])
        big = countries.filtered(lambda c: c.code in ("BE", "FR", "DE"))
        rows = {r["keys"][0]: r["values"][0] for r in result["rows"]}
        self.assertEqual(rows, {False: len(countries) - len(big), True: len(big)})
        self.assertEqual(result["rows"][0]["labels"][0], "No")      # the larger group first
        kpi = self.ok(self.stored(self.admin, self.widget("kpi")))
        self.assertEqual(kpi["rows"][0]["values"][0], sum(countries.mapped("phone_code")))
        self.assertEqual(kpi["measures"][0]["key"], "phones")

    def test_a_table_and_its_limit(self):
        result = self.ok(self.stored(self.admin, self.widget("table", order=[{"field": "code", "dir": "asc"}], limit=5)))
        self.assertEqual([r[0] for r in result["rows"]], sorted(self.env["res.country"].search([("code", "!=", False)]).mapped("code"))[:5])
        self.assertTrue(result["truncated"]["rows"])
        self.assertEqual([c["type"] for c in result["columns"]], ["char", "char", "integer"])

    def test_dates_are_buckets_of_the_viewers_calendar(self):
        defn = definition(query=DAYS, columns=[{"name": "day", "type": "date", "role": "dimension"},
                                              {"name": "moment", "type": "datetime", "role": "dimension"},
                                              {"name": "n", "type": "integer", "role": "measure"}])
        defn["code"], defn["metrics"] = "days", []
        self.make(defn, "days")

        def months(column, tz):
            w = {"id": "m", "type": "bar", "dataset": "sql:days", "order": [{"field": column, "dir": "asc"}],
                 "wells": {"axis": {"field": column, "interval": "month"}, "values": [{"field": "n", "agg": "sum"}]}}
            page = self.page_of(self.admin, w)
            env = self.env(user=self.admin, context=dict(self.env.context, tz=tz))
            result = self.ok(env["dwo.dashboard.engine"].run_widget(page.id, "m"))
            return [(r["labels"][0], r["values"][0]) for r in result["rows"]]
        self.assertEqual(months("day", "UTC"), [("December 2025", 1), ("January 2026", 31), ("February 2026", 28), ("March 2026", 31)])
        # the moments start at 20:00 UTC: in Ho Chi Minh City (UTC+7) 31 December 20:00 is already 1 January
        self.assertEqual(months("moment", "Asia/Ho_Chi_Minh"),
                         [("January 2026", 31), ("February 2026", 28), ("March 2026", 31), ("April 2026", 1)])  # 20:00 UTC is 03:00 next day

    def test_a_page_filter_reaches_the_query(self):
        flt = {"id": "pick", "type": "selection", "label": "Code", "values": ["BE", "FR", "XX"],
               "bind": [{"dataset": "sql:countries", "field": "code"}]}
        w = self.widget()
        page = self.page_of(self.admin, w)
        spec = copy.deepcopy(page.spec)
        spec["filters"] = [flt]
        page.write({"spec": spec})
        engine = self.env["dwo.dashboard.engine"].with_user(self.admin)
        result = self.ok(engine.run_widget(page.id, "s", {"pick": ["BE", "FR"]}))
        self.assertEqual(sum(r["values"][0] for r in result["rows"]), 2)
        self.assertEqual(sum(r["values"][0] for r in self.ok(engine.run_widget(page.id, "s", {"pick": ["BE'; DROP TABLE x; --"]}))["rows"]),
                         len(self.env["res.country"].search([("code", "!=", False)])))   # a value that is not offered is ignored

    def test_the_row_cap_and_the_timeout(self):
        defn = definition(query="SELECT n FROM generate_series(1, 1000000) AS n", columns=[{"name": "n", "type": "integer", "role": "measure"}])
        defn["code"], defn["metrics"] = "many", []
        self.make(defn, "many")
        w = {"id": "t", "type": "table", "dataset": "sql:many", "wells": {"columns": [{"field": "n"}]}, "limit": 500}
        self.env["ir.config_parameter"].sudo().set_param("dwo_dashboard.max_rows", "100")
        result = self.ok(self.stored(self.admin, w))
        self.assertLessEqual(len(result["rows"]), 100)
        slow = definition(query="SELECT count(*) AS n FROM generate_series(1, 2000000000)", columns=[{"name": "n", "type": "integer", "role": "measure"}])
        slow["code"], slow["metrics"] = "slow", []
        self.make(slow, "slow")
        self.env["ir.config_parameter"].sudo().set_param("dwo_dashboard.query_timeout", "1")
        answer = self.stored(self.admin, {"id": "k", "type": "kpi", "dataset": "sql:slow", "wells": {"value": {"field": "n", "agg": "sum"}}})
        self.assertEqual((answer["ok"], answer["error"]["code"]), (False, "timeout"))


class TestSqlAttacks(SqlCase):
    """Each of these must be refused or harmless, at save and (for a record written around the checks) at run."""

    def run_raw(self, query, columns=None):
        """A dataset written straight to the table: only the engine's own guards stand between the query and the database."""
        defn = definition(query=query, columns=columns or [{"name": "a", "type": "integer", "role": "measure"}])
        defn["code"], defn["metrics"] = "raw", []
        self.env.cr.execute("DELETE FROM dwo_dataset WHERE ref = 'sql:raw'")
        self.env["dwo.dataset"].with_context(tracking_disable=True)
        self.env.cr.execute("INSERT INTO dwo_dataset (kind, code, label, ref, definition_text) VALUES ('sql', 'raw', '{\"en_US\": \"x\"}', 'sql:raw', %s)",
                            [json.dumps(defn)])
        self.env.invalidate_all()
        return self.stored(self.admin, {"id": "r", "type": "kpi", "dataset": "sql:raw", "wells": {"value": {"field": "a", "agg": "sum"}}})

    def test_the_text_is_refused_at_run_too(self):
        for query in ("SELECT 1 AS a; DROP TABLE res_country", "SELECT pg_read_file('/etc/passwd')::int AS a",
                      "SELECT set_config('role', 'none', true)::int AS a", "SELECT current_setting('is_superuser')::int AS a",
                      "SELECT length(query_to_xml('select 1', true, true, ''))::int AS a", "SELECT 1 AS a FROM t) AS q; DROP TABLE x; --"):
            answer = self.run_raw(query)
            self.assertFalse(answer["ok"], query)
            self.assertIn(answer["error"]["code"], ("invalid", "failed"), query)

    def test_a_table_the_login_cannot_read_is_a_permission_error(self):
        answer = self.run_raw("SELECT count(*) AS a FROM res_users")
        self.assertEqual((answer["ok"], answer["error"]["code"]), (False, "access"))
        self.assertFalse(self.run_raw("SELECT count(*) AS a FROM ir_config_parameter")["ok"])

    def test_a_table_that_holds_secrets_is_refused_even_through_a_view_the_login_can_read(self):
        answer = self.run_raw("SELECT count(*) AS a FROM dwo_t_secret_view")        # the view expands to res_users in the plan
        self.assertFalse(answer["ok"])
        self.assertIn("may not read", answer["error"]["message"])
        self.env["ir.config_parameter"].sudo().set_param("dwo_dashboard.sql_denied_tables", "res_lang")   # a database adds its own
        self.assertIn("may not read", self.run_raw("SELECT count(*) AS a FROM res_lang")["error"]["message"])

    def test_a_function_scan_other_than_the_two_allowed_is_refused(self):
        self.assertTrue(self.run_raw("SELECT sum(n) AS a FROM generate_series(1, 3) AS n")["ok"])
        self.assertTrue(self.run_raw("SELECT sum(n) AS a FROM unnest(ARRAY[1, 2, 3]) AS n")["ok"])
        answer = self.run_raw("SELECT count(*) AS a FROM regexp_matches('abc', 'b') AS m")
        self.assertFalse(answer["ok"])
        self.assertIn("function", answer["error"]["message"])

    def test_writing_is_impossible(self):
        for query in ("WITH d AS (DELETE FROM res_country RETURNING id) SELECT count(*) AS a FROM d",
                      "SELECT 1 AS a FROM (SELECT 1) x WHERE EXISTS (INSERT INTO res_lang DEFAULT VALUES RETURNING 1)"):
            self.assertFalse(self.run_raw(query)["ok"], query)
        self.assertTrue(self.env["res.country"].search_count([]))     # nothing was deleted

    def test_the_login_itself_is_checked_every_time(self):
        cr = self.admin_conn.cursor()
        cr.execute("ALTER ROLE %s CREATEDB" % ROLE)
        try:
            self.assertEqual(self.stored(self.admin, self.widget())["error"]["code"], "sql_setup")
        finally:
            cr.execute("ALTER ROLE %s NOCREATEDB" % ROLE)
        self.assertTrue(self.stored(self.admin, self.widget())["ok"])


class TestSqlColumns(SqlCase):
    """What the login can read is the boundary: a column that looks like a credential must not be readable by it."""

    def test_a_login_that_can_read_a_credential_column_is_refused(self):
        defn = definition(query="SELECT id AS a, name AS b FROM dwo_t_tokens", columns=[
            {"name": "a", "type": "integer", "role": "measure"}, {"name": "b", "type": "text", "role": "dimension"}])
        defn["metrics"] = []
        self.make(defn, "tok")
        w = {"id": "t", "type": "table", "dataset": "sql:tok", "wells": {"columns": [{"field": "a"}, {"field": "b"}]}}
        self.assertTrue(self.stored(self.admin, w)["ok"])       # the login has id and name only
        sql_engine._CHECKED.clear()
        cr = self.admin_conn.cursor()
        cr.execute("GRANT SELECT (access_token) ON dwo_t_tokens TO %s" % ROLE)
        try:
            answer = self.stored(self.admin, w)
            self.assertEqual((answer["ok"], answer["error"]["code"]), (False, "sql_setup"))   # "run the setup script again"
        finally:
            cr.execute("REVOKE SELECT (access_token) ON dwo_t_tokens FROM %s" % ROLE)
            sql_engine._CHECKED.clear()
        self.assertTrue(self.stored(self.admin, w)["ok"])

    def test_the_credential_column_is_unreachable_even_if_the_text_tries(self):
        for query in ("SELECT length(access_token) AS a FROM dwo_t_tokens", 'SELECT length("access_token"::text) AS a FROM dwo_t_tokens'):
            defn = definition(query=query, columns=[{"name": "a", "type": "integer", "role": "measure"}])
            defn["metrics"] = []
            self.make(defn, "tk")
            answer = self.stored(self.admin, {"id": "k", "type": "kpi", "dataset": "sql:tk", "wells": {"value": {"field": "a", "agg": "sum"}}})
            self.assertEqual((answer["ok"], answer["error"]["code"]), (False, "access"), query)
            self.env["dwo.dataset"].search([("code", "=", "tk")]).unlink()

    def test_quoted_function_names_are_refused_too(self):
        for query in ('SELECT "set_config"(\'role\', \'none\', true) AS a', 'SELECT pg_catalog."pg_read_file"(\'/etc/passwd\') AS a'):
            self.assertTrue(scan(query)[0], query)


class TestSqlWho(SqlCase):

    def test_who_may_see_it(self):
        self.assertTrue(self.stored(self.user, self.widget())["ok"])           # every dashboard user (the default group)
        self.make(definition(groups=["dwo_dashboard.group_dwo_dashboard_manager"]), "countries2")
        w = dict(self.widget(), dataset="sql:countries2")
        denied = self.env["dwo.dashboard.spec"].with_user(self.user).validate({
            "schema": "dwo-dashboard/1", "grid": {"cols": 12}, "widgets": [dict(w, x=0, y=0, w=6, h=3)]})
        self.assertFalse(denied["valid"])                                       # a person outside the group cannot even save it
        self.assertTrue(self.stored(self.manager, w)["ok"])
        # a page shared with somebody outside the group: the widget refuses to run for them
        page = self.page_of(self.manager, w)
        page.share_with([self.user.id], [], "view")
        answer = self.env["dwo.dashboard.engine"].with_user(self.user).run_widget(page.id, "s")
        self.assertEqual((answer["ok"], answer["error"]["code"]), (False, "access"))

    def test_the_page_must_be_readable_before_a_query_runs(self):
        page = self.page_of(self.admin, self.widget())
        stranger = self.env["dwo.dashboard.engine"].with_user(self.user)
        answer = stranger.run_widget(page.id, "s")                                # not shared with them
        self.assertEqual((answer["ok"], answer["error"]["code"]), (False, "access"))
        page.share_with([self.user.id], [], "view")
        self.assertTrue(stranger.run_widget(page.id, "s")["ok"])                  # shared: it runs, as them
        page.revoke_share(page.share_ids[0].id)
        self.assertEqual(stranger.run_widget(page.id, "s")["error"]["code"], "access")

    def test_a_preview_needs_a_page_the_person_can_edit(self):
        engine = lambda user: self.env["dwo.dashboard.engine"].with_user(user)
        w = self.widget()
        self.assertEqual(engine(self.user).run_preview(w)["error"]["code"], "access")           # no page at all
        self.assertEqual(engine(self.user).run_preview(w, None, None, 999999)["error"]["code"], "access")
        page = self.page_of(self.admin, w)
        self.assertEqual(engine(self.user).run_preview(w, None, None, page.id)["error"]["code"], "access")   # not theirs
        page.share_with([self.user.id], [], "view")
        self.assertEqual(engine(self.user).run_preview(w, None, None, page.id)["error"]["code"], "access")   # may only look
        page.share_with([self.user.id], [], "edit")
        self.assertTrue(engine(self.user).run_preview(w, None, None, page.id)["ok"])
        self.assertTrue(engine(self.admin).run_preview(w, None, None, page.id)["ok"])

    def test_no_click_goes_through_a_sql_widget(self):
        page = self.page_of(self.admin, self.widget())
        engine = self.env["dwo.dashboard.engine"].with_user(self.admin)
        self.assertFalse(engine.drill_records(page.id, "s", True)["ok"])                         # no records behind a SQL group
        answer = engine.run_widget(page.id, "s", None, {"select": {"widget": "s", "key": True}})
        self.assertTrue(answer["ok"])


class TestSqlStorage(SqlCase):

    def test_the_query_is_never_readable_by_a_plain_user(self):
        user = self.env["dwo.dataset"].with_user(self.user).browse(self.dataset.id)
        for name in ("definition_text", "sql_query", "sql_options"):
            with self.assertRaises(AccessError, msg=name):
                user.read([name])
        self.assertTrue(user.read(["label", "kind", "code", "ref"]))            # the rest of the record is public
        self.assertNotIn("FROM res_country", json.dumps(self.env["dwo.dataset"].with_user(self.user).search_read([], ["label", "ref"])))
        self.assertTrue(self.stored(self.user, self.widget())["ok"])             # yet they can run it, and see it in Explore
        self.assertIn("sql:countries", {d["ref"] for d in self.env["dwo.dashboard.explore"].with_user(self.user).list_datasets()})

    def test_the_pieces_of_the_form_and_the_draft(self):
        manager = self.env["dwo.dataset"].with_user(self.manager)
        draft = manager.create({"kind": "sql", "code": "draft", "label": "Draft", "sql_query": "SELECT 1 AS one"})   # no columns yet
        self.assertEqual(draft.sql_query, "SELECT 1 AS one")
        self.assertEqual(draft.sql_group_ids.ids, [self.env.ref("dwo_dashboard.group_dwo_dashboard_user").id])
        with self.assertRaises(ValidationError):
            manager.create({"kind": "sql", "code": "draft2", "label": "x", "sql_query": "SELECT 1; SELECT 2"})
        draft.sql_group_ids = [(6, 0, [self.env.ref("dwo_dashboard.group_dwo_dashboard_manager").id])]
        self.assertEqual(json.loads(draft.sudo().definition_text)["sql"]["groups"], ["dwo_dashboard.group_dwo_dashboard_manager"])
        draft.sql_options = json.dumps({"columns": [{"name": "one", "type": "integer", "role": "measure"}]})
        self.assertEqual(draft.sudo()._definition()["sql"]["columns"][0]["name"], "one")
        with self.assertRaises(ValidationError):
            draft.sql_options = "{nope"
        self.assertEqual(draft.sudo()._definition()["code"], "draft")

    def test_the_test_button_names_what_does_not_match(self):
        defn = definition(columns=definition()["sql"]["columns"] + [{"name": "ghost", "type": "integer", "role": "measure"}])
        broken = self.make(dict(defn, metrics=[]), "broken").with_user(self.manager)
        with self.assertRaises(UserError) as ctx:
            broken.action_test()
        self.assertIn("ghost", str(ctx.exception))
        wrong = definition(columns=[dict(c, type="text", role="dimension") if c["name"] == "phone" else c for c in definition()["sql"]["columns"]])
        note = self.make(dict(wrong, metrics=[]), "wrong").with_user(self.manager).action_test()
        self.assertEqual(note["params"]["type"], "warning")
        self.assertIn("phone", note["params"]["message"])

    def test_only_managers_write_and_the_definition_is_checked(self):
        Dataset = self.env["dwo.dataset"]
        with self.assertRaises(AccessError):
            Dataset.with_user(self.user).create({"kind": "sql", "code": "mine", "label": "x", "definition_text": json.dumps(definition())})
        Dataset.with_user(self.manager).create({"kind": "sql", "code": "countries", "label": "dup", "definition_text": json.dumps(definition())}) \
            if False else None
        for bad in ("SELECT 1; SELECT 2", "SELECT 'a%' AS x", "SELECT pg_read_file('x') AS x", "DELETE FROM res_country"):
            with self.assertRaises(ValidationError, msg=bad):
                self.make(dict(definition(query=bad), code="bad"), "bad")
        nobody = self.make(definition(groups=[]), "nobody")          # no group written: every dashboard user, shown in the form
        self.assertEqual(nobody.sql_group_ids.ids, [self.env.ref("dwo_dashboard.group_dwo_dashboard_user").id])

    def test_the_test_button_and_the_column_filler(self):
        dataset = self.env["dwo.dataset"].with_user(self.manager).browse(self.dataset.id)
        note = dataset.action_test()
        self.assertEqual(note["tag"], "display_notification")
        self.assertIn("code, name, phone, big", note["params"]["message"])
        defn = definition(columns=[{"name": "code", "type": "integer", "role": "measure", "label": "My code"}])
        defn["metrics"] = []
        filled = self.make(dict(defn, code="filled"), "filled").with_user(self.manager)
        filled.action_fill_columns()
        columns = {c["name"]: c for c in json.loads(filled.definition_text)["sql"]["columns"]}
        self.assertEqual(list(columns), ["code", "name", "phone", "big"])
        self.assertEqual(columns["code"]["label"], "My code")                    # what was written is kept...
        self.assertEqual((columns["code"]["type"], columns["code"]["role"]), ("text", "dimension"))   # ...but the type is the truth
        self.assertEqual((columns["phone"]["type"], columns["phone"]["role"]), ("integer", "measure"))
        user = self.env["dwo.dataset"].with_user(self.user).browse(self.dataset.id)
        with self.assertRaises(AccessError):
            user.action_test()                                                  # reading a dataset is not the right to try a query

    def test_explore_shows_the_columns_and_never_the_query(self):
        explore = self.env["dwo.dashboard.explore"]
        self.assertIn("sql:countries", {d["ref"] for d in explore.with_user(self.user).list_datasets()})
        described = explore.with_user(self.user).describe_dataset("sql:countries")
        self.assertNotIn("query", json.dumps(described))
        self.assertEqual({f["name"] for f in described["fields"] if f["measure"]}, {"phone"})
        self.make(definition(groups=["dwo_dashboard.group_dwo_dashboard_manager"]), "managers_only")
        self.assertNotIn("sql:managers_only", {d["ref"] for d in explore.with_user(self.user).list_datasets()})
        with self.assertRaises(AccessError):
            explore.with_user(self.user).describe_dataset("sql:managers_only")
        self.env["ir.config_parameter"].sudo().set_param("dwo_dashboard.sql_enabled", "0")
        self.assertNotIn("sql:countries", {d["ref"] for d in explore.with_user(self.user).list_datasets()})

    def test_the_assistant_never_sees_a_sql_dataset(self):
        ai = self.env["dwo.dashboard.ai"]
        self.assertEqual(ai._describe_datasets(["sql:countries"]), "")      # only Odoo models are described to the service
