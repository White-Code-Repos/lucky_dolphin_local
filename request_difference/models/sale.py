# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api , _
from odoo.exceptions import UserError, ValidationError


# sale order
#add waiting price state
class SaleOrder(models.Model):
    _inherit = 'sale.order'


    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        if vals.get('order_line'):
            for line in vals.get('order_line'):
                extra_qty = 0.0
                if vals.get('order_line')[0][2]['product_id']:
                    product_id = vals.get('order_line')[0][2]['product_id']
                    qty = vals.get('order_line')[0][2]['product_uom_qty']
                    product_brw = self.env['product.product'].browse(product_id)
                    if product_brw.req_diff:
                        if product_brw.qty_available  <  qty:
                            extra_qty = qty - product_brw.qty_available
                        if extra_qty:
                            if product_brw.seller_ids:
                                for i in product_brw.seller_ids:
                                    product_line_vals = {
					'product_id':product_id,
					'name': product_brw.description_purchase or product_brw.name,
					'price_unit': i.price,
					'product_uom': product_brw.uom_po_id.id,
					'product_qty':float(extra_qty),
				        'date_planned': fields.Date.today(),				 			
				          }
                                    purchase_vals = {
					'partner_id' :i.name.id,
					'currency_id' : result.currency_id.id,
					'order_line' :[(0,0, product_line_vals)],
					'date_order': fields.Datetime.now(),
					}
                                    create_purchase = self.env['purchase.order'].create(purchase_vals)
                
        return result



