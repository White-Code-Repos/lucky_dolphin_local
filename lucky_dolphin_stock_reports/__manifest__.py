# -*- coding: utf-7 -*-
{
    'name': 'Lucky Dolphin Stock Reports',
    'summary': 'Lucky Dolphin Stock Reports',

    'description': """
        This module add the following features in sale module
            1- Make changes in delivery Slips\n
    """,
    'depends': ['stock'],
    'data': [
        # reports
        'reports/report_deliveryslip_doc.xml',
        'reports/report_views.xml',
    ],

    'installable': True,
    'auto_install': False,
    'sequence': 1
}