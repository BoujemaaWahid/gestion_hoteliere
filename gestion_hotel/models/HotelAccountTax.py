from odoo import api, fields, models

class AccountTaxHotel(models.Model):
    _inherit = 'account.tax'
    idTvaHotel = fields.Char()

