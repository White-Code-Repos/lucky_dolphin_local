import base64

from odoo import models, api


class MailComposeMessageInherit(models.TransientModel):
    _inherit = "mail.compose.message"

    @api.multi
    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        res = super(MailComposeMessageInherit, self).onchange_template_id(
            template_id, composition_mode, model, res_id)
        if not self.env.context.get("multi_quotations_ids"):
            return res

        quotations = self.env['sale.order'].browse(self.env.context['multi_quotations_ids'])
        record_type = 'Order'
        # Here we assume that first record type is the same type for all other records
        if quotations[0].state not in ('draft', 'sent'):
            record_type = "Quotation"

        attachments = []
        records_names = []
        client_ref_names = []
        for record in quotations:
            quotation_pdf = self.env.ref('sale.action_report_saleorder').sudo().render_qweb_pdf([record.id])[0]
            attachment = {
                'name': "{}.pdf".format((record.name or '').replace('/', '_')),
                'datas': base64.encodebytes(quotation_pdf),
                'datas_fname': "{}.pdf".format((record.name or '').replace('/', '_')),
                'res_model': 'sale.order',
                'res_id': record.id,
                'type': 'binary'
            }
            attachments.append(self.env['ir.attachment'].create(attachment))
            records_names.append((record.name or 'n/a').replace("/", "_"))
            client_ref_names.append((record.client_order_ref or 'n/a').replace("/", "_"))

        res['value']['attachment_ids'] = [(4, attachment.id) for attachment in attachments]

        res['value']['subject'] = "{company_name} your RFQs {client_refs} => {our_refs}".format(
            company_name=quotations[0].company_id.name,
            type=record_type,
            our_refs=", ".join(records_names),
            client_refs=", ".join(client_ref_names)
        )
        return res

    def action_send_mail(self):
        res = super(MailComposeMessageInherit, self).send_mail()
        if not self.env.context.get("multi_quotations_ids"):
            return res
        quotations = self.env['sale.order'].browse(self.env.context['multi_quotations_ids'])
        for quotation in quotations:
            if quotation.state == 'draft':
                quotation.state = "sent"
        return res
