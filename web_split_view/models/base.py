from odoo import api, models


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_id_by_xmlid(self, xml_id):
        """Resolve an external id (e.g. ``base.view_partner_tree``) to a database id, False if unknown."""
        if not xml_id:
            return False
        record = self.env.ref(xml_id, raise_if_not_found=False)
        return record.id if record else False
