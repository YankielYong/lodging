from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CheckIn(models.Model):
    _name = 'lodging.check_in'
    _inherit = ['mail.thread']
    _description = _('Check-In')

    name = fields.Char(string=_('Nº'), default=lambda self: _('Register Check-In'), readonly=True)
    read_only = fields.Boolean(default=False)
    reservation_id = fields.Many2one('lodging.reservation', string=_('Reservation'), readonly=True)
    room_id = fields.Many2one('lodging.room', string=_('Room'), readonly=True)
    guests_ids = fields.Many2many('res.partner', string=_('Guests'), required=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if val.get('name', _('Register Check-In')) == _('Register Check-In'):
                val['name'] = self.env['ir.sequence'].next_by_code('lodging.check_in') or _('Register Check-In')
        result = super(CheckIn, self).create(vals_list)
        for rec in result:
            rec.read_only = True
            rec.room_id.state = 'busy'
            rec.reservation_id.state = 'inprogress'
            rec.reservation_id.check_in_id = rec.id
            for guest in rec.guests_ids:
                guest.guest = True
        return result
    
    @api.constrains('guests_ids')
    def _constrains_guests_ids(self):
        for rec in self:
            capacity = rec.room_id.capacity
            if len(rec.guests_ids) > capacity:
                m1 = _("The capacity of this room is")
                m2 = _("guests")
                m3 = _("guest")
                if capacity > 1:
                    raise ValidationError(f'{m1} {capacity} {m2}')
                else:
                    raise ValidationError(f'{m1} {capacity} {m3}')
            elif len(rec.guests_ids) < 1:
                raise ValidationError(_('There must be at least 1 guest'))
    