from odoo import models, fields, api


class StockPickingInherit(models.Model):
    _inherit = "stock.picking"

    vessel_id = fields.Many2one(related="sale_id.vessel_id")
    delivery_port_id = fields.Many2one(related="sale_id.delivery_port_id")
    client_order_ref = fields.Char(related="sale_id.client_order_ref")
    
    batch_id = fields.Many2one("sale.order.batch", string="Operation#",compute='compute_batch_id')
    commit_delivery_date = fields.Datetime("Commitment Delivery Date",related='batch_id.commit_delivery_date')

    @api.depends('origin')
    def compute_batch_id(self):
        for obj in self:
            saleorder = self.env['sale.order'].search([('name', '=', obj.origin)], limit=1)
            purchaseorder = self.env['purchase.order'].search([('name', '=', obj.origin)], limit=1)
            if saleorder:
                obj.batch_id = obj.saleorder.batch_id.id

            if purchaseorder:
                obj.batch_id = purchaseorder.batch_id.id


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.multi
    def _get_picking(self):
        for rec in self:
            pack_levels = self.env['stock.package_level'].search([('package_id', '=', rec.id)])
            if pack_levels:
                rec.picking_id = pack_levels[0].picking_id
            return False

    picking_id = fields.Many2one('stock.picking', compute=_get_picking)
    vessel_id = fields.Many2one(related="picking_id.vessel_id")
    delivery_port_id = fields.Many2one(related="picking_id.delivery_port_id")
    client_order_ref = fields.Char(related="picking_id.client_order_ref")

