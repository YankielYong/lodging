from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CheckOut(models.Model):
    _name = 'lodging.check_out'
    _inherit = ['mail.thread']
    _description = _('Check-Out')

    name = fields.Char(string=_('Nº'), default=lambda self: _('Register Check-Out'), readonly=True)
    reservation_id = fields.Many2one('lodging.reservation', string=_('Reservation'), readonly=True)
    room_id = fields.Many2one('lodging.room', string=_('Room'), readonly=True)
    guests_ids = fields.Many2many('res.partner', string=_('Guests'), readonly=True)
    
    
    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if val.get('name', _('Register Check-Out')) == _('Register Check-Out'):
                val['name'] = self.env['ir.sequence'].next_by_code('lodging.check_out') or _('Register Check-Out')
        result = super(CheckOut, self).create(vals_list)
        for rec in result:
            rec.reservation_id.active = False
            rec.reservation_id.state = 'finished'
            rec.room_id.state = 'available'
        return result
