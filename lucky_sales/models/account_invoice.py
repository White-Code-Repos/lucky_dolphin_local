# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_order_id = fields.Many2one('sale.order',string='Sale Order', compute='_compute_sale_order')

    sale_purchase_id = fields.Many2one('purchase.order',string='Purchase Order', compute='_compute_purchase_order')

    eta = fields.Datetime("ETA",related='sale_purchase_id.eta')
    batch_id = fields.Many2one("sale.order.batch", string="Operation#",related='sale_purchase_id.batch_id')
    vessel_id = fields.Many2one("res.partner", string="Vessel", domain="[('is_vessel', '=', True)]"
                                ,related='sale_purchase_id.vessel_id')
    arrival_port_id = fields.Many2one("delivery.carrier",related='sale_purchase_id.arrival_port_id')
    delivery_port_id = fields.Many2one("delivery.carrier",related='sale_purchase_id.delivery_port_id')

    @api.depends('origin')
    def _compute_sale_order(self):
        for invoice in self:
            saleorder = self.env['sale.order'].search([('name', '=', invoice.origin)], limit=1)
            if saleorder:
                invoice.sale_order_id = saleorder.id

    @api.depends('origin')
    def _compute_purchase_order(self):
        for invoice in self:
            purchaseorder = self.env['purchase.order'].search([('name', '=', invoice.origin)], limit=1)
            if purchaseorder:
                invoice.sale_purchase_id = purchaseorder.id