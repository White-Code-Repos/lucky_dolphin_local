from odoo import models, fields, api


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    batch_id = fields.Many2one("sale.order.batch", string="Operation#")
    commit_delivery_date = fields.Datetime("Commitment Delivery Date",related='batch_id.commit_delivery_date',store=True)
    vessel_id = fields.Many2one("res.partner", string="Vessel", domain="[('is_vessel', '=', True)]",related='batch_id.vessel_id',store=True)
    eta = fields.Datetime("ETA",related='batch_id.eta',store=True)
    arrival_port_id = fields.Many2one("delivery.carrier",related='batch_id.arrival_port_id',store=True)
    delivery_port_id = fields.Many2one("delivery.carrier",related='batch_id.delivery_port_id',store=True)