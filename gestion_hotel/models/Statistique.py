from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
import datetime


class MainCourante(models.Model):
    _name = 'hotel.stat.payment'
    _rec_name = 'date_order'
    isAll = fields.Boolean(string="All Payments")
    date_debut = fields.Date(string="from", required=False, default=datetime.date.today())
    date_fin = fields.Date(string="to", required=False, default=datetime.date.today())
    date_order = fields.Date(string="", required=False, default=datetime.date.today())
    hidingFiled = fields.Text()
    currency_id = fields.Many2one(
        'res.currency', string='Currency')


    montant_totale = fields.Monetary(string="Total", required=False)
    payments = fields.Many2many("account.payment", string="Result", )


    @api.multi
    def setAll(self):

        for rec in self:
            state = "('posted')"
            query = "select id,amount from account_payment where state in {} and reservation_hotel_id is not null".format(state)
            r = self._cr.execute(query)
            r = self._cr.fetchall()
            array = []
            total = 0
            rec.isAll = True
            for x in r:
                array.append(x[0])
                total += x[1]
            rec.montant_totale = total
            rec.payments = array
            self.sumMoney = rec.montant_totale
            self.pays = array
            self.all_money = True
    @api.multi
    def setNotAll(self):
        for rec in self:
         rec.isAll = False
         self.all_money = False
         self.forChange()

    def getResult(self, state, date1, date2):
        query = "select id,amount from account_payment where state in {} and (payment_date between '{}' and '{}') and reservation_hotel_id is not null".format(state, date1, date2)
        r = self._cr.execute(query)
        r = self._cr.fetchall()
        return r

    @api.onchange('date_debut','date_fin')
    def onChangeXXX(self):
        if self.date_debut and self.date_fin:
            if self.date_debut>self.date_fin:
                raise ValidationError(_("The start date should be less than end date"))
        self.forChange()

    def forChange(self):
        for rec in self:
            state = "('posted')"
            r = self.getResult(state, rec.date_debut, rec.date_fin)
            array = []
            total = 0
            for x in r:
                array.append(x[0])
                total += x[1]
            rec.montant_totale = total

            if len(array)>0:
                rec.payments = array

            else:
                rec.payments = None



    def getValuesPaymentsCreate(self):

        state = "('posted')"
        query = "select id,amount from account_payment where state in {} and reservation_hotel_id is not null".format(state)
        r = self._cr.execute(query)
        r = self._cr.fetchall()
        array = []
        total = 0
        for x in r:
            array.append(x[0])
            total += x[1]
        return {'X':array,'Y':total}

    @api.model
    def create(self, values):

        array = []
        total = 0

        if values['isAll'] == False:
            state = "('posted')"
            r = self.getResult(state,values['date_debut'],values['date_fin'])
            for x in r:
                array.append(x[0])
                total += x[1]
        else:
            V = self.getValuesPaymentsCreate()
            array = V.X
            total = V.Y

        values['payments'] = [[6,False,array]]
        values['montant_totale'] = total

        return super(MainCourante, self).create(values)

    @api.multi
    def write(self, values):
        array = []
        total = 0
        if 'isAll' in values.keys():
            if values['isAll'] == False :
                if 'date_debut' in values.keys() and 'date_fin' in values.keys():
                    state = "('posted')"
                    r = self.getResult(state, values['date_debut'], values['date_fin'])
                    for x in r:
                        array.append(x[0])
                        total += x[1]
                    values['payments'] = [[6, False, array]]
                    values['montant_totale'] = total

            else:
                V = self.getValuesPaymentsCreate()
                array = V['X']
                total = V['Y']
                values['payments'] = [[6, False, array]]
                values['montant_totale'] = total

        return super(MainCourante, self).write(values)

    @api.multi
    def get_report(self):
        """Call when button 'Get Report' clicked.
        """

        if self.isAll:

            V = self.getValuesPaymentsCreate()
            self.write({'payments': [[6, False, V['X']]]})
            self.write({'montant_totale': V['Y']})

        else:
            array = []
            total = 0
            state = "('posted')"
            r = self.getResult(state, self.date_debut, self.date_fin)
            for x in r:
                array.append(x[0])
                total += x[1]
            self.write({'payments': [[6, False, array]]})
            self.write({'montant_totale': total})


        payArray = []
        for pym in self.payments:
            payArray.append(pym.id)
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_debut': self.date_debut,
                'date_fin': self.date_fin,
                'payment_ids':payArray,
                'isAll':self.isAll,
                'total':self.montant_totale
            },
        }
        return self.env.ref('gestion_hotel.hotel_stat_main_courante_report_file').report_action(self, data=data)



class RoomsStates(models.Model):
    _name = 'hotel.stat.rooms_states'
    _rec_name = 'date_order'

    date_debut = fields.Date(string="from", required=False, default=datetime.date.today())
    date_fin = fields.Date(string="to", required=False, default=datetime.date.today())
    date_order = fields.Date(string="", required=False, default=datetime.date.today())
    rooms = fields.Many2many("hotel.room", string="Result", )

    available = fields.Boolean(string="Available",  default=True)
    occupied = fields.Boolean(string="Occupied",  default=False)


    @api.onchange('date_debut','date_fin','available','occupied','out')
    def onChangeXXX(self):
        if self.date_debut and self.date_fin:
            if self.date_debut>self.date_fin:
                raise ValidationError(_("The start date should be less than end date"))
        self.forChange()

    def forChange(self):
        for rec in self:
            date1 = rec.date_debut
            date2 = rec.date_fin

            rooms_array = []

            if rec.available == True:

                rooms_array = self.concatArrays(rooms_array, self.getAvailableRooms(date1, date2))
            if rec.occupied : rooms_array = self.concatArrays(rooms_array, self.getOccupiedRooms(date1, date2))


            self.rooms = rooms_array

    def concatArrays(self,R0, R1):
        for i in R1:
            R0.append(i)
        return R0

    def getAvailableRooms(self,date1,date2):

        query = "select Room.* from hotel_room Room where Room.id not in (select hotel_room_id from hotel_reservation_hotel_room_rel,hotel_reservation where ((('{}' between CAST(hotel_reservation.checkin AS date) and CAST(hotel_reservation.checkout AS date)) or ('{}' between CAST(hotel_reservation.checkin AS date) and CAST(hotel_reservation.checkout AS date)))or((CAST(hotel_reservation.checkin AS date) between '{}' and '{}') or (CAST(hotel_reservation.checkout AS date) between '{}' and '{}')))and (hotel_reservation.state = 'consuming')and hotel_reservation_hotel_room_rel.hotel_reservation_id = hotel_reservation.id)".format(
            date1, date2, date1, date2, date1, date2)

        r = self._cr.execute(query)
        r = self._cr.fetchall()

        ids = []
        for i in r:
            if i[6] is None:
                ids.append(i[0])
            elif i[6] > date2:
                ids.append(i[0])

        return ids

    def getOccupiedRooms(self,date1,date2):
        query = "select Room.* from hotel_room Room where Room.id in (select hotel_room_id from hotel_reservation_hotel_room_rel,hotel_reservation where ((('{}' between CAST(hotel_reservation.checkin AS date) and CAST(hotel_reservation.checkout AS date)) or ('{}' between CAST(hotel_reservation.checkin AS date) and CAST(hotel_reservation.checkout AS date)))or((CAST(hotel_reservation.checkin AS date) between '{}' and '{}') or (CAST(hotel_reservation.checkout AS date) between '{}' and '{}')))and (hotel_reservation.state = 'consuming')and hotel_reservation_hotel_room_rel.hotel_reservation_id = hotel_reservation.id)".format(
            date1, date2, date1, date2, date1, date2)

        r = self._cr.execute(query)
        r = self._cr.fetchall()

        ids = []
        for i in r:
                ids.append(i[0])
        return ids

    # def getOutRooms(self,date2):
    #     query = "select * from hotel_room where valid_date_end is not null and valid_date_end<='{}'".format(date2)
    #     r = self._cr.execute(query)
    #     r = self._cr.fetchall()
    #     ids = []
    #
    #     print(date2)
    #     for i in r:
    #             ids.append(i[0])
    #     print(ids)
    #     return ids
