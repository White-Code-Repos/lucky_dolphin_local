# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import models, fields, api , _
from odoo.exceptions import UserError, ValidationError


# Delivery Carrier
class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    before_fixed_price = fields.Text('Before Fixed Price')
    after_fixed_price = fields.Text('After Fixed Price')

