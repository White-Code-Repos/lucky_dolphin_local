from odoo import http,_
from odoo.http import request
import base64 
import json
import werkzeug



class file_download(http.Controller):
    @http.route(['/opening/delivery/<model("sale.order.batch"):opening>'], type='http', auth="public",website=True)
    def opening_delivery(self, opening, **post):
        filename="Delivery_Slip.pdf"
        pdf = ''
        delivery_slip_ids = []
        if opening.order_ids:
            try:
                ids = opening.order_ids.mapped('picking_ids').mapped('id')
                pdf = request.env.ref('lucky_dolphin_stock_reports.action_report_delivery').sudo().render_qweb_pdf(ids)[0]
                pdfhttpheaders = [
                    ('Content-Type', 'application/pdf'),
                    ('Content-Length', len(pdf)),('Content-Disposition', 'attachment; filename=' + filename + ';')
            ]
            except:
                raise werkzeug.exceptions.NotFound("There is no product for the linked sale order")
        else:
            raise werkzeug.exceptions.NotFound("No Delivery Slip found for linked sale!") 
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/opening/invoice/<model("sale.order.batch"):opening>'], type='http', auth="public",website=True)
    def opening_invoice(self, opening, **post):
        filename="Invoice.pdf"
        if opening.order_ids:

            # for sale_order_id in opening.order_ids:
            #     if sale_order_id.invoice_ids:
            ids = opening.order_ids.filtered(lambda r: r.print_invoice == True).mapped('invoice_ids').mapped('id')
            if ids:
                pdf = request.env.ref('account.account_invoices').sudo().render_qweb_pdf(ids)[0]
                pdfhttpheaders = [
                    ('Content-Type', 'application/pdf'),
                    ('Content-Length', len(pdf)),('Content-Disposition', 'attachment; filename=' + filename + ';')
                ]
                return request.make_response(pdf, headers=pdfhttpheaders)
            else:
                raise werkzeug.exceptions.NotFound("No Invoices linked to the sale orders")
        else:
            raise werkzeug.exceptions.NotFound("No Account Invoice found for linked sale!") 
