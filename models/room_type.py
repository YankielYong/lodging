from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RoomType(models.Model):
    _name = 'lodging.room.type'
    _inherit = ['mail.thread']
    _description = _('Room Type')
    
    name = fields.Char(string=_('Name'), required=True)
    capacity = fields.Integer(string=_('Capacity'), required=True)
    description = fields.Text(string=_('Description'))
    
    @api.constrains('capacity')
    def _constrains_capacity(self):
        for rec in self:
            if rec.capacity < 1:
                raise ValidationError(_('Capacity must be a positive number'))
    