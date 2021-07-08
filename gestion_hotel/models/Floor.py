from odoo import models, fields, api,exceptions,_

class HotelFloor(models.Model):
    _name = "hotel.floor"
    _description = "Floor"
    name = fields.Char('Floor Name', required=True, index=True)
    rooms = fields.One2many(comodel_name="hotel.room", inverse_name="floor", string="Rooms", required=False, )
    sequence = fields.Integer(index=True)
    _sql_constraints = [('floor_name_unique', 'unique(name)', _("Floor name already exist"))]