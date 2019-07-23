# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class SaleForecastingReportXls(models.AbstractModel):
    _inherit = 'report.report_xlsx.abstract'
    _name = 'report.lucky_sale_reports.sale_order_xls_report'

    def generate_xlsx_report(self, workbook, data, sale_orders):
        worksheet = workbook.add_worksheet("Sale Order Report")
        f1 = workbook.add_format({'bold': True, 'font_color': 'black', })
        f2 = workbook.add_format({'font_color': 'black', })
        f3 = workbook.add_format({'font_color': 'black', 'border': True, 'bold': True})
        f4 = workbook.add_format({'font_color': 'black', 'border': True, })
        report_line_number = 1
        line_number = 0
        for sale_order in sale_orders:
            # partner address
            partner_address = ''
            if sale_order.partner_id.zip:
                partner_address += str(sale_order.partner_id.zip) + ' '
            if sale_order.partner_id.city:
                partner_address += str(sale_order.partner_id.city) + ' , '
            if sale_order.partner_id.state_id:
                partner_address += str(sale_order.partner_id.state_id.name)

            worksheet.write(report_line_number, 5, sale_order.partner_id.name, f2)
            report_line_number += 1
            worksheet.write(report_line_number, 5, sale_order.partner_id.street, f2)
            report_line_number += 1
            worksheet.write(report_line_number, 5, partner_address, f2)
            report_line_number += 1
            worksheet.write(report_line_number, 5, sale_order.partner_id.country_id.name, f2)
            if sale_order.partner_id.vat:
                worksheet.write(report_line_number, 5, "Tax ID :" + sale_order.partner_id.vat, f2)
                report_line_number += 1

            # order details
            if sale_order.state in ['draft', 'sent']:
                worksheet.write(report_line_number, 0, "Quotation #" + sale_order.name, f1)
                report_line_number += 1

            elif sale_order.state not in ['draft', 'sent']:
                worksheet.write(report_line_number, 0, "Order #" + sale_order.name, f1)
                report_line_number += 1

            if sale_order.client_order_ref:
                worksheet.write(report_line_number, 0, "Your Reference : ", f2)
                worksheet.write(report_line_number + 1, 0, sale_order.client_order_ref, f2)

            if sale_order.confirmation_date and sale_order.state not in ['draft', 'sent']:
                worksheet.write(report_line_number, 1,
                                "Date Ordered : ", f2)
                worksheet.write(report_line_number + 1, 1,
                                fields.Datetime.to_string(sale_order.confirmation_date), f2)

            if sale_order.date_order and sale_order.state in ['draft', 'sent']:
                worksheet.write(report_line_number, 2,
                                "Quotation Date : ", f2)
                worksheet.write(report_line_number + 1, 2,
                                fields.Datetime.to_string(sale_order.date_order), f2)

            if sale_order.user_id.name:
                worksheet.write(report_line_number, 3, "Salesperson : ", f2)
                worksheet.write(report_line_number + 1, 3, sale_order.user_id.name, f2)

            if sale_order.payment_term_id.name:
                worksheet.write(report_line_number, 4, "Payment Terms : ", f2)
                worksheet.write(report_line_number + 1, 4, sale_order.payment_term_id.name, f2)

            if sale_order.validity_date and sale_order.state in ['draft', 'sent']:
                worksheet.write(report_line_number, 5,
                                "Expiration Date : ", f2)
                worksheet.write(report_line_number + 1, 5,
                                fields.Date.to_string(sale_order.validity_date), f2)
            report_line_number += 3
            worksheet.write(report_line_number, 0, "Description", f3)
            worksheet.write(report_line_number, 1, "Quantity", f3)
            worksheet.write(report_line_number, 2, "Unit Price", f3)
            worksheet.write(report_line_number, 3, "Disc.(%)", f3)
            worksheet.write(report_line_number, 4, "Taxes", f3)
            if self.env.user.has_group('account.group_show_line_subtotals_tax_excluded'):
                worksheet.write(report_line_number, 5, "Amount", f3)
            if self.env.user.has_group('account.group_show_line_subtotals_tax_included'):
                worksheet.write(report_line_number, 6, "Total Price", f3)
            report_line_number += 1
            line_number = report_line_number
            for line in sale_order.order_line:
                worksheet.write(line_number, 0, line.name, f4)
                if self.env.user.has_group('uom.group_uom'):
                    worksheet.write(line_number, 1, str(line.product_uom_qty) + line.product_uom.name, f4)
                else:
                    worksheet.write(line_number, 1, line.product_uom_qty, f4)

                worksheet.write(line_number, 2, line.price_unit, f4)

                if self.env.user.has_group('sale.group_discount_per_so_line'):
                    worksheet.write(line_number, 3, line.discount, f4)
                else:
                    worksheet.write(line_number, 3, ' ', f4)
                worksheet.write(line_number, 4, ', '.join(map(lambda x: (x.description or x.name), line.tax_id)),
                                f4)
                if self.env.user.has_group('account.group_show_line_subtotals_tax_excluded'):
                    worksheet.write(line_number, 5,
                                    str(line.price_subtotal) + ' ' + str(sale_order.pricelist_id.currency_id.symbol),
                                    f4)
                if self.env.user.has_group('account.group_show_line_subtotals_tax_included'):
                    worksheet.write(line_number, 6,
                                    str(line.price_total) + ' ' + str(sale_order.pricelist_id.currency_id.symbol), f4)
                line_number += 1

            worksheet.write(line_number, 4, "Subtotal", f1)
            worksheet.write(line_number, 5,
                            str(sale_order.amount_untaxed) + ' ' + str(sale_order.pricelist_id.currency_id.symbol), f2)
            line_number += 1

            for amount_by_group in sale_order.amount_by_group:
                worksheet.write(line_number, 4, amount_by_group[0], f1)
                worksheet.write(line_number, 5,
                                str(amount_by_group[1]) + ' ' + str(sale_order.pricelist_id.currency_id.symbol), f2)
                line_number += 1

            worksheet.write(line_number, 4, "Total", f1)
            worksheet.write(line_number, 5,
                            str(sale_order.amount_total) + ' ' + str(sale_order.pricelist_id.currency_id.symbol), f2)
            line_number += 1

            if sale_order.note:
                worksheet.write(line_number, 0,
                                'Note : ' + sale_order.note, f2)
                line_number += 1

            if sale_order.fiscal_position_id and sale_order.fiscal_position_id.note:
                worksheet.write(line_number, 0,
                                'Fiscal Position Remark : ' + sale_order.fiscal_position_id.note, f2)
                line_number += 1

            if sale_order.signature:
                worksheet.write(line_number, 0,
                                'Signature : ' + sale_order.signed_by, f2)
                line_number += 1

            report_line_number = line_number + 2
