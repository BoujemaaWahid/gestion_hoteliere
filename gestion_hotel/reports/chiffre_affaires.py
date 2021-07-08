from odoo import api, fields, models
import datetime
from statistics import mean
class Chiffre_affaire(models.Model):
    _name = 'hotel.chiffre_affaire'
    _rec_name = 'name'
    name = fields.Char()
    parent = fields.Text("parent")
    YC = fields.Boolean(string="Clients",  default=True)
    YM = fields.Boolean(string="Months",  )
    YS = fields.Boolean(string="Saisons",  )
    YR = fields.Boolean(string="Regions",  )
    status = fields.Selection(string="", selection=[('cl', 'Clients'), ('mt', 'Months'), ('sm', 'Saisons'),('rm','Regions')], default="cl", required=False, )

    @api.onchange('status')
    def onchange_method(self):
        self.parent = ""
        if self.status == "cl":
            self.parent = self.account_payments_clients()
            return
        if self.status == "mt":
            self.parent = self.account_paymetns_months()
            return
        if self.status == "sm":
            self.parent = self.account_paymetns_saisons()
        if self.status == "rm":
            self.parent = self.account_payment_regions()
            return




    def account_payments_clients(self):
        AC = self.query_account_payments()
        clients_header = self.mkHeader(AC[1],"clients")
        AC = AC[0]
        RP = self.query_res_partner()
        year_clients = self.mkValuesClients(clients_header, AC, RP)
        year_clients = {"tab": {"header": clients_header, "body": year_clients[0]}, "best": year_clients[1],
                        "CA_Total": year_clients[2],"Type":"Client"}
        return year_clients


    def account_paymetns_months(self):
        AC = self.query_account_payments()
        months_header = self.mkHeader(AC[1], "months")

        AC = AC[0]
        year_months = self.mkValuesMonths(months_header, AC)
        year_months = {"tab": {"header": months_header, "body": year_months[0]}, "best": year_months[1],
                        "CA_Total": year_months[2],"Type":"Month"}

        return year_months

    def account_paymetns_saisons(self):
        AC = self.query_account_payments()
        saison_header = self.mkHeader(AC[1], "saisons")
        AC = AC[0]
        year_saison = self.mkValuesSaisons(saison_header, AC)
        year_saison = {"tab": {"header": saison_header, "body": year_saison[0]}, "best": year_saison[1],
                        "CA_Total": year_saison[2],"Type":"Saison"}

        return year_saison

    def account_payment_regions(self):
        AC = self.query_account_payments()
        region_header = self.mkHeader(AC[1], "Region")
        AC = AC[0]
        reg = self.mkValuesRegion(region_header,AC)
        year_region = {"tab": {"header": region_header, "body": reg[0]}, "best": reg[1],
                        "CA_Total": reg[2],"Type":"Region"}
        print(year_region)
        return year_region

    def mkValuesRegion(self,header,payments):
        regions = self.query_regions_clients()
        years = header[1:len(header) - 1]

        body = list()
        BEC = list()
        for cl in regions:
            reg = {"name":cl['region']}
            values = list()
            for y in years:
                values.append(self.getSumAmount(y,['partner_id',cl['ids']],payments))

            rsv2 = round(sum(values),2)
            if rsv2 != 0:
                BEC.append(rsv2)
            values.append(round(sum(values),2))


            reg.update({"values": values})
            moyenne = mean(values)
            if moyenne != 0:
                body.append(reg)

        tValue = list()
        for i in range(0, len(years)):
            s = 0
            for j in body:
                s += j['values'][i]
            tValue.append(round(s,2))
        CA = round(sum(tValue),2)
        tValue.append(CA)
        body.append({"name": "total", "values": tValue})
        return [body, self.getBest(BEC, body), CA]







    def mkValuesSaisons(self,header,payments):
        saisons = {"Winter": [12, 1, 2], "Spring": [5, 4, 3], 'Summer': [8, 7, 6], 'Autumn': [11, 10, 9]}
        BEC = list()
        years = header[1:len(header) - 1]
        body = list()

        for s in saisons:
            values = list()
            for y in years:
                values.append(self.getSumAmount(y, ['month', saisons[s]], payments))
            BEC.append(round(sum(values),2))
            values.append(round(sum(values),2))
            body.append({"name": s, "values": values})
        tValue = list()
        for i in range(0, len(years)):
            s = 0
            for j in body:
                s += j['values'][i]
            tValue.append(round(s,2))
        CA = round(sum(tValue),2)
        tValue.append(CA)
        body.append({"name": "total", "values": tValue})
        return [body, self.getBest(BEC, body), CA]



    def mkValuesMonths(self, header,payments):
        BEC = list()
        months = self.getMonthList()
        years = header[1:len(header)-1]
        body = list()
        for i, j in months:
            values = list()
            row = {}
            for year in years:
                values.append(self.getSumAmount(year, ['month', [j]], payments))
            BEC.append(round(sum(values),2))
            values.append(round(sum(values),2))
            row.update({"name": i, "values": values})
            body.append(row)
        tValue = list()
        for i in range(0, len(years)):
            s = 0
            for j in body:
                s += j['values'][i]
            tValue.append(round(s,2))
        CA = round(sum(tValue),2)
        tValue.append(CA)
        body.append({"name": "total", "values": tValue})
        return [body, self.getBest(BEC, body), CA]


    def mkValuesClients(self,header, payments, clients):
        years = header[1:len(header) - 1]
        body = list()
        BEC = list()
        for cl in clients:
            client = {"name":cl['name'],"id":cl['id'],"codePassager":cl['codePassager']}
            values = list()
            for y in years:
                values.append(self.getSumAmount(y,['partner_id',[cl['id']]],payments))

            rsv2 = round(sum(values),2)
            if rsv2 != 0 and cl['codePassager'] != '#F0X009#':
                BEC.append(rsv2)
            values.append(round(sum(values),2))

            client.update({"values": values})
            moyenne = mean(values)
            if moyenne != 0 and cl['codePassager'] != '#F0X009#':
                body.append(client)

        tValue = list()
        for i in range(0, len(years)):
            s = 0
            for j in body:
                s += j['values'][i]
            tValue.append(round(s,2))
        CA = round(sum(tValue),2)
        tValue.append(CA)
        body.append({"name": "total", "values": tValue})
        return [body, self.getBest(BEC, body), CA]




    def getSumAmount(self,year,fact,payments):
        sum = 0
        for p in payments:
            if( p[fact[0]] in fact[1] and (p['year'] == int(year))):
                sum += p['amount']
        return round(sum,2)

    def query_regions_clients(self):
        query = "select distinct(city) from res_partner where city is not NULL"
        AC = self._cr.execute(query)
        AC = self._cr.fetchall()
        regions = list()
        for cmp in range(0, len(AC)):
            query = "select id from res_partner where city = '{}'".format(AC[cmp][0])
            BC = self._cr.execute(query)
            BC = self._cr.fetchall()
            ids = list()
            for jmp in range(0,len(BC)):
                ids.append(BC[jmp][0])
            regions.append({"region":AC[cmp][0],"ids":ids})
        return regions




    def query_account_payments(self):
        query = "select {},{},{},{},{} from account_payment where state='posted'"
        query = query.format("id", "EXTRACT(YEAR from payment_date) as year",
                                                                 "EXTRACT(MONTH from payment_date) as month",
                                                                 "CAST(amount AS Float)", "partner_id")
        AC = self._cr.execute(query)
        AC = self._cr.fetchall()
        years = list()
        for cmp in range(0,len(AC)):
            years.append(int(AC[cmp][1]))
            AC[cmp] = {"id":AC[cmp][0],"year":AC[cmp][1],"month":AC[cmp][2],"amount":AC[cmp][3],"partner_id":AC[cmp][4]}
        return [AC,years]

    def query_res_partner(self):
        query = "select {},{} from res_partner"
        query = query.format("id", "name")
        AC = self._cr.execute(query)
        AC = self._cr.fetchall()
        partner = self.env['res.partner']
        for cmp in range(0, len(AC)):
            code = partner.search([('id','=',AC[cmp][0])])
            code = code['codePassager']
            AC[cmp] = {"id": AC[cmp][0], "name": AC[cmp][1],'codePassager':code}

        return AC

    def mkHeader(self, years, fact):
        now = datetime.datetime.now()
        minYear = None
        maxYear = None
        if len(years) == 0:
            minYear = now.year
            maxYear = now.year
        else:
            minYear = max(years)
            maxYear = min(years)
        l = list()
        l.append("Year/{}".format(fact))
        for i in range(minYear, maxYear + 1):
            l.append(str(i))
        l.append('totale')
        return l

    def getBest(self,list, body):
        if len(list) == 0:
            return {'name':"",'value':""}
        mx = max(list)
        mx = list.index(mx)
        o = body[mx]
        x = o['values'][len(o['values']) - 1]
        o = {"name": o['name'], "value": x}
        return o

    def getMonthList(self):
        monthList = list()
        for i in range(1, 13):
            month = datetime.date(1900, i, 1).strftime('%B')
            monthList.append([month, i])
        return monthList


    @api.multi
    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'obj': self.parent,
            },
        }
        return self.env.ref('gestion_hotel.hotel_chiffre_affaire_report_file').report_action(self, data=data)
