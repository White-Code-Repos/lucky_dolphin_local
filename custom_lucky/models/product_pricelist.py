# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api , _
from datetime import datetime, timedelta,date
from odoo.exceptions import UserError, ValidationError


# Product Pricelist
class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    base = fields.Selection([
        ('list_price', 'Public Price'),
        ('standard_price', 'Cost'),
        ('pricelist', 'Other Pricelist'),
	('market_price','Market Price')], "Based on",
        default='list_price', required=True,
        help='Base price for computation.\n'
             'Public Price: The base price will be the Sale/public Price.\n'
             'Cost Price : The base price will be the cost price.\n'
             'Other Pricelist : Computation of the base price based on another Pricelist.')


    last_po_to_market = fields.Selection([('less_market','PO > Market'),('less_po','PO =< Market')], string='Last Po To Market',default="less_po")
    req_to_min = fields.Selection([('less_min','Requested > Safety Stock'),('less_req','Requested =< Safety Stock')], string='Requested to Safety stock')
    min_to_available = fields.Selection([('less_available','safety stock > Available'),('less_min','safety stock =< Available')], string='Safety stock to Available')
    req_to_available = fields.Selection([('less_avail','Requested > Available'),('more_avail','Requested <= Available')], string='Requested to Available')

    min_price_diff =  fields.Float("Min Price Diff")
    max_price_diff = fields.Float("Max Price Diff")
    market_type = fields.Selection([('last_purchase_price','Last Purchase Price'),('market_price','Market Price')], string='Type')
    factor = fields.Float(string='Factor')
    dropship = fields.Boolean('Dropship')
    last_po_0 = fields.Boolean('Last PO is 0')
    available_is_0 = fields.Boolean('Available is 0')
