from odoo import http

class send_message(http.Controller):
    @http.route("/list_room/free", type="json", auth="user")
    def send(self,date1,date2):
        res=http.request.env['hotel.reservation'].getFreeRooms(date1,date2)
        #ress = self._cr.execute("select * from res.partner")
        return res

