# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api , _
from odoo.exceptions import UserError, ValidationError


# purchase order
#add waiting price state
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id._convert(
                            order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.order_line:
                for line in order.order_line:
                    line.product_id.last_purchase_price = line.price_unit
                    line.product_id.last_po_currency = line.currency_id.id
            """if order.order_line:
                line_ids = []
                for line in order.order_line:
                    print ("IIIIIIIIIIIIIIIIIIIIIIII",line)
                    order_line_search = self.env['purchase.order.line'].search([('product_id','=',line.product_id.id ),('order_id.state','in',('purchase','done'))])
                    if order_line_search:
                        for lines in order_line_search:
                            line_ids.append(lines.id) 
                final_list = sorted(line_ids, key=int, reverse=True)
                print ("_________final_list_______",final_list)"""
        return True

# Purchase order Line
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        vals = {}
        res = super(PurchaseOrderLine, self).onchange_product_id()
        name = self.product_id.description_purchase 
        vals.update(name=name)
        self.update(vals)
        return res

