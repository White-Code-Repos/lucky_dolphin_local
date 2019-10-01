# -*- coding: utf-8 -*-
import base64
from odoo import models, api


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    @api.multi
    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        res = super(MailComposeMessage, self).onchange_template_id(template_id, composition_mode, model, res_id)
        if not self.env.context.get("xls_multi_quotations_ids"):
            return res

        sale_order_objects = self.env['sale.order'].browse(self.env.context['xls_multi_quotations_ids'])

        record_type = 'Order'
        # Here we assume that first record type is the same type for all other records
        if sale_order_objects[0].state not in ('draft', 'sent'):
            record_type = "Quotation"

        attachments = []
        records_names = []
        client_ref_names = []
        for record in sale_order_objects:
            quotation_xls = \
                self.env.ref('lucky_sale_reports.sale_order_xls_report').sudo().render_xlsx([record.id], data=False)[0]
            attachment = {
                'name': "{}.xls".format((record.name or '').replace('/', '_')),
                'datas': base64.encodebytes(quotation_xls),
                'datas_fname': "{}.xls".format((record.name or '').replace('/', '_')),
                'res_model': 'sale.order',
                'res_id': record.id,
                'type': 'binary'
            }
            attachments.append(self.env['ir.attachment'].create(attachment))
            records_names.append((record.name or 'n/a').replace("/", "_"))
            client_ref_names.append((record.client_order_ref or 'n/a').replace("/", "_"))

        res['value']['attachment_ids'] = [(4, attachment.id) for attachment in attachments]

        res['value']['subject'] = "{company_name} your RFQs {client_refs} => {our_refs}".format(
            company_name=sale_order_objects[0].company_id.name,
            type=record_type,
            our_refs=", ".join(records_names),
            client_refs=", ".join(client_ref_names)
        )
        return res

    def action_send_mail(self):
        res = super(MailComposeMessage, self).send_mail()
        if not self.env.context.get("xls_multi_quotations_ids"):
            return res
        sale_order_objects = self.env['sale.order'].browse(self.env.context['xls_multi_quotations_ids'])
        for order in sale_order_objects:
            if order.state == 'draft':
                order.state = "sent"
        return res
