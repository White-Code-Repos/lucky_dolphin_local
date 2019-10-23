# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import os
import base64
import random
class Mail(models.Model):
    _inherit = 'mail.message'

    is_attachment_downloaded = fields.Boolean('Is Attachment Downloaded',readonly=True,default=False)

    @api.model
    def download_attachment(self):
        mails = self.env['mail.message'].search([('is_attachment_downloaded','=',False)])
        cwd = os.environ['HOME']
        dir_path = os.path.join(cwd,"mail_attachments")
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        for mail in mails:
            for attachment in mail.attachment_ids:
                completeName = os.path.join(dir_path,attachment.datas_fname)
                if not os.path.exists(completeName):
                    file1 = open(completeName,'wb')
                else:
                    temp_name = completeName.split('.')
                    temp_name[0] = temp_name[0] + '_' +str(random.randrange(0,10000,9))
                    completeName = temp_name[0] + '.' + temp_name[1]
                    file1 = open(completeName,'wb')
                content = base64.b64decode(attachment.datas)
                file1.write(content)
                file1.close()
            mail.is_attachment_downloaded = True
