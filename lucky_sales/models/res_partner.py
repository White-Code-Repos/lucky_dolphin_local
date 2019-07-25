from odoo import models, fields


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    vessel_ids = fields.One2many("lucky.vessel", 'partner_id', "Vessels")
    is_vessel = fields.Boolean(string='Is Vessel')
    partner_id = fields.Many2one('res.partner', string='Partner')
    partner_ids = fields.One2many('res.partner','partner_id',string='Vessel Agents')
    code = fields.Char(string='Code')
