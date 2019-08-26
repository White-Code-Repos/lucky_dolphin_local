# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ProductPricelist(models.Model):
    _name = 'product.pricelist.line'
    _description = 'Pricelist Line'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, ondelete='cascade')
    applied_on = fields.Selection([
        ('product_category', 'Product Category'),
        ('product', 'Product'), ], string="Apply On",
        default='product_category', required=True, )
    name = fields.Char(string='Name', compute='get_pricelist_line_name', required=True)
    product_id = fields.Many2one('product.product', string='Product')
    categ_id = fields.Many2one('product.category', string='Product Category')
    percentage_from = fields.Float(string='Percentage From', required=True)
    percentage_to = fields.Float(string='Percentage To', required=True)
    apply_percentage = fields.Float(string='Apply Percentage', required=True)
    apply_sign = fields.Selection([
        ('minus', '-'), ('plus', '+'), ], string="Sign", default='plus', required=True, )

    @api.multi
    @api.depends('categ_id', 'product_id', 'applied_on')
    def get_pricelist_line_name(self):
        for line in self:
            if line.categ_id and line.applied_on == 'product_category':
                line.name = _("Category: %s") % (line.categ_id.name)
            elif line.product_id and line.applied_on == 'product':
                line.name = line.product_id.name

    @api.onchange('applied_on')
    def onchange_applied_on(self):
        for line in self:
            if line.applied_on != 'product':
                line.product_id = False
            if line.applied_on != 'product_category':
                line.categ_id = False

    @api.constrains('percentage_from', 'percentage_to')
    def check_percentages(self):
        for line in self:
            if line.percentage_from and line.percentage_to and line.percentage_from > line.percentage_to:
                raise ValidationError(_('Percentage from must be less than percentage to for pricelist line.'))
