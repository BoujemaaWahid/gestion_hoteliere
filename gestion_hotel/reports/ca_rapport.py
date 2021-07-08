from odoo import api, fields, models
import json
import datetime
class ca_rapport(models.Model):
    _name = 'report.gestion_hotel.hotel_c_a_template_report3'


    @api.model
    def _get_report_values(self, docids, data=None):
        uid = data['context']['uid']
        user_ = self.env['res.users']
        user = user_.search([('id','=',uid)])
        company = user['company_id']
        obj = data["form"]["obj"].replace('\'','"')
        obj = json.loads(obj)
        docargs = {
            'TAB':obj,
            'company':company,
            'today':datetime.date.today()
        }
        return docargs