# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    qty_applied_on = fields.Selection(
        [('in_stock', 'In Stock'), ('out_of_stock', 'Out Of Stock'), ('other', 'Other'), ],
        string="Apply On", default='other', required=True, )

    updated_range = fields.Integer(string='Updated Range')
    product_pricelist_line_ids = fields.One2many('product.pricelist.line', 'pricelist_id', string='Pricelist Lines')

    @api.multi
    @api.constrains('qty_applied_on', 'updated_range')
    def check_updated_range_value(self):
        for pricelist in self:
            if pricelist.qty_applied_on and pricelist.updated_range <= 0:
                raise ValidationError(_('Updated range must be greater than zero.'))
