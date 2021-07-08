from odoo import api, fields, models,_

class HotelAccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    nightsNumber = fields.Integer(string="Nights Number", required=False, default=1)
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        self.price_subtotal *=self.nightsNumber
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            currency = self.invoice_id.currency_id
            date = self.invoice_id._get_currency_rate_date()
            price_subtotal_signed = currency._convert(price_subtotal_signed, self.invoice_id.company_id.currency_id, self.company_id or self.env.user.company_id, date or fields.Date.today())
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

class HotelAccountInvoice(models.Model):
     _inherit = 'account.invoice'
     nightsNumber = fields.Integer(string="Nights Number", required=False, )
     is_reservation = fields.Boolean(string="", default=False )
     check_in_customer = fields.Date(string="Checkin", required=False, )
     check_out_customer = fields.Date(string="Checkout", required=False, )
     tax_hotel_sejour = fields.Monetary(string = 'Tax séjour', default=0)
     reservation_adults = fields.Integer(string = 'Reservation adults',default=1,required=False)
     reservation_id = fields.Many2one(comodel_name="hotel.reservation", string="Reservation", required=False, )



     @api.multi
     def finalize_invoice_move_lines(self, move_lines):
         """ finalize_invoice_move_lines(move_lines) -> move_lines

             Hook method to be overridden in additional modules to verify and
             possibly alter the move lines to be created by an invoice, for
             special cases.
             :param move_lines: list of dictionaries with the account.move.lines (as for create())
             :return: the (possibly updated) final move_lines to create for this invoice
         """
         if self.is_reservation == False:
             return move_lines

         tax_hotel_rooms = self.env['account.tax']
         tax_hotel_rooms = tax_hotel_rooms.search([('idTvaHotel', '=', '#F0X009#')])
         finalVal = self.reservation_adults * self.nightsNumber * tax_hotel_rooms['amount']
         move_lines[0][2]['credit'] = move_lines[0][2]['credit'] + finalVal

         X = len(move_lines) - 2
         somme = 0

         for cmp in range(0, X):
             somme += move_lines[cmp][2]['credit']

         somme += move_lines[X][2]['credit']


         move_lines[len(move_lines)-1][2]['debit'] = somme



         return move_lines




     @api.one
     @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                  'currency_id', 'company_id', 'date_invoice', 'type')
     def _compute_amount(self):
         round_curr = self.currency_id.round
         self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
         self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)

         if self.is_reservation :
             tax_hotel_rooms = self.env['account.tax']
             tax_hotel_rooms = tax_hotel_rooms.search([('idTvaHotel','=','#F0X009#')])
             finalVal = self.reservation_adults * self.nightsNumber * tax_hotel_rooms['amount']
             self.write({'tax_hotel_sejour':finalVal})


         self.amount_total = self.amount_untaxed + self.amount_tax+ self.tax_hotel_sejour
         amount_total_company_signed = self.amount_total
         amount_untaxed_signed = self.amount_untaxed
         if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
             currency_id = self.currency_id
             amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id,
                                                                self.company_id,
                                                                self.date_invoice or fields.Date.today())
             amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id,
                                                          self.company_id, self.date_invoice or fields.Date.today())
         sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
         self.amount_total_company_signed = amount_total_company_signed * sign
         self.amount_total_signed = self.amount_total * sign
         self.amount_untaxed_signed = amount_untaxed_signed * sign



