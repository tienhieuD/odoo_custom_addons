# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
from unittest.mock import patch

from lxml import etree

from odoo.addons.dwo_attpreview_core import catalog
from odoo.addons.dwo_attpreview_core.models import cache as cache_module
from odoo.tests import TransactionCase, tagged

from .sample_engine import patch_sample_engine

SETTINGS_FIELDS = {"dwo_attpreview_max_file_size_mb", "dwo_attpreview_engines",
                   "module_dwo_attpreview_office", "module_dwo_attpreview_mail"}
REMOVED_FIELDS = ("dwo_attpreview_render_timeout", "dwo_attpreview_cache_ttl_days", "dwo_attpreview_cache_max_mb",
                  "dwo_attpreview_cache_count", "dwo_attpreview_cache_size_mb")


@tagged("post_install", "-at_install")
class TestAttPreviewSettings(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Settings = self.env["res.config.settings"]

    def test_01_settings_screen_is_minimal(self):
        view = self.Settings.get_views([(False, "form")])["views"]["form"]
        tree = etree.fromstring(view["arch"])
        app = tree.xpath("//app[@name='dwo_attpreview_core']")[0]
        names = {f.get("name") for f in app.iter("field")}
        self.assertEqual(names, SETTINGS_FIELDS)
        self.assertEqual(app.xpath(".//button"), [], "no button (Clear cache, Manage engines) any more")
        widgets = {f.get("name"): f.get("widget") for f in app.iter("field")}
        for name in ("module_dwo_attpreview_office", "module_dwo_attpreview_mail"):
            self.assertEqual(widgets[name], "dwo_attpreview_engine_boolean")
        for name in REMOVED_FIELDS:
            self.assertNotIn(name, self.Settings._fields)

    def test_02_old_model_and_menu_are_gone(self):
        self.assertNotIn("dwo.attpreview.engine.config", self.env.registry)
        self.assertFalse(self.env["ir.model"].search([("model", "=", "dwo.attpreview.engine.config")]))
        self.assertFalse(self.env["ir.actions.act_window"].search([("res_model", "=", "dwo.attpreview.engine.config")]))
        self.assertNotIn("dwo.attpreview.engine.sample", self.env.registry, "the sample engine is not a product model")

    def test_03_max_file_size_default_and_save(self):
        self.assertEqual(self.Settings.default_get(["dwo_attpreview_max_file_size_mb"])["dwo_attpreview_max_file_size_mb"], 20)
        self.Settings.create({"dwo_attpreview_max_file_size_mb": 33}).execute()
        self.assertEqual(self.env["ir.config_parameter"].sudo().get_param("dwo_attpreview.max_file_size_mb"), "33")

    def test_04_every_catalog_entry_has_a_tick_and_facts(self):
        entries = catalog.load_catalog()
        self.assertEqual({e["module"] for e in entries}, {"dwo_attpreview_office", "dwo_attpreview_mail"})
        for entry in entries:
            self.assertIn("module_" + entry["module"], self.Settings._fields)
            self.assertEqual(entry["store_url"], "https://apps.odoo.com/apps/modules/" + entry["module"])
            self.assertTrue(entry["name"] and entry["extensions"])

    def test_05_engine_infos_installed_engines(self):
        infos = self.Settings._dwo_attpreview_engine_infos()
        office, mail = infos["dwo_attpreview_office"], infos["dwo_attpreview_mail"]
        self.assertEqual((office["state"], mail["state"]), ("installed", "installed"))
        self.assertEqual(office["extensions"][0], "xlsx")
        self.assertTrue({"doc", "xls", "ppt", "csv", "tsv", "xlsm", "docm", "pptm", "potx"} <= set(office["extensions"]))
        self.assertEqual(mail["store_url"], "https://apps.odoo.com/apps/modules/dwo_attpreview_mail")
        record = self.Settings.create({})
        self.assertEqual(record.dwo_attpreview_engines["dwo_attpreview_office"]["state"], "installed")
        self.assertTrue(record.module_dwo_attpreview_office and record.module_dwo_attpreview_mail,
                        "installed engines are ticked")

    def test_06_module_states(self):
        self.assertEqual(self.Settings._dwo_attpreview_module_state("dwo_attpreview_core"), "installed")
        self.assertEqual(self.Settings._dwo_attpreview_module_state("dwo_no_such_module"), "missing")
        row = self.env["ir.module.module"].sudo().search([("name", "=", "dwo_attpreview_mail")])
        for db_state, expected in (("uninstalled", "available"), ("uninstallable", "missing"),
                                   ("to install", "installed"), ("installed", "installed")):
            row.state = db_state
            self.env.invalidate_all()
            self.assertEqual(self.Settings._dwo_attpreview_module_state("dwo_attpreview_mail"), expected, db_state)

    def test_07_missing_module_info(self):
        fake = {"module": "dwo_attpreview_fake", "name": "Fake", "extensions": ["fk"],
                "store_url": "https://apps.odoo.com/apps/modules/dwo_attpreview_fake"}
        with patch.object(catalog, "load_catalog", lambda: [fake]):
            info = self.Settings._dwo_attpreview_engine_infos()["dwo_attpreview_fake"]
        self.assertEqual(info["state"], "missing")
        self.assertNotIn("price", info)

    def test_08_cache_cleanup_defaults(self):
        self.assertEqual((cache_module.CACHE_TTL_DAYS, cache_module.CACHE_MAX_MB), (30, 500))
        cron = self.env.ref("dwo_attpreview_core.cron_cleanup_cache")
        self.assertTrue(cron.active)
        self.assertEqual((cron.interval_number, cron.interval_type), (1, "days"))
        patch_sample_engine(self)
        att = self.env["ir.attachment"].create({"name": "a.txt", "raw": b"hello"})
        Cache = self.env["dwo.attpreview.cache"]
        engine = self.env["dwo.attpreview.engine"]._dwo_find_engine("a.txt")
        old, fresh = Cache._get_or_render(att, engine), Cache._get_or_render(
            self.env["ir.attachment"].create({"name": "b.txt", "raw": b"hi"}), engine)
        old.last_access = "2000-01-01 00:00:00"
        self.assertEqual((cron.model_id.model, cron.code.strip()), ("dwo.attpreview.cache", "model._cron_cleanup()"))
        Cache._cron_cleanup()  # what the job runs, with the constants (nothing in Settings)
        self.assertFalse(old.exists())
        self.assertTrue(fresh.exists())
        # a hidden system parameter still overrides the cap
        self.env["ir.config_parameter"].sudo().set_param("dwo_attpreview.cache_max_mb", "0")
        Cache._cron_cleanup()
        self.assertFalse(fresh.exists())

    def test_08b_form_gets_engine_infos(self):
        """Odoo 18: the Settings form opens with onchange() on a new record; the widget needs the engine infos there."""
        spec = {"dwo_attpreview_engines": {}, "module_dwo_attpreview_office": {}}
        value = self.Settings.onchange({}, [], spec)["value"]
        self.assertEqual(value["dwo_attpreview_engines"]["dwo_attpreview_office"]["state"], "installed")
        self.assertTrue(value["module_dwo_attpreview_office"])

    def test_09_unticking_an_installed_engine_asks_to_uninstall(self):
        """The ticks work through the `module_` mechanism of Odoo. Odoo 18 (unlike 19, which opens the
        ``base.module.uninstall`` wizard): unticking warns at once (onchange) and Save uninstalls the module."""
        mail = self.env["ir.module.module"].sudo().search([("name", "=", "dwo_attpreview_mail")])
        warning = self.Settings.onchange_module(False, "module_dwo_attpreview_mail")
        self.assertIn("uninstall", warning["warning"]["message"])
        Module = type(self.env["ir.module.module"])
        uninstalled = []
        with patch.object(Module, "button_immediate_uninstall", lambda self: uninstalled.extend(self.ids)):
            self.Settings.create({"module_dwo_attpreview_mail": False}).execute()
        self.assertEqual(uninstalled, mail.ids)
        # a ticked, installed engine changes nothing
        self.assertEqual(self.Settings.create({}).execute()["tag"], "reload")
