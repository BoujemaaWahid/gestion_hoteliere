from odoo import models, fields, api,exceptions,_, modules
from ast import literal_eval
from odoo.exceptions import ValidationError

class HotelClients(models.Model):
    _inherit = "res.partner"
    _description = "Clients"
    client_cin_code = fields.Char(size=8, string="ID card code", required=True)
    # client_passport_code = fields.Char(size=8, string="ID card code", required=True)

    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable", oldname="property_account_payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=False)
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
                                                     string="Account Receivable", oldname="property_account_receivable",
                                                     domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
                                                     help="This account will be used instead of the default one as the receivable account for the current partner",
                                                     required=False)
    reservations = fields.One2many(comodel_name="hotel.reservation", inverse_name="partner_id", required=False, )

    codePassager = fields.Char(string="", required=False, default="")

    _sql_constraints = [
        ('cin_client_unique', 'unique(client_cin_code)', _("Id card code already exist")),
    ]

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.codePassager == "#F0X009#":
                raise ValidationError(_("This record is a reference, it can't be deleted."))
            else :
                return super(HotelClients,self).unlink()


