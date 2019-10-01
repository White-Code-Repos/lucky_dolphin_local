# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from odoo import tools

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    qty_applied_on = fields.Selection(
        [('in_stock', 'In Stock'), ('out_of_stock', 'Out Of Stock'), ('other', 'Other'), ],
        string="Apply On", default='other', required=True, )

    updated_range = fields.Integer(string='Updated Range')
    product_pricelist_line_ids = fields.One2many('product.pricelist.line', 'pricelist_id', string='Pricelist Lines')

    @api.multi
    @api.constrains('qty_applied_on', 'updated_range')
    def check_updated_range_value(self):
        for pricelist in self:
            if pricelist.qty_applied_on and pricelist.updated_range <= 0:
                raise ValidationError(_('Updated range must be greater than zero.'))


    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        If date in context: Date of the pricelist (%Y-%m-%d)

            :param products_qty_partner: list of typles products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Date.context_today(self)
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = list(categ_ids)

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules
        self._cr.execute(
            'SELECT item.id '
            'FROM product_pricelist_item AS item '
            'LEFT JOIN product_category AS categ '
            'ON item.categ_id = categ.id '
            'WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))'
            'AND (item.product_id IS NULL OR item.product_id = any(%s))'
            'AND (item.categ_id IS NULL OR item.categ_id = any(%s)) '
            'AND (item.pricelist_id = %s) '
            'AND (item.date_start IS NULL OR item.date_start<=%s) '
            'AND (item.date_end IS NULL OR item.date_end>=%s)'
            'ORDER BY item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc',
            (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))
        # NOTE: if you change `order by` on that query, make sure it matches
        # _order from model to avoid inconstencies and undeterministic issues.

        item_ids = [x[0] for x in self._cr.fetchall()]
        items = self.env['product.pricelist.item'].browse(item_ids)
        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False
            #Check if the product is dropship
            #if product is dropship, apply the pricelist rule else skip
            # if dropship in product.route_ids.ids:
                # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
                # An intermediary unit price may be computed according to a different UoM, in
                # which case the price_uom_id contains that UoM.
                # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['uom.uom'].browse([self._context['uom']])._compute_quantity(qty, product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            dropship = self.env.ref('stock_dropshipping.picking_type_dropship').id
            price_uom = self.env['uom.uom'].browse([qty_uom_id])

            def compute_price_ct(items):
                price = product.price_compute('list_price')[product.id]
                suitable_rule = False
                for rule in items:
                    if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                        continue
                    if is_product_template:
                        if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                            continue
                        if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                            # product rule acceptable on template if has only one variant
                            continue
                    else:
                        if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                            continue
                        if rule.product_id and product.id != rule.product_id.id:
                            continue

                    if rule.categ_id:
                        cat = product.categ_id
                        while cat:
                            if cat.id == rule.categ_id.id:
                                break
                            cat = cat.parent_id
                        if not cat:
                            continue
                    if rule.base == 'pricelist' and rule.base_pricelist_id:
                        price_tmp = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)])[product.id][0]  # TDE: 0 = price, 1 = rule
                        price = rule.base_pricelist_id.currency_id._convert(price_tmp, self.currency_id, self.env.user.company_id, date, round=False)
                    elif rule.base == 'market_price':
                        if rule.market_type:
                            if rule.factor and rule.req_to_min == 'less_min' and rule.min_to_available=='less_available' and rule.req_to_available == 'less_avail':
                                if qty_in_product_uom > product.min_qty and product.min_qty > product.available and qty_in_product_uom > product.available:
                                    price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                    suitable_rule = rule
                                    break
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_min' and rule.min_to_available=='less_available' and rule.req_to_available == 'more_avail':
                                if qty_in_product_uom > product.min_qty and product.min_qty > product.available and qty_in_product_uom <= product.available:
                                    price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                    suitable_rule = rulesuitable_rule = rule

                                    break
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_min' and rule.min_to_available=='less_min' and rule.req_to_available=='less_avail':
                                if qty_in_product_uom > product.min_qty and product.min_qty <= product.available and qty_in_product_uom > product.available:
                                    price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                    suitable_rule = rule
                                    break
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_min' and rule.min_to_available=='less_min' and rule.req_to_available=='more_avail':
                                if qty_in_product_uom > product.min_qty and product.min_qty <= product.available and qty_in_product_uom <= product.available:
                                    price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                    suitable_rule = rule
                                    break
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_req' and rule.min_to_available=='less_min' and rule.req_to_available=='less_avail':
                                if qty_in_product_uom <= product.min_qty and product.min_qty <= product.available and qty_in_product_uom > product.available:
                                    price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                    suitable_rule = rule
                                    break
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_req' and rule.min_to_available=='less_min' and rule.req_to_available=='more_avail' and (product.price_diff >= rule.min_price_diff) and (product.price_diff <= rule.max_price_diff):
                                if qty_in_product_uom <= product.min_qty and product.min_qty <= product.available and qty_in_product_uom <= product.available:
                                    price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                    suitable_rule = rule
                                    break
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_req' and rule.min_to_available=='less_available' and rule.req_to_available=='less_avail':
                                if qty_in_product_uom <= product.min_qty and product.min_qty > product.available and qty_in_product_uom > product.available:
                                    price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                    suitable_rule = rule
                                    break
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_req' and rule.min_to_available=='less_available' and rule.req_to_available=='more_avail' and (product.price_diff >= rule.min_price_diff) and (product.price_diff <= rule.max_price_diff):
                                if qty_in_product_uom <= product.min_qty and product.min_qty > product.available and qty_in_product_uom <= product.available:
                                    price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                    suitable_rule = rule
                                    break
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_min' and rule.min_to_available=='less_min':
                                if not rule.req_to_available:
                                    if qty_in_product_uom > product.min_qty and product.min_qty <= product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_min' and rule.min_to_available=='less_available':
                                if not rule.req_to_available:
                                    if qty_in_product_uom > product.min_qty and product.min_qty > product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_req' and rule.min_to_available=='less_min' and (product.price_diff >= rule.min_price_diff) and (product.price_diff <= rule.max_price_diff):
                                if not rule.req_to_available:
                                    if product.min_qty and qty_in_product_uom <= product.min_qty and product.min_qty <= product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_req' and rule.min_to_available=='less_available' and (product.price_diff >= rule.min_price_diff) and (product.price_diff <= rule.max_price_diff):
                                if not rule.req_to_available:
                                    if product.min_qty and qty_in_product_uom <= product.min_qty and product.min_qty > product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_req' and rule.req_to_available=='less_avail':
                                if not rule.min_to_available:
                                    if qty_in_product_uom <= product.min_qty and qty_in_product_uom > product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_req' and rule.req_to_available=='more_avail' and (product.price_diff >= rule.min_price_diff) and (product.price_diff <= rule.max_price_diff):
                                if not rule.min_to_available:
                                    if qty_in_product_uom <= product.min_qty and qty_in_product_uom <= product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_min' and rule.req_to_available=='more_avail':
                                if not rule.min_to_available:
                                    if qty_in_product_uom > product.min_qty and qty_in_product_uom <= product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_min' and rule.req_to_available=='less_avail':
                                if not rule.min_to_available:
                                    if qty_in_product_uom > product.min_qty and qty_in_product_uom > product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_req' and (product.price_diff <= rule.min_price_diff):
                                continue
                            elif rule.factor and rule.req_to_available == 'more_avail' and (product.price_diff <= rule.min_price_diff):
                                continue
                            elif rule.factor and rule.min_to_available=='less_available' and rule.req_to_available == 'more_avail' and (product.price_diff >= rule.min_price_diff) and (product.price_diff <= rule.max_price_diff):
                                if not rule.req_to_min:
                                    if product.min_qty > product.available and qty_in_product_uom <= product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.min_to_available=='less_min' and rule.req_to_available == 'more_avail' and (product.price_diff >= rule.min_price_diff) and (product.price_diff <= rule.max_price_diff):
                                if not rule.req_to_min:
                                    if product.min_qty <= product.available and qty_in_product_uom <= product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.min_to_available=='less_min' and rule.req_to_available == 'less_avail':
                                if not rule.req_to_min:
                                    if product.min_qty <= product.available and qty_in_product_uom > product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.min_to_available=='less_available' and rule.req_to_available == 'less_avail':
                                if not rule.req_to_min:
                                    if product.min_qty > product.available and qty_in_product_uom > product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_min':
                                if not rule.min_to_available and rule.req_to_available:
                                    if qty_in_product_uom > product.min_qty:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.req_to_min == 'less_req' and (product.price_diff >= rule.min_price_diff) and (product.price_diff <= rule.max_price_diff):
                                if not rule.min_to_available and rule.req_to_available:
                                    if qty_in_product_uom <= product.min_qty:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.min_to_available == 'less_available':
                                if not rule.req_to_min and rule.req_to_available:
                                    if product.min_qty > product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.min_to_available == 'less_min':
                                if not rule.req_to_min and rule.req_to_available:
                                    if product.min_qty <= product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.req_to_available == 'more_avail' and (product.price_diff >= rule.min_price_diff) and (product.price_diff <= rule.max_price_diff):
                                if not rule.req_to_min and rule.min_to_available:
                                    if qty_in_product_uom <= product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            elif rule.factor and rule.req_to_available == 'less_avail':
                                if not rule.req_to_min and rule.min_to_available:
                                    if qty_in_product_uom > product.available:
                                        price = product.price_compute(rule.market_type)[product.id] * rule.factor
                                        suitable_rule = rule
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            else:
                                # price = product.price_compute(rule.market_type)[product.id]
                                continue
                        else:
                            continue
                    else:
                        # if base option is public price take sale price else cost price of product
                        # price_compute returns the price in the context UoM, i.e. qty_uom_id
                        price = product.price_compute(rule.base)[product.id]

                    convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))
                    if price is not False:
                        if rule.compute_price == 'fixed':
                            price = convert_to_price_uom(rule.fixed_price)
                        elif rule.compute_price == 'percentage':
                            price = (price - (price * (rule.percent_price / 100))) or 0.0
                        else:
                            # complete formula
                            price_limit = price
                            price = (price - (price * (rule.price_discount / 100))) or 0.0
                            if rule.price_round:
                                price = tools.float_round(price, precision_rounding=rule.price_round)

                            if rule.price_surcharge:
                                price_surcharge = convert_to_price_uom(rule.price_surcharge)
                                price += price_surcharge

                            if rule.price_min_margin:
                                price_min_margin = convert_to_price_uom(rule.price_min_margin)
                                price = max(price, price_limit + price_min_margin)

                            if rule.price_max_margin:
                                price_max_margin = convert_to_price_uom(rule.price_max_margin)
                                price = min(price, price_limit + price_max_margin)
                        suitable_rule = rule
                # Final price conversion into pricelist currency
                if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                    if suitable_rule.base == 'standard_price':
                        cur = product.cost_currency_id
                    elif suitable_rule.base == 'market_price':
                        if suitable_rule.market_type == 'last_purchase_price':
                            if not self.currency_id == product.last_po_currency:
                                cur = product.last_po_currency
                                price = cur._convert(price, self.currency_id, self.env.user.company_id, date, round=False)
                        elif suitable_rule.market_type == 'market_price':
                            if not self.currency_id == product.market_price_currency:
                                cur = product.market_price_currency
                                price = cur._convert(price, self.currency_id, self.env.user.company_id, date, round=False)

                # if product.market_price_currency.id != self.currency_id.id:
                #     price = product.market_price_currency._convert(price, self.currency_id, self.env.user.company_id, date, round=False)

                results[product.id] = (price, suitable_rule and suitable_rule.id or False)

            if dropship in product.route_ids.ids:
                dropship_rules = items.filtered(lambda rule: rule.dropship)
                compute_price_ct(dropship_rules)
            elif product.last_purchase_price==0.00:
                last_po_0_rules = items.filtered(lambda rule: rule.last_po_0)
                compute_price_ct(last_po_0_rules)
            elif product.available ==0.00:
                available_rules = items.filtered(lambda rule: rule.available_is_0)
                compute_price_ct(available_rules)
            else:
                compute_price_ct(items.filtered(lambda rule: rule.available_is_0==False and rule.dropship==False and rule.last_po_0==False))

        return results
