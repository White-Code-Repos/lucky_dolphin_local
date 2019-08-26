from odoo import models, fields, api
from odoo.exceptions import UserError
from . import CREW_ORDER_TYPES


class LuckyCrew(models.Model):
    _name = "lucky.crew"

    name = fields.Char(default=lambda s: s.env['ir.sequence'].next_by_code('lucky.crew'))
    crew_name = fields.Char("Full Name")
    ticket_no = fields.Char()
    passport = fields.Char()
    airway_id = fields.Many2one("lucky.airway", "Carrier")
    nationality = fields.Many2one('res.country')
    flight_no = fields.Char("Flight Number")
    flight_date = fields.Datetime()
    crew_type = fields.Selection(related='order_id.crew_type')
    vessel_id = fields.Many2one(related='order_id.vessel_id')
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
            'crew_type': self[0].order_id.crew_type,
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
    def get_crew_configs(self, crew_type):
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


class CrewConfig(models.Model):
    _name = 'lucky.crew.config'

    product_id = fields.Many2one('product.product')
    sale_price = fields.Float()
    cost_price = fields.Float()
    count = fields.Integer()
    crew_type = fields.Selection(CREW_ORDER_TYPES)

    @api.model
    def get_crew_config(self, count, crew_type):
        crew_config = self.search([('crew_type', '=', crew_type), ('count', '=', count)])
        if not crew_config:
            # There should be a configuration with empty count to handle crews > max number
            crew_config = self.search([('crew_type', '=', crew_type), ('count', '=', 0)])
            if not crew_config:
                raise UserError('No crew configurations found for count: {}'.format(count))
        return crew_config[0]
