from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductAlternativeLine(models.Model):
    _name = "product.alternative.line"

    product_id = fields.Many2one("product.product")
    alternative_id = fields.Many2one("product.product")
    product_tmpl_id = fields.Many2one("product.template")
    alternative_tmpl_id = fields.Many2one("product.template")

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    alternative_ids = fields.One2many("product.alternative.line", "product_tmpl_id")
    price1 = fields.Char(string="Price 1")
    price2 = fields.Char(string="Price 2")
    price3 = fields.Char(string="Price 3")
    @api.multi
    @api.constrains('alternative_ids')
    def _check_alternatives(self):
        for product in self:
            product_ids = []
            for line in product.alternative_ids:
                if product.id == line.alternative_tmpl_id.id:
                    raise ValidationError("You can't add the product as alternative to itself")
                if line.alternative_tmpl_id.id in product_ids:
                    line.unlink()
                    continue
                product_ids.append(line.alternative_tmpl_id.id)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductTemplateInherit, self).create(vals_list)
        for product_product in res.product_variant_ids:
            alternative_list = []
            product_product.price1 = res.price1
            product_product.price2 = res.price2
            product_product.price3 = res.price3
            for alternative in res.alternative_ids:
                alternative_list.append((0, 0, {'alternative_id': alternative.alternative_id.id, 'product_id': product_product.id}))
            product_product.alternative_ids = alternative_list
        return res

    @api.multi
    def write(self, vals):
        update_product_prices, update_product_alternatives = False, False
        alternative_list = []
        if 'price1' or 'price2' or 'price3' in vals.keys():
            update_product_prices = True
        if 'alternative_ids' in vals.keys():
            update_product_alternatives = True
        res = super(ProductTemplateInherit, self).write(vals)
        if update_product_prices:
            for product_product in self.product_variant_ids:
                product_product.price1 = self.price1
                product_product.price2 = self.price2
                product_product.price3 = self.price3
        if update_product_alternatives:
            for alternative in self.alternative_ids:
                alternative_list.append((0, 0, {'alternative_id': alternative.alternative_id.id, 'product_id': product_product.id}))
            for product_product in self.product_variant_ids:
                product_product.alternative_ids.unlink()
                product_product.alternative_ids = alternative_list
        return res

class ProductInherit(models.Model):
    _inherit = 'product.product'

    alternative_ids = fields.One2many("product.alternative.line", "product_id")
    price1 = fields.Char(string="Price 1")
    price2 = fields.Char(string="Price 2")
    price3 = fields.Char(string="Price 3")
    @api.multi
    @api.constrains('alternative_ids')
    def _check_alternatives(self):
        for product in self:
            product_ids = []
            for line in product.alternative_ids:
                if product.id == line.alternative_id.id:
                    raise ValidationError("You can't add the product as alternative to itself")
                if line.alternative_id.id in product_ids:
                    line.unlink()
                    continue
                product_ids.append(line.alternative_id.id)