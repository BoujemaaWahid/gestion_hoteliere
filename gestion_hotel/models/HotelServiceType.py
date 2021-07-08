from odoo import models, fields, api,exceptions,_
from datetime import  datetime,date
from odoo.exceptions import ValidationError

class ServiceType(models.Model):
    _name="hotel.service.type"
    _description = "Service Type"
    name = fields.Char('Category', size=64, required=True)
    services = fields.One2many(comodel_name="hotel.services", inverse_name="category", string="Services", required=True, )
    _sql_constraints = [('service_type_name_unique', 'unique(name)', _("Service type name already exist"))]