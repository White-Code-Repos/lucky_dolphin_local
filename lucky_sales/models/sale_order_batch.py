from odoo import models, fields, api,exceptions
from odoo.http import request

class SaleOrderBatch(models.Model):
    _name = "sale.order.batch"

    @api.multi
    def _get_orders_count(self):
        for record in self:
            record.parcels_in = 0
            record.parcels_out = 0
            record.crew_in = 0
            record.crew_out = 0
            record.is_repair = False
            for order in record.order_ids:
                if order.order_internal_type == "service":
                    record.is_repair = True
                if order.order_internal_type == "parcel":
                    if order.parcel_type in ['air_in', 'oc_in']:
                        for parcel in order.parcel_ids:
                            record.parcels_in += parcel.pieces_no
                    elif order.parcel_type in ['air_out', 'oc_out']:
                        for parcel in order.parcel_ids:
                            record.parcels_out += parcel.pieces_no
                if order.order_internal_type == "crew_ch":
                    if order.crew_type == "in":
                        record.crew_in += len(order.crew_ids)
                    elif order.crew_type == "out":
                        record.crew_out += len(order.crew_ids)

    @staticmethod
    def _get_summary_table(data):
        res = "<table border='1'>"
        for rec in data:
            res += """
            <tr>
                <td>{name}</td>
                <td>{packages}</td>
            </tr>
            """.format(name=rec['name'], packages=rec['packages'])
        res += "</table>"
        return res

    @api.multi
    def _get_warehouse_summary(self):
        for record in self:
            drop_shippings = []
            warehouses = []
            pack_move_count = 0
            for order in record.order_ids:
                if order.order_internal_type == "normal":
                    for picking in order.picking_ids:
                        packages = picking.move_line_ids.mapped('result_package_id')
                        pack_move_count += len(packages)
                        packages_str = "{} package ({})".format(len(packages),
                                                                ",".join([p.name for p in packages]))
                        if picking.picking_type_id.name == 'Dropship':
                            drop_shipping = {
                                'name': picking.partner_id.name,
                                'packages': packages_str
                            }
                            drop_shippings.append(drop_shipping)
                        else:
                            packages.write({'operation_id': record.id})
                            warehouse = {
                                'name': picking.location_id.name,
                                'packages': packages_str
                            }
                            warehouses.append(warehouse)
            record.pack_move_count = pack_move_count
            self.drop_ship_summary = self._get_summary_table(drop_shippings)
            self.wh_summary = self._get_summary_table(warehouses)


    @api.one
    @api.depends('order_ids')
    def _purchase_order_count(self):
        for order_id in self.order_ids:
                self.purchase_order_count += len(order_id.purchase_order_ids)

    name = fields.Char(default=lambda s: s.env['ir.sequence'].next_by_code('sale.order.batch'),
                       readonly=True, string="Operation#")
    partner_id = fields.Many2one('res.partner', readonly=True)
    vessel_id = fields.Many2one("res.partner", readonly=True)
    vessel_agent_id = fields.Many2one("res.partner")
    # arrival_port_id = fields.Many2one("lucky.port")
    # delivery_port_id = fields.Many2one("lucky.port")

    arrival_port_id = fields.Many2one("delivery.carrier")
    delivery_port_id = fields.Many2one("delivery.carrier")
    eta = fields.Datetime("ETA")
    commit_delivery_date = fields.Datetime("Commitment Delivery Date")
    order_ids = fields.One2many("sale.order", 'batch_id')
    state = fields.Selection([('draft', "Draft"), ('done', "Done")], default='draft')
    parcels_in = fields.Integer(compute=_get_orders_count, string="Incoming Parcels PCS.")
    parcels_out = fields.Integer(compute=_get_orders_count, string="Outgoing Parcels PCS.")
    crew_in = fields.Integer(compute=_get_orders_count, string="Crew Embarkation")
    crew_out = fields.Integer(compute=_get_orders_count, string="Crew disembarkation")
    is_repair = fields.Boolean("Repair?", compute=_get_orders_count)
    wh_summary = fields.Html("Warehouses Summary", compute=_get_warehouse_summary)
    drop_ship_summary = fields.Html("Drop Shipping Summary", compute=_get_warehouse_summary)
    remark = fields.Text(string='Remark')
    parcel_awb = fields.Char('Parcel AWB',compute='_parcel_awb')
    purchase_order_count = fields.Integer(compute='_purchase_order_count')
    pack_move_ids = fields.One2many(comodel_name='stock.quant.package',inverse_name='operation_id')
    pack_move_count = fields.Integer(compute='_get_warehouse_summary')

    @api.multi
    def purchase_order_action(self):

        action = self.env.ref('purchase.purchase_rfq').read()[0]
        purchase_orders = self.mapped('order_ids').mapped('purchase_order_ids').mapped('purchase_order_id')
        if len(purchase_orders) > 0:
            action['domain'] = [('id', 'in', purchase_orders.ids)]
        return action

    def _parcel_awb(self):
        self.parcel_awb = ""
        for sale_id in self.order_ids:
            for parcel_awb_id in sale_id.parcel_ids:
                self.parcel_awb += parcel_awb_id[0]['bill_no']
                self.parcel_awb += ','
        self.parcel_awb = self.parcel_awb[:-1] #removing last comma

    @api.multi
    def write(self, vals):
        super().write(vals)
        for rec in self:
            for order in rec.order_ids:
                for changed_attr in vals:
                    setattr(order, changed_attr, vals[changed_attr])

    @api.multi
    def delivery_action_pdf(self):
        # return {
        #      'type' : 'ir.actions.act_url',
        #      'url': '/opening/delivery/%s' % (self.id),
        #      'target' :'new'
        #      }
        ids = self.order_ids.mapped('picking_ids')
        if ids:
            return self.env.ref('stock.action_report_delivery').report_action(ids)
        else:
            raise exceptions.UserError("There is no picking for this order")
        # data = self.read()[0]
        # active_ids = self.order_ids
        # datas = {
        #     'ids': active_ids,
        #     'model': 'stock.picking',
        #     'form': data
        # }
        # return self.env['report'].get_action(self, 'lucky_dolphin_stock_reports.report_deliveryslip_doc',data=datas)

    @api.multi
    def invoice_action_pdf(self):
        if True not in self.order_ids.mapped('print_invoice'):
            raise exceptions.UserError("you are not allowed to print invoices")
        else:
            return {
                'type' : 'ir.actions.act_url',
                'url': '/opening/invoice/%s' % (self.id),
                'target' :'new'
                }

    @api.multi
    def pack_move_action(self):
        action = self.env.ref('stock.action_package_view').read()[0]
        if self.pack_move_count > 0:
            action['domain'] = [('id', 'in', self.pack_move_ids.ids)]
            return action

class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    operation_id = fields.Many2one('sale.order.batch',string='Operation')
