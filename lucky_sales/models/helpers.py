from odoo import models, fields


class LuckyAirway(models.Model):
    _name = "lucky.airway"

    name = fields.Char(required=True)
    code = fields.Char()
    customs_site = fields.Selection([
        ('CAI', "Village"),
        ('AF', "Air France"),
        ('LU', "Lufthansa"),
    ])


class LuckyVessel(models.Model):
    _name = "lucky.vessel"

    partner_id = fields.Many2one("res.partner")
    name = fields.Char()


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    vessel_ids = fields.One2many("lucky.vessel", 'partner_id', "Vessels")


class LuckyPort(models.Model):
    _name = "lucky.port"

    name = fields.Char()
