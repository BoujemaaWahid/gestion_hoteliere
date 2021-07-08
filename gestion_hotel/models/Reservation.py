
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
from odoo.exceptions import ValidationError, UserError
import pytz
import dateutil.parser

class HotelReservation(models.Model):

    _name = "hotel.reservation"
    _rec_name = "reservation_no"
    _description = "Reservation"
    _order = 'reservation_no desc'
    _inherit = ['mail.thread']
    is_email_cancel_sended = fields.Boolean(string="",  default=False)
    bool_= fields.Boolean(default=True,compute='delay_reservation',)
    showlabel = fields.Boolean(string="showlabel", default=False )
    passager = fields.Boolean(string="Passager",  default=True)
    passager_name = fields.Char(string="Passager name", required=False, )
    passager_cin = fields.Char(string="Cin", required=False, size=8)
    passager_passport = fields.Char(string="Passport", required=False,)
    passager_phone = fields.Char(string="Phone", required=False, )
    passager_email = fields.Char(string="Email", required=False, )
    passager_street = fields.Char(string="Street", required=False, )

    reservation_no = fields.Char(string='Reservation No', readonly=True,)
    services_ids = fields.Many2many("hotel.services",string="Consommation", )
    body = fields.Char(string="Cancel", required=False, default="")
    date_order = fields.Datetime('Date Ordered', readonly=True, required=True,
                                 index=True,
                                 default=(lambda *a: time.strftime(dt)))

    partner_shipping_id = fields.Many2one('res.partner', 'Delivery Address',
                                          readonly=True,
                                          states={'draft':
                                                  [('readonly', False)]},
                                          help="Delivery address"
                                          "for current reservation. ")

    partner_id = fields.Many2one('res.partner', 'Client', readonly=True,
                                 index=True,

                                 states={'draft': [('readonly', False)]})

    partner_order_id = fields.Many2one('res.partner', 'Ordering Contact',
                                       readonly=True,
                                       states={'draft':
                                               [('readonly', False)]},
                                       help="The name and address of the "
                                       "contact that requested the order "
                                       "or quotation.")

    partner_invoice_id = fields.Many2one('res.partner', 'Invoice Address',
                                         readonly=True,
                                         states={'draft':
                                                 [('readonly', False)]},
                                         help="Invoice address for "
                                         "current reservation.")

    checkin = fields.Datetime('Expected-Date-Arrival', required=True,)


    checkout = fields.Datetime('Expected-Date-Departure', required=True,)


    adults = fields.Integer('Adults', readonly=True,
                            states={'draft': [('readonly', False)]},
                            help='List of adults there in guest list. ', default=1)

    children = fields.Integer('Children', readonly=True,
                              states={'draft': [('readonly', False)]},
                              help='Number of children there in guest list.')

    partner_shipping_id = fields.Many2one('res.partner', 'Delivery Address',
                                          readonly=True,
                                          states={'draft':
                                                  [('readonly', False)]},
                                          help="Delivery address"
                                          "for current reservation. ")


    pricelist_id = fields.Many2one('product.pricelist', 'Scheme',
                                    readonly=True,
                                   states={'draft': [('readonly', False)]},
                                   help="Pricelist for current reservation.")

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),('consuming', 'Consuming'),
                              ('cancel', 'Cancel'), ('done', 'Done')],
                             'State', readonly=True,
                             default=lambda *a: 'draft')
    warehouse_id = fields.Many2one('stock.warehouse', 'Hotel', readonly=True,
                                   index=True,
                                   required=True, default=1,
                                   states={'draft': [('readonly', False)]})



    rooms_ids = fields.Many2many(comodel_name="hotel.room", string="Rooms")
    #products_reservations = fields.Many2many(comodel_name="hotel.products.reservations", string="Products")
    products_reservations = fields.One2many(comodel_name="hotel.products.reservations", inverse_name="reservation", string="Products", required=False, )
    invoice_id_reservation = fields.Many2one(comodel_name="account.invoice", string="Invoice", required=False, )
    isFacturated = fields.Boolean(string="",  default=False)
    nightNumber = fields.Integer(string="Nights", required=False)
    showFactureButton = fields.Boolean(string="",  default=False)
    mydummy = fields.Datetime(string="Dummy", required=False,)
    is_mobile = fields.Boolean(string="online",  default=False)
    number_rooms_for_mobile = fields.Integer(string="Rooms number", required=False)
    types_rooms_for_mobile_text = fields.Text(string="Rooms types", required=False)

    # @api.model
    # def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
    #
    #     for node in eview.xpath("//field[@name='user_id']"):
    #
    #             node.set('domain', user_filter)

    def getFreeRooms(self, date1, date2):
        request = "select Room.id from hotel_room Room where Room.id not in (select hotel_room_id from hotel_reservation_hotel_room_rel,hotel_reservation where ('{}' between CAST(hotel_reservation.checkin AS date) and CAST(hotel_reservation.checkout AS date))or('{}' between CAST(hotel_reservation.checkin AS date) and CAST(hotel_reservation.checkout AS date)) and (hotel_reservation.state = 'confirm' or hotel_reservation.state = 'consuming'))".format(date1,date2)

        r = self._cr.execute(request)
        r = self._cr.fetchall()
        rooms = self.env["hotel.room"].search([("id","in",r)])
        jsonRoomsArray = []
        for room_ in rooms:
            jsonRoomsArray.append({"id":room_.id,"name":room_.name})
        return jsonRoomsArray


    @api.model
    def create(self, vals):
        if not vals:
            vals = {}
        vals['showlabel'] = True;
        vals['reservation_no'] = self.env['ir.sequence'].\
            next_by_code('hotel.reservation') or 'New'

        date_time_obj = vals['checkout']
        if type(date_time_obj) is str:
            date_time_obj = datetime.strptime(date_time_obj, '%Y-%m-%d %H:%M:%S')
            vals['mydummy'] =  date_time_obj + timedelta(days=1)

        else:
            x = str(date_time_obj)

            if vals['checkin'].hour == 23 and vals['checkin'].minute > 5:
                vals['checkin'] += timedelta(days=1)
                y = str(vals['checkin'])
                vals['checkin'] = dateutil.parser.parse(y).date()
            vals['mydummy'] = dateutil.parser.parse(x).date()


        if vals['passager'] == True:
            resPartnersPsg = self.env['res.partner']
            vals['partner_id'] = resPartnersPsg.search([('codePassager','=','#F0X009#')]).id






        return super(HotelReservation, self).create(vals)



    @api.multi
    def write(self, values):
        keys = values.keys()
        if 'checkout' in keys:
            date_time_obj = values['checkout']
            date_time_obj = datetime.strptime(date_time_obj, '%Y-%m-%d %H:%M:%S')
            for rec in self:
                rec.mydummy = date_time_obj + timedelta(days=1)
        if 'rooms_ids' in keys:
            self.backToavailableRoomsConfirmed(values['rooms_ids'], self.rooms_ids)

        return super(HotelReservation, self).write(values)

    def backToavailableRoomsConfirmed(self,newRooms, oldRooms):
        self.when_writing_new_rooms(newRooms[0][2])
        rooms = self.env['hotel.room']
        for r1 in oldRooms:
            room = rooms.search([('id', '=', r1.id)])
            if r1 not in newRooms[0][2]:
                room.write({'state':'available'})
                room.write({'isConsuming':False})

        for r2 in newRooms[0][2]:
            for rec in self:
                if rec.state == "confirm" or rec.state == "consuming":
                    room = rooms.search([('id', '=', r2)])
                    room.write({'state': 'occupied'})
                    if rec.state=="consuming":
                        room.write({'isConsuming': True})





    def when_writing_new_rooms(self,rooms_ids):
        for req in self:
            fd = str(dateutil.parser.parse(str(req.checkin)).date())
            ld = str(dateutil.parser.parse(str(req.checkout)).date())
            idsRoomsToCheck = []
            for roomsIdsFormReservation in rooms_ids:
                idsRoomsToCheck.append(roomsIdsFormReservation)
            lengthOfArrayRooms = len(idsRoomsToCheck)

            idsRoomsToCheck = str(tuple(idsRoomsToCheck))
            k = idsRoomsToCheck.rfind(",")

            if k>0 and lengthOfArrayRooms == 1:
                 idsRoomsToCheck = idsRoomsToCheck[:k] + idsRoomsToCheck[k+1:]

            request = "select HRV.reservation_no, HRV.checkout, HRV.checkin from hotel_room HRM, hotel_reservation HRV, hotel_reservation_hotel_room_rel REL where HRM.id = REL.hotel_room_id and HRV.id = REL.hotel_reservation_id and (HRV.state = 'confirm' or HRV.state='consuming') and (((HRV.checkin between '"+fd+"' and '"+ld+"')or (HRV.checkout between '"+fd+"' and '"+ld+"'))or(('"+fd+"' between HRV.checkin and HRV.checkout)or ('"+ld+"' between HRV.checkin and HRV.checkout))) and HRM.id in "+idsRoomsToCheck



            r = self._cr.execute(request)
            r = self._cr.fetchall()
            if len(r) > 0:
                reservationNumber = r[0][0]
                checkoutCustomer = str(dateutil.parser.parse(str(r[0][1])).date())
                checkinCustomer = str(dateutil.parser.parse(str(r[0][2])).date())

                raise ValidationError(_("You are trying to modify a reservation in a date already confirmed for other reservation.\n reservation code in this date : "+reservationNumber+"\n checkin : "+checkinCustomer+"\n checkout : "+checkoutCustomer))
            else:
                for roomsIdsFormReservation in req.rooms_ids:
                    if roomsIdsFormReservation['state'] == "out":
                        raise ValidationError(_("You are trying to modify a reservation in a room out of order :\n room name : "+roomsIdsFormReservation['name']))





    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.partner_invoice_id = False
            self.partner_shipping_id = False
            self.partner_order_id = False
        else:
            addr = self.partner_id.address_get(['delivery', 'invoice',
                                                'contact'])
            self.partner_invoice_id = addr['invoice']
            self.partner_order_id = addr['contact']
            self.partner_shipping_id = addr['delivery']
            self.pricelist_id = self.partner_id.property_product_pricelist.id


    @api.multi
    def confirmed_reservation(self):
        for req in self:
            if len(req.rooms_ids) == 0:
                raise ValidationError(_("Please select rooms to confirm."))

            fd = req.checkin
            ld = req.checkout
            fd = str(dateutil.parser.parse(str(fd)).date())
            ld = str(dateutil.parser.parse(str(ld)).date())
            idsRoomsToCheck = []
            for roomsIdsFormReservation in req.rooms_ids:
                idsRoomsToCheck.append(roomsIdsFormReservation['id'])
            lengthOfArrayRooms = len(idsRoomsToCheck)

            idsRoomsToCheck = str(tuple(idsRoomsToCheck))
            k = idsRoomsToCheck.rfind(",")

            if k>0 and lengthOfArrayRooms == 1:
                 idsRoomsToCheck = idsRoomsToCheck[:k] + idsRoomsToCheck[k+1:]

            request = "select HRV.reservation_no, HRV.checkout, HRV.checkin from hotel_room HRM, hotel_reservation HRV, hotel_reservation_hotel_room_rel REL where HRM.id = REL.hotel_room_id and HRV.id = REL.hotel_reservation_id and HRV.state in ('confirm','consuming') and (((HRV.checkin between '" + fd + "' and '" + ld + "')or (HRV.checkout between '" + fd + "' and '" + ld + "'))or(('" + fd + "' between HRV.checkin and HRV.checkout)or ('" + ld + "' between HRV.checkin and HRV.checkout))) and HRM.id in " + idsRoomsToCheck
            r = self._cr.execute(request)
            r = self._cr.fetchall()
            if len(r) > 0:
                reservationNumber = r[0][0]
                checkoutCustomer = str(dateutil.parser.parse(str(r[0][1])).date())

                raise ValidationError(_("You are trying to confirm a reservation in a date already confirmed for other reservation.\n reservation code in this date : "+reservationNumber+"\n checkout : "+checkoutCustomer))
            else:
                for roomsIdsFormReservation in req.rooms_ids:
                    if roomsIdsFormReservation['state'] == "out":
                        raise ValidationError(_("You are trying to confirm a reservation in a room out of order :\n room name : "+roomsIdsFormReservation['name']))
                self.state = "confirm"

    @api.multi
    def cancel_reservation(self):
        self.state = "cancel"
    @api.multi
    def set_done(self):
        for rec in self:
            for room in rec.rooms_ids:
                changeRoom = self.env['hotel.room'].search([('id', '=', room['id'])])
                changeRoom['state'] = "available"
                changeRoom['isConsuming'] = False;
        self.showFactureButton = True
        self.state = 'done';


    @api.multi
    def consuming_reservation(self):
        for req in self:
            for r in req.rooms_ids:
                changeRoom = self.env['hotel.room'].search([('id', '=', r['id'])])
                changeRoom['state'] = "occupied"
                changeRoom['isConsuming'] = True;
        self.state = "consuming"

    @api.depends('bool_')
    def delay_reservation(self):
        for rec in self:
            if rec["checkin"].date()< datetime.now().date():
                for roomsIds in rec.rooms_ids:
                    if roomsIds['isConsuming'] == False and rec.state != 'cancel' and rec.state != 'done':
                        rec.write({'state':'cancel'})



    def getProductsToInvoiceRooms(self):
        product = []
        for rec in self:
            for r in rec.rooms_ids:
                product.append(r.type.product_id.id)
        countingProducts = []
        while(len(product)>0):
            id = product[0]
            qty = product.count(id)
            product = self.removeOccurance(id,product)
            countingProducts.append({'id':id,'qty':qty})

        return countingProducts

    def getProductsToInvoiceServices(self):
        product = []
        for rec in self:
            for r in rec.services_ids:
                product.append(r.product_id.id)
        countingProducts = []
        while(len(product)>0):
            id = product[0]
            qty = product.count(id)
            product = self.removeOccurance(id,product)
            countingProducts.append({'id':id,'qty':qty})

        return countingProducts


    def getHotelReservationProducts(self):
        products = []
        for rec in self:
            for p in rec.products_reservations:
                products.append({'id':p.product.id,'qty':p.quantity})
        return products


    def createProductsInvoice(self):
        rooms = self.getProductsToInvoiceRooms()
        services = self.getProductsToInvoiceServices()
        productsReserv = self.getHotelReservationProducts()
        Products = []

        for x in rooms:
            Products.append(x)

        for x in services:
            Products.append(x)

        for x in productsReserv:
            Products.append(x)


        InvoiceProducts = []
        nights = None
        for x in self:
            nights = x.nightNumber

        for product in Products:
            pp = self.env['product.product'].search([('id', '=', product['id'])])
            analytic_tag_ids = self.getAnalyticIds(pp)
            invoice_line_tax_ids = self.getInvoiceLineTaxIds(pp)
            setNight = 1

            if pp['typeOfProduct'] == 'to_rooms_categ':
                setNight = nights
            acd = self.env['account.account']
            acd = acd.search([('code','=','707100')])
            if acd:
                acd = acd.id

            else: acd = 630

            obj = {
                'sequence': 10,
                'display_type': False,
                'account_id': acd,
                'quantity': product['qty'],
                'discount': 0,
                'product_id': product['id'],
                'origin': False,
                'is_rounding_line': False,
                'name': pp.name,
                'account_analytic_id': False,
                'analytic_tag_ids': analytic_tag_ids,
                'uom_id': pp.uom_id.id,
                'nightsNumber':setNight,
                'price_unit': pp.lst_price,
                'invoice_line_tax_ids': invoice_line_tax_ids,
                'currency_id': 1
            }

            preparingProduct = [0,'v',obj]
            InvoiceProducts.append(preparingProduct)
        return InvoiceProducts



    def getAnalyticIds(self, pp):
        analytyic = pp.route_ids
        if len(analytyic) == 0:
            return [[6,False,[]]]
        else:
            ids = []
            for x in analytyic:
               ids.append(x.id)
            return [[6,False,ids]]

    def getInvoiceLineTaxIds(self, pp):
        taxes = pp.taxes_id
        if len(taxes) == 0:
            return [[6,False,[]]]
        else:
            ids = []
            for x in taxes:
               ids.append(x.id)
            return [[6,False,ids]]



    def removeOccurance(self, item, product):
        while(product.count(item)>0):
            product.remove(item)
        return product


    @api.multi
    def get_invoice_reservation(self):
        invoiceAccount = self.env['account.invoice']
        invoice_line_ids = self.createProductsInvoice()
        check_out_customer = None
        check_in_customer = None
        for rec in self:
            partner_id = rec.partner_id
            night = rec.nightNumber
            check_in_customer = rec.checkin.date()
            check_out_customer = rec.checkout.date()
            ad = rec.adults
        rec = (invoiceAccount.create({
            'partner_id':partner_id.id,
            'date_invoice': datetime.today().date(),
            'invoice_line_ids':invoice_line_ids,
            'nightsNumber':night,
            'is_reservation':True,
            'reservation_id':self.id,
            'check_in_customer':check_in_customer,
            'check_out_customer':check_out_customer,
            'reservation_adults':ad

        }))
        for cec in self:
            cec.invoice_id_reservation = rec.id
            cec.isFacturated = True
        self.showFactureButton = False
        return rec









    @api.multi
    def set_to_draft_reservation(self):
        for rec in self:
            rec.state = "draft"


    @api.multi
    def send_cancelled_email(self):
        if(self.internet_on() == False):
            raise ValidationError(_("Internet off"))

        msg = None
        for rec in self:
            msg = rec.body
        if not msg:
            raise ValidationError(_("Message is Empty please write a cause"))

        import smtplib, ssl
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        sender_email = "gestionhotel2019@gmail.com"

        password = "0000/0000"




        partnerEmail = None
        for rec in self:
            if rec.passager:
                partnerEmail = rec.passager_email
                break
            else:
                em = rec.partner_id
                partnerEmail = em.email
                break

        if type(partnerEmail) is bool:
            raise ValidationError(_("Client Has No Email"))
        receiver_email = partnerEmail

        message = MIMEMultipart("alternative")
        message["Subject"] = "Annulation de Reservation No :" + rec.reservation_no
        message["From"] = sender_email
        message["To"] = receiver_email
        text = rec.body

        part1 = MIMEText(text, "plain")
        message.attach(part1)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )

        for rec in self:
            rec.is_email_cancel_sended = True

    def internet_on(self):
        import socket
        try:
            socket.create_connection(("www.google.com", 80))
            return True
        except:
            pass
            return False

    @api.multi
    def action_send_reservation_mail(self):
        if(self.internet_on() == False):
            raise ValidationError(_("Internet off"))

        import smtplib
        partnerEmail = None
        for rec in self:
            if rec.passager :
                partnerEmail = rec.passager_email
                break
            else:
                em = rec.partner_id
                partnerEmail = em.email
                break
        if type(partnerEmail) is bool:
            raise ValidationError(_("Client Has No Email"))
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login("gestionhotel2019@gmail.com","0000/0000")
        subject = "Confirmation de Reservation No :"+rec.reservation_no

        d_checkin = str(rec.checkin.date())
        body = "Votre reservation est confirmer pour le date :"+d_checkin

        message = 'Subject: {}\n\n{}'.format(subject,body)

        server.sendmail("gestionhotel2019@gmail.com",partnerEmail,message)
        server.quit()



    @api.constrains('rooms_ids','adults','children')
    def check_reservation_rooms(self):
        for reserv in self:

            cap = 0
            if reserv.adults <= 0:
                raise ValidationError(_('Adults must be more than 0'))

            if ( (len(reserv.rooms_ids) == 0)and(reserv.is_mobile == False) ):
                raise ValidationError(_("Please Select Rooms For Reservation."))

            for room in reserv.rooms_ids:
                cap += room.capacity
                if (reserv.adults + reserv.children ) > cap:
                    raise ValidationError(_('Room Capacity Exceeded \n'
                                          ' Please Select Rooms According to'
                                          ' Members Accomodation.'
                                            ))
            if ( len(reserv.rooms_ids)>0 and reserv.is_mobile==True):
                L = len(reserv.rooms_ids)
                if L != reserv.number_rooms_for_mobile:
                    raise ValidationError(_("Rooms number does not much to client needs"))

                RTS_03 = reserv.types_rooms_for_mobile_text
                RTS_03 = RTS_03.split(",")
                RTS_02 = list()
                for IiI in RTS_03:
                    iId = self.env['hotel.room.type'].search([('name', '=', IiI)])
                    RTS_02.append(iId.id)


                print(RTS_02)
                RTS_01 = list()

                for R in self.rooms_ids:
                    RTS_01.append(R['type'].id)
                print(RTS_01)
                RTS_01.sort()
                RTS_02.sort()
                if (RTS_01 != RTS_02):
                    raise ValidationError(_("Rooms types not satisfied"))




    @api.onchange('checkin','checkout')
    def countNightNumber(self):
        for rec in self:
            if rec.checkout and rec.checkin:
                self.checkIfOutWhenConfirmed(rec.checkout)
                n = (rec.checkout.date() - rec.checkin.date()).days
                rec['nightNumber'] = n


    def checkIfOutWhenConfirmed(self, checkout):
        for rec in self:
            if (rec.state!="draft") and (checkout.date() < datetime.today().date()):
                raise ValidationError(_("Checkout date can't be less than today"))


    @api.constrains('checkin', 'checkout')
    def check_in_out_dates(self):
        """
        When date_order is less then check-in date or
        Checkout date should be greater than the check-in date.
        """
        if self.checkout and self.checkin:
            if self.checkin.date() < self.date_order.date():
                raise ValidationError(_('Check-in date should be greater than \
                                         the current date.'))
            if self.checkout < self.checkin:
                raise ValidationError(_('Check-out date should be greater \
                                         than Check-in date.'))

