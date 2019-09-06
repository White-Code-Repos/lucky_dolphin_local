# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api , _
from datetime import datetime, timedelta,date
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval


# Product Template ,add selection field
class ProductTemplate(models.Model):
    _inherit = 'product.template'
 
    def _get_product_speed_state(self):
        print (">>>>>>>>>>>>>>>self>>>>>>>",self)
        for product in self:
            today = fields.Date.today()
            dead_days = self.env['ir.config_parameter'].sudo().get_param('dead_product_days')
            slow_days = self.env['ir.config_parameter'].sudo().get_param('slow_product_days')
            print ("********************TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
            before_365_date = today - timedelta(days=float(dead_days))
            before_90_date = today - timedelta(days=float(slow_days))
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
                    product.write({'product_speed':'dead_product'})
                    
                if not stock_90_move_ids and  bet_365_to_90_move_ids :
                    product.product_speed_state = 'slow_product'
                    product.write({'product_speed':'slow_product'})
                if stock_365_move_ids and stock_90_move_ids:
                    product.product_speed_state = 'fast_product'
                    product.write({'product_speed':'fast_product'})
                print (">>>>>>>>>>>>>product.product_speed>>>>>>>>>>>.",product.product_speed )
        return


    product_speed_state = fields.Selection([('fast_product','Fast Products'),('slow_product','Slow Products'),('dead_product','Dead Products')], string='Product Speed State', compute='_get_product_speed_state', readonly=True) 
    market_price = fields.Float('Market Price',default=0.0)
    last_purchase_price = fields.Float('Last Purchase Price',readonly=True)
    min_qty = fields.Integer('Safety Stock')
    price_diff = fields.Float(compute='_get_price_diff',string='Price Difference %', store=True, readonly=True)
    product_speed = fields.Selection([('fast_product','Fast Products'),('slow_product','Slow Products'),('dead_product','Dead Products')], string='Product Speed State', readonly=True)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_speed_state = fields.Selection([('fast_product','Fast Products'),('slow_product','Slow Products'),('dead_product','Dead Products')], string='Product Speed State', related="product_tmpl_id.product_speed_state", readonly=True)

