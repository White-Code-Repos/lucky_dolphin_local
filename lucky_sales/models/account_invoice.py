# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_order_id = fields.Many2one('sale.order',string='Sale Order', compute='_compute_sale_order')

    sale_purchase_id = fields.Many2one('purchase.order',string='Purchase Order', compute='_compute_purchase_order')

    batch_id = fields.Many2one("sale.order.batch", string="Operation#",compute='compute_batch_id')
    eta = fields.Datetime("ETA",related='batch_id.eta')
    vessel_id = fields.Many2one("res.partner", string="Vessel", domain="[('is_vessel', '=', True)]"
                                ,related='batch_id.vessel_id')
    arrival_port_id = fields.Many2one("delivery.carrier",related='batch_id.arrival_port_id')
    delivery_port_id = fields.Many2one("delivery.carrier",related='batch_id.delivery_port_id')
    commit_delivery_date = fields.Datetime("Commitment Delivery Date",related='batch_id.commit_delivery_date',store=True)
    sale_purchase_number = fields.Many2one('purchase.order','Po Number', compute='_compute_sale_purchase_number')

    @api.depends('sale_order_id')
    def _compute_sale_purchase_number(self):
        for invoice in self:
            if invoice.sale_order_id:
                purchaseorder = self.env['purchase.order'].search([('origin', '=', invoice.sale_order_id.name)], limit=1)
                self.sale_purchase_number = purchaseorder.id

    @api.depends('origin')
    def _compute_sale_order(self):
        for invoice in self:
            saleorder = self.env['sale.order'].search([('name', '=', invoice.origin)], limit=1)
            if saleorder:
                invoice.sale_order_id = saleorder.id

    @api.depends('origin')
    def compute_batch_id(self):
        for invoice in self:
            saleorder = self.env['sale.order'].search([('name', '=', invoice.origin)], limit=1)
            purchaseorder = self.env['purchase.order'].search([('name', '=', invoice.origin)], limit=1)
            if saleorder:
                invoice.sale_order_id = saleorder.id
                invoice.batch_id = invoice.sale_order_id.batch_id.id

            if purchaseorder:
                invoice.batch_id = purchaseorder.batch_id.id

