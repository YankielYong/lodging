import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied

class Reservation(models.Model):
    _name = 'lodging.reservation'
    _inherit = ['mail.thread']
    _description = _('Reservation')
    _order = 'arrival_date, exit_date'
    
    name = fields.Char(string=_('Nº'), default=lambda self: _('New Reservation'), readonly=True)
    read_only = fields.Boolean(default=False)
    active = fields.Boolean(default=True)
    arrival_date = fields.Date(
        string=_('Arrival Date'),
        default=fields.Date.context_today,
        required=True,
    )
    number_of_days = fields.Integer(string=_('Number of days'), required=True, default=1)
    exit_date = fields.Date(
        string=_('Exit Date'),
        compute='_compute_exit_date',
        store=True
    )
    state = fields.Selection(
        string=_('State'),
        selection=[
            ('pending', 'Pending'),
            ('inprogress', 'In Progress'),
            ('finished', 'Finished'),
            ('cancelled', 'Cancelled')
        ],
        default='pending', tracking=True, readonly=True
    )
    check_in_id = fields.Many2one('lodging.check_in', string='Check-In', readonly=True)
    guests_ids = fields.Many2many('res.partner', compute='_compute_guests_ids', string='Guests', store=True)
    partner_id = fields.Many2one('res.partner', string=_('Customer'), required=True)
    room_id = fields.Many2one('lodging.room', string=_('Room'), required=True)
    
    def register_check_in(self):
        for rec in self:
            date = datetime.datetime.now() + datetime.timedelta(hours=-5)
            today = datetime.date(date.year, date.month, date.day)
            if rec.arrival_date != today:
                raise AccessDenied('Today is not the reserved arrival date')
        return{
            'res_model': 'lodging.check_in',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('lodging.view_lodging_check_in_form').id
        }
        
    def register_check_out(self):
        self.env['lodging.check_out'].create({
            'reservation_id': self.id,
            'room_id': self.room_id.id,
            'guests_ids': self.guests_ids.ids
        })
        
    def cancel_reservation(self):
        for rec in self:
            rec.state = 'cancelled'
            rec.active = False
    
    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if val.get('name', _('New Reservation')) == _('New Reservation'):
                val['name'] = self.env['ir.sequence'].next_by_code('lodging.reservation') or _('New Reservation')
        result = super(Reservation, self).create(vals_list)
        for rec in result:
            rec.read_only = True
            guest = []
            guest.append(rec.partner_id.id)
            rec.write({'guests_ids': [(6, 0, guest)]})
        return result
    
    @api.depends('check_in_id')
    def _compute_guests_ids(self):
        for rec in self:
            rec.guests_ids = rec.check_in_id.guests_ids
    
    @api.depends('arrival_date', 'number_of_days')
    def _compute_exit_date(self):
        for rec in self:
            if rec.arrival_date and rec.number_of_days and rec.number_of_days > 0:
                rec.exit_date = rec.arrival_date + datetime.timedelta(days=rec.number_of_days)
            else:
                rec.exit_date = ''
                
    @api.onchange('exit_date')
    def _room_domain(self):
        rooms = self.env['lodging.room'].search([]).ids
        reservations = self.env['lodging.reservation'].search(['|', ('state', '=', 'pending'), ('state', '=', 'inprogress')])
        for reservation in reservations:
            if reservation.arrival_date < self.exit_date and reservation.exit_date > self.arrival_date:
                try:
                    rooms.remove(reservation.room_id.id)
                except:
                    print("Error")
        domain = {'room_id': [('id', 'in', rooms)]}
        return {'domain': domain}
                
    @api.constrains('number_of_days')
    def _constrains_number_of_days(self):
        for rec in self:
            if rec.number_of_days < 1:
                raise ValidationError('The number of days must be greater than 0')
            
    @api.constrains('arrival_date')
    def _constrains_arrival_date(self):
        for rec in self:
            date = datetime.datetime.now() + datetime.timedelta(hours=-5)
            today = datetime.date(date.year, date.month, date.day)
            if rec.arrival_date < today:
                raise ValidationError('Today is not the arrival date')
