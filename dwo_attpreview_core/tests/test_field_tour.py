# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
"""Tours of the Preview buttons on file fields: binary, many2many_binary, a list of attachments, many2one."""
import base64

from odoo.tests import HttpCase, tagged

from .sample_engine import patch_sample_engine

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")


@tagged("post_install", "-at_install")
class TestFieldPreviewTour(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        partner_model = env["ir.model"]._get("res.partner")
        # fields made for the test only (rolled back with the test, like a field added by a user)
        env["ir.model.fields"].create([
            {"name": "x_dwo_file", "ttype": "binary", "field_description": "Contract",
             "model_id": partner_model.id},
            {"name": "x_dwo_file_name", "ttype": "char", "field_description": "Contract name",
             "model_id": partner_model.id},
            {"name": "x_dwo_attachment_id", "ttype": "many2one", "relation": "ir.attachment",
             "field_description": "Main document", "model_id": partner_model.id},
            {"name": "x_dwo_file_ids", "ttype": "many2many", "relation": "ir.attachment",
             "relation_table": "x_dwo_partner_file_rel", "column1": "partner_id", "column2": "attachment_id",
             "field_description": "Documents", "model_id": partner_model.id},
            {"name": "x_dwo_list_ids", "ttype": "many2many", "relation": "ir.attachment",
             "relation_table": "x_dwo_partner_list_rel", "column1": "partner_id", "column2": "attachment_id",
             "field_description": "Document list", "model_id": partner_model.id},
            {"name": "x_dwo_ro_file", "ttype": "binary", "field_description": "Archived contract",
             "model_id": partner_model.id},
            {"name": "x_dwo_ro_file_name", "ttype": "char", "field_description": "Archived contract name",
             "model_id": partner_model.id},
            {"name": "x_dwo_ro_attachment_id", "ttype": "many2one", "relation": "ir.attachment",
             "field_description": "Archived document", "model_id": partner_model.id},
        ])
        env["ir.ui.view"].create({
            "name": "dwo_attpreview_core test fields",
            "model": "res.partner",
            "inherit_id": env.ref("base.view_partner_form").id,
            "arch": """
                <xpath expr="//sheet" position="inside">
                    <group name="dwo_files" string="Files">
                        <field name="x_dwo_file_name" invisible="1"/>
                        <field name="x_dwo_file" filename="x_dwo_file_name"/>
                        <field name="x_dwo_attachment_id"/>
                        <field name="x_dwo_file_ids" widget="many2many_binary"/>
                        <field name="x_dwo_ro_file_name" invisible="1"/>
                        <field name="x_dwo_ro_file" filename="x_dwo_ro_file_name" readonly="1"/>
                        <field name="x_dwo_ro_attachment_id" readonly="1"/>
                        <field name="x_dwo_list_ids">
                            <list><field name="name"/></list>
                        </field>
                    </group>
                </xpath>""",
        })

    def setUp(self):
        super().setUp()
        patch_sample_engine(self)

    def _att(self, name, raw, **vals):
        return self.env["ir.attachment"].create(dict({"name": name, "raw": raw}, **vals))

    def test_tour_binary_attachment_form(self):
        # base.action_attachment: the field "File Content" (raw in Odoo 20, datas before) of the attachment itself
        att = self._att("notes.sample", b"binary tour content")
        self.start_tour("/odoo/action-base.action_attachment/%d" % att.id,
                        "dwo_attpreview_core_field_binary_tour", login="admin")

    def test_tour_partner_file_fields(self):
        partner = self.env["res.partner"].create({
            "name": "Field Tour Partner",
            "x_dwo_file": base64.b64encode(b"contract tour content").decode(),  # Odoo 20: base64 as str (bytes raise)
            "x_dwo_file_name": "contract.sample",
            "x_dwo_ro_file": base64.b64encode(b"readonly binary content").decode(),  # Odoo 20: base64 as str (bytes raise)
            "x_dwo_ro_file_name": "archived.sample",
        })
        files = self._att("report.sample", b"m2m tour content", res_model="res.partner", res_id=partner.id)
        listed = self._att("listed.sample", b"list tour content", res_model="res.partner", res_id=partner.id)
        unknown = self._att("archive.xyz", b"\x00\x01binary", res_model="res.partner", res_id=partner.id)
        main = self._att("main.sample", b"m2o tour content", res_model="res.partner", res_id=partner.id)
        old = self._att("old.sample", b"readonly m2o content", res_model="res.partner", res_id=partner.id)
        partner.write({
            "x_dwo_file_ids": [(6, 0, files.ids)],
            "x_dwo_list_ids": [(6, 0, (listed | unknown).ids)],
            "x_dwo_attachment_id": main.id,
            "x_dwo_ro_attachment_id": old.id,
        })
        self.start_tour("/odoo/res.partner/%d" % partner.id, "dwo_attpreview_core_field_partner_tour",
                        login="admin")

    def test_tour_binary_not_stored_as_attachment(self):
        # ir.mail_server.smtp_ssl_certificate is attachment=False: read from the table, no attachment made
        server = self.env["ir.mail_server"].create({
            "name": "Tour server", "smtp_host": "localhost", "smtp_authentication": "certificate", "smtp_encryption": "ssl",
            "smtp_ssl_certificate": base64.b64encode(PNG).decode(), "smtp_ssl_private_key": base64.b64encode(b"key").decode(),  # Odoo 20: base64 as str (bytes raise)
        })
        n_att = self.env["ir.attachment"].sudo().search_count([])
        self.start_tour("/odoo/action-base.action_ir_mail_server_list/%d" % server.id,
                        "dwo_attpreview_core_field_table_tour", login="admin")
        self.assertEqual(self.env["ir.attachment"].sudo().search_count([]), n_att)

    def test_tour_attachments_menu_list(self):
        # the list of the Attachments menu (a list with selectors, not a field)
        self._att("menu list.sample", b"menu list content")
        self.start_tour("/odoo/action-base.action_attachment", "dwo_attpreview_core_field_menu_list_tour",
                        login="admin")
