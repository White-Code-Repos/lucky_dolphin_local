# -*- coding: utf-8 -*-
{
    'name': 'Lucky Dolphin Sale Stock',
    'summary': 'Lucky Dolphin Sale Stock',

    'description': """
        This module add the following features in sale module
            1- Add price list lines depend on product qty.\n
            2- Edit price in sale order line depend on product qty and price list.\n
    """,
    'depends': ['sale_management', 'stock', 'purchase', ],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/product_pricelist_line_view.xml',
        'views/product_pricelist_inherit_view.xml',

    ],

    'installable': True,
    'auto_install': False,
    'sequence': 1
}
