from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductAlternativeLine(models.Model):
    _name = "product.alternative.line"

    product_id = fields.Many2one("product.product")
    alternative_id = fields.Many2one("product.product")


class ProductInherit(models.Model):
    _inherit = 'product.product'

    alternative_ids = fields.One2many("product.alternative.line", "product_id")

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
