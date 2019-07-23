from odoo import models, fields, api


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
            for order in record.order_ids:
                if order.order_internal_type == "normal":
                    for picking in order.picking_ids:
                        packages = picking.move_line_ids.mapped('result_package_id')
                        packages_str = "{} package ({})".format(len(packages),
                                                                ",".join([p.name for p in packages]))
                        if picking.picking_type_id.name == 'Dropship':
                            drop_shipping = {
                                'name': picking.partner_id.name,
                                'packages': packages_str
                            }
                            drop_shippings.append(drop_shipping)
                        else:
                            warehouse = {
                                'name': picking.location_id.name,
                                'packages': packages_str
                            }
                            warehouses.append(warehouse)
            self.drop_ship_summary = self._get_summary_table(drop_shippings)
            self.wh_summary = self._get_summary_table(warehouses)

    name = fields.Char(default=lambda s: s.env['ir.sequence'].next_by_code('sale.order.batch'),
                       readonly=True, string="Operation#")
    partner_id = fields.Many2one('res.partner', readonly=True)
    vessel_id = fields.Many2one("lucky.vessel", readonly=True)
    vessel_agent_id = fields.Many2one("res.partner")
    arrival_port_id = fields.Many2one("lucky.port")
    delivery_port_id = fields.Many2one("lucky.port")
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

    @api.multi
    def write(self, vals):
        super().write(vals)
        for rec in self:
            for order in rec.order_ids:
                for changed_attr in vals:
                    setattr(order, changed_attr, vals[changed_attr])
