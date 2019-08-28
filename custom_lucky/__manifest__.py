# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

{
    'name': 'Custom Lucky Modules',
    'author': 'Divya Vyas',
    'description': """
================================================================================

1. add field in sales.
2.request Price

================================================================================
""",
    'depends': ['base', 'sale','sale_management','delivery','purchase','product','sale_margin'],
    'version': '12.0.1.0.0',
    'data': [
	 'security/ir.model.access.csv',
	'views/inherit_product_template_view.xml',
	'views/inherit_sale_order_view.xml',	
	'views/inherit_product_pricelist_view.xml',
	'views/inherit_purchase_order.xml',
      ],
    'installable': True,
}
