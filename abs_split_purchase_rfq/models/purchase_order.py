# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2019-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api,fields,models,_
from odoo.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit ='purchase.order'

    # Define function to split purchase ordeline when we click on button
    def btn_split_rfq(self):
        for record in self: 
            if record.order_line:
                cnt = 0
                for rec in record.order_line: 
                    if rec.split: 
                        cnt += 1
                if cnt >= 1:
                    quotation_id = self.copy()
                    if quotation_id:
                        for line in quotation_id.order_line:
                            if not line.split:
                                line.unlink()
                            else:
                                line.split = False
                    for order_line in record.order_line:
                        if order_line.split:
                            self.env['purchase.order.line'].browse(order_line.id).unlink() 
                else:
                    raise ValidationError(_('Please Select Order Line To Split'))

