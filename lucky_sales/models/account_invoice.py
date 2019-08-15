# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_order_id = fields.Many2one('sale.order',string='Sale Order', compute='_compute_sale_order')

    @api.depends('origin')
    def _compute_sale_order(self):
        for invoice in self:
            saleorder = self.env['sale.order'].search([('name', '=', invoice.origin)], limit=1)
            if saleorder:
                invoice.sale_order_id = saleorder.id