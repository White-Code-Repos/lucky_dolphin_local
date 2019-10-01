# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

{
    'name': 'Request Diiference',
    'author': 'Divya Vyas',
    'description': """
================================================================================
If request difference checked in product, the system will check the difference between requested quantity in confirmed sale order and forecasted quantity and make an RFQ with the difference for all products in separated RFQs per vendor line inside product
================================================================================
""",
    'depends': ['base', 'sale','purchase','purchase','product'],
    'version': '12.0.1.0.0',
    'data': [
	'views/inherit_product_template_view.xml',
      ],
    'installable': True,
}
