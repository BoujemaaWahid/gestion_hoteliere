from odoo import api, fields, models
import json
import datetime
import math

class MainCouranteRapportHotel(models.AbstractModel):
    _name = 'report.gestion_hotel.hotel_stat_rooms_template_report2'

    @api.model
    def _get_report_values(self, docids, data=None):
        uid = data['context']['uid']
        user_ = self.env['res.users']
        user = user_.search([('id','=',uid)])
        company = user['company_id']
        header = data["form"]["header"].replace('\'','"')
        header = json.loads(header)
        body = data["form"]["body"].replace('\'','"')
        body = body.replace('True','1')
        body = body.replace('False','0')

        body = json.loads(body)

        # date_debut = datetime.datetime.strptime(data['form']['date_debut'], '%Y-%m-%d %H:%M:%S')
        # date_fin = datetime.datetime.strptime(data['form']['date_fin'], '%Y-%m-%d %H:%M:%S')
        bigArray = self.FormatRooms(header[0]["header"],body)
        bigArray = str(bigArray).replace('\'','"')
        bigArray = json.loads(bigArray)

        docargs = {
            'date_debut':data['form']['date_debut'],
            'date_fin':data['form']['date_fin'],
            # 'header':header[0]["header"],
            # 'body':body,
            'TAB':bigArray,
            'company':company,
            'today':datetime.date.today()
        }
        return docargs

    def getArrays(self, row):
        R = []
        x = True
        cmp = 0
        while x:
            array = []
            if cmp < len(row['value']) - 7:
                l2 = row['value'][cmp:cmp + 7]
                cmp += 7
            else:
                x = False
                l2 = row['value'][cmp:len(row['value'])]

            room = {'name': row['name'], 'isOut': row['isOut'], 'value': l2}
            R.append(room)
        return R

    def FormatRooms(self, l, rooms):
        x = True
        cmp = 0
        array = []
        l.remove('Rooms')
        while x:
            if cmp < len(l) - 7:
                l2 = l[cmp:cmp + 7]
                cmp += 7
                l2.insert(0, 'Rooms')
                array.append(l2)
            else:
                x = False
                l2 = l[cmp:len(l)]
                l2.insert(0, 'Rooms')
                array.append(l2)

        Rooms = []
        for cmp in range(0, len(rooms)):
            X = self.getArrays(rooms[cmp])
            Rooms.append(X)

        BigArray = []
        for xc in range(0, len(array)):
            header = array[xc]
            lineRooms = []
            for rxc in range(0, len(Rooms)):
                line0 = Rooms[rxc][0]

                Rooms[rxc].pop(0)
                lineRooms.append(line0)

            X = {"header": header, "body": lineRooms}
            BigArray.append(X)
        return BigArray;

