from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    vessel_ids = fields.One2many("lucky.vessel", 'partner_id', "Vessels")
    is_vessel = fields.Boolean(string='Is Vessel')
    partner_id = fields.Many2one('res.partner', string='Partner')
    partner_ids = fields.One2many('res.partner','partner_id',string='Vessel Agents')
    code = fields.Char(string='Code')
    code_2 = fields.Char(string='Code')
    is_agent = fields.Boolean(string="Is Agent")
    fax_number = fields.Char(string='Fax Number')
    phone2 = fields.Char(string="Phone 2")
    phone3 = fields.Char(string="Phone 3")
    phone4 = fields.Char(string="Phone 4")
    port = fields.Char(string="Port")
    egypt_port_id = fields.Many2one('egypt.ports',string='Egypt Port')
    is_courier = fields.Boolean(string='Is Courier')
    customs_site = fields.Char(string='Customs Site')
    response_time = fields.Char(string='Response Time')
    price_computation = fields.Char(string='Price Computation')
    quality_of_service = fields.Char(string='Quality of Service')

    @api.model
    def create(self, vals):
        if vals.get('supplier', False):
            if not (self.user_has_groups('purchase.group_purchase_manager') or self.user_has_groups('purchase.group_purchase_user')):
                raise UserError(_("You are not allowed to add a vendor, only purchase team can add vendors."))
        return super(ResPartnerInherit, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('supplier', False):
            if not (self.user_has_groups('purchase.group_purchase_manager') or self.user_has_groups('purchase.group_purchase_user')):
                raise UserError(_("You are not allowed to add a vendor, only purchase team can add vendors."))
        return super(ResPartnerInherit, self).write(vals)