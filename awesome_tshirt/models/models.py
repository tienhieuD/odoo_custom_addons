from odoo import _, api, fields, models

class Contact(models.Model):
    _name = 'awesome.contact'
    _description = 'Contact one'
    
    name = fields.Char('Name', required=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('preactive', 'Pre Active'),
        ('postactive', 'Post Active'),
    ])
    phone = fields.Char('Phone')
    address = fields.Char('Address')

class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('split', "Split")])

class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('split', "Split")], ondelete={'split': 'cascade'})