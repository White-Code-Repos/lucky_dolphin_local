# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api , _
from datetime import datetime, timedelta,date
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval


# Product Template ,add selection field
class ProductTemplate(models.Model):
    _inherit = 'product.template'
 

    req_diff = fields.Boolean("Requeste the difference")
   
