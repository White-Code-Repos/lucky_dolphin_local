from odoo import models, fields, api
from odoo.exceptions import UserError
from . import SERVICE_ORDER_TYPES


class LuckyService(models.Model):
    _name = "lucky.service"

    name = fields.Char(default=lambda s: s.env['ir.sequence'].next_by_code('lucky.service'))
    service_type = fields.Selection(related='order_id.service_type')
    vessel_id = fields.Many2one(related='order_id.vessel_id')
    report = fields.Text()
    eta = fields.Datetime(related='order_id.eta')
    delivery_port_id = fields.Many2one(related='order_id.delivery_port_id')
    arrival_port_id = fields.Many2one(related='order_id.arrival_port_id')
    partner_id = fields.Many2one(related='order_id.partner_id')
    order_id = fields.Many2one('sale.order')
    purchase_order_id = fields.Many2one('purchase.order')
    vendor_id = fields.Many2one('res.partner')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('ready', 'Ready'),
        ('done', 'Done'),
    ], default="draft")

    @api.multi
    def create_po(self):
        # Check if all selected quotations are for the same partner
        if len(set(self.mapped("vendor_id"))) > 1:
            raise UserError("You must select quotations for the same partner")

        purchase_order = self.env['purchase.order'].create({
            'partner_id': self[0].vendor_id.id,
            'order_internal_type': self[0].order_id.order_internal_type,
            'service_type': self[0].order_id.service_type,
        })
        self.write({
            'purchase_order_id': purchase_order.id
        })

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'target': 'current',
            'res_id': purchase_order.id,
        }

    @api.multi
    def get_service_configs(self, service_type):
        # Aggregate crew who have same flight no and same flight date
        crew_aggregation = {}
        for line in self:
            key = (line.flight_no, line.flight_date)
            crew_aggregation[key] = crew_aggregation.get(key, 0) + 1
        crew_configs = []
        for crew_count in crew_aggregation.values():
            crew_config = self.env['lucky.crew.config'].get_crew_config(crew_count, crew_type)
            crew_configs.append((crew_config, crew_count))
        return crew_configs


class ServiceConfig(models.Model):
    _name = 'lucky.service.config'

    product_id = fields.Many2one('product.product')
    sale_price = fields.Float()
    cost_price = fields.Float()
    service_type = fields.Selection(SERVICE_ORDER_TYPES)

    @api.model
    def get_service_config(self, service_type):
        service_config = self.search([('service_type', '=', service_type)])
        if not service_config:
            raise UserError('No crew configurations found for Service Type: {}'.format(service_type))
        return service_config[0]
