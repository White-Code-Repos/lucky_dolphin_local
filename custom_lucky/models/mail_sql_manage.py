from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval



class MailMessage(models.Model):
    _inherit = 'mail.message'

    mail_action = fields.Char('Mail Action')
