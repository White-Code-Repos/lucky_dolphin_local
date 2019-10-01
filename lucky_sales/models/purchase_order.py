from odoo import models, fields, api
from . import ORDER_TYPES, PARCEL_ORDER_TYPES, CREW_ORDER_TYPES, SERVICE_ORDER_TYPES


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"
    order_internal_type = fields.Selection(ORDER_TYPES, default="normal")

    parcel_type = fields.Selection(PARCEL_ORDER_TYPES)
    crew_type = fields.Selection(CREW_ORDER_TYPES)
    service_type = fields.Selection(SERVICE_ORDER_TYPES)

    parcel_ids = fields.One2many("lucky.parcel", 'purchase_order_id')
    crew_ids = fields.One2many("lucky.crew", 'purchase_order_id')
    service_ids = fields.One2many("lucky.service", 'purchase_order_id')

    @api.multi
    def create_parcel_order_lines(self):
        for order in self:
            order.order_line.unlink()
            for line in order.parcel_ids:
                parcel_config = self.env['lucky.parcel.config'].get_parcel_config(line.weight, order.parcel_type)
                # Create Sale order line for each parcel line
                self.env['purchase.order.line'].create({
                    'name': parcel_config.product_id.name,
                    'product_id': parcel_config.product_id.id,
                    'product_qty': 1,
                    'product_uom': parcel_config.product_id.uom_id.id,
                    'price_unit': parcel_config.cost_price,
                    'order_id': order.id,
                    'date_planned': order.date_planned,
                })

    @api.multi
    def create_crew_order_lines(self):
        for order in self:
            order.order_line.unlink()
            configs = order.crew_ids.get_crew_configs(order.crew_type)
            for crew_config, crew_count in configs:
                # Create Purchase order line for each parcel line
                self.env['purchase.order.line'].create({
                    'name': crew_config.product_id.name,
                    'product_id': crew_config.product_id.id,
                    'product_qty': 1,
                    'product_uom': crew_config.product_id.uom_id.id,
                    'price_unit': crew_config.cost_price * crew_count,
                    'order_id': order.id,
                    'date_planned': order.date_planned,
                })

    @api.multi
    def create_service_order_lines(self):
        for order in self:
            order.order_line.unlink()
            for line in order.service_ids:
                service_config = self.env['lucky.parcel.config'].get_service_config(order.service_type)
                # Create Sale order line for each service line
                self.env['purchase.order.line'].create({
                    'name': service_config.product_id.name,
                    'product_id': service_config.product_id.id,
                    'product_qty': 1,
                    'product_uom': service_config.product_id.uom_id.id,
                    'price_unit': service_config.cost_price,
                    'order_id': order.id,
                    'date_planned': order.date_planned,
                })

class PurchaseOrderListing(models.Model):
    _name = 'purchase.order.listing'
    _rec_name = 'purchase_order_id'

    purchase_order_id = fields.Many2one('purchase.order')
    sale_id = fields.Many2one('sale.order', string="Sale Order")

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def create(self, vals):
        res = super(PurchaseOrderLine, self).create(vals)
        dropship = self.env.ref('stock_dropshipping.picking_type_dropship').id
        if res.order_id.origin and dropship in res.product_id.route_ids.ids:
            res.sale_order_id.purchase_order_ids = [(0, 0, {'purchase_order_id': res.order_id.id})]
        return res