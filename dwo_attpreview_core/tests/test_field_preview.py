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
        cls.company = cls.env.company
        # a binary field stored as an attachment (named after the field, not after the file)
        cls.company.write({"name": "notes.sample", "layout_background_image": base64.b64encode(b"company file")})
        # a binary field stored in its table (attachment=False), readable by administrators only
        cls.server = cls.env["ir.mail_server"].create({
            "name": "cert.sample", "smtp_host": "localhost", "smtp_authentication": "certificate", "smtp_encryption": "ssl",
            "smtp_ssl_certificate": base64.b64encode(b"certificate text"),
            "smtp_ssl_private_key": base64.b64encode(b"key"),
        })

    def setUp(self):
        super().setUp()
        patch_sample_engine(self)

    def _info(self, env=None, **kw):
        with patch(REQUEST, new=SimpleNamespace(env=env or self.env)):
            return self.ctrl.field_info(**kw)

    def test_01_attachment_datas_is_the_attachment_itself(self):
        att = self.env["ir.attachment"].create({"name": "a.sample", "raw": b"hello"})
        out = self._info(model="ir.attachment", res_id=att.id, field="datas", filename_field="name")
        with patch(REQUEST, new=SimpleNamespace(env=self.env)):
            same = self.ctrl.info(att.id)
        self.assertEqual(out.pop("attachment_id"), att.id)
        self.assertEqual(out, same)
        self.assertEqual(out["content"], "hello")

    def test_02_field_stored_as_attachment_uses_the_real_file_name(self):
        out = self._info(model="res.company", res_id=self.company.id, field="layout_background_image",
                         filename_field="name")
        self.assertEqual((out["mode"], out["engine"], out["content"]), ("rendered", "sample", "company file"))
        self.assertEqual(out["name"], "notes.sample")
        self.assertEqual(out["source"], "field")
        self.assertNotIn("attachment_id", out)  # the client must not use the URLs of the attachment
        self.assertIn("/web/content?model=res.company&id=%d&field=layout_background_image" % self.company.id,
                      out["download_url"])
        self.assertTrue(out["download_url"].endswith("download=true"))
        # rendered once and cached on the attachment of the field
        att = self.env["ir.attachment"].sudo().search([
            ("res_model", "=", "res.company"), ("res_id", "=", self.company.id),
            ("res_field", "=", "layout_background_image")])
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
        self.server.smtp_ssl_certificate = base64.b64encode(PNG)
        out = self._info(model="ir.mail_server", res_id=self.server.id, field="smtp_ssl_certificate")
        self.assertEqual((out["mode"], out["mimetype"]), ("native", "image/png"))
        self.assertEqual(out["url"], "/web/content?model=ir.mail_server&id=%d&field=smtp_ssl_certificate"
                                     "&download=false" % self.server.id)
        self.assertEqual(out["name"], "SSL Certificate")  # no file name field: the label of the field

    def test_05_size_limit(self):
        self.env["ir.config_parameter"].sudo().set_param("dwo_attpreview.max_file_size_mb", "0")
        out = self._info(model="ir.mail_server", res_id=self.server.id, field="smtp_ssl_certificate",
                         filename_field="name")
        self.assertEqual(out["mode"], "error")
        self.assertIn("larger than the preview limit", out["error"])
        out = self._info(model="res.company", res_id=self.company.id, field="layout_background_image",
                         filename_field="name")
        self.assertEqual(out["mode"], "error")

    def test_06_access(self):
        uenv = self.env(user=self.user)
        # the record (ir.mail_server is for administrators) and the field (groups) are checked
        self.assertEqual(self._info(uenv, model="ir.mail_server", res_id=self.server.id,
                                    field="smtp_ssl_certificate")["mode"], "denied")
        self.assertEqual(self._info(uenv, model="res.company", res_id=self.company.id,
                                    field="layout_background_image", filename_field="name")["mode"], "rendered")
        field = self.env["res.company"]._fields["layout_background_image"]
        with patch.object(field, "groups", "base.group_system"):
            self.assertEqual(self._info(uenv, model="res.company", res_id=self.company.id,
                                        field="layout_background_image")["mode"], "denied")
        # a file name field the user may not read is refused too
        name_field = self.env["res.company"]._fields["name"]
        with patch.object(name_field, "groups", "base.group_system"):
            self.assertEqual(self._info(uenv, model="res.company", res_id=self.company.id,
                                        field="layout_background_image", filename_field="name")["mode"], "denied")

    def test_07_bad_requests_are_denied_not_errors(self):
        for kw in (
            dict(model="no.such.model", res_id=1, field="x"),
            dict(model="res.company", res_id=self.company.id, field="name"),  # not a binary field
            dict(model="res.company", res_id=self.company.id, field="no_such_field"),
            dict(model="res.company", res_id=999999, field="layout_background_image"),
            dict(model="res.company", res_id="abc", field="layout_background_image"),
        ):
            self.assertEqual(self._info(**kw)["mode"], "denied", kw)

    def test_08_empty_field(self):
        self.company.layout_background_image = False
        out = self._info(model="res.company", res_id=self.company.id, field="layout_background_image")
        self.assertEqual(out["mode"], "error")
