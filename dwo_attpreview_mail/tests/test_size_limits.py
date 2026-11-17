# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSizeLimits(TransactionCase):
    """Each group of file types has its own size limit (#86): the default, the Settings value, a clear refusal."""

    def _engine(self):
        return next(e for e in self.env["dwo.attpreview.engine"]._dwo_get_engines() if e._dwo_engine_code == "mail")

    def test_defaults_and_override(self):
        engine = self._engine()
        self.assertTrue(engine._dwo_engine_size_groups)
        for key, extensions, default in engine._dwo_engine_size_groups:
            ext = sorted(extensions)[0]
            self.assertEqual(engine._dwo_size_limit_mb("a." + ext.upper()), default)
            self.env["ir.config_parameter"].sudo().set_param("dwo_attpreview.max_mb." + key, "3")
            self.assertEqual(engine._dwo_size_limit_mb("a." + ext), 3)
            self.env["ir.config_parameter"].sudo().set_param("dwo_attpreview.max_mb." + key, False)
            self.assertEqual(engine._dwo_size_limit_mb("a." + ext), default)

    def test_refused_above_limit(self):
        engine = self._engine()
        key, extensions, _default = engine._dwo_engine_size_groups[0]
        ext = sorted(extensions)[0]
        self.env["ir.config_parameter"].sudo().set_param("dwo_attpreview.max_mb." + key, "1")
        att = self.env["ir.attachment"].create({"name": "big." + ext, "raw": b"0" * (1024 * 1024 + 1)})
        with self.assertRaises(UserError):
            self.env["dwo.attpreview.cache"]._render(att, engine)

    def test_settings_fields(self):
        engine = self._engine()
        settings = self.env["res.config.settings"].create({})
        for key, _ext, default in engine._dwo_engine_size_groups:
            self.assertEqual(settings["dwo_attpreview_max_mb_" + key], default)
