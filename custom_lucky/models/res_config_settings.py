# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from ast import literal_eval

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dead_product_days = fields.Float('Dead Products Days',default=365.0)
    slow_product_days = fields.Float('Slow Products Days',default=90.0)



    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        
        cp_obj = self.env['ir.config_parameter']
        dead_product  = cp_obj.sudo().get_param('dead_product_days') or 0.0 
        slow_product  = cp_obj.sudo().get_param('slow_product_days') or 0.0
        res.update(
            dead_product_days=float(dead_product),
            slow_product_days=float(slow_product) 
        )
        
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        
        cp_obj = self.env['ir.config_parameter']
        cp_obj.sudo().set_param('dead_product_days', self.dead_product_days )
        cp_obj.sudo().set_param('slow_product_days', self.slow_product_days)

