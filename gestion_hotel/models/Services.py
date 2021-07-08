from odoo import models, fields, api,exceptions,_


class EmployeesServices(models.Model):
    _inherit = "hr.employee"
    _sql_constraints = [
        ('services_employees_identification_id_unique', 'unique(identification_id)', _("Id card code already exist")),
    ]
    services_ids = fields.Many2many("hotel.services", string="Services", )


class ProductProduct(models.Model):
    _inherit = "product.product"
    typeOfProduct = fields.Selection(string="Product Family", selection=[
        ('to_rooms_categ', 'Rooms categorie'),
        ('to_service', 'Hotel Services'),
        ('to_room', 'Hotel Room'),
        ('to_other','Other'),], required=False, default="to_other", readonly=True)

    @api.model
    def create(self, vals):
        print(vals)
        return super(ProductProduct, self).create(vals)




class Services(models.Model):
    _name = "hotel.services"
    _description = "Hotel services"



    product_id = fields.Many2one('product.product', 'Product_id',
                                 required=True, delegate=True,
                                 ondelete='cascade')

    reservations_ids = fields.Many2many("hotel.reservation", string="Reservations", )

    employees_ids = fields.Many2many("hr.employee", string="Employees", )
    service_manager = fields.Many2one('res.users', string='Service Manager', required=False)

    category = fields.Many2one('hotel.service.type', string='Service Category',
                               required=True)

    isVotable = fields.Boolean(string="Votable",  default=False)

    voteValue = fields.Float(string="Vote average",  required=False, default=0)

    state = fields.Selection([
        ('available','Available'),
        ('out','Out of order'),
    ], string="State", required=True, default = 'available')

    description = fields.Char('Service description', required=False)


    _sql_constraints = [('service_name_unique', 'unique(name)', _("Service name already exist"))]
    have_employees = fields.Boolean(string="Employees in service",default=True, compute="is_there_any_employees")

    @api.depends('have_employees')
    def is_there_any_employees(self):
        for rec in self:
            if(rec.employees_ids):
                rec.have_employees = True

    @api.multi
    def setVotable(self):
        for rec in self:
            rec.isVotable = True

    @api.multi
    def setNonVotable(self):
        for rec in self:
            rec.isVotable = False

    @api.multi
    def set_out_of_order(self):
        self.state = 'out'

    @api.multi
    def set_available(self):
        self.state = 'available'


    @api.onchange("typeOfProduct")
    def setProductRoom(self):
        self.typeOfProduct = "to_service"
