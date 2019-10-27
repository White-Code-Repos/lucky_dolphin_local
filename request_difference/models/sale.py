# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api , _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


# sale order
#add waiting price state
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()

        po_ids = self.env['purchase.order'].search([('origin','ilike',self.name)])
        for po in po_ids:
                po.write({
                    'batch_id':self.batch_id.id
                })
                for line in po.order_line:
                    if line.product_qty <= line.product_id.qty_available:
                        line.unlink()
                        if len(po.order_line)==0:
                            po.write({
                                'state':'cancel'
                            })
                            po.unlink()
                    else :
                        line.update({
                            'product_qty': (line.product_qty - line.product_id.qty_available)
                        })

        return result



