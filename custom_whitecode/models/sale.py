# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api , _
from odoo.exceptions import UserError, ValidationError


# sale order
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    comment = fields.Text('Comment')
    before_fixed_price = fields.Text('Before Fixed Price')
    #after_fixed_price = fields.Text('After Fixed Price')
    profit_margin = fields.Selection([
    ('10', "10%"),
    ('20', "20%"),
],'Profit Margin')

    @api.model
    def create(self, vals):
        sale = super(SaleOrder, self).create(vals)
        if vals.get('comment'):
            quotation_comment_obj = self.env['quotation.comment']
            value = {'comment': vals.get('comment') ,'sale_number': sale.name}
            create_quotation_comment = quotation_comment_obj.create(value)
        return sale


    @api.onchange('carrier_id')
    def onchange_carrier_id(self):
        if self.state in ('draft', 'sent'):
            #self.after_fixed_price = self.carrier_id.after_fixed_price
            if self.carrier_id:
                before_value = self.carrier_id.before_fixed_price or '' 
                after_value = self.carrier_id.after_fixed_price or ''
                fixed_value = str(self.carrier_id.fixed_price)
                self.before_fixed_price =  before_value + '  '  + fixed_value + ' ' + after_value

    @api.multi
    def write(self, vals):
        sale = super(SaleOrder, self).write(vals)
        if vals.get('comment'):
            quotation_comment_obj = self.env['quotation.comment']
            search_qut_comment_ids = quotation_comment_obj.search([('sale_number','=', self.name)])
            if search_qut_comment_ids:
                search_qut_comment_ids[0].write({'comment': vals.get('comment')})
            else:
                value = {'comment': vals.get('comment') ,'sale_number': self.name}
                create_quotation_comment = quotation_comment_obj.create(value)
        return sale


# sale order Line
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_speed_state = fields.Selection([('fast_product','Fast Products'),('slow_product','Slow Products'),('dead_product','Dead Products')], string='Product Speed State',related='product_id.product_speed_state', readonly=True)
 

    @api.multi
    def get_reprice(self):
        self.write({'price_state':'request'})
        self.order_id.write({'state':'waiting_price'})

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change() 
        vals = {}
        name = self.product_id.description_sale
        vals.update(name=name)
        self.update(vals)
        for line in self:
            if line.order_id.profit_margin:
                if line.order_id.profit_margin == '10':
                    line.price_unit = line.product_id.standard_price * 1.1
                elif line.order_id.profit_margin == '20':
                    line.price_unit = line.product_id.standard_price * 1.2
            else:
                return res
