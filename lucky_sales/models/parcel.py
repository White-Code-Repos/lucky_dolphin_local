from odoo import models, fields, api
from odoo.exceptions import UserError
from . import PARCEL_ORDER_TYPES


class LuckyParcel(models.Model):
    _name = "lucky.parcel"

    name = fields.Char(default=lambda s: s.env['ir.sequence'].next_by_code('lucky.parcel'))
    airway_id = fields.Many2one("lucky.airway")
    customs_site = fields.Selection(related="airway_id.customs_site")
    bill_no = fields.Char("AWB")
    weight = fields.Float()
    pieces_no = fields.Integer("Number of pieces")
    flight_no = fields.Char("Flight Number")
    flight_date = fields.Datetime()
    parcel_type = fields.Selection(related='order_id.parcel_type')
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

    @api.onchange("bill_no")
    def get_air_line(self):
        if self.bill_no and len(self.bill_no) >= 3:
            airway = self.env['lucky.airway'].search([('code', '=', self.bill_no[:3])])
            print(airway)
            if airway:
                self.airway_id = airway[0].id

    @api.multi
    def create_po(self):
        # Check if all selected quotations are for the same partner
        if len(set(self.mapped("vendor_id"))) > 1:
            raise UserError("You must select quotations for the same partner")

        purchase_order = self.env['purchase.order'].create({
            'partner_id': self[0].vendor_id.id,
            'order_internal_type': self[0].order_id.order_internal_type,
            'parcel_type': self[0].order_id.parcel_type,
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


class ParcelConfig(models.Model):
    _name = 'lucky.parcel.config'

    product_id = fields.Many2one('product.product')
    sale_price = fields.Float()
    cost_price = fields.Float()
    min_weight = fields.Float()
    max_weight = fields.Float()
    parcel_type = fields.Selection(PARCEL_ORDER_TYPES)


    @api.model
    def get_parcel_config(self, weight, parcel_type):
        parcel_config = self.search([
            ('parcel_type', '=', parcel_type), ('min_weight', '<=', weight),
            '|', ('max_weight', '>=', weight), ('max_weight', '=', 0)
        ])
        if not parcel_config:
            raise UserError('No parcel configurations found for weight: {}'.format(weight))
        return parcel_config[0]
