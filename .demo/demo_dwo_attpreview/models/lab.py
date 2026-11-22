# -*- coding: utf-8 -*-
"""Attachment Preview Lab: one record per preview module, with every kind of file field.

The demo server is public, so what a visitor may upload is limited (see ``MAX_FILES`` and ``MAX_BYTES``):

* ``web.max_file_upload_size`` (system parameter, set by the data of this module) and the Nginx
  ``client_max_body_size`` of the demo refuse a request bigger than 100 MB before it is stored;
* every file a visitor adds beyond the 10 of a record is deleted by ``_lab_sweep`` (after a save, after a chatter
  message and every minute by a cron), so the disk of the server stays safe. The sample files, made by the
  ``post_init_hook``, are never counted or deleted: they are the attachments (and lines) up to the ids stored in the
  parameters ``demo_dwo_attpreview.sample_attachment_id`` and ``.sample_line_id``.
"""
from datetime import timedelta

from odoo import api, fields, models

MAX_FILES = 10
MAX_BYTES = 100 * 1024 * 1024
ANY_FIELD = ["|", ("res_field", "=", False), ("res_field", "!=", False)]  # the search of ir.attachment hides res_field


class AwesomePreview(models.Model):
    _name = "awesome.preview"
    _description = "Attachment Preview Lab"
    _inherit = ["mail.thread"]
    _order = "sequence, id"

    name = fields.Char(required=True, tracking=False)
    sequence = fields.Integer(default=10)
    module_name = fields.Char("Module", readonly=True)
    description = fields.Text("What to try", readonly=True)
    file_binary = fields.Binary("Binary field", attachment=True)
    file_binary_name = fields.Char("File name")
    file_m2o = fields.Many2one("ir.attachment", "Many2one to an attachment", ondelete="set null")
    file_m2m = fields.Many2many("ir.attachment", "awesome_preview_attachment_rel", "preview_id", "attachment_id",
                                string="Many2many attachments")
    line_ids = fields.One2many("awesome.preview.file", "preview_id", string="One2many lines with a file")
    attachment_ids = fields.One2many(
        "ir.attachment", "res_id", string="One2many attachments of the record",
        domain=[("res_model", "=", "awesome.preview"), ("res_field", "=", False)])

    # ---- limits -----------------------------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._lab_sweep()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._lab_sweep()
        return res

    @api.model
    def _lab_sample_ids(self):
        """(last id of the sample attachments, last id of the sample lines)."""
        param = self.env["ir.config_parameter"].sudo()
        return (int(param.get_param("demo_dwo_attpreview.sample_attachment_id", 0)),
                int(param.get_param("demo_dwo_attpreview.sample_line_id", 0)))

    def _lab_sweep(self):
        """Delete what a visitor added beyond the limits: lines and files after the 10th of a record, any file over
        100 MB. The oldest ones are kept. Samples are never touched."""
        sample_att, sample_line = self._lab_sample_ids()
        Attachment = self.env["ir.attachment"].sudo()
        for rec in self.sudo().filtered("id"):
            lines = rec.line_ids.filtered(lambda line: line.id > sample_line).sorted("id")
            lines[MAX_FILES:].unlink()
            lines = lines[:MAX_FILES]
            files = (rec.file_m2m | rec.file_m2o
                     | Attachment.search([("res_model", "=", self._name), ("res_id", "=", rec.id)] + ANY_FIELD)
                     | Attachment.search([("res_model", "=", "awesome.preview.file"),
                                          ("res_id", "in", rec.line_ids.ids)] + ANY_FIELD))
            files = files.exists().filtered(lambda att: att.id > sample_att).sorted("id")
            too_big = files.filtered(lambda att: att.file_size > MAX_BYTES)
            keep = (files - too_big)[:MAX_FILES]
            (too_big | (files - too_big - keep)).unlink()

    @api.model
    def _cron_lab_sweep(self):
        """Every minute: the same sweep for every record, and the files that belong to no record (uploaded in a form
        that was never saved) after 30 minutes."""
        self.search([])._lab_sweep()
        sample_att, __ = self._lab_sample_ids()
        Attachment = self.env["ir.attachment"].sudo()
        linked = set(self.search([]).file_m2m.ids) | set(self.search([]).file_m2o.ids)
        stale = Attachment.search([
            ("res_model", "=", self._name), ("res_id", "in", [0, False]), ("id", ">", sample_att),
            ("create_date", "<", fields.Datetime.now() - timedelta(minutes=30))] + ANY_FIELD)
        stale.filtered(lambda att: att.id not in linked).unlink()


class AwesomePreviewFile(models.Model):
    _name = "awesome.preview.file"
    _description = "Attachment Preview Lab: file line"
    _order = "id"

    preview_id = fields.Many2one("awesome.preview", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    file = fields.Binary(attachment=True)
    file_name = fields.Char("File name")

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.preview_id._lab_sweep()
        return lines

    def write(self, vals):
        res = super().write(vals)
        self.preview_id._lab_sweep()
        return res


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model_create_multi
    def create(self, vals_list):
        messages = super().create(vals_list)
        for msg in messages.filtered(lambda m: m.model == "awesome.preview" and m.res_id):
            self.env["awesome.preview"].browse(msg.res_id)._lab_sweep()
        return messages
