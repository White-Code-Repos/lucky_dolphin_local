# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import UserError
from datetime import timedelta


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        for line in self:
            min_product_vendor_price = 0
            last_product_purchase_price = 0
            product_percentage = 0
            pricelist_percentage = 0
            if line.product_id and line.order_id.pricelist_id.qty_applied_on != 'other':
                pricelist_updated_range = line.order_id.pricelist_id.updated_range

                # last order point for product
                last_product_orderpoint = self.env['stock.warehouse.orderpoint'].sudo().search(
                    [('product_id', '=', line.product_id.id)], order='create_date desc', limit=1)

                # product price from last purchase order
                last_product_purchase_price = self.env['purchase.order.line'].sudo().search(
                    [('product_id', '=', line.product_id.id), ('order_id.state', 'in', ['purchase', 'done'])],
                    order='create_date desc', limit=1).price_unit

                # min price of product from vendor in specific duration depend on updated_range from pricelist
                product_date = fields.Datetime.now() - timedelta(days=pricelist_updated_range)
                product_supplierinfo_objects = self.env['product.supplierinfo'].sudo().search(
                    [('product_tmpl_id', '=', line.product_id.product_tmpl_id.id), ('create_date', '>=', product_date)])
                if product_supplierinfo_objects:
                    min_product_vendor_price = min(
                        [supplier_info.price for supplier_info in product_supplierinfo_objects])
                if min_product_vendor_price > 0:
                    product_percentage = ((
                                              min_product_vendor_price - last_product_purchase_price) / min_product_vendor_price) * 100

                # conditions part for stock qty
                for pricelist_line in line.order_id.pricelist_id.product_pricelist_line_ids:
                    if (
                                    pricelist_line.product_id == line.product_id or pricelist_line.categ_id == line.product_id.categ_id) and pricelist_line.percentage_from <= product_percentage <= pricelist_line.percentage_to:
                        if pricelist_line.apply_sign == 'minus':
                            pricelist_percentage = -1 * pricelist_line.apply_percentage
                        elif pricelist_line.apply_sign == 'plus':
                            pricelist_percentage = pricelist_line.apply_percentage
                    break

                line.price_unit = min_product_vendor_price + (pricelist_percentage / 100) * min_product_vendor_price
            else:
                return res
