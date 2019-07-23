from odoo import models, fields, api
from . import ORDER_TYPES, PARCEL_ORDER_TYPES, CREW_ORDER_TYPES, SERVICE_ORDER_TYPES


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    batch_id = fields.Many2one("sale.order.batch", string="Operation#")
    vessel_agent_id = fields.Many2one("res.partner")
    vessel_id = fields.Many2one("lucky.vessel")
    arrival_port_id = fields.Many2one("lucky.port")
    delivery_port_id = fields.Many2one("lucky.port")
    order_internal_type = fields.Selection(ORDER_TYPES, default="normal")
    parcel_type = fields.Selection(PARCEL_ORDER_TYPES)
    crew_type = fields.Selection(CREW_ORDER_TYPES)
    service_type = fields.Selection(SERVICE_ORDER_TYPES)
    eta = fields.Datetime("ETA")
    parcel_ids = fields.One2many("lucky.parcel", 'order_id')
    crew_ids = fields.One2many("lucky.crew", 'order_id')
    service_ids = fields.One2many("lucky.service", 'order_id')
    commit_delivery_date = fields.Datetime("Commitment Delivery Date")
    client_order_ref = fields.Char("INQ/PO")

    @api.model
    def create(self, vals_list):
        order = super().create(vals_list)

        # link order to a previous batch or create a new one
        batch_model = self.env['sale.order.batch']
        batches = batch_model.search([
            ('vessel_id', '=', order.vessel_id.id),
            ('partner_id', '=', order.partner_id.id),
            ('eta', '=', order.eta),
        ])
        if batches:
            order.batch_id = batches[0].id
        else:
            new_batch = batch_model.create({
                'vessel_id': order.vessel_id.id,
                'vessel_agent_id': order.vessel_agent_id.id,
                'eta': order.eta,
                'partner_id': order.partner_id.id,
                'delivery_port_id': order.delivery_port_id.id,
                'arrival_port_id': order.arrival_port_id.id,
                'commit_delivery_date': order.commit_delivery_date,
            })
            order.batch_id = new_batch.id

        # Add Parcels lines into sale order lines
        if order.order_internal_type == 'parcel':
            for parcel in order.parcel_ids:
                pass
        return order

    @api.onchange("eta")
    def change_commit_date(self):
        self.commit_delivery_date = self.eta

    @api.multi
    def create_parcel_order_lines(self):
        for order in self:
            order.order_line.unlink()
            for line in order.parcel_ids:
                parcel_config = self.env['lucky.parcel.config'].get_parcel_config(line.weight, order.parcel_type)
                # Create Sale order line for each parcel line
                self.env['sale.order.line'].create({
                    'name': parcel_config.product_id.name,
                    'product_id': parcel_config.product_id.id,
                    'product_uom_qty': 1,
                    'product_uom': parcel_config.product_id.uom_id.id,
                    'price_unit': parcel_config.sale_price,
                    'order_id': order.id,
                })

    @api.multi
    def create_crew_order_lines(self):
        for order in self:
            order.order_line.unlink()
            configs = order.crew_ids.get_crew_configs(order.crew_type)
            for crew_config, crew_count in configs:
                # Create Sale order line for each parcel line
                self.env['sale.order.line'].create({
                    'name': crew_config.product_id.name,
                    'product_id': crew_config.product_id.id,
                    'product_uom_qty': 1,
                    'product_uom': crew_config.product_id.uom_id.id,
                    'price_unit': crew_config.sale_price * crew_count,
                    'order_id': order.id,
                })

    @api.multi
    def create_service_order_lines(self):
        for order in self:
            order.order_line.unlink()
            for line in order.service_ids:
                service_config = self.env['lucky.service.config'].get_service_config(order.parcel_type)
                # Create Sale order line for each parcel line
                self.env['sale.order.line'].create({
                    'name': service_config.product_id.name,
                    'product_id': service_config.product_id.id,
                    'product_uom_qty': 1,
                    'product_uom': service_config.product_id.uom_id.id,
                    'price_unit': service_config.sale_price,
                    'order_id': order.id,
                })
