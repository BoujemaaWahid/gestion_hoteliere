from odoo import models, fields, api, exceptions,_
from odoo.exceptions import ValidationError

class HotelRoomType(models.Model):
    _name = "hotel.room.type"
    _description = "Room Type"


    product_id = fields.Many2one('product.product', 'Product_id',
                                 required=True, delegate=True,
                                 ondelete='cascade')

    rooms = fields.One2many(comodel_name="hotel.room", inverse_name="type", string="Rooms", required=False, )
    state = fields.Selection(string="", selection=[('available', 'Available'),
                               ('saturated', 'Saturated'), ('empty','Empty')],default='empty' )
    _sql_constraints = [('room_type_unique', 'unique(name)', _("Type name already exist"))]

    @api.onchange("typeOfProduct")
    def setProductType(self):
        self.typeOfProduct = "to_rooms_categ"

