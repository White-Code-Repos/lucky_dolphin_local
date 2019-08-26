# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def send_multiple_xls_quotations(self):
        # Check if all selected quotations are for the same partner
        if len(set(self.mapped("partner_id"))) > 1:
            raise UserError("You must select quotations for the same partner")

        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('lucky_sale_reports',
                                                             'multi_quotations_sender_xls_template')[1]
        except ValueError:
            template_id = False
        ctx = {
            'xls_multi_quotations_ids': self.ids,
            'default_model': 'sale.order',
            'default_res_id': self[0].id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }
