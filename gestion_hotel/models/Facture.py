from odoo import models, fields, api,exceptions,_

class HotelFacture(models.Model):
    _name = "hotel.facture"

    name = fields.Char('Folio Number', readonly=True, index=True, default='New')

    order_id = fields.Many2one('sale.order', 'Order', delegate=True,
                               required=True, ondelete='cascade')
    # rooms o2m
    # services o2m


    hotel_invoice_id = fields.Many2one('account.invoice', 'Invoice',
                                       copy=False)

    duration_dummy = fields.Float('Duration Dummy')

