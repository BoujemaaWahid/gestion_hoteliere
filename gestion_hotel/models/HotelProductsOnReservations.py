from odoo import api, fields, models

class ProductsReservations(models.Model):
    _name = 'hotel.products.reservations'
    product = fields.Many2one(comodel_name="product.product", string="Product", required=True, )
    quantity = fields.Integer(string="Quantity", required=True, default=1)
    reservation = fields.Many2one(comodel_name="hotel.reservation", string="Reservations", required=False, )