from odoo import models, fields, api,exceptions,_
from datetime import  datetime,date
from odoo.exceptions import ValidationError

class EquipementRoomHotel(models.Model):
    _inherit = 'maintenance.equipment'
    rooms_equipement_ids = fields.Many2many("hotel.room", string="Rooms", )




class Room(models.Model):
    _name = 'hotel.room'
    _description = 'Hotel Room'
    # name = fields.Char(string="Name", required=True, )
    # max_adult = fields.Integer()
    # max_child = fields.Integer()
    isConsuming = fields.Boolean(default=False  )
    occupied_by = fields.Char(string="current Client", default = "None")
    state = fields.Selection([('available', 'Available'),
                               ('occupied', 'Occupied'),
                               ('out', 'Out of order')],
                              'Status',
                              default='available',
                              required=True, readonly=True)

    capacity = fields.Integer('Capacity', required=True, default=1)
    image = fields.Binary(attachment=True)
    valid_date_begin = fields.Date(string="Date begin available", required=False)
    valid_date_end = fields.Date(string="Date end available", required=False) #default=lambda self: date.today()
    floor = fields.Many2one(comodel_name="hotel.floor", string="Floor", required=False, )
    equipements = fields.Many2many("maintenance.equipment", string="Room equipement", )
    reservations_ids = fields.Many2many("hotel.reservation", string="Room reservation", )

    type = fields.Many2one(comodel_name="hotel.room.type", string="Type", required=True, )
    notes = fields.Char(string="Description", required=False)
    product_id = fields.Many2one('product.product', 'Product_id',
                                 required=True, delegate=True,
                                 ondelete='cascade')


    _sql_constraints = [('name_room_unique', 'unique(name)', _("Room name already exist"))]


    @api.multi
    def set_available(self):
        self.state = "available"

    @api.multi
    def set_Occupied(self):
        self.state = "occupied"

    @api.multi
    def set_Out_Of_Order(self):
        self.state = "out"

    @api.onchange("typeOfProduct")
    def setProductRoom(self):
        self.typeOfProduct = "to_room"


    @api.constrains('valid_date_end')
    def _check_is_end_date_is_bigger_than_date_begin(self):
        for record in self:
            vdb = type(record.valid_date_begin)
            vde = type(record.valid_date_end)
            if vdb is bool and vde is not bool:
                raise ValidationError("Setting the availabilty of room require the date to start and the date of end wich mean after this date the room will be out of order to a maintenance reason")
            elif  vdb is not bool and vde is not bool:
                if record.valid_date_end <= record.valid_date_begin:
                    raise ValidationError('The end validating date should be after begin validating date')

    @api.constrains('valid_date_begin')
    def _check2(self):
        for record in self:
            vdb = type(record.valid_date_begin)
            vde = type(record.valid_date_end)
            if vdb is not bool and vde is bool:
                raise ValidationError("Setting the availabilty of room require the date to start and the date of end wich mean after this date the room will be out of order to a maintenance reason")

    @api.constrains('capacity')
    def _check_capacity_value(self):
            if self.capacity <= 0:
                raise ValidationError('Capacity shouldnt be 0')


    @api.model
    def create(self, values):
        typeRoom = self.env['hotel.room.type'].search([('id','=',values['type'])])
        typeRoom.state = "available"
        print(values)
        return super(Room, self).create(values)


    @api.multi
    def write(self,vals):
        stated =""
        keys = vals.keys()
        if('state' in keys):
            for rec in self:
                for room in rec.type.rooms:
                    if room.id == rec.id:
                        stated = vals['state']
                    else:
                        stated=room.state
                    if(stated=='available'):
                        rec.type.state = 'available'
                        break
                    else:
                        rec.type.state = 'saturated'
        return super(Room,self).write(vals);