class QuickRoomReservation(models.TransientModel):
    _name = 'quick.room.reservation'
    _description = 'Quick Room Reservation'
    passager = fields.Boolean(string="Passager",  default=True)
    passager_name = fields.Char(string="Name", required=False, )
    passager_cin = fields.Char(string="Cin", required=False, size=8)
    passager_passport = fields.Char(string="Passport", required=False,)
    passager_phone = fields.Char(string="Phone", required=False, )
    passager_email = fields.Char(string="Email", required=False, )
    passager_street = fields.Char(string="Street", required=False, )

    partner_id = fields.Many2one('res.partner', string="Customer",
                                 )
    check_in = fields.Datetime('Check In', required=True)
    check_out = fields.Datetime('Check Out', required=True)
    room_id = fields.Many2one('hotel.room', 'Room', required=True)
    # warehouse_id = fields.Many2one('stock.warehouse', 'Hotel', required=False)
    pricelist_id = fields.Many2one('product.pricelist', 'pricelist')
    partner_invoice_id = fields.Many2one('res.partner', 'Invoice Address',
                                         )
    partner_order_id = fields.Many2one('res.partner', 'Ordering Contact',
                                       )
    partner_shipping_id = fields.Many2one('res.partner', 'Delivery Address',
                                          )
    adults = fields.Integer('Adults', size=64)
    children = fields.Integer('Children')
    nightNumber = fields.Integer(string="Nights", required=False)


    @api.onchange('check_out',"check_in")
    def on_change_check_out(self):
        if self.check_out and self.check_in:
            if self.check_out < self.check_in:
                raise ValidationError(_('Checkout date should be greater \
                                         than Checkin date.'))
            self.nightNumber =(self.check_out.date()-self.check_in.date()).days


    @api.onchange('partner_id')
    def onchange_partner_id_res(self):
        if not self.partner_id:
            self.partner_invoice_id = False
            self.partner_shipping_id = False
            self.partner_order_id = False
        else:
            addr = self.partner_id.address_get(['delivery', 'invoice',
                                                'contact'])
            self.partner_invoice_id = addr['invoice']
            self.partner_order_id = addr['contact']
            self.partner_shipping_id = addr['delivery']
            self.pricelist_id = self.partner_id.property_product_pricelist.id

    @api.model
    def default_get(self, fields):
        if self._context is None:
            self._context = {}
        res = super(QuickRoomReservation, self).default_get(fields)
        if self._context:
            keys = self._context.keys()

            if 'date' in keys:
                res.update({'check_in': self._context['date']})

            if 'room_id' in keys:
                roomid = self._context['room_id']
                res.update({'room_id': int(roomid)})
        return res
    @api.multi
    def room_reserve(self):
        rec = {}
        hotel_res_obj = self.env['hotel.reservation']
        for res in self:
            if(self.passager):
                rec = (hotel_res_obj.create
                       ({'passager': res.passager,
                         'passager_name': res.passager_name,
                         'passager_cin': res.passager_cin,
                         'passager_passport': res.passager_passport,
                         'checkin': res.check_in,
                         'checkout': res.check_out,
                         'passager_phone': res.passager_phone,
                         'passager_email':res.passager_email,
                         'passager_street':res.passager_street,
                         'adults': res.adults,
                         'children':res.children,
                         'rooms_ids': [[6, False, [res.room_id.id]]],
                         'nightNumber':res.nightNumber,
                         }))
            else:
                rec = (hotel_res_obj.create
                       ({'partner_id': res.partner_id.id,
                         'passager': res.passager,
                         'partner_invoice_id': res.partner_invoice_id.id,
                         'partner_order_id': res.partner_order_id.id,
                         'partner_shipping_id': res.partner_shipping_id.id,
                         'checkin': res.check_in,
                         'checkout': res.check_out,
                         'pricelist_id': res.pricelist_id.id,
                         'adults': res.adults,
                         'children':res.children,
                         'rooms_ids': [[6, False, [res.room_id.id]]],
                         'nightNumber': res.nightNumber,
                         }))
        return rec;




class InvoiceRegle(models.Model):
    _inherit="account.payment"
    is_hotel_reservation = fields.Boolean(string="",  default=False)
    reservation_hotel_id = fields.Many2one(comodel_name="hotel.reservation", string="Reservation no", required=False, )
    def action_validate_invoice_payment(self):

        if any(len(record.invoice_ids) != 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        for record in self:
            print("Invoice : ", record.invoice_ids,"    Self : ",self.id)
            rev = self.env['hotel.reservation']
            rev = rev.search([('invoice_id_reservation','=',record.invoice_ids.id)])
            if len(rev) > 0:
                record.reservation_hotel_id = rev
                record.is_hotel_reservation = True
        return self.post()

    @api.model
    def create(self, vals):
        rslt = super(InvoiceRegle, self).create(vals)
        # When a payment is created by the multi payments wizard in 'multi' mode,
        # its partner_bank_account_id will never be displayed, and hence stay empty,
        # even if the payment method requires it. This condition ensures we set
        # the first (and thus most prioritary) account of the partner in this field
        # in that situation.
        self.createRegionCa(vals['partner_id'],vals['payment_date'],round(vals['amount'],2))
        self.createClientCa(vals['partner_id'],vals['payment_date'],round(vals['amount'],2))
        self.createMonthstCa(vals['payment_date'],round(vals['amount'],2))
        self.createSaisonstCa(vals['payment_date'],round(vals['amount'],2))
        if not rslt.partner_bank_account_id and rslt.show_partner_bank_account and rslt.partner_id.bank_ids:
            rslt.partner_bank_account_id = rslt.partner_id.bank_ids[0]
        return rslt

    def createRegionCa(self, partner_id, date, inc):
        date = datetime.strptime(date, "%Y-%m-%d")
        year = date.year
        region_ca = self.env['hotel.region_ca_c']
        caf = self.env['hotel.chiffre_affaire']
        res_partner = self.env['res.partner']
        Cca = caf.account_payment_regions()

        yearsCa = Cca['tab']['header'][1:len(Cca['tab']['header']) - 1]
        bodyCa = Cca['tab']['body'][0:len(Cca['tab']['body']) - 1]
        r = self._cr.execute("delete from hotel_region_ca_c")

        list_name_city = list()
        for bca in bodyCa:
            list_name_city.append(bca['name'])

        ppp = self.env['res.partner'].search([("id", "=", partner_id)])
        if ppp['city'] not in list_name_city:
            bodyCa.append({'name': ppp['city'], 'values': [0, 0]})

        for yca in range(0, len(yearsCa)):
            for bca in bodyCa:
                amount = bca['values'][yca]
                region_name = res_partner.search([("id","=",partner_id)])
                region_name = region_name['city']
                if (year == int(yearsCa[yca]) and region_name == bca['name']):
                    amount += inc
                d = {"name": bca['name'], "amount": amount, "year": int(yearsCa[yca])}
                region_ca.create(d)

    def createClientCa(self,partner_id,date,inc):
        date = datetime.strptime(date, "%Y-%m-%d")
        year = date.year
        clients_ca = self.env['hotel.client_ca_c']
        caf = self.env['hotel.chiffre_affaire']
        Cca = caf.account_payments_clients()

        yearsCa = Cca['tab']['header'][1:len(Cca['tab']['header']) - 1]
        bodyCa = Cca['tab']['body'][0:len(Cca['tab']['body']) - 1]
        r = self._cr.execute("delete from hotel_client_ca_c")

        list_ids_partners = list()
        for bca in bodyCa:
            list_ids_partners.append(bca['id'])
        if partner_id not in list_ids_partners:
            ppp = self.env['res.partner'].search([("id","=",partner_id)])
            bodyCa.append({'name':ppp['name'],'id':partner_id,'values':[0,0]})

        for yca in range(0, len(yearsCa)):
            for bca in bodyCa:
                amount = bca['values'][yca]
                if (year == int(yearsCa[yca]) and partner_id == bca['id']):
                    amount+=inc
                d = {"name": bca['name'], "amount": amount, "year": int(yearsCa[yca])}
                clients_ca.create(d)


    def createMonthstCa(self,date,inc):
        date = datetime.strptime(date, "%Y-%m-%d")
        year = date.year
        import datetime as DRT
        month = DRT.date(1900, date.month, 1).strftime('%B')
        months_ca = self.env['hotel.months_ca_c']
        caf = self.env['hotel.chiffre_affaire']
        Mca = caf.account_paymetns_months()

        yearsCa = Mca['tab']['header'][1:len(Mca['tab']['header']) - 1]
        bodyCa = Mca['tab']['body'][0:len(Mca['tab']['body']) - 1]
        r = self._cr.execute("delete from hotel_months_ca_c")
        for yca in range(0, len(yearsCa)):
             for bca in bodyCa:
                amount = bca['values'][yca]
                if (year == int(yearsCa[yca]) and bca['name'] == month):
                    amount+=inc
                d = {"name": bca['name'], "amount": amount, "year": int(yearsCa[yca])}
                months_ca.create(d)


    def createSaisonstCa(self,date,inc):
        saisons = {"Winter": [12, 1, 2], "Spring": [5, 4, 3], 'Summer': [8, 7, 6], 'Autumn': [11, 10, 9]}
        date = datetime.strptime(date, "%Y-%m-%d")
        year = date.year
        month = date.month
        saison = None

        if month in saisons['Winter']:
            saison="Winter"
        elif month in saisons['Spring']:
            saison="Spring"
        elif month in saisons['Summer']:
            saison="Summer"
        else:
            saison="Autumn"

        saisons_ca = self.env['hotel.saisons_ca_c']
        caf = self.env['hotel.chiffre_affaire']
        Sca = caf.account_paymetns_saisons()

        yearsCa = Sca['tab']['header'][1:len(Sca['tab']['header']) - 1]
        bodyCa = Sca['tab']['body'][0:len(Sca['tab']['body']) - 1]
        r = self._cr.execute("delete from hotel_saisons_ca_c")
        for yca in range(0, len(yearsCa)):
             for bca in bodyCa:
                amount = bca['values'][yca]
                if (year == int(yearsCa[yca]) and bca['name'] == saison):
                    amount+=inc
                d = {"name": bca['name'], "amount": amount, "year": int(yearsCa[yca])}
                saisons_ca.create(d)

# {
# 	"jsonrpc": "2.0",
# 	"method": "call",
# 	"params": {"date1":"2019-02-12","date2":"2019-02-15"}
# }
