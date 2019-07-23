from odoo import models, fields


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    vessel_ids = fields.One2many("lucky.vessel", 'partner_id', "Vessels")
