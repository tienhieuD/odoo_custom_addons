from odoo import fields, models


class WebpTestResult(models.TransientModel):
    """Odoo 12 has no `display_notification` client action: show the test result in a small dialog."""
    _name = 'dwo.webp.test.result'
    _description = 'Auto WebP test result'

    title = fields.Char(readonly=True)
    message = fields.Text(readonly=True)
    success = fields.Boolean(readonly=True)
