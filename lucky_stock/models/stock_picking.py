from odoo import models, fields, api


class StockPickingInherit(models.Model):
    _inherit = "stock.picking"

    vessel_id = fields.Many2one(related="sale_id.vessel_id")
    delivery_port_id = fields.Many2one(related="sale_id.delivery_port_id")
    client_order_ref = fields.Char(related="sale_id.client_order_ref")


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

