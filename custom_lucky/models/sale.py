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
            if len(vals.get('order_line')) == 1:
                if vals.get('order_line')[0][2]['product_id']:
                    product_id = vals.get('order_line')[0][2]['product_id']
                    product_brw = self.env['product.product'].browse(product_id)
                    if product_brw.standard_price == 0.0:
                        result.write({'state':'waiting_price'})
                    else:
                        result.write({'state':'draft'})
            else:
                for line in vals.get('order_line'):
                    if line[2]:
                        product_id = line[2].get('product_id', False)
                        product_brw = product_id and self.env['product.product'].browse(product_id)
                        if product_brw and product_brw.standard_price == 0.0:
                            result.write({'state':'waiting_price'})

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

    @api.multi
    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        if vals.get('order_line'):
            if len(vals.get('order_line')) == 1:
                # if vals.get('order_line')[0][2] and vals.get('order_line')[0][2]['product_id']:
                if vals.get('order_line')[0][2] and self.order_line.product_id.id:
                    product_id = self.order_line.product_id.id
                    product_brw = self.env['product.product'].browse(product_id)
                    if product_brw.standard_price == 0.0:
                        self.write({'state':'waiting_price'})
                    else:
                        self.write({'state':'draft'})
            else:
                for line in vals.get('order_line'):
                    if line[2]:
                        sale_order_line_ids = self.order_line
                        for product_id in sale_order_line_ids:
                            product_brw = self.env['product.product'].browse(product_id)
                            if product_brw.standard_price == 0.0:
                                self.write({'state':'waiting_price'})
        return result


    @api.multi
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        if  self.order_line:
            for line in  self.order_line:
                if line.price_state == 'request':
                    raise UserError(_(
                'You can not proceed confirm order becuase one of the line has requested price')) 
        return res

    @api.multi
    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'confirmation_date': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
        for line in self.order_line:
            if line.product_id:
                line.product_id.product_tmpl_id._get_product_speed_state()
        return True

    state = fields.Selection([
        ('draft', 'Quotation'),
	('waiting_price','Waiting Price'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3,default='draft')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)], 'waiting_price': [('readonly', False)],'sent': [('readonly', False)]}, help="Pricelist for current sales order.")

    

    # @api.multi
    # @api.onchange('pricelist_id', 'order_line')
    # def onchange_pricelist_id(self):
    #     if self.pricelist_id:
    #         if self.order_line:
    #             for line in self.order_line:
    #                 if line.order_id.pricelist_id and line.order_id.partner_id:
    #                     product = line.product_id.with_context(
    #                         lang=line.order_id.partner_id.lang,
    #                         partner=line.order_id.partner_id.id,
    #                         quantity=line.product_uom_qty,
    #                         date=line.order_id.date_order,
    #                         pricelist=line.order_id.pricelist_id.id,
    #                         uom=line.product_uom.id,
    #                         fiscal_position=self.env.context.get('fiscal_position')
    #                     )
    #                     line.price_unit = self.env['account.tax']._fix_tax_included_price(line._get_display_price(product), product.taxes_id, line.tax_id)
    #

    @api.multi
    def update_pricelist(self):
        if self.pricelist_id:
            if self.order_line:
                lines = self.order_line
                for line in lines:
                    product = line.product_id.with_context(
			    lang=line.order_id.partner_id.lang,
			    partner=line.order_id.partner_id,
			    quantity= line.product_uom_qty,
			    date=line.order_id.date_order,
			    pricelist=line.order_id.pricelist_id.id,
			    uom=line.product_uom.id
			)
                    line.price_unit = self.env['account.tax']._fix_tax_included_price_company(line._get_display_price(product), product.taxes_id, line.tax_id, line.company_id)


#sale order line
#add requested and priced value stage
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.multi
    def action_price(self):
        if self.overall_cost:
            if self.vendor_id:
                vals ={'name' : self.vendor_id.id,
			'price':self.overall_cost,
			#'delay':1 ,
			'min_qty': self.min_qty,
			'date_start': self.date_start,	
			'date_end': self.date_end,
			'currency_id' :self.currency_id.id,
				}
                self.product_id.write({'variant_seller_ids': [(0,0,vals)]})
            if self.not_available:
                self.write({'purchase_price':self.overall_cost,'price_state':'not_available'})
            else:
                self.write({'purchase_price':self.overall_cost,'price_state':'price'})
                if self.order_id:
                    request = False
                    for line in self.order_id.order_line:
                        if line.price_state == 'request':
                            request = True
                    if request == False:
                       self.order_id.write({'state': 'draft'})
                      
    @api.depends('order_id')
    def _get_line_price_state(self):
        for line in self:
            if line.product_id:
                if line.product_id.standard_price:
                    line.price_state = 'price'
                else: 
                    line.price_state = 'request'
        return 
    
    @api.depends('overhead_cost','price_purchase')
    def _get_overall_cost(self):
        for line in self:
            if line.overhead_cost or line.price_purchase :
                line.overall_cost = line.overhead_cost + line.price_purchase
            else: 
                line.overall_cost = 0.0
        return 


    @api.model
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.product_id:
                line.product_id.product_tmpl_id._get_product_speed_state()
        return lines

    @api.depends( 'product_id')
    def _get_vendors(self):
        for line in self:
            line.vendors = [(6,0,[l.name.id for l in line.product_id.seller_ids])]

    @api.multi
    def get_reprice(self):
        self.write({'price_state':'request'})
        self.order_id.write({'state':'waiting_price'})

    price_state = fields.Selection([('price','Priced'),('request','Requested'),('not_available','Not Available')],'Price State', compute='_get_line_price_state',store=True, readonly=True)
    vendor_id = fields.Many2one('res.partner','Vendor')
    overhead_cost =  fields.Float('Overhead Cost',defaults=0.0)
    price_purchase =  fields.Float('Purchase Price',default=0.0)
    overall_cost = fields.Float(compute='_get_overall_cost' ,string='Overall Cost',store=True,  readonly=True)
    
    product_cost = fields.Float(related="product_id.standard_price")
    vendors = fields.Many2many('res.partner',compute='_get_vendors' )
    min_qty =fields.Float("Minimal Quantity",default= 1.0 )
    date_start = fields.Date("Validity")
    date_end = fields.Date("End Date")
    not_available = fields.Boolean('Not Available')


