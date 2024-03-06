import base64

from odoo import models, fields, api, _, modules
from odoo.exceptions import UserError, ValidationError

def _get_default_image():
        image_path = modules.get_module_resource('lodging', 'static/src/img', 'room.png')
        return base64.b64encode(open(image_path, 'rb').read())

class Room(models.Model):
    _name = 'lodging.room'
    _inherit = ['mail.thread']
    _description = _('Room')
    _order = 'number'
    
    name = fields.Char(string=_('Nº'), default=lambda self: _('New Room'), tracking=True)
    name_room = fields.Char(default=lambda self: _('Room'))
    number = fields.Integer(string=_('Number'), required=True, tracking=True)
    room_type_id = fields.Many2one('lodging.room.type', string=_('Room Type'), required=True, tracking=True)
    capacity = fields.Integer(string=_('Capacity'), compute='_compute_capacity', default="0")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.company.currency_id)
    night_price = fields.Monetary(string=_('Night Price'), required=True, tracking=True)
    image = fields.Binary(string=_('Image'), default=_get_default_image(), tracking=True)
    state = fields.Selection(
        string=_('State'),
        selection=[
            ('available', 'Available'),
            ('busy', 'Busy'),
        ],
        default="available", tracking=True, readonly=True
    )

    _sql_constraints = [('unique_number', 'unique (number)', 'There is already a room with this number')]
    
    def name_get(self):
        res = []
        for rec in self:
            name = f'{rec.name} - {rec.room_type_id.name} - {rec.night_price}{rec.currency_id.symbol}'
            res.append((rec.id, name))
        return res
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('number', operator, name), ('room_type_id', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
            
    @api.model_create_multi
    def create(self, vals_list):
        result = super(Room, self).create(vals_list)
        for rec in result:
            rec.name = f"{rec.name_room} {rec.number}"
        return result
        
    @api.depends('room_type_id')
    def _compute_capacity(self):
        for rec in self:
            rec.capacity = rec.room_type_id.capacity
    
    @api.constrains('night_price')
    def _check_night_price(self):
        for rec in self:
            if rec.night_price <= 0:
                raise ValidationError(_('The night price must be greater than 0'))
            
    @api.constrains('number')
    def _check_number(self):
        for rec in self:
            if rec.number < 1:
                raise ValidationError(_("The number must be greater than 0"))
    