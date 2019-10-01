# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api , _
from datetime import datetime, timedelta,date
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval


# Product Template ,add selection field
class ProductTemplate(models.Model):
    _inherit = 'product.template'
 

    #compute method for product speed state
    def _get_product_speed_state(self):
        print (">>>>>>>>>>>>>>>self>>>>>>>",self)
        for product in self:
            today = fields.Date.today()
            before_365_date = today - timedelta(days=365)
            before_90_date = today - timedelta(days=90)
            convert_before_datetime = datetime.strptime(before_365_date.strftime('%Y-%m-%d'), '%Y-%m-%d')
            convert_90_datetime =  datetime.strptime(before_90_date.strftime('%Y-%m-%d'), '%Y-%m-%d')
            today_datetime = fields.datetime.now()
            product_ids = self.env['product.product'].search([('product_tmpl_id','=',product.id )])
            if product_ids:
                stock_365_move_ids = self.env['stock.move'].search([('product_id','=',product_ids[0].id),('date','>=',convert_before_datetime),('date','<=',today_datetime),('state','=','done')])
                stock_90_move_ids = self.env['stock.move'].search([('product_id','=',product_ids[0].id),('date','>=',convert_90_datetime),('date','<=',today_datetime),('state','=','done')])
                bet_365_to_90_move_ids = self.env['stock.move'].search([('product_id','=',product_ids[0].id),('date','>=',convert_before_datetime),('date','<=',convert_90_datetime),('state','=','done')])
                if not stock_365_move_ids:
                    product.product_speed_state = 'dead_product'
                if not stock_90_move_ids and  bet_365_to_90_move_ids :
                    product.product_speed_state = 'slow_product'
                if stock_365_move_ids and stock_90_move_ids:
                    product.product_speed_state = 'fast_product'
                
        return

    @api.depends('market_price', 'last_purchase_price')
    def _get_price_diff(self):
        for product in self:
            if product:
               purchase_price = product.last_purchase_price
               market_price = product.market_price
               if purchase_price:
                   product.price_diff = ((market_price - purchase_price) / purchase_price) * 100
               else:
                   product.price_diff = 0.0
        return 

    product_speed_state = fields.Selection([('fast_product','Fast Products'),('slow_product','Slow Products'),('dead_product','Dead Products')], string='Product Speed State', compute='_get_product_speed_state',  store=True, readonly=True) 
    market_price = fields.Float('Market Price',default=0.0)
    last_purchase_price = fields.Float('Last Purchase Price',readonly=True)
    min_qty = fields.Integer('Safety Stock')
    price_diff = fields.Float(compute='_get_price_diff',string='Price Difference %', store=True, readonly=True,
        help="Price Difference % = ((Market Price - Last Purchase Price) / Last Purchase Price) * 100\n\
            For Example: If Market Price = 100, Last Purchase Price = 75\n\
            then Price Difference % = 50\
        ")
    available = fields.Float('available',compute='_compute_quantities')
    last_po_currency = fields.Many2one('res.currency')
    market_price_currency = fields.Many2one('res.currency')
    req_diff = fields.Boolean("Requeste the difference")
    #add extra product speed field for group by 
    arabic_name = fields.Char('Arabic Name')

    @api.depends(
        'product_variant_ids',
        'product_variant_ids.stock_move_ids.product_qty',
        'product_variant_ids.stock_move_ids.state',
    )
    def _compute_quantities(self):
        res = self._compute_quantities_dict()
        for template in self:
            template.qty_available = res[template.id]['qty_available']
            template.virtual_available = res[template.id]['virtual_available']
            template.incoming_qty = res[template.id]['incoming_qty']
            template.outgoing_qty = res[template.id]['outgoing_qty']
            template.available = res[template.id]['virtual_available']

class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_speed_state = fields.Selection([('fast_product','Fast Products'),('slow_product','Slow Products'),('dead_product','Dead Products')], string='Product Speed State', related="product_tmpl_id.product_speed_state", readonly=True)

