# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class popup_notification(models.Model):
    _name = "popup.notification"

    title = fields.Char()
    message = fields.Text()
    status = fields.Selection([('shown', 'shown'), ('draft', 'draft')], defaul='draft')
    partner_ids = fields.Many2many('res.users')
    sale_id = fields.Integer('Sale')
    show = fields.Boolean('Show',default=True)

    @api.multi
    def get_notifications(self):
        result = []
        for obj in self:
            result.append({
                'title': obj.title,
                'message': obj.message,
                'status': obj.status,
                'id': obj.id,
		'sale_id':obj.sale_id,
            })
        return result


class SaleOrder(models.Model):
    _inherit = 'sale.order'
  
    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        purchase_user_id = self.env.ref('purchase.group_purchase_user').id
        purchase_manager_id = self.env.ref('purchase.group_purchase_manager').id
        if purchase_user_id and purchase_manager_id:
            user_ids  = self.env['res.users'].search([('groups_id','in',[purchase_user_id  ,purchase_user_id])])
            if user_ids:
                values = {'status': 'draft','title': 'Notification'  ,'sale_id': result.id,'message': "New sale order created:"+ str(result.name) ,'partner_ids': [(6, 0, [ i.id for i in user_ids])]}
                self.env['popup.notification'].create(values)
        return result
