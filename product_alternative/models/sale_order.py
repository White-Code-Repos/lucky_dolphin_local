from odoo import models, api
from odoo.tools import float_compare


class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_id')
    def _onchange_product_id_uom_check_availability(self):
        if not self.product_uom or (self.product_id.uom_id.category_id.id != self.product_uom.category_id.id):
            self.product_uom = self.product_id.uom_id
        return self._onchange_product_id_check_availability()

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(self.product_id.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    alternative_qty = 0
                    alternative_product = None
                    for line in self.product_id.alternative_ids:
                        print("checking: ", line.alternative_id.name)
                        alternative_available_qty = line.alternative_id.virtual_available
                        print(line.alternative_id.id, alternative_available_qty)
                        if float_compare(product_qty, alternative_available_qty, precision_digits=precision) == -1 \
                                and alternative_available_qty > alternative_qty:
                            alternative_qty = alternative_available_qty
                            alternative_product = line.alternative_id
                    message = "You plan to sell {} {} but you only have {} {} available!\nThe stock on hand is {} {}.\n".format(
                        self.product_uom_qty, self.product_uom.name, self.product_id.virtual_available,
                        self.product_id.uom_id.name, self.product_id.qty_available,
                        self.product_id.uom_id.name
                    )
                    if alternative_product:
                        self.product_id = alternative_product.id
                        message += "So the system automatically changed it to alternative {}".format(
                            alternative_product.name
                        )
                    else:
                        message += "The system couldn't automatically change the product with an alternative"
                    warning_message = {
                        'title': 'Not enough inventory!',
                        'message': message
                    }
                    return {'warning': warning_message}
        return {}
