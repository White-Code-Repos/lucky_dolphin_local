# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

{
    'name': 'Custom WhiteCode',
    'author': 'Divya Vyas',
    'description': """
================================================================================

1. add field in sales.

================================================================================
""",
    'depends': ['base', 'sale','contacts','sale_management','delivery','lucky_sales','custom_lucky'],
    'version': '12.0.1.0.0',
    'data': [
	'security/ir.model.access.csv',
        'views/quotation_comment_view.xml',
	'views/sale_order_report_templates.xml',
        'views/inherit_sale_view.xml',
	'views/delivery_carrier_view.xml',
      ],
    'installable': True,
}
