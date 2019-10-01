{
    'name': 'Lucky Dolphin Sales',
    'depends': ['sale', 'purchase', 'base', 'delivery'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/parcel_view.xml',
        'views/crew_view.xml',
        'views/service_view.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/sale_order_batch_view.xml',
        'views/res_partner_view.xml',
        'views/egypt_ports_view.xml',
        'views/saleorder_report.xml',
        # 'views/report_delivery_slip.xml',
        'report/report_action_operation.xml',
       'views/invoice_report.xml',
        'views/sale_order_batch_report.xml',
    ]
}
