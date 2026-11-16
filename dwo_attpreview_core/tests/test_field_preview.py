# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
"""/dwo_attpreview/field_info: the file of a binary field, stored as an attachment or in the table."""
import base64
from types import SimpleNamespace
from unittest.mock import patch

from odoo.tests import TransactionCase, new_test_user, tagged
from odoo.addons.dwo_attpreview_core.controllers.main import AttPreviewController
from .sample_engine import patch_sample_engine

REQUEST = "odoo.addons.dwo_attpreview_core.controllers.main.request"
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")


@tagged("post_install", "-at_install")
class TestFieldPreview(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ctrl = AttPreviewController()
        cls.user = new_test_user(cls.env, login="dwo_fp_user", groups="base.group_user")
        # a binary field stored as an attachment (named after the field, not after the file)
        # Odoo 20: res.company.layout_background_image is gone; ir.ui.menu.web_icon_data is such a field, readable
        # by internal users, with a char "name" (the attribute keeps its name to keep the diff with 19 small)
        cls.company = cls.env["ir.ui.menu"].create({
            "name": "notes.sample", "web_icon_data": base64.b64encode(b"company file").decode()})
        # a binary field stored in its table (attachment=False), readable by administrators only
        cls.server = cls.env["ir.mail_server"].create({
            "name": "cert.sample", "smtp_host": "localhost", "smtp_authentication": "certificate", "smtp_encryption": "ssl",
            "smtp_ssl_certificate": base64.b64encode(b"certificate text").decode(),  # Odoo 20: base64 as str (bytes raise)
            "smtp_ssl_private_key": base64.b64encode(b"key").decode(),  # Odoo 20: base64 as str (bytes raise)
        })

    def setUp(self):
        super().setUp()
        patch_sample_engine(self)

    def _info(self, env=None, **kw):
        with patch(REQUEST, new=SimpleNamespace(env=env or self.env)):
            return self.ctrl.field_info(**kw)

    def test_01_attachment_datas_is_the_attachment_itself(self):
        att = self.env["ir.attachment"].create({"name": "a.sample", "raw": b"hello"})
        # Odoo 20: ir.attachment has no "datas" field any more, its file is "raw"
        out = self._info(model="ir.attachment", res_id=att.id, field="raw", filename_field="name")
        with patch(REQUEST, new=SimpleNamespace(env=self.env)):
            same = self.ctrl.info(att.id)
        self.assertEqual(out.pop("attachment_id"), att.id)
        self.assertEqual(out, same)
        self.assertEqual(out["content"], "hello")

    def test_02_field_stored_as_attachment_uses_the_real_file_name(self):
        out = self._info(model="ir.ui.menu", res_id=self.company.id, field="web_icon_data",
                         filename_field="name")
        self.assertEqual((out["mode"], out["engine"], out["content"]), ("rendered", "sample", "company file"))
        self.assertEqual(out["name"], "notes.sample")
        self.assertEqual(out["source"], "field")
        self.assertNotIn("attachment_id", out)  # the client must not use the URLs of the attachment
        self.assertIn("/web/content?model=ir.ui.menu&id=%d&field=web_icon_data" % self.company.id,
                      out["download_url"])
        self.assertTrue(out["download_url"].endswith("download=true"))
        # rendered once and cached on the attachment of the field
        att = self.env["ir.attachment"].sudo().search([
            ("res_model", "=", "ir.ui.menu"), ("res_id", "=", self.company.id),
            ("res_field", "=", "web_icon_data")])
        self.assertEqual(self.env["dwo.attpreview.cache"].sudo().search_count([("attachment_id", "=", att.id)]), 1)

    def test_03_field_in_table_is_rendered_without_attachment_or_cache(self):
        Att = self.env["ir.attachment"].sudo()
        Cache = self.env["dwo.attpreview.cache"].sudo()
        every = ["|", ("res_field", "=", False), ("res_field", "!=", False)]
        n_att, n_cache = Att.search_count(every), Cache.search_count([])
        out = self._info(model="ir.mail_server", res_id=self.server.id, field="smtp_ssl_certificate",
                         filename_field="name")
        self.assertEqual((out["mode"], out["content"], out["name"]), ("rendered", "certificate text", "cert.sample"))
        self.assertEqual(Att.search_count(every), n_att)
        self.assertEqual(Cache.search_count([]), n_cache)

    def test_04_field_in_table_native_file(self):
        self.server.smtp_ssl_certificate = base64.b64encode(PNG).decode()  # Odoo 20: base64 as str (bytes raise)
        out = self._info(model="ir.mail_server", res_id=self.server.id, field="smtp_ssl_certificate")
        self.assertEqual((out["mode"], out["mimetype"]), ("native", "image/png"))
        self.assertEqual(out["url"], "/web/content?model=ir.mail_server&id=%d&field=smtp_ssl_certificate"
                                     "&download=false" % self.server.id)
        self.assertEqual(out["name"], "SSL Certificate")  # no file name field: the label of the field

    def test_05_size_limit(self):
        self.env["ir.config_parameter"].sudo().set_int("dwo_attpreview.max_file_size_mb", "0")  # Odoo 20: set_param is gone, typed setters
        out = self._info(model="ir.mail_server", res_id=self.server.id, field="smtp_ssl_certificate",
                         filename_field="name")
        self.assertEqual(out["mode"], "error")
        self.assertIn("larger than the preview limit", out["error"])
        out = self._info(model="ir.ui.menu", res_id=self.company.id, field="web_icon_data",
                         filename_field="name")
        self.assertEqual(out["mode"], "error")

    def test_06_access(self):
        uenv = self.env(user=self.user)
        # the record (ir.mail_server is for administrators) and the field (groups) are checked
        self.assertEqual(self._info(uenv, model="ir.mail_server", res_id=self.server.id,
                                    field="smtp_ssl_certificate")["mode"], "denied")
        self.assertEqual(self._info(uenv, model="ir.ui.menu", res_id=self.company.id,
                                    field="web_icon_data", filename_field="name")["mode"], "rendered")
        field = self.env["ir.ui.menu"]._fields["web_icon_data"]
        # Odoo 20: the environment memoizes the fields it may read; forget them after changing the groups
        uenv.__dict__.pop("_field_access_memo", None)
        with patch.object(field, "groups", "base.group_system"):
            self.assertEqual(self._info(uenv, model="ir.ui.menu", res_id=self.company.id,
                                        field="web_icon_data")["mode"], "denied")
        # a file name field the user may not read is refused too
        name_field = self.env["ir.ui.menu"]._fields["name"]
        uenv.__dict__.pop("_field_access_memo", None)  # Odoo 20: see above
        with patch.object(name_field, "groups", "base.group_system"):
            self.assertEqual(self._info(uenv, model="ir.ui.menu", res_id=self.company.id,
                                        field="web_icon_data", filename_field="name")["mode"], "denied")

    def test_07_bad_requests_are_denied_not_errors(self):
        for kw in (
            dict(model="no.such.model", res_id=1, field="x"),
            dict(model="ir.ui.menu", res_id=self.company.id, field="name"),  # not a binary field
            dict(model="ir.ui.menu", res_id=self.company.id, field="no_such_field"),
            dict(model="ir.ui.menu", res_id=999999, field="web_icon_data"),
            dict(model="ir.ui.menu", res_id="abc", field="web_icon_data"),
        ):
            self.assertEqual(self._info(**kw)["mode"], "denied", kw)

    def test_08_empty_field(self):
        self.company.web_icon_data = False
        out = self._info(model="ir.ui.menu", res_id=self.company.id, field="web_icon_data")
        self.assertEqual(out["mode"], "error")
