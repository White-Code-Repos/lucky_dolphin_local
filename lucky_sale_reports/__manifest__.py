# -*- coding: utf-7 -*-
{
    'name': 'Lucky Dolphin Sale Reports',
    'summary': 'Lucky Dolphin Sale Reports',

    'description': """
        This module add the following features in sale module
            1- Xls report for sale order.\n
            2- Send multiple quotations by mail with xls files.\n
    """,
    'depends': ['sale_management', 'report_xlsx'],
    'data': [
        # data
        'data/mail_template_data_view.xml',
        # views
        'views/sale_order_inherit_view.xml',
        # reports
        'reports/sale_order_xls_report_view.xml',
    ],

    'installable': True,
    'auto_install': False,
    'sequence': 1
}
