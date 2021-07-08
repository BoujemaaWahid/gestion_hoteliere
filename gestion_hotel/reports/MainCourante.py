from odoo import api, fields, models
import datetime
import math

class MainCouranteRapportHotel(models.AbstractModel):
    _name = 'report.gestion_hotel.main_courante_template_report1'

    @api.model
    def _get_report_values(self, docids, data=None):
        uid = data['context']['uid']
        user_ = self.env['res.users']
        user = user_.search([('id','=',uid)])
        company = user['company_id']
        docargs = {
            'doc_ids':  data['ids'],
            'doc_model': data['model'],
            'date_debut':data['form']['date_debut'],
            'date_fin':data['form']['date_fin'],
            'payments':self.get_payments(data['form']['payment_ids']),
            'total':data["form"]["total"],
            'isAll':data["form"]["isAll"],
            'company':company,
            'today':datetime.date.today()
        }
        print("docargs : ",docargs)
        return docargs

    def get_payments(self,payments):
        array = []
        x =self.env["account.payment"]
        x= x.search([("id",'in',payments)])


        for p in x:
            array.append(p)
        return array