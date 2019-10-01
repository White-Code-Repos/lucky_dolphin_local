import odoo
import odoo.http as http
from odoo import fields, http, SUPERUSER_ID,_
from odoo.http import request


class PopupController(odoo.http.Controller):

    @http.route('/popup_notifications/notify', type='json', auth="none")
    def notify(self):
        user_id = request.session.uid
        context = dict(request.context)
        search_notif_ids = request.env['popup.notification'].sudo().search(
            [('partner_ids', '=', user_id), ('status', '!=', 'shown')])
        return search_notif_ids.get_notifications()

    @http.route('/popup_notifications/notify_ack', type='json', auth="none")
    def notify_ack(self, notif_id, type='json'):
        notif_obj = request.env['popup.notification'].sudo().browse([notif_id])
        if notif_obj:
            notif_obj.status = 'shown'


    @http.route('/web/action/load', type='json', auth="none")
    def notify_sale(self, sale_id, type='json'):
        if sale_id:
            print ("MMMMMMMMMMMMMMMMMMM", sale_id)
            return {
		 'type': 'ir.actions.act_window',

		'tag': 'reload',               

		 'name': _('Quotations'),               

		 'res_model': 'sale.order',               

		 'view_type': 'form',               

		 'view_mode': 'form',               

		 'view_id': sale_id,               

		 'target': 'new',               

                 }


