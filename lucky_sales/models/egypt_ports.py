from odoo import models, fields

class EgyptPorts(models.Model):
    _name = "egypt.ports"

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')