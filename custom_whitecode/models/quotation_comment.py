# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api , _
from odoo.exceptions import UserError, ValidationError


# sale order
class QuotationComment(models.Model):
    _name = 'quotation.comment'

    sale_number = fields.Char('Sale Number')
    comment = fields.Text('Comment')

