from odoo import api, fields, models
class HclientCa(models.Model):
    _name = 'hotel.client_ca_c'
    _rec_name = 'name'
    _description = 'New Description'
    name = fields.Char(string="name",required=False)
    year = fields.Integer(string="Year", required=False, )
    amount = fields.Float(string="amount",  required=False, )

class HclientCa12(models.Model):
    _name = 'hotel.months_ca_c'
    _rec_name = 'name'
    _description = 'New Description'
    name = fields.Char(string="name",required=False)
    year = fields.Integer(string="Year", required=False, )
    amount = fields.Float(string="amount",  required=False, )

class HclientCa13(models.Model):
    _name = 'hotel.saisons_ca_c'
    _rec_name = 'name'
    _description = 'New Description'
    name = fields.Char(string="name",required=False)
    year = fields.Integer(string="Year", required=False, )
    amount = fields.Float(string="amount",  required=False, )

class HclientCa14(models.Model):
    _name = 'hotel.region_ca_c'
    _rec_name = 'name'
    _description = 'New Description'
    name = fields.Char(string="name",required=False)
    year = fields.Integer(string="Year", required=False, )
    amount = fields.Float(string="amount",  required=False, )
