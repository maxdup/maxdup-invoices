import locale

from InvoiceGenerator.api import Invoice
from InvoiceGenerator.pdf import SimpleInvoice, prepare_invoice_draw, currency
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from operator import mul


class MyInvoice(SimpleInvoice):
    def gen(self, filename):
        self.filename = filename
        prepare_invoice_draw(self)

        self._drawMain()
        self._drawTitle()

        self._drawProvider(self.TOP - 25, self.LEFT + 3)
        self._drawClient(self.TOP - 25, self.LEFT + 91)

        self._drawDates(self.TOP - 7, self.LEFT + 90)
        self._drawItems(self.TOP - 55, self.LEFT)

        self.pdf.showPage()
        self.pdf.save()

    def _drawCreator(self, TOP, LEFT):
        return

    def _drawMain(self):
        # Borders
        self.pdf.rect(
            self.LEFT * mm,
            (self.TOP - 45) * mm,
            (self.LEFT + 156) * mm,
            30 * mm,
            stroke=True,
            fill=False,
        )
        path = self.pdf.beginPath()
        path.moveTo((self.LEFT + 88) * mm, (self.TOP - 15) * mm)
        path.lineTo((self.LEFT + 88) * mm, (self.TOP - 45) * mm)
        self.pdf.drawPath(path, True, True)

    def _drawClient(self, TOP, LEFT):
        self._drawAddress(TOP, LEFT + 2, 88, 36,
                          'Customer', self.invoice.client)

    def _drawProvider(self, TOP, LEFT):
        self._drawAddress(TOP, LEFT + 2, 88, 36,
                          'Provider', self.invoice.provider)

    def _drawTitle(self):
        self.pdf.drawString(self.LEFT*mm, self.TOP*mm, self.invoice.title)
        self.pdf.drawString((self.LEFT + 90) * mm,
                            self.TOP*mm,
                            'Invoice num.: %s' % self.invoice.number)

    def _drawItemsHeader(self,  TOP,  LEFT):
        path = self.pdf.beginPath()
        path.moveTo(LEFT * mm, (TOP - 4) * mm)
        path.lineTo((LEFT + 176) * mm, (TOP - 4) * mm)
        self.pdf.drawPath(path, True, True)

        self.pdf.setFont('DejaVu-Bold', 7)
        self.pdf.drawString((LEFT + 1) * mm, (TOP - 2)
                            * mm, _(u'List of items'))

        self.pdf.drawString((LEFT + 1) * mm, (TOP - 9) * mm, _(u'Description'))
        items_are_with_tax = self.invoice.use_tax
        if items_are_with_tax:
            i = 9
            self.pdf.drawRightString(
                (LEFT + 73) * mm, (TOP - i) * mm, _(u'Units'))
            self.pdf.drawRightString(
                (LEFT + 88) * mm,
                (TOP - i) * mm,
                _(u'Price per one'),
            )
            self.pdf.drawRightString(
                (LEFT + 115) * mm,
                (TOP - i) * mm,
                _(u'Total price'),
            )
            self.pdf.drawRightString(
                (LEFT + 137) * mm,
                (TOP - i) * mm,
                _(u'Tax'),
            )
            self.pdf.drawRightString(
                (LEFT + 146) * mm,
                (TOP - i) * mm,
                _(u'Total price with tax'),
            )
            i += 5
        else:
            i = 9
            self.pdf.drawRightString(
                (LEFT + 135) * mm,
                (TOP - i) * mm,
                _(u'Hours'),
            )
            self.pdf.drawRightString(
                (LEFT + 158) * mm,
                (TOP - i) * mm,
                _(u'Hourly Rate'),
            )
            self.pdf.drawRightString(
                (LEFT + 173) * mm,
                (TOP - i) * mm,
                _(u'Total'),
            )
            i += 5
        return i

    def _drawItems(self, TOP, LEFT):  # noqa

        # Items
        i = self._drawItemsHeader(TOP, LEFT)
        self.pdf.setFont('DejaVu', 7)

        items_are_with_tax = self.invoice.use_tax

        # List
        will_wrap = False
        for item in self.invoice.items:
            if TOP - i < 30 * mm:
                will_wrap = True

            style = ParagraphStyle('normal', fontName='DejaVu', fontSize=7)
            p = Paragraph(item.description, style)
            p2 = Paragraph(item.commits, style)

            pwidth, pheight = p.wrapOn(
                self.pdf, 70*mm if items_are_with_tax else 120*mm, 30*mm)
            i_add = max(float(pheight)/mm, 4.23)

            pwidth2, pheight2 = p2.wrapOn(
                self.pdf, 70*mm if items_are_with_tax else 115*mm, 30*mm)
            i_add2 = max(float(pheight2)/mm, 4.23)

            if will_wrap and TOP - i - i_add - i_add2 < 8 * mm:
                will_wrap = False
                self.pdf.rect(LEFT * mm, (TOP - i) * mm, (LEFT + 156)
                              * mm, (i + 2) * mm, stroke=True, fill=False)  # 140,142
                self.pdf.showPage()

                i = self._drawItemsHeader(self.TOP, LEFT)
                TOP = self.TOP
                self.pdf.setFont('DejaVu', 7)

            # leading line
            path = self.pdf.beginPath()
            path.moveTo(LEFT * mm, (TOP - i + 3.5) * mm)
            path.lineTo((LEFT + 176) * mm, (TOP - i + 3.5) * mm)
            self.pdf.setLineWidth(0.1)
            self.pdf.drawPath(path, True, True)
            self.pdf.setLineWidth(1)

            i += i_add
            p.drawOn(self.pdf, (LEFT + 1) * mm, (TOP - i + 3) * mm)
            i += i_add2
            p2.drawOn(self.pdf, (LEFT + 5) * mm, (TOP - (i) + 3) * mm)

            i1 = i - i_add2
            i1 -= 4.23

            if items_are_with_tax:
                if float(int(item.count)) == item.count:
                    self.pdf.drawRightString((LEFT + 85) * mm, (TOP - i1) * mm, u'%s %s' % (
                        locale.format("%i1", item.count, grouping=True), item.unit))
                else:
                    self.pdf.drawRightString((LEFT + 85) * mm, (TOP - i1) * mm, u'%s %s' % (
                        locale.format("%.2f", item.count, grouping=True), item.unit))
                self.pdf.drawRightString((LEFT + 110) * mm, (TOP - i1) * mm, currency(
                    item.price, self.invoice.currency, self.invoice.currency_locale))
                self.pdf.drawRightString((LEFT + 134) * mm, (TOP - i1) * mm, currency(
                    item.total, self.invoice.currency, self.invoice.currency_locale))
                self.pdf.drawRightString(
                    (LEFT + 144) * mm, (TOP - i1) * mm, '%.0f %%' % item.tax)
                self.pdf.drawRightString((LEFT + 173) * mm, (TOP - i1) * mm, currency(
                    item.total_tax, self.invoice.currency, self.invoice.currency_locale))
                i1 += 5
            else:
                if float(int(item.count)) == item.count:
                    self.pdf.drawRightString((LEFT + 135) * mm, (TOP - i1) * mm, u'%s %s' % (
                        locale.format("%i1", item.count, grouping=True), item.unit))
                else:
                    self.pdf.drawRightString((LEFT + 135) * mm, (TOP - i1) * mm, u'%s %s' % (
                        locale.format("%.2f", item.count, grouping=True), item.unit))
                self.pdf.drawRightString((LEFT + 156) * mm, (TOP - i1) * mm, currency(
                    item.price, self.invoice.currency, self.invoice.currency_locale))
                self.pdf.drawRightString((LEFT + 173) * mm, (TOP - i1) * mm, currency(
                    item.total, self.invoice.currency, self.invoice.currency_locale))
                i1 += 5

        if will_wrap:
            self.pdf.rect(LEFT * mm, (TOP - i) * mm, (LEFT + 156)
                          * mm, (i + 2) * mm, stroke=True, fill=False)  # 140,142
            self.pdf.showPage()

            i = 0
            TOP = self.TOP
            self.pdf.setFont('DejaVu', 7)

        if self.invoice.rounding_result:
            path = self.pdf.beginPath()
            path.moveTo(LEFT * mm, (TOP - i) * mm)
            path.lineTo((LEFT + 176) * mm, (TOP - i) * mm)
            i += 5
            self.pdf.drawPath(path, True, True)
            self.pdf.drawString((LEFT + 1) * mm, (TOP - i) * mm, _(u'Rounding'))
            self.pdf.drawString((LEFT + 68) * mm, (TOP - i) * mm, currency(
                self.invoice.difference_in_rounding, self.invoice.currency, self.invoice.currency_locale))
            i += 3

        path = self.pdf.beginPath()
        path.moveTo(LEFT * mm, (TOP - i) * mm)
        path.lineTo((LEFT + 176) * mm, (TOP - i) * mm)
        self.pdf.drawPath(path, True, True)

        if not items_are_with_tax:
            self.pdf.setFont('DejaVu-Bold', 11)
            self.pdf.drawString((LEFT + 100) * mm, (TOP - i - 7) * mm, '%s: %s' % (_(u'Total'),
                                                                                   currency(self.invoice.price, self.invoice.currency, self.invoice.currency_locale)))
        else:
            self.pdf.setFont('DejaVu-Bold', 6)
            self.pdf.drawString((LEFT + 1) * mm, (TOP - i - 2)
                                * mm, _(u'Breakdown VAT'))
            vat_list, tax_list, total_list, total_tax_list = [_(u'VAT rate')], [_(u'Tax')], [
                _(u'Without VAT')], [_(u'With VAT')]
            for vat, items in self.invoice.generate_breakdown_vat().items():
                vat_list.append("%s%%" % locale.format('%.2f', vat))
                tax_list.append(
                    currency(items['tax'], self.invoice.currency, self.invoice.currency_locale))
                total_list.append(
                    currency(items['total'], self.invoice.currency, self.invoice.currency_locale))
                total_tax_list.append(currency(
                    items['total_tax'], self.invoice.currency, self.invoice.currency_locale))

            self.pdf.setFont('DejaVu', 6)
            text = self.pdf.beginText((LEFT + 1) * mm, (TOP - i - 5) * mm)
            text.textLines(vat_list)
            self.pdf.drawText(text)

            text = self.pdf.beginText((LEFT + 11) * mm, (TOP - i - 5) * mm)
            text.textLines(tax_list)
            self.pdf.drawText(text)

            text = self.pdf.beginText((LEFT + 27) * mm, (TOP - i - 5) * mm)
            text.textLines(total_list)
            self.pdf.drawText(text)

            text = self.pdf.beginText((LEFT + 45) * mm, (TOP - i - 5) * mm)
            text.textLines(total_tax_list)
            self.pdf.drawText(text)

            # VAT note
            if self.invoice.client.vat_note:
                text = self.pdf.beginText((LEFT + 1) * mm, (TOP - i - 11) * mm)
                text.textLines([self.invoice.client.vat_note])
                self.pdf.drawText(text)

            self.pdf.setFont('DejaVu-Bold', 11)
            self.pdf.drawString(
                (LEFT + 100) * mm,
                (TOP - i - 14) * mm,
                u'%s: %s' % (_(u'Total with tax'), currency(self.invoice.price_tax, self.invoice.
                                                            currency, self.invoice.currency_locale)),
            )

        if items_are_with_tax:
            self.pdf.rect(LEFT * mm, (TOP - i - 17) * mm, (LEFT + 156)
                          * mm, (i + 19) * mm, stroke=True, fill=False)  # 140,142
        else:
            self.pdf.rect(LEFT * mm, (TOP - i - 11) * mm, (LEFT + 156)
                          * mm, (i + 13) * mm, stroke=True, fill=False)  # 140,142

        self._drawCreator(TOP - i - 20, self.LEFT + 98)
