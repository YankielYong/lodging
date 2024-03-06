from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    guest = fields.Boolean(default=False)
    
    