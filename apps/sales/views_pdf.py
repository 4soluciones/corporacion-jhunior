import decimal
import io

import reportlab
from django.conf import settings
from django.http import HttpResponse
from reportlab.graphics.barcode import code93
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.colors import HexColor, white, Color
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Spacer, Image, Flowable
from reportlab.platypus import Table
from reportlab.rl_settings import defaultPageSize

from apps.sales.number_letters import number_money
from .models import Order
from ..accounting.zone import utc_to_local

PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT, leading=8, fontName='Square', fontSize=8))
styles.add(ParagraphStyle(name='Title1', alignment=TA_JUSTIFY, leading=8, fontName='Helvetica', fontSize=12))
styles.add(ParagraphStyle(name='Left-text', alignment=TA_LEFT, leading=8, fontName='Square', fontSize=8))
styles.add(ParagraphStyle(name='Left_Square', alignment=TA_LEFT, leading=10, fontName='Square', fontSize=10))
styles.add(ParagraphStyle(name='Justify_Square', alignment=TA_JUSTIFY, leading=10, fontName='Square', fontSize=10))
styles.add(
    ParagraphStyle(name='Justify_Newgot_title', alignment=TA_JUSTIFY, leading=14, fontName='Newgot', fontSize=14))
styles.add(
    ParagraphStyle(name='Center_Newgot_title', alignment=TA_CENTER, leading=15, fontName='Newgot', fontSize=15))
styles.add(
    ParagraphStyle(name='Center_Newgots', alignment=TA_CENTER, leading=13, fontName='Newgot', fontSize=13))
styles.add(
    ParagraphStyle(name='Center_Newgots_invoice', alignment=TA_CENTER, leading=13, fontName='Newgot', fontSize=13,
                   textColor=white))
styles.add(
    ParagraphStyle(name='Left_Newgots', alignment=TA_LEFT, leading=14, fontName='Newgot', fontSize=13))
styles.add(ParagraphStyle(name='Justify_Newgot', alignment=TA_JUSTIFY, leading=10, fontName='Newgot', fontSize=10))
styles.add(ParagraphStyle(name='Center_Newgot', alignment=TA_CENTER, leading=11, fontName='Newgot', fontSize=11))
styles.add(ParagraphStyle(name='CenterNewgotBold', alignment=TA_CENTER, leading=9, fontName='Newgot', fontSize=9))
styles.add(
    ParagraphStyle(name='CenterNewgotBold_Footer', alignment=TA_CENTER, leading=9, fontName='Newgot', fontSize=6))
styles.add(ParagraphStyle(name='LeftNewgotBold', alignment=TA_LEFT, leading=9, fontName='Newgot', fontSize=9))
styles.add(ParagraphStyle(name='Right_Newgot', alignment=TA_RIGHT, leading=12, fontName='Newgot', fontSize=12))
styles.add(
    ParagraphStyle(name='Justify_Lucida', alignment=TA_JUSTIFY, leading=11, fontName='Lucida-Console', fontSize=11))
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, leading=14, fontName='Square', fontSize=12))
styles.add(ParagraphStyle(name='Justify-Dotcirful', alignment=TA_JUSTIFY, leading=11, fontName='Dotcirful-Regular',
                          fontSize=11))
styles.add(
    ParagraphStyle(name='Justify-Dotcirful-table', alignment=TA_JUSTIFY, leading=12, fontName='Dotcirful-Regular',
                   fontSize=7))
styles.add(ParagraphStyle(name='Justify_Bold', alignment=TA_JUSTIFY, leading=8, fontName='Square-Bold', fontSize=8))
styles.add(ParagraphStyle(name='CenterBold', alignment=TA_CENTER, leading=8, fontName='Square-Bold', fontSize=8))
styles.add(
    ParagraphStyle(name='Justify_Square_Bold', alignment=TA_JUSTIFY, leading=5, fontName='Square-Bold', fontSize=10))
styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, leading=8, fontName='Square', fontSize=8))
styles.add(ParagraphStyle(name='Center_a4', alignment=TA_CENTER, leading=12, fontName='Square', fontSize=12))
styles.add(ParagraphStyle(name='Justify_a4', alignment=TA_JUSTIFY, leading=12, fontName='Square', fontSize=12))
styles.add(
    ParagraphStyle(name='Center-Dotcirful', alignment=TA_CENTER, leading=12, fontName='Dotcirful-Regular', fontSize=10))
styles.add(ParagraphStyle(name='CenterNewgotBoldInvoiceNumber', alignment=TA_CENTER, leading=11, fontName='Newgot',
                          fontSize=11))
styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT, leading=12, fontName='Square', fontSize=12))
styles.add(ParagraphStyle(name='CenterTitle', alignment=TA_CENTER, leading=14, fontName='Square-Bold', fontSize=14))
styles.add(ParagraphStyle(name='CenterTitle-Dotcirful', alignment=TA_CENTER, leading=12, fontName='Dotcirful-Regular',
                          fontSize=10))
styles.add(ParagraphStyle(name='CenterTitle2', alignment=TA_CENTER, leading=8, fontName='Square-Bold', fontSize=12))
styles.add(ParagraphStyle(name='Center_Regular', alignment=TA_CENTER, leading=8, fontName='Ticketing', fontSize=11))
styles.add(ParagraphStyle(name='Center2', alignment=TA_CENTER, leading=8, fontName='Ticketing', fontSize=8))
styles.add(ParagraphStyle(name='Center3', alignment=TA_JUSTIFY, leading=8, fontName='Ticketing', fontSize=7))
styles.add(ParagraphStyle(name='narrow_justify', alignment=TA_JUSTIFY, leading=11, fontName='Narrow', fontSize=10))
styles.add(
    ParagraphStyle(name='narrow_justify_observation', alignment=TA_JUSTIFY, leading=9, fontName='Narrow', fontSize=8))
styles.add(ParagraphStyle(name='narrow_center', alignment=TA_CENTER, leading=10, fontName='Narrow', fontSize=10))
styles.add(ParagraphStyle(name='narrow_center_pie', alignment=TA_CENTER, leading=8, fontName='Narrow', fontSize=8))
styles.add(ParagraphStyle(name='narrow_left', alignment=TA_LEFT, leading=12, fontName='Narrow', fontSize=10))
styles.add(ParagraphStyle(name='narrow_a_justify', alignment=TA_JUSTIFY, leading=10, fontName='Narrow-a', fontSize=9))
styles.add(
    ParagraphStyle(name='narrow_b_justify', alignment=TA_JUSTIFY, leading=11, fontName='Narrow-b',
                   fontSize=10))
styles.add(
    ParagraphStyle(name='narrow_b_tittle_justify', alignment=TA_JUSTIFY, leading=12, fontName='Narrow-b', fontSize=12))
styles.add(ParagraphStyle(name='narrow_b_left', alignment=TA_LEFT, leading=9, fontName='Narrow-b', fontSize=8))
styles.add(ParagraphStyle(name='narrow_c_justify', alignment=TA_JUSTIFY, leading=10, fontName='Narrow-c', fontSize=10))
styles.add(ParagraphStyle(name='narrow_d_justify', alignment=TA_JUSTIFY, leading=10, fontName='Narrow-d', fontSize=10))
style = styles["Normal"]
styles.add(ParagraphStyle(name='CenterNewgotBoldGuideNumber', alignment=TA_CENTER, leading=11, fontName='Newgot',
                          fontSize=11))

reportlab.rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
pdfmetrics.registerFont(TTFont('Narrow', 'Arial Narrow.ttf'))
# pdfmetrics.registerFont(TTFont('Narrow-a', 'ARIALN.TTF'))
pdfmetrics.registerFont(TTFont('Narrow-b', 'ARIALNB.TTF'))
pdfmetrics.registerFont(TTFont('Narrow-c', 'Arialnbi.ttf'))
pdfmetrics.registerFont(TTFont('Narrow-d', 'ARIALNI.TTF'))
pdfmetrics.registerFont(TTFont('Square', 'square-721-condensed-bt.ttf'))
pdfmetrics.registerFont(TTFont('Square-Bold', 'sqr721bc.ttf'))
pdfmetrics.registerFont(TTFont('Newgot', 'newgotbc.ttf'))
pdfmetrics.registerFont(TTFont('Dotcirful-Regular', 'DotcirfulRegular.otf'))
pdfmetrics.registerFont(TTFont('Ticketing', 'ticketing.regular.ttf'))
pdfmetrics.registerFont(TTFont('Lucida-Console', 'lucida-console.ttf'))
pdfmetrics.registerFont(TTFont('Square-Dot', 'square_dot_digital-7.ttf'))
pdfmetrics.registerFont(TTFont('Serif-Dot', 'serif_dot_digital-7.ttf'))
pdfmetrics.registerFont(TTFont('Enhanced-Dot-Digital', 'enhanced-dot-digital-7.regular.ttf'))
pdfmetrics.registerFont(TTFont('Merchant-Copy-Wide', 'MerchantCopyWide.ttf'))
pdfmetrics.registerFont(TTFont('Dot-Digital', 'dot_digital-7.ttf'))
pdfmetrics.registerFont(TTFont('Raleway-Dots-Regular', 'RalewayDotsRegular.ttf'))
pdfmetrics.registerFont(TTFont('Ordre-Depart', 'Ordre-de-Depart.ttf'))
pdfmetrics.registerFont(TTFont('Nationfd', 'Nationfd.ttf'))
pdfmetrics.registerFont(TTFont('Kg-Primary-Dots', 'KgPrimaryDots-Pl0E.ttf'))
pdfmetrics.registerFont(TTFont('Dot-line', 'Dotline-LA7g.ttf'))
pdfmetrics.registerFont(TTFont('Dot-line-Light', 'DotlineLight-XXeo.ttf'))
pdfmetrics.registerFont(TTFont('Jd-Lcd-Rounded', 'JdLcdRoundedRegular-vXwE.ttf'))

logo = "static/assets/pdfimg/logo.png"
watermark = "static/assets/pdfimg/logo.png"


def ticket(request, pk=None):
    order_set = Order.objects.filter(number=pk, type='V')
    order_obj = order_set.first()
    person_obj = order_obj.person
    user_obj = order_obj.user
    w = 2.83 * inch - 4 * 0.05 * inch

    date = utc_to_local(order_obj.update_at)
    document_type = str(order_obj.get_type_display()).upper()
    document_number = 'Nº ' + str(order_obj.number).zfill(6 - len(str(order_obj.number)))
    line = '--------------------------------------------------------------'
    # ------------------------------------------------------------------
    pdf_user = Table(
        [('USUARIO: ', Paragraph(user_obj.first_name.upper(), styles["narrow_b_left"]))] +
        [('FECHA: ',
          date.strftime("%d/%m/%Y") + '  HORA: ' + str(utc_to_local(order_obj.update_at).strftime('%H:%M:%S')))],
        colWidths=[w * 20 / 100, w * 80 / 100])
    style_user = [
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),  # all columns
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('BOTTOMPADDING', (0, 0), (0, -1), -2),  # all columns
        ('BOTTOMPADDING', (1, 0), (1, -1), -2),  # all columns
        ('BOTTOMPADDING', (1, 0), (1, 0), 2),  # all columns
        ('LEFTPADDING', (0, 0), (0, -1), 2),  # first column
        ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), -3),
        # ('RIGHTPADDING', (1, 0), (1, -1), 0.5),  # second column
    ]
    pdf_user.setStyle(TableStyle(style_user))
    # ------------------------------------------------------------------
    if person_obj:
        pdf_person = Table(
            [('CLIENTE: ', Paragraph(person_obj.names.upper(), styles["narrow_b_left"]))] +
            [(person_obj.get_document_display() + ':', person_obj.number)],
            colWidths=[w * 20 / 100, w * 80 / 100])
        style_person = [
            ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),  # all columns
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),  # all columns
            ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
            ('BOTTOMPADDING', (0, 0), (0, -1), 0),  # all columns
            ('BOTTOMPADDING', (1, 0), (1, -1), 0),  # all columns
            ('BOTTOMPADDING', (1, 0), (1, 0), 4),  # all columns
            ('LEFTPADDING', (0, 0), (0, -1), 2),  # first column
            ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),  # second column
            # ('RIGHTPADDING', (1, 0), (1, -1), 0.5),  # second column
        ]
        pdf_person.setStyle(TableStyle(style_person))
    # ----------------------------------------------------------------
    # style_header = [
    #     ('FONTNAME', (0, 0), (-1, -1), 'Ticketing'),  # all columns
    #     ('FONTSIZE', (0, 0), (-1, -1), 9),  # all columns
    #     ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#0362BB')),  # all columns
    #     ('BACKGROUND', (0, 0), (-1, 1), HexColor('#0362BB')),
    #     ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
    #     ('BOTTOMPADDING', (0, 0), (-1, -1), 1),  # all columns
    #     ('TOPPADDING', (0, 0), (-1, -1), 1),  # all columns
    #     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
    #     ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
    # ]
    # pdf_header = Table(
    #     [('DESCRIPCIÓN', 'CANT', 'UM', 'PRECIO', 'IMPORTE')],
    #     colWidths=[w * 43 / 100, w * 11 / 100, w * 10 / 100, w * 18 / 100, w * 18 / 100]
    # )
    # pdf_header.setStyle(TableStyle(style_header))
    # -------------------------------------------------------------------
    # row = []
    # total = round(decimal.Decimal(0.00), 2)
    # for d in order_obj.orderdetail_set.all():
    #     product = Paragraph(str(d.product.name).capitalize(), styles["Left-text"])
    #     unit = d.get_unit_display()
    #     price = round(decimal.Decimal(d.price), 2)
    #     quantity = round(decimal.Decimal(d.quantity), 2)
    #     amount = round(decimal.Decimal(d.quantity * d.price), 2)
    #     row.append((product, str(round(quantity, 2)), str(unit), str(price), str(amount)))
    #     total = total + amount
    # pdf_detail = Table(row, colWidths=[w * 43 / 100, w * 11 / 100, w * 10 / 100, w * 18 / 100, w * 18 / 100])
    # style_detail = [
    #     ('FONTNAME', (0, 0), (-1, -1), 'Square'),
    #     ('FONTSIZE', (0, 0), (-1, -1), 8),
    #     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    #     ('TOPPADDING', (0, 0), (-1, -1), 1),
    #     ('TOPPADDING', (0, 0), (0, -1), -3),
    #     ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    #     ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
    #     ('ALIGNMENT', (1, 0), (2, -1), 'CENTER'),
    #     ('ALIGNMENT', (3, 0), (4, -1), 'RIGHT'),
    #     ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    #     ('LEFTPADDING', (0, 0), (-1, -1), 2),
    #     ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#9E9E9E')),
    # ]
    # pdf_detail.setStyle(TableStyle(style_detail))
    # --------------------------------------------------------------------------
    totals = [
        # ['SUBTOTAL', str(round(decimal.Decimal(order_obj.total) - decimal.Decimal(order_obj.total_discount), 2))],
        # ['DESCUENTO', str(round(decimal.Decimal(order_obj.total_discount), 2))],
        ['TOTAL ', ' S/. ' + str(round(decimal.Decimal(order_obj.total), 2))]
    ]

    pdf_total = Table(totals, colWidths=[w * 20 / 100, w * 20 / 100])

    total_style = [
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
        ('ALIGNMENT', (1, 0), (1, -1), 'RIGHT'),
        # ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#9E9E9E')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
    ]
    pdf_total.setStyle(TableStyle(total_style))

    # pdf_total_letter = 'SON: ' + str(
    #     number_money(round(decimal.Decimal(order_obj.total), 2), str(order_obj.get_coin_display())))
    # -----------------------------------------------------------------------------------------------
    # style_qr = [
    #     ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),   # all columns
    #     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
    #     ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # first column
    #     ('TOPPADDING', (0, 0), (-1, -1), 0),
    #     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    #     ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
    #     ('FONTSIZE', (0, 0), (-1, -1), 30),
    # ]
    # datatable = code93.Standard93(str(order_obj.number).zfill(6 - len(str(order_obj.number))))
    # pdf_bar = Table([('', datatable, '')], colWidths=[w * 5 / 100, w * 90 / 100, w * 5 / 100])
    # pdf_bar.setStyle(TableStyle(style_qr))
    # -----------------------------------------------------------------------------------------------
    style_qr = [
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),   # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # first column
        ('TOPPADDING', (0, 0), (-1, -1), -10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), -10),
    ]
    qr_text = str(str(order_obj.number).zfill(6 - len(str(order_obj.number))))
    pdf_qr = Table([('', get_qr(qr_text), '')], colWidths=[w * 5 / 100, w * 90 / 100, w * 5 / 100])
    pdf_qr.setStyle(TableStyle(style_qr))
    # -----------------------------------------------------------------------------------------------
    buff = io.BytesIO()

    ml = 0.0 * inch
    mr = 0.0 * inch
    ms = 0.0 * inch
    mi = 0.03 * inch

    doc = SimpleDocTemplate(buff,
                            pagesize=(2.83 * inch, 11.6 * inch),
                            rightMargin=mr,
                            leftMargin=ml,
                            topMargin=ms,
                            bottomMargin=mi,
                            title=str(order_obj.get_type_display()) + "-" + str(
                                str(order_obj.number).zfill(6 - len(str(order_obj.number))))
                            )
    pdf = []
    pdf.append(Paragraph(document_type, styles["Center_Newgot"]))
    pdf.append(Spacer(1, 3))
    pdf.append(Paragraph(document_number, styles["Center_Newgot"]))
    pdf.append(Spacer(1, -2))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(pdf_user)
    pdf.append(Spacer(1, -4))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    if person_obj:
        pdf.append(pdf_person)
    pdf.append(pdf_total)
    pdf.append(Spacer(1, -3))
    # pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    # pdf.append(pdf_bar)
    # pdf.append(Spacer(1, -4))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(pdf_qr)
    pdf.append(Spacer(1, -4))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(Paragraph("www.4soluciones.net", styles["CenterNewgotBold_Footer"]))
    doc.build(pdf)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ventas_{}.pdf"'.format(order_obj.number)
    response.write(buff.getvalue())
    buff.close()
    return response


def quotation(request, pk=None):
    order_set = Order.objects.filter(number=pk, type='T')
    order_obj = order_set.first()
    subsidiary_obj = order_obj.subsidiary
    person_obj = order_obj.person
    user_obj = order_obj.user
    w = 2.83 * inch - 4 * 0.05 * inch
    title_business = str(subsidiary_obj.business_name) + '\n' + str(
        subsidiary_obj.address) + '\n RUC ' + str(
        subsidiary_obj.ruc) + '\n TELF. ' + str(subsidiary_obj.phone)
    date = utc_to_local(order_obj.update_at)
    document_type = str('COTIZACIÓN').upper()
    document_number = 'Nº ' + str(order_obj.number).zfill(7)
    line = '--------------------------------------------------------------'
    I = Image(logo)
    I.drawHeight = 4.0 * inch / 2.9
    I.drawWidth = 5.0 * inch / 2.9
    # ------------------------------------------------------------------
    pdf_user = Table(
        [('USUARIO: ', Paragraph(user_obj.first_name.upper(), styles["narrow_b_left"]))] +
        [('FECHA: ',
          date.strftime("%d/%m/%Y") + '  HORA: ' + str(utc_to_local(order_obj.update_at).strftime('%H:%M:%S')))] +
        [('COTIZACIÓN Nº: ', str(order_obj.number).zfill(7))],
        colWidths=[w * 25 / 100, w * 75 / 100])
    style_user = [
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),  # all columns
        ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),  # all columns
        ('FONTNAME', (0, 3), (-1, -1), 'Narrow-b'),  # all columns
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('BOTTOMPADDING', (0, 0), (0, -1), 0),  # all columns
        ('BOTTOMPADDING', (1, 0), (1, -1), 0),  # all columns
        ('BOTTOMPADDING', (1, 0), (1, 0), 4),  # all columns
        ('LEFTPADDING', (0, 0), (0, -1), 2),  # first column
        ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),  # second column
        # ('RIGHTPADDING', (1, 0), (1, -1), 0.5),  # second column
    ]
    pdf_user.setStyle(TableStyle(style_user))
    # ------------------------------------------------------------------
    client_name = '-'
    client_doc = 'DNI'
    client_number = '-'
    client_address = '-'
    if person_obj:
        client_name = Paragraph(person_obj.names.upper(), styles["narrow_b_left"])
        client_doc = person_obj.get_document_display()
        client_number = Paragraph(person_obj.number, styles["narrow_b_left"])
        client_address = Paragraph(person_obj.address.upper(), styles["narrow_b_left"])
    pdf_person = Table(
        [('CLIENTE: ', client_name)] +
        [(client_doc + ':', client_number)] +
        [('DIRECCIÓN: ', client_address)],
        # [('FECHA EMISIÓN: ', date.strftime("%d/%m/%Y"))] +
        # [('MONEDA: ', 'SOLES')],
        colWidths=[w * 20 / 100, w * 80 / 100])
    style_person = [
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),  # all columns
        ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),  # all columns
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('BOTTOMPADDING', (0, 0), (0, -1), -4),  # all columns
        ('BOTTOMPADDING', (1, 0), (1, -1), -4),  # all columns
        ('BOTTOMPADDING', (1, 2), (1, 2), 1),  # all columns
        ('BOTTOMPADDING', (1, 0), (1, 1), 1),  # all columns
        ('LEFTPADDING', (0, 0), (0, -1), 2),  # first column
        ('LEFTPADDING', (1, 0), (1, -1), 2),  # first column
        ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),  # second column
        # ('RIGHTPADDING', (1, 0), (1, -1), 0.5),  # second column
    ]
    pdf_person.setStyle(TableStyle(style_person))
    # ----------------------------------------------------------------
    style_header = [
        ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
        # ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#9E9E9E')),  # all columns
        ('BACKGROUND', (0, 0), (-1, 1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),  # all columns
        ('TOPPADDING', (0, 0), (-1, -1), 1),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
    ]
    pdf_header = Table(
        [('DESCRIPCIÓN', 'CANT', 'P/U', 'TOTAL')],
        colWidths=[w * 47 / 100, w * 15 / 100, w * 16 / 100, w * 22 / 100]
    )
    pdf_header.setStyle(TableStyle(style_header))
    # -------------------------------------------------------------------
    row = []
    total = round(decimal.Decimal(0.00), 4)
    for d in order_obj.orderdetail_set.filter(is_invoice=False, is_state=True):
        product = Paragraph(str(d.product.code) + ' ' + str(d.product.name).upper() + ' ' + str(
            d.product.measure() + ' ' + str(d.unit)),
                            styles["narrow_b_left"])
        price = round(decimal.Decimal(d.price), 4)
        quantity = round(decimal.Decimal(d.quantity), 4)
        amount = round(decimal.Decimal(d.quantity * d.price), 4)
        row.append((product, str(round(quantity, 2)), str(price), str(amount)))
        total = total + amount
    if len(row) <= 0:
        row.append(('', '', '', ''))
    pdf_detail = Table(row, colWidths=[w * 47 / 100, w * 15 / 100, w * 16 / 100, w * 22 / 100])
    style_detail = [
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (0, -1), 1),
        # ('TOPPADDING', (1, 0), (1, -1), -1),
        # ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        # ('BOTTOMPADDING', (1, 0), (1, -1), 2),
        ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),
        ('ALIGNMENT', (1, 0), (3, -1), 'RIGHT'),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        # ('LEFTPADDING', (0, 0), (0, -1), -10),
        ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#9E9E9E')),
    ]
    pdf_detail.setStyle(TableStyle(style_detail))
    # --------------------------------------------------------------------------
    totals = [
        # ['GRAVADA', 'S/. ' + str(round(decimal.Decimal(total) / decimal.Decimal(1.1800), 4))],
        # ['DESCUENTO', str(round(decimal.Decimal(0.00), 2))],
        # ['IGV 18.00%',
        #  'S/. ' + str(round(decimal.Decimal(total) - decimal.Decimal(total) / decimal.Decimal(1.1800), 4))],
        ['TOTAL',
         'S/. ' + str(decimal.Decimal(total).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_DOWN))]
    ]

    total_right = Table(totals, colWidths=[w * 40 / 100, w * 40 / 100])

    total_right_style = [
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
        ('ALIGNMENT', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#9E9E9E')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        # # ('FONTNAME', (0, 0), (-1, 2), 'Narrow-a'),

        # ('TEXTCOLOR', (0, 3), (-1, -1), colors.white),
        # ('ALIGNMENT', (0, 0), (1, -1), 'LEFT'),
        # ('ALIGNMENT', (1, 0), (-1, -1), 'RIGHT'),
        # ('BACKGROUND', (0, 3), (-1, -1), HexColor('#5f64de')),
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

    ]
    total_right.setStyle(TableStyle(total_right_style))
    total_space = [
        [''],
    ]
    total_left = Table(total_space, colWidths=[w * 45 / 100])
    total_left_style = [
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),
    ]
    total_left.setStyle(TableStyle(total_left_style))

    total_table = [
        [total_left, total_right],
    ]
    pdf_total = Table(total_table, colWidths=[w * 20 / 100, w * 80 / 100])
    total_style = [
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # three column
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),  # first column
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.red),
    ]
    pdf_total.setStyle(TableStyle(total_style))

    pdf_total_letter = 'SON: ' + str(
        number_money(round(decimal.Decimal(order_obj.total), 4), str(order_obj.get_coin_display())))
    # ----------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------
    style_qr = [
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),   # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # first column
        ('TOPPADDING', (0, 0), (-1, -1), -10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), -10),
    ]
    datatable = str(order_obj.number)
    pdf_qr = Table([('', get_qr(datatable), '')], colWidths=[w * 15 / 100, w * 70 / 100, w * 15 / 100])
    pdf_qr.setStyle(TableStyle(style_qr))
    # -----------------------------------------------------------------------------------------------
    counter = order_obj.orderdetail_set.filter(is_state=True).count()
    buff = io.BytesIO()

    ml = 0.0 * inch
    mr = 0.0 * inch
    ms = 0.0 * inch
    mi = 0.039 * inch

    doc = SimpleDocTemplate(buff,
                            pagesize=(2.83 * inch, 11.6 * inch + counter * 25.4),
                            rightMargin=mr,
                            leftMargin=ml,
                            topMargin=ms,
                            bottomMargin=mi,
                            title=document_number
                            )
    pdf = []
    # pdf.append(I)
    # pdf.append(Spacer(1, 3))
    # pdf.append(Paragraph(title_business.upper().replace("\n", "<br />"), styles["CenterNewgotBold"]))
    # pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(Paragraph(document_type, styles["CenterNewgotBoldInvoiceNumber"]))
    pdf.append(Spacer(1, 3))
    pdf.append(Paragraph(document_number, styles["CenterNewgotBoldInvoiceNumber"]))
    pdf.append(Spacer(1, -2))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(pdf_person)
    pdf.append(Spacer(1, -4))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(pdf_user)
    pdf.append(Spacer(1, 3))
    pdf.append(pdf_header)
    pdf.append(pdf_detail)
    pdf.append(Spacer(1, 2))
    pdf.append(pdf_total)
    pdf.append(Spacer(1, -4))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(Paragraph(pdf_total_letter.upper(), styles["LeftNewgotBold"]))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(Paragraph("PERNOS JHUNIOR S.R.L.", styles["CenterNewgotBold"]))
    doc.build(pdf)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="COTIZACION_{}.pdf"'.format(str(order_obj.number).zfill(7))
    response.write(buff.getvalue())
    buff.close()
    return response


def logistic(request, pk=None):
    order_obj = Order.objects.get(number=pk)
    subsidiary_obj = order_obj.subsidiary
    user_obj = order_obj.user
    person_obj = order_obj.person
    w = 2.83 * inch - 4 * 0.05 * inch
    title_business = str(subsidiary_obj.business_name) + '\n' + str(
        subsidiary_obj.address) + '\n RUC ' + str(
        subsidiary_obj.ruc) + '\n TELF. ' + str(subsidiary_obj.phone)
    date = utc_to_local(order_obj.update_at)
    document_type = str('TICKET').upper()
    document_number = 'ORDEN Nº ' + str(order_obj.number)
    line = '--------------------------------------------------------------'
    I = Image(logo)
    I.drawHeight = 4.0 * inch / 2.9
    I.drawWidth = 5.0 * inch / 2.9
    # ------------------------------------------------------------------
    pdf_user = Table(
        [('USUARIO: ', Paragraph(user_obj.first_name.upper(), styles["narrow_b_left"]))] +
        [('FECHA: ',
          date.strftime("%d/%m/%Y") + '  HORA: ' + str(utc_to_local(order_obj.update_at).strftime('%H:%M:%S')))] +
        [('ORDEN Nº: ', str(order_obj.number))],
        colWidths=[w * 20 / 100, w * 80 / 100])
    style_user = [
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),  # all columns
        ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),  # all columns
        ('FONTNAME', (0, 3), (-1, -1), 'Narrow-b'),  # all columns
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('BOTTOMPADDING', (0, 0), (0, -1), 0),  # all columns
        ('BOTTOMPADDING', (1, 0), (1, -1), 0),  # all columns
        ('BOTTOMPADDING', (1, 0), (1, 0), 4),  # all columns
        ('LEFTPADDING', (0, 0), (0, -1), 2),  # first column
        ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),  # second column
        # ('RIGHTPADDING', (1, 0), (1, -1), 0.5),  # second column
    ]
    pdf_user.setStyle(TableStyle(style_user))
    # ------------------------------------------------------------------
    client_name = '-'
    client_doc = 'DNI'
    client_number = '-'
    client_address = '-'
    if person_obj:
        client_name = Paragraph(person_obj.names.upper(), styles["narrow_b_left"])
        client_doc = person_obj.get_document_display()
        client_number = Paragraph(person_obj.number, styles["narrow_b_left"])
        client_address = Paragraph(person_obj.address.upper(), styles["narrow_b_left"])
    pdf_person = Table(
        [('CLIENTE: ', client_name)] +
        [(client_doc + ':', client_number)] +
        [('DIRECCIÓN: ', client_address)],
        # [('FECHA EMISIÓN: ', date.strftime("%d/%m/%Y"))] +
        # [('MONEDA: ', 'SOLES')],
        colWidths=[w * 20 / 100, w * 80 / 100])
    style_person = [
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),  # all columns
        ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),  # all columns
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('BOTTOMPADDING', (0, 0), (0, -1), -4),  # all columns
        ('BOTTOMPADDING', (1, 0), (1, -1), -4),  # all columns
        ('BOTTOMPADDING', (1, 2), (1, 2), 1),  # all columns
        ('BOTTOMPADDING', (1, 0), (1, 1), 1),  # all columns
        ('LEFTPADDING', (0, 0), (0, -1), 2),  # first column
        ('LEFTPADDING', (1, 0), (1, -1), 2),  # first column
        ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),  # second column
        # ('RIGHTPADDING', (1, 0), (1, -1), 0.5),  # second column
    ]
    pdf_person.setStyle(TableStyle(style_person))
    # ----------------------------------------------------------------
    style_header = [
        ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
        # ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#9E9E9E')),  # all columns
        ('BACKGROUND', (0, 0), (-1, 1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),  # all columns
        ('TOPPADDING', (0, 0), (-1, -1), 1),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
    ]
    pdf_header = Table(
        [('CODIGO', 'DESCRIPCIÓN', 'CANT', 'UNIDADES')],
        colWidths=[w * 10 / 100, w * 60 / 100, w * 15 / 100, w * 15 / 100]
    )
    pdf_header.setStyle(TableStyle(style_header))
    # -------------------------------------------------------------------
    row = []
    total = round(decimal.Decimal(0.00), 4)
    for d in order_obj.orderdetail_set.filter(is_invoice=True, is_state=True).order_by('id'):
        code = str(d.product.code)
        unit = str(d.get_unit_display())
        product = Paragraph(str(d.product.name).upper() + ' ' + str(
            d.product.measure()),
                            styles["narrow_b_left"])
        quantity = round(decimal.Decimal(d.quantity), 4)
        row.append((code, product, str(round(quantity, 2)), str(unit)))
    if len(row) <= 0:
        row.append(('', '', '', ''))
    pdf_detail = Table(row, colWidths=[w * 10 / 100, w * 60 / 100, w * 15 / 100, w * 15 / 100])
    style_detail = [
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (0, -1), 1),
        # ('TOPPADDING', (1, 0), (1, -1), -1),
        # ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        # ('BOTTOMPADDING', (1, 0), (1, -1), 2),
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        # ('LEFTPADDING', (0, 0), (0, -1), -10),
        # ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#9E9E9E')),
    ]
    pdf_detail.setStyle(TableStyle(style_detail))

    # -----------------------------------------------------------------------------------------------
    counter = order_obj.orderdetail_set.filter(is_state=True).count()
    buff = io.BytesIO()

    ml = 0.0 * inch
    mr = 0.0 * inch
    ms = 0.0 * inch
    mi = 0.039 * inch

    doc = SimpleDocTemplate(buff,
                            pagesize=(2.83 * inch, 11.6 * inch + counter * 25.4),
                            rightMargin=mr,
                            leftMargin=ml,
                            topMargin=ms,
                            bottomMargin=mi,
                            title=document_number
                            )
    pdf = []
    pdf.append(Paragraph(document_type, styles["CenterNewgotBoldInvoiceNumber"]))
    pdf.append(Spacer(1, 3))
    pdf.append(Paragraph(document_number, styles["CenterNewgotBoldInvoiceNumber"]))
    pdf.append(Spacer(1, -2))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(pdf_person)
    pdf.append(Spacer(1, -4))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(pdf_user)
    pdf.append(Spacer(1, 3))
    pdf.append(pdf_header)
    pdf.append(pdf_detail)
    doc.build(pdf)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pago_{}.pdf"'.format(order_obj.number)
    response.write(buff.getvalue())
    buff.close()
    return response


# def ticket(request, pk=None):
#     order_obj = Order.objects.get(id=pk)
#     subsidiary_obj = order_obj.subsidiary
#     person_obj = order_obj.person
#     w = 3.25 * inch - 8 * 0.05 * inch
#     title_business = str(subsidiary_obj.business_name) + '\n' + str(subsidiary_obj.address) + '\n' + str(
#         subsidiary_obj.ruc)
#     date = utc_to_local(order_obj.update_at)
#     document_type = str(order_obj.get_type_display()).upper()
#     document_number = 'Nº ' + str(order_obj.number).zfill(6 - len(str(order_obj.number)))
#     line = '--------------------------------------------------------------------'
#     I = Image(logo)
#     I.drawHeight = 3.0 * inch / 2.9
#     I.drawWidth = 3.0 * inch / 2.9
#     # ------------------------------------------------------------------
#     if person_obj:
#         pdf_person = Table(
#             [('CLIENTE: ', Paragraph(person_obj.names.upper(), styles["Left-text"]))] +
#             [(person_obj.get_document_display() + ':', person_obj.number)] +
#             # [('DIRECCIÓN: ', Paragraph(person_obj.address.upper(), styles["Left-text"]))] +
#             [('FECHA: ', date.strftime("%d/%m/%Y"))],
#             colWidths=[w * 20 / 100, w * 80 / 100])
#         style_person = [
#             ('FONTNAME', (0, 0), (-1, -1), 'Square'),  # all columns
#             # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),  # all columns
#             ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#             ('BOTTOMPADDING', (0, 0), (0, -1), 0),  # all columns
#             ('BOTTOMPADDING', (1, 0), (1, -1), 0),  # all columns
#             ('BOTTOMPADDING', (1, 0), (1, 0), 4),  # all columns
#             ('LEFTPADDING', (0, 0), (0, -1), 2),  # first column
#             ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),  # second column
#             # ('RIGHTPADDING', (1, 0), (1, -1), 0.5),  # second column
#         ]
#         pdf_person.setStyle(TableStyle(style_person))
#     # ----------------------------------------------------------------
#     style_header = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Ticketing'),  # all columns
#         ('FONTSIZE', (0, 0), (-1, -1), 9),  # all columns
#         ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#0362BB')),  # all columns
#         ('BACKGROUND', (0, 0), (-1, 1), HexColor('#0362BB')),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 1),  # all columns
#         ('TOPPADDING', (0, 0), (-1, -1), 1),  # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
#     ]
#     pdf_header = Table(
#         [('DESCRIPCIÓN', 'CANT', 'UM', 'PRECIO', 'IMPORTE')],
#         colWidths=[w * 43 / 100, w * 11 / 100, w * 10 / 100, w * 18 / 100, w * 18 / 100]
#     )
#     pdf_header.setStyle(TableStyle(style_header))
#     # -------------------------------------------------------------------
#     row = []
#     total = round(decimal.Decimal(0.00), 2)
#     for d in order_obj.orderdetail_set.all():
#         product = Paragraph(str(d.product.name).capitalize(), styles["Left-text"])
#         unit = d.get_unit_display()
#         price = round(decimal.Decimal(d.price), 2)
#         quantity = round(decimal.Decimal(d.quantity), 2)
#         amount = round(decimal.Decimal(d.quantity * d.price), 2)
#         row.append((product, str(round(quantity, 2)), str(unit), str(price), str(amount)))
#         total = total + amount
#     pdf_detail = Table(row, colWidths=[w * 43 / 100, w * 11 / 100, w * 10 / 100, w * 18 / 100, w * 18 / 100])
#     style_detail = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Square'),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('TOPPADDING', (0, 0), (-1, -1), 1),
#         ('TOPPADDING', (0, 0), (0, -1), -3),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('ALIGNMENT', (1, 0), (2, -1), 'CENTER'),
#         ('ALIGNMENT', (3, 0), (4, -1), 'RIGHT'),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 2),
#         ('LEFTPADDING', (0, 0), (-1, -1), 2),
#         ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#9E9E9E')),
#     ]
#     pdf_detail.setStyle(TableStyle(style_detail))
#     # --------------------------------------------------------------------------
#     totals = [
#         ['SUBTOTAL', str(round(decimal.Decimal(order_obj.total) - decimal.Decimal(order_obj.total_discount), 2))],
#         ['DESCUENTO', str(round(decimal.Decimal(order_obj.total_discount), 2))],
#         ['TOTAL', str(round(decimal.Decimal(order_obj.total), 2))]
#     ]
#
#     total_right = Table(totals, colWidths=[w * 20 / 100, w * 20 / 100])
#
#     total_right_style = [
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 2),
#         ('LEFTPADDING', (0, 0), (-1, -1), 2),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('ALIGNMENT', (1, 0), (1, -1), 'RIGHT'),
#         ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#9E9E9E')),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
#         ('TOPPADDING', (0, 0), (-1, -1), 1),
#         # # ('FONTNAME', (0, 0), (-1, 2), 'Narrow-a'),
#
#         # ('TEXTCOLOR', (0, 3), (-1, -1), colors.white),
#         # ('ALIGNMENT', (0, 0), (1, -1), 'LEFT'),
#         # ('ALIGNMENT', (1, 0), (-1, -1), 'RIGHT'),
#         # ('BACKGROUND', (0, 3), (-1, -1), HexColor('#5f64de')),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#
#     ]
#     total_right.setStyle(TableStyle(total_right_style))
#     total_space = [
#         [''],
#     ]
#     total_left = Table(total_space, colWidths=[w * 60 / 100])
#     total_left_style = [
#         ('RIGHTPADDING', (0, 0), (-1, -1), 10),
#         ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
#         ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),
#     ]
#     total_left.setStyle(TableStyle(total_left_style))
#
#     total_table = [
#         [total_left, total_right],
#     ]
#     pdf_total = Table(total_table, colWidths=[w * 60 / 100, w * 40 / 100])
#     total_style = [
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # three column
#         ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),  # first column
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.red),
#     ]
#     pdf_total.setStyle(TableStyle(total_style))
#
#     pdf_total_letter = 'SON: ' + str(
#         number_money(round(decimal.Decimal(order_obj.total), 2), str(order_obj.get_coin_display())))
#     # -----------------------------------------------------------------------------------------------
#     style_qr = [
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),   # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # first column
#         ('TOPPADDING', (0, 0), (-1, -1), 0),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
#         ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
#     ]
#     datatable = code93.Standard93(str(order_obj.number).zfill(6 - len(str(order_obj.number))))
#     pdf_bar = Table([('', datatable, '')], colWidths=[w * 5 / 100, w * 90 / 100, w * 5 / 100])
#     pdf_bar.setStyle(TableStyle(style_qr))
#     # -----------------------------------------------------------------------------------------------
#     counter = round(float(order_obj.orderdetail_set.count()), 2)
#     buff = io.BytesIO()
#
#     ml = 0.05 * inch
#     mr = 0.055 * inch
#     ms = 0.039 * inch
#     mi = 0.039 * inch
#
#     doc = SimpleDocTemplate(buff,
#                             pagesize=(3.14961 * inch, 5.8 * inch + counter * 14.4),
#                             rightMargin=mr,
#                             leftMargin=ml,
#                             topMargin=ms,
#                             bottomMargin=mi,
#                             title=str(order_obj.get_type_display()) + "-" + str(
#                                 str(order_obj.number).zfill(6 - len(str(order_obj.number))))
#                             )
#     pdf = []
#     pdf.append(I)
#     pdf.append(Spacer(1, 3))
#     pdf.append(Paragraph(title_business.upper().replace("\n", "<br />"), styles["CenterNewgotBold"]))
#     pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
#     pdf.append(Paragraph(document_type, styles["CenterNewgotBold"]))
#     pdf.append(Spacer(1, 3))
#     pdf.append(Paragraph(document_number, styles["CenterNewgotBold"]))
#     pdf.append(Spacer(1, -2))
#     pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
#     if person_obj:
#         pdf.append(pdf_person)
#         pdf.append(Spacer(1, 3))
#     pdf.append(pdf_header)
#     pdf.append(pdf_detail)
#     pdf.append(Spacer(1, 2))
#     pdf.append(pdf_total)
#     pdf.append(Spacer(1, -4))
#     pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
#     pdf.append(Paragraph(pdf_total_letter.upper(), styles["LeftNewgotBold"]))
#     pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
#     pdf.append(pdf_bar)
#     pdf.append(Spacer(1, -4))
#     pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
#     pdf.append(Paragraph("www.4soluciones.net", styles["CenterNewgotBold"]))
#     doc.build(pdf)
#     response = HttpResponse(content_type='application/pdf')
#     response.write(buff.getvalue())
#     buff.close()
#     return response
def get_qr(table):
    # generate and rescale QR
    qr_code = qr.QrCodeWidget(table)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    drawing = Drawing(
        3.5 * cm, 3.5 * cm, transform=[3.5 * cm / width, 0, 0, 3.5 * cm / height, 0, 0])
    drawing.add(qr_code)

    return drawing


# def document(request, pk=None, t=None):
#     order_obj = Order.objects.get(id=pk)
#     client_obj = order_obj.client
#     if t == 1:
#         _a4 = (8.3 * inch, 11.7 * inch)
#         ml = 0.25 * inch
#         mr = 0.25 * inch
#         ms = 0.25 * inch
#         mi = 0.25 * inch
#
#         _bts = 8.3 * inch - 0.25 * inch - 0.25 * inch
#         I = Image(logo)
#         I.drawHeight = 3.00 * inch / 2.9
#         I.drawWidth = 5.6 * inch / 2.9
#         subsidiary_obj = get_subsidiary_by_user(order_obj.user)
#         client_header_style = [
#             ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),  # all columns
#             ('GRID', (0, 0), (-1, -1), 1, HexColor('#5f64de')),  # all columns
#             ('BACKGROUND', (0, 0), (-1, -1), HexColor('#5f64de')),
#             # Establecer el color de fondo de la segunda fila    ]
#             ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
#             ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 5),  # all columns
#             ('RIGHTPADDING', (-1, 0), (-1, -1), 10),  # second column
#             ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#         ]
#         client_header = Table([('INFORMACIÓN DEL CLIENTE', 'DATOS DE LA ' + str(order_obj.get_type_display()).upper())],
#                               colWidths=[_bts * 75 / 100, _bts * 25 / 100])
#         client_header.setStyle(TableStyle(client_header_style))
#
#         title = [
#             [Paragraph(str(subsidiary_obj.business_name), styles["narrow_b_tittle_justify"])],
#             [Paragraph(str(subsidiary_obj.address), styles["narrow_b_justify"])],
#             [Paragraph('Correo: ' + str(subsidiary_obj.email), styles['narrow_b_justify'])],
#             [Paragraph('Telefono: ' + str(subsidiary_obj.phone), styles['narrow_b_justify'])],
#         ]
#         T = Table(title)
#         title_style = [
#             # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#             # ('TEXTCOLOR', (0, 0), (-1, -1), colors.red)
#             ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),
#             ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ]
#         T.setStyle(TableStyle(title_style))
#
#         document = [
#             ['RUC ' + str(subsidiary_obj.ruc)],
#             [str(order_obj.get_type_display()).upper()],
#             [str(subsidiary_obj.serial) + ' - ' + str(str(order_obj.number).zfill(10))],
#         ]
#         D = Table(document)
#         document_style = [
#             # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
#             ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
#             ('FONTSIZE', (0, 0), (-1, -1), 13),
#             ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
#             ('SPAN', (0, 0), (0, 0))
#         ]
#         D.setStyle(TableStyle(document_style))
#         H = [
#             [I, T, D],
#         ]
#         document_header = Table(H, colWidths=[_bts * 25 / 100, _bts * 50 / 100, _bts * 25 / 100])
#         header_style = [
#             # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#             ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # first column
#             ('SPAN', (0, 0), (0, 0)),  # first row
#             # ('LINEBELOW', (0, -1), (-1, -1), 0.5, purple, 1, None, None, 4, 1),
#             ('BACKGROUND', (2, 0), (-1, 1), HexColor('#5f64de')),  # Establecer el color de fondo de la segunda fila
#             ('LINEBEFORE', (1, 0), (-1, -1), 0.1, colors.grey),
#             # Establezca el color de la línea izquierda de la tabla en
#         ]
#         document_header.setStyle(TableStyle(header_style))
#         # ---------------------------------Datos Cliente----------------------------#
#         client_address = '-'
#         client_phone = '-'
#         client_email = '-'
#         if client_obj.address:
#             client_address = client_obj.address
#         if client_obj.telephone:
#             client_phone = client_obj.telephone
#         if client_obj.email:
#             client_email = client_obj.email
#         client = [
#             ['CLIENTE :', Paragraph(str(client_obj.full_name.upper()), styles["narrow_a_justify"])],
#             [str(client_obj.type.abbreviation) + ' :', str(client_obj.document)],
#             ['DIRECCION :', Paragraph(str(client_address.upper()), styles["narrow_a_justify"])],
#             ['TELEFONO  :', str(client_phone)],
#             ['CORREO     :', str(client_email).upper()]
#         ]
#         C = Table(client, colWidths=[_bts * 10 / 100, _bts * 64 / 100])
#         client_style = [
#             # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#             ('FONTNAME', (0, 0), (-1, -1), 'Narrow-a'),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#             ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),  # first column
#             ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
#         ]
#         C.setStyle(TableStyle(client_style))
#         employee_obj = Employee.objects.get(user=order_obj.user)
#         order = [
#             ['FECHA: ', str(order_obj.create_at.strftime("%d-%m-%Y"))],
#             ['ESTADO: ', str(order_obj.get_status_display()).upper()],
#             ['USUARIO: ', str(employee_obj.user.first_name).upper()],
#             ['MONEDA: ', str(order_obj.coin.description).upper()]
#
#         ]
#         if order_obj.type == 'AL' or order_obj.type == 'TA':
#             date_init = ['INICIO: ', str(order_obj.date_init.strftime("%d-%m-%Y"))]
#             date_end = ['TERMINO: ', str(order_obj.date_end.strftime("%d-%m-%Y"))]
#             order.append(date_init)
#             order.append(date_end)
#         O = Table(order, colWidths=[_bts * 12 / 100, _bts * 14 / 100])
#         O.setStyle(TableStyle(client_style))
#         CH2 = [
#             [C, O],
#         ]
#         document_client = Table(CH2, colWidths=[_bts * 74 / 100, _bts * 26 / 100])
#         cd_style = [
#             # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#             ('ALIGNMENT', (0, 0), (0, -1), 'CENTER'),  # first column
#         ]
#         document_client.setStyle(TableStyle(cd_style))
#         # ------------ENCABEZADO DEL DETALLE-------------------#
#         header_detail_style = [
#             ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),  # all columns
#             ('GRID', (0, 0), (-1, -1), 1, HexColor('#5f64de')),  # all columns
#             ('BACKGROUND', (0, 0), (-1, 1), HexColor('#5f64de')),
#             # Establecer el color de fondo de la segunda fila    ]
#             ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
#             ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 5),  # all columns
#             ('RIGHTPADDING', (1, 0), (1, -1), 10),  # second column
#             ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#             ('ALIGNMENT', (2, 0), (2, -1), 'LEFT'),  # second column
#         ]
#         width_table = [_bts * 5 / 100, _bts * 44 / 100, _bts * 12 / 100, _bts * 15 / 100,
#                        _bts * 12 / 100,
#                        _bts * 12 / 100]
#         document_header_detail = Table([('Nº', 'DESCRIPCIÓN', 'CANTIDAD', 'UND MED', 'PRECIO', 'IMPORTE')],
#                                        colWidths=width_table)
#         document_header_detail.setStyle(TableStyle(header_detail_style))
#
#         # -------------------DETAIL---------------------#
#         row_detail = []
#         count = 0
#         total_amount = 0
#         for d in order_obj.orderdetail_set.order_by('id'):
#             _product = Paragraph(
#                 (str(d.product.name.upper()) + '\n' + str(d.description.upper())).replace("\n", "<br/>"),
#                 styles["narrow_a_justify"])
#             _unit = str(d.unit.description.upper())
#             _quantity = str(round(decimal.Decimal(d.quantity), 2))
#             _price = str(round(decimal.Decimal(d.price), 2))
#             _amount = str(round(decimal.Decimal(d.quantity) * decimal.Decimal(d.price), 2))
#             if d.is_state:
#                 values = '•'
#             else:
#                 count = count + 1
#                 values = count
#                 total_amount = total_amount + d.quantity * d.price
#             row_detail.append((str(values), _product, _quantity, _unit, _price, _amount))
#
#         document_body_detail = Table(row_detail,
#                                      colWidths=[_bts * 5 / 100, _bts * 44 / 100, _bts * 12 / 100,
#                                                 _bts * 15 / 100, _bts * 12 / 100, _bts * 12 / 100])
#         body_detail_style = [
#             # ('GRID', (0, 0), (-1, -1), 0.1, colors.blue),
#             ('FONTNAME', (0, 0), (-1, -1), 'Narrow-a'),
#             ('FONTSIZE', (0, 0), (-1, -1), 9),
#             ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#             ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#             ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#             ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),  # three column
#             ('ALIGNMENT', (2, 0), (3, -1), 'CENTER'),  # three column
#             ('ALIGNMENT', (4, 0), (-1, -1), 'RIGHT'),  # three column
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # first column
#             ('RIGHTPADDING', (3, 0), (3, -1), 10),  # first column
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # all columns
#             # ('BACKGROUND', (4, 0), (4, -1), colors.blue),  # four column
#         ]
#         document_body_detail.setStyle(TableStyle(body_detail_style))
#         # -------------- Footer Detail ----------------------------
#         money = str(order_obj.coin.abbreviation)
#         total_discount = decimal.Decimal(order_obj.discount_output)
#         sub_total = (total_amount / decimal.Decimal(1.1800)) - total_discount
#         total_invoice = order_obj.total_output
#         total_igv = total_invoice - sub_total
#         total = [
#             ['GRAVADA', money + ' ' + str(round(sub_total, 2))],
#             ['DESCUENTO', money + ' ' + str(round(total_discount, 2))],
#             ['I.G.V.(18%)', money + ' ' + str(round(total_igv, 2))],
#             ['TOTAL', money + ' ' + str(round(total_invoice, 2))]
#         ]
#         TT = Table(total, colWidths=[_bts * 15 / 100, _bts * 15 / 100])
#
#         total_style = [
#             ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#             ('FONTNAME', (0, 0), (-1, 2), 'Narrow-a'),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),
#             ('FONTSIZE', (0, 3), (-1, -1), 11),
#             ('FONTNAME', (0, 3), (-1, -1), 'Newgot'),
#             ('TEXTCOLOR', (0, 3), (-1, -1), colors.white),
#             ('ALIGNMENT', (0, 0), (1, -1), 'LEFT'),
#             ('ALIGNMENT', (1, 0), (-1, -1), 'RIGHT'),
#             ('BACKGROUND', (0, 3), (-1, -1), HexColor('#5f64de')),
#             # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#             ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#5f64de')),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
#         ]
#         TT.setStyle(TableStyle(total_style))
#         total_letter = [
#             ['SON: ' + number_money(round(total_invoice, 2),
#                                     str(order_obj.coin.description.upper())).upper()],
#             # [t_bank],
#         ]
#         TL = Table(total_letter, colWidths=[_bts * 70 / 100])
#         total_letter_style = [
#             ('RIGHTPADDING', (0, 0), (-1, -1), 10),
#             ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
#             ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),
#             # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),
#         ]
#         TL.setStyle(TableStyle(total_letter_style))
#
#         total_ = [
#             [TL, TT],
#         ]
#         document_total = Table(total_, colWidths=[_bts * 70 / 100, _bts * 30 / 100])
#         total_style = [
#             ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # three column
#             ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),  # first column
#             # ('GRID', (0, 0), (-1, -1), 0.5, colors.red),
#         ]
#         document_total.setStyle(TableStyle(total_style))
#         # -----------------------accounting bank------------------------------
#         table_cashing = []
#         table_cashing.append(('DESCRIPCIÓN DEL BANCO', '           MONEDA                  CUENTA BANCARIA                         CUENTA CCI'))
#         bank_set = Casing.objects.filter(type='T', subsidiary=subsidiary_obj, is_enabled=True)
#         for c in bank_set:
#             _description = Paragraph(str(c.description.upper()), styles["narrow_a_justify"])
#             row_account = []
#             for d in c.account_set.all():
#                 row_account.append((str(d.coin.description.upper()), str(d.account), str(d.cci)))
#             if row_account:
#                 account_table = Table(row_account,
#                                       colWidths=[_bts * 15 / 100, _bts * 20 / 100, _bts * 25 / 100])
#                 account_table_style = [
#                     # ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#7a3621')),
#                     ('FONTNAME', (0, 0), (-1, -1), 'Narrow-a'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 10),
#                     ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#                     ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#                     ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#                     # ('BACKGROUND', (0, 0), (-1, -1), colors.blue),  # four column
#                 ]
#                 account_table.setStyle(TableStyle(account_table_style))
#
#                 table_cashing.append((str(c.name.upper()), account_table))
#         if bank_set:
#             document_casing = Table(table_cashing,
#                                     colWidths=[_bts * 40 / 100, _bts * 60 / 100])
#             # ----------------------header accounting ---------------------------
#             # document_header_accounting = Table([('DESCRIPCIÓN DEL BANCO', 'MONEDA', 'CUENTA BANCARIA', 'CUENTA CCI')],
#             #                                    colWidths=[_bts * 40 / 100, _bts * 15 / 100, _bts * 20 / 100,
#             #                                               _bts * 25 / 100])
#             # header_accounting_style = [
#             #     ('FONTNAME', (0, 0), (-1, -1), 'Narrow-a'),  # all columns
#             #     ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#5f64de')),  # all columns
#             #     ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
#             #     ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
#             #     ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#             #     ('BOTTOMPADDING', (0, 0), (-1, -1), 5),  # all columns
#             #     ('RIGHTPADDING', (1, 0), (1, -1), 10),  # second column
#             #     ('ALIGNMENT', (0, 0), (-1, 0), 'CENTER'),  # all column
#             #     ('BACKGROUND', (0, 0), (-1, 0), HexColor('#5f64de')),  # four column
#             # ]
#             # document_header_accounting.setStyle(TableStyle(header_accounting_style))
#             document_casing_style = [
#                 ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#5873e8')),
#                 ('FONTNAME', (0, 0), (-1, -1), 'Narrow-a'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 10),
#                 ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#                 ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#                 # ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 # ('BOTTOMPADDING', (0, 0), (0, 1), 5),  # all columns
#                 ('BACKGROUND', (0, 0), (-1, 0), HexColor('#5f64de')),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
#             ]
#             document_casing.setStyle(TableStyle(document_casing_style))
#         # --------------------------------------------------------------------------------------
#         footer = [
#             [Paragraph(
#                 'Observaciones: ' + str(subsidiary_obj.observation_output),
#                 styles["narrow_justify_observation"]), '            '],
#             [Paragraph(' ', styles["narrow_justify"]),
#              Paragraph(' ', styles["narrow_justify"])],
#             [Paragraph(' ', styles["narrow_justify"]),
#              Paragraph(' ', styles["narrow_justify"])],
#             [Paragraph(' ', styles["narrow_justify"]),
#              Paragraph(' ', styles["narrow_justify"])],
#             [Paragraph(' ', styles["narrow_justify"]),
#              Paragraph(' ', styles["narrow_justify"])],
#             [Paragraph('_____________________', styles["narrow_center"]),
#              Paragraph('_____________________', styles["narrow_center"])],
#             [Paragraph('Área Logística', styles["narrow_center"]),
#              Paragraph('V°B° Administración', styles["narrow_center"])]
#         ]
#         document_footer = Table(footer, colWidths=[_bts * 50 / 100, _bts * 50 / 100])
#         footer_style = [
#             # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#             ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
#             ('FONTSIZE', (0, 0), (-1, -1), 8),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#             ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
#             ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
#         ]
#         document_footer.setStyle(TableStyle(footer_style))
#         # ------------------------------------------------------------------------------------------
#         buff = io.BytesIO()
#         doc = SimpleDocTemplate(buff,
#                                 pagesize=(8.3 * inch, 11.7 * inch),
#                                 rightMargin=mr,
#                                 leftMargin=ml,
#                                 topMargin=ms,
#                                 bottomMargin=mi,
#                                 title=str(order_obj.get_type_display()) + "-" + str(str(order_obj.number).zfill(10)),
#
#                                 )
#         dictionary = []
#         dictionary.append(document_header)
#         dictionary.append(PrintDraw(count_row=count))
#         dictionary.append(Spacer(1, 10))
#         dictionary.append(client_header)
#         dictionary.append(document_client)
#         dictionary.append(Spacer(1, 16))
#         dictionary.append(document_header_detail)
#         dictionary.append(document_body_detail)
#         dictionary.append(Spacer(1, 5))
#         dictionary.append(document_total)
#         dictionary.append(Spacer(1, 25))
#         dictionary.append(document_footer)
#         dictionary.append(Spacer(1, 15))
#         if bank_set:
#             # dictionary.append(document_header_accounting)
#             dictionary.append(document_casing)
#         response = HttpResponse(content_type='application/pdf')
#         doc.build(dictionary, canvasmaker=NumberedCanvas, onFirstPage=footer_draw, onLaterPages=footer_draw)
#         response.write(buff.getvalue())
#         buff.close()
#         return response
#     elif t == 2:
#         _wt = 3.25 * inch - 8 * 0.05 * inch
#         client_name = "-"
#         client_document = "-"
#         client_phone = "-"
#         client_address = "-"
#         title_business = str(order_obj.subsidiary.business_name) + '\n' + str(
#             order_obj.subsidiary.address) + '\n' + str(
#             order_obj.subsidiary.ruc)
#         date = utc_to_local(order_obj.create_add)
#         _time = date.strftime('%H:%M:%S')
#         _date = date.strftime("%d/%m/%Y")
#         document_type = str(order_obj.get_type_display()).upper()
#         document_number_order = 'Nº ' + str(order_obj.number).zfill(10)
#         if client_obj.full_name:
#             client_name = client_obj.full_name
#         if client_obj.document:
#             client_document = client_obj.document
#         if client_obj.telephone:
#             client_phone = client_obj.telephone
#         if client_obj.address:
#             client_address = client_obj.address
#         if client_obj.email:
#             client_email = client_obj.email
#         line = '---------------------------------------------------------'
#         I = Image(logo)
#         I.drawHeight = 3.35 * inch / 2.9
#         I.drawWidth = 5.5 * inch / 2.9
#         style_table = [
#             ('FONTNAME', (0, 0), (-1, -1), 'Square'),  # all columns
#             # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # all columns
#             ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#             ('BOTTOMPADDING', (0, 0), (-1, -1), -2),  # all columns
#             ('LEFTPADDING', (0, 0), (0, -1), 0.5),  # first column
#             ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),  # second column
#             ('RIGHTPADDING', (1, 0), (1, -1), 0.5),  # second column
#         ]
#         col_withs_table = [_wt * 23 / 100, _wt * 77 / 100]
#         document_client = Table(
#             [('CLIENTE: ', Paragraph(client_name, styles["Left-text"]))] +
#             [(client_obj.type.abbreviation, client_document)] +
#             [('DIRECCIÓN: ', Paragraph(client_address, styles["Left-text"]))] +
#             [('TELEFONO: ', client_phone)] +
#             [('CORREO: ', client_email)] +
#             [('FECHA: ', _date + '  HORA: ' + _time)],
#             colWidths=col_withs_table)
#         document_client.setStyle(TableStyle(style_table))
#         my_style_header = [
#             ('FONTNAME', (0, 0), (-1, -1), 'Ticketing'),  # all columns
#             ('FONTSIZE', (0, 0), (-1, -1), 9),  # all columns
#             ('BOTTOMPADDING', (0, 0), (-1, -1), -6),  # all columns
#             ('RIGHTPADDING', (3, 0), (3, -1), 0),  # four column
#             ('ALIGNMENT', (3, 0), (3, -1), 'RIGHT'),  # four column
#             ('LEFTPADDING', (0, 0), (0, -1), 0),  # first column
#             ('FONTNAME', (0, 2), (-1, 2), 'Ticketing'),  # third row
#             ('FONTSIZE', (0, 2), (-1, 2), 9),  # third row
#             ('LEFTPADDING', (2, 0), (2, -1), 5),
#             ('ALIGNMENT', (2, 0), (2, -1), 'CENTER'),
#             ('LEFTPADDING', (1, 0), (1, -1), 0),
#             ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),
#             ('RIGHTPADDING', (4, 0), (4, -1), 0),
#             ('ALIGNMENT', (4, 0), (4, -1), 'RIGHT'),
#         ]
#
#         document_header = Table(
#             [('PRODUCTO', 'CANT', 'UM', 'PRECIO', 'IMPORTE')],
#             colWidths=[_wt * 40 / 100, _wt * 10 / 100, _wt * 10 / 100, _wt * 20 / 100, _wt * 20 / 100]
#         )
#         document_header.setStyle(TableStyle(my_style_header))
#
#         my_style_table_detail = [
#             ('FONTNAME', (0, 0), (-1, -1), 'Square'),
#             # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#             ('FONTSIZE', (0, 0), (-1, -1), 8),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
#             ('LEFTPADDING', (0, 0), (0, -1), 0),  # first column
#             ('ALIGNMENT', (1, 0), (1, -1), 'CENTER'),  # second column
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('ALIGNMENT', (2, 0), (2, -1), 'CENTER'),  # third column
#             ('ALIGNMENT', (3, 0), (3, -1), 'RIGHT'),
#             ('RIGHTPADDING', (3, 0), (3, -1), 0),
#             ('ALIGNMENT', (4, 0), (4, -1), 'RIGHT'),
#             ('RIGHTPADDING', (4, 0), (4, -1), 0),
#         ]
#         _rows = []
#         total = 0
#         for d in order_obj.orderdetail_set.filter(is_state=False):
#             _product = Paragraph(d.product.name.upper(), styles["Left-text"])
#             _amount = d.quantity * d.price
#             _rows.append((_product, str(decimal.Decimal(round(d.quantity, 2))), d.unit.name, str(round(d.price, 2)),
#                           str(decimal.Decimal(round(_amount, 2)))))
#             total = total + _amount
#         document_detail = Table(_rows,
#                                 colWidths=[_wt * 40 / 100, _wt * 10 / 100, _wt * 10 / 100, _wt * 20 / 100,
#                                            _wt * 20 / 100])
#         document_detail.setStyle(TableStyle(my_style_table_detail))
#
#         my_style_total = [
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#             ('FONTNAME', (0, 0), (-1, -1), 'Ticketing'),  # all columns
#             ('FONTSIZE', (0, 0), (-1, -1), 9),  # all columns
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # all columns
#             # ('RIGHTPADDING', (2, 0), (2, -1), 0),  # third column
#             ('ALIGNMENT', (1, 0), (1, -1), 'RIGHT'),  # third column
#             # ('RIGHTPADDING', (3, 0), (3, -1), 0.3),  # four column
#             # ('ALIGNMENT', (3, 0), (3, -1), 'RIGHT'),  # four column
#             # ('LEFTPADDING', (0, 0), (-1, -1), 0.5),  # first column
#             # ('FONTNAME', (0, 2), (-1, 2), 'Square-Bold'),  # third row
#             # ('FONTSIZE', (0, 2), (-1, 2), 10),  # third row
#         ]
#         money = str(order_obj.coin.abbreviation)
#         total_discount = (total * order_obj.discount_output) / decimal.Decimal(100.00)
#         total_amount = (total - total_discount) * decimal.Decimal(1.1800)
#         total_igv = total_amount - total
#         if order_obj.subsidiary.is_igv:
#             table_total = [
#                 ['GRAVADA', money + ' ' + str(round(total, 2))],
#                 ['DESCUENTO', money + ' ' + str(round(total_discount, 2))],
#                 ['I.G.V.(18%)', money + ' ' + str(round(total_igv, 2))],
#                 ['TOTAL', money + ' ' + str(round(total_amount, 2))]
#             ]
#         else:
#             table_total = [
#                 ['EXONERADA', money + ' ' + str(round(total_amount, 2))],
#                 ['DESCUENTO', money + ' ' + str(round(total_discount, 2))],
#                 ['I.G.V.(18%)', money + ' ' + str(round(decimal.Decimal(0.00), 2))],
#                 ['TOTAL', money + ' ' + str(round(total_amount, 2))]
#             ]
#
#         document_total = Table(table_total,
#                                colWidths=[_wt * 30 / 100, _wt * 30 / 100])
#         document_total.setStyle(TableStyle(my_style_total))
#
#         footer = 'SON: ' + number_money(round(total_amount, 2), str(order_obj.coin.description.upper())).upper()
#         counter = order_obj.orderdetail_set.count()
#         _dictionary = []
#         _dictionary.append(I)
#         _dictionary.append(Spacer(1, 5))
#         _dictionary.append(Paragraph(title_business.replace("\n", "<br />"), styles["Center"]))
#         _dictionary.append(Paragraph(line, styles["Center2"]))
#         _dictionary.append(Paragraph(document_type, styles["Center_Regular"]))
#         # _dictionary.append(Draws(count_row=1))
#         _dictionary.append(Spacer(1, 3))
#         _dictionary.append(Paragraph(document_number_order, styles["Center_Regular"]))
#         _dictionary.append(Spacer(1, 3))
#         _dictionary.append(document_client)
#         _dictionary.append(Paragraph(line, styles["Center2"]))
#         _dictionary.append(Spacer(1, 3))
#         _dictionary.append(Paragraph('DETALLE DE PRODUCTOS', styles["Center_Regular"]))
#         _dictionary.append(Spacer(1, 3))
#         _dictionary.append(Paragraph(line, styles["Center2"]))
#         _dictionary.append(document_header)
#         _dictionary.append(Spacer(1, 2))
#         _dictionary.append(Paragraph(line, styles["Center2"]))
#         _dictionary.append(document_detail)
#         _dictionary.append(Spacer(1, 3))
#         _dictionary.append(Paragraph(line, styles["Center2"]))
#         _dictionary.append(Spacer(1, 3))
#         _dictionary.append(document_total)
#         _dictionary.append(Paragraph(line, styles["Center2"]))
#         _dictionary.append(Spacer(1, 3))
#         _dictionary.append(Paragraph(footer, styles["Center"]))
#         _dictionary.append(Paragraph(line, styles["Center2"]))
#         _dictionary.append(Spacer(1, 3))
#         _dictionary.append(
#             Paragraph(str("***" + str(order_obj.get_type_display()).upper() + "***").replace('***', '"'),
#                       styles["Center2"]))
#         _dictionary.append(Spacer(1, 2))
#         _dictionary.append(Paragraph(line, styles["Center2"]))
#         _dictionary.append(Spacer(1, 1))
#         _dictionary.append(Paragraph(
#             "www.jcarrillo.com",
#             styles["Center2"]))
#         buff = io.BytesIO()
#
#         ml = 0.05 * inch
#         mr = 0.055 * inch
#         ms = 0.039 * inch
#         mi = 0.039 * inch
#
#         doc = SimpleDocTemplate(buff,
#                                 pagesize=(3.14961 * inch, 8.5 * inch + (inch * 0.15 * counter)),
#                                 rightMargin=mr,
#                                 leftMargin=ml,
#                                 topMargin=ms,
#                                 bottomMargin=mi,
#                                 title=str(order_obj.get_type_display()) + "-" + str(str(order_obj.number).zfill(10))
#                                 )
#         doc.build(_dictionary)
#         # doc.build(elements)
#         # doc.build(Story)
#
#         response = HttpResponse(content_type='application/pdf')
#
#         # response['Content-Dlisposition'] = 'inline; filename="somefilename.pdf"'
#         # response['Content-Disposition'] = 'attachment; filename="ORDEN[{}].pdf"'.format(
#         #     str(order_obj.subsidiary_store.subsidiary.serial) + '-' + str(order_obj.id))
#
#         response.write(buff.getvalue())
#         buff.close()
#         return response
#
#
# class PrintDraw(Flowable):
#     def __init__(self, width=200, height=3, count_row=None):
#         self.width = width
#         self.height = height
#         self.count_row = count_row
#
#     def wrap(self, *args):
#         """Provee el tamaño del área de dibujo"""
#         return (self.width, self.height)
#
#     def draw(self):
#         canvas = self.canv
#         canvas.saveState()
#         canvas.setLineWidth(4)
#         # canvas.setFillColor(red)
#         # canvas.setFillColor(Color(0, 0, 0, alpha=0.2))
#         # canvas.drawImage(watermark, 70, -550, mask='auto', width=600 / 1.5, height=600 / 1.5)
#         # canvas.setFillColor(Color(0, 0.2, 0.6, alpha=0.1))
#         canvas.setStrokeGray(0.6)
#         row_d = self.count_row
#         # canvas.setFont('Newgot', 30)
#         # canvas.setFillColorRGB(0.5, 0.5, 0.5)
#         # pie = "static/img/pie1.png"
#         # canvas.setFillColor(Color(2, 50, 0, alpha=1))
#         # canvas.drawImage(pie, 10, -730, mask='auto', width=800 / 1.5, height=130 / 1.5)
#         canvas.roundRect(-7, 1, 563, 90, 8, stroke=1, fill=0)
#         canvas.restoreState()
#
#
# def footer_draw(canvas, doc):
#     canvas.saveState()
#     pageNumber = canvas._pageNumber
#     if pageNumber > 0:
#         canvas.setFillColor(Color(0, 0, 0, alpha=0.4))
#         canvas.drawImage(watermark, 75, (doc.height - 370) / 2, width=400, height=400)
#         canvas.setStrokeGray(0.3)
#         # canvas.drawString(10 * cm, cm, 'Pagina ' + str(pageNumber))
#         # p = Paragraph('Pagina ' + str(pageNumber),
#         #               styles["narrow_center"])
#         footer1 = Paragraph("CONDICIONES Y TÉRMINOS DEL SERVICIO",
#                             styles["narrow_center_pie"])
#         footer2 = Paragraph(
#             "Los servicios deben ser ejecutados de acuerdo a las especificaciones técnicas indicadas en la Orden de Servicio o anexos a ella. Las facturas serán recepcionadas con una copia de la orden de servicio.",
#             styles["narrow_center_pie"])
#         footer3 = Paragraph("No se aceptarán facturas por montos diferentes a la presente orden de servicio.",
#                             styles["narrow_center_pie"])
#         # footer4 = Paragraph("NOTAS",
#         #                     styles["narrow_center_pie"])
#         footer5 = Paragraph("NOTA: La recepción de la presente orden de compra significa la aceptación de la misma.",
#                             styles["narrow_center_pie"])
#         w1, h1 = footer1.wrap(doc.width, doc.bottomMargin)
#         w2, h2 = footer2.wrap(doc.width, doc.bottomMargin)
#         w3, h3 = footer3.wrap(doc.width, doc.bottomMargin)
#         # w4, h4 = footer4.wrap(doc.width, doc.bottomMargin)
#         w5, h5 = footer5.wrap(doc.width, doc.bottomMargin)
#         # w, h = p.wrap(doc.width, doc.bottomMargin)
#         footer1.drawOn(canvas, doc.leftMargin, h1 + 35)
#         footer2.drawOn(canvas, doc.leftMargin, h2 + 9)
#         footer3.drawOn(canvas, doc.leftMargin, h3 + 9)
#         # footer4.drawOn(canvas, doc.leftMargin, h4 + 9)
#         footer5.drawOn(canvas, doc.leftMargin, h5)
#         # p.drawOn(canvas, 10 * cm, h)
#         canvas.setLineWidth(1)
#         canvas.setStrokeColor(black)
#         # canvas.line(15, 75, 580, 75)
#         canvas.line(15, 52, 580, 52)
#         # canvas.setFont('Times-Roman', 9)
#         # canvas.setLineWidth(4)
#         # canvas.setFillColor(Color(0, 0, 0, alpha=1))
#         # canvas.setStrokeGray(0.9)
#         # canvas.roundRect(18, 730, 563, 90, 8, stroke=1, fill=0)
#         canvas.restoreState()
#
#
# def draw_barcode(canvas, doc):
#     canvas.saveState()
#     page_num = canvas._pageNumber
#     mybarcode = qr_code('www.mousevspython.com - Page %s' % page_num)
#     mybarcode.drawOn(canvas, 40, 40)
#     canvas.restoreState()
#
#
# def qr_code(table):
#     # generate and rescale QR
#     qr_code = qr.QrCodeWidget(table)
#     bounds = qr_code.getBounds()
#     width = bounds[2] - bounds[0]
#     height = bounds[3] - bounds[1]
#     drawing = Drawing(
#         3.5 * cm, 3.5 * cm, transform=[3.5 * cm / width, 0, 0, 3.5 * cm / height, 0, 0])
#     drawing.add(qr_code)
#
#     return drawing
#
#
# def assigmentpdf(request, pk=None):
#     order_obj = Order.objects.get(id=pk)
#     client_obj = order_obj.client
#     _a4 = (8.3 * inch, 11.7 * inch)
#     ml = 0.25 * inch
#     mr = 0.25 * inch
#     ms = 0.25 * inch
#     mi = 0.25 * inch
#
#     _bts = 8.3 * inch - 0.25 * inch - 0.25 * inch
#     I = Image(logo)
#     I.drawHeight = 3.00 * inch / 2.9
#     I.drawWidth = 5.6 * inch / 2.9
#     subsidiary_obj = get_subsidiary_by_user(order_obj.user)
#     responsible_style = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),  # all columns
#         ('GRID', (0, 0), (-1, -1), 1, HexColor('#5f64de')),  # all columns
#         ('BACKGROUND', (0, 0), (0, -1), HexColor('#5f64de')),
#         ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
#         ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 5),  # all columns
#         ('RIGHTPADDING', (-1, 0), (-1, -1), 10),  # second column
#         ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),  # all column
#     ]
#     responsible = Table([('RESPONSABLE  DE LA ORDEN: ', str(order_obj.responsible).upper())],
#                         colWidths=[_bts * 25 / 100, _bts * 75 / 100])
#     responsible.setStyle(TableStyle(responsible_style))
#
#     client_header_style = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),  # all columns
#         ('GRID', (0, 0), (-1, -1), 1, HexColor('#5f64de')),  # all columns
#         ('BACKGROUND', (0, 0), (-1, -1), HexColor('#5f64de')),
#         # Establecer el color de fondo de la segunda fila    ]
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
#         ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 5),  # all columns
#         ('RIGHTPADDING', (-1, 0), (-1, -1), 10),  # second column
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#     ]
#     client_header = Table([('INFORMACIÓN DEL CLIENTE', 'DATOS DE LA ' + str(order_obj.get_type_display()).upper())],
#                           colWidths=[_bts * 75 / 100, _bts * 25 / 100])
#     client_header.setStyle(TableStyle(client_header_style))
#
#     title = [
#         [Paragraph(str(subsidiary_obj.business_name), styles["narrow_b_tittle_justify"])],
#         [Paragraph(str(subsidiary_obj.address), styles["narrow_b_justify"])],
#         [Paragraph('Correo: ' + str(subsidiary_obj.email), styles['narrow_b_justify'])],
#         [Paragraph('Telefono: ' + str(subsidiary_obj.phone), styles['narrow_b_justify'])],
#     ]
#     T = Table(title)
#     title_style = [
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         # ('TEXTCOLOR', (0, 0), (-1, -1), colors.red)
#         ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#     ]
#     T.setStyle(TableStyle(title_style))
#
#     document = [
#         ['RUC ' + str(subsidiary_obj.ruc)],
#         [str(order_obj.get_type_display()).upper()],
#         [str(subsidiary_obj.serial) + ' - ' + str(str(order_obj.number).zfill(10))],
#     ]
#     D = Table(document)
#     document_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
#         ('FONTSIZE', (0, 0), (-1, -1), 13),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
#         ('SPAN', (0, 0), (0, 0))
#     ]
#     D.setStyle(TableStyle(document_style))
#     H = [
#         [I, T, D],
#     ]
#     document_header = Table(H, colWidths=[_bts * 25 / 100, _bts * 50 / 100, _bts * 25 / 100])
#     header_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # first column
#         ('SPAN', (0, 0), (0, 0)),  # first row
#         # ('LINEBELOW', (0, -1), (-1, -1), 0.5, purple, 1, None, None, 4, 1),
#         ('BACKGROUND', (2, 0), (-1, 1), HexColor('#5f64de')),  # Establecer el color de fondo de la segunda fila
#         ('LINEBEFORE', (1, 0), (-1, -1), 0.1, colors.grey),
#         # Establezca el color de la línea izquierda de la tabla en
#     ]
#     document_header.setStyle(TableStyle(header_style))
#     # ---------------------------------Datos Cliente----------------------------#
#     client_address = '-'
#     client_phone = '-'
#     client_email = '-'
#     if client_obj.address:
#         client_address = client_obj.address
#     if client_obj.telephone:
#         client_phone = client_obj.telephone
#     if client_obj.email:
#         client_email = client_obj.email
#     client = [
#         ['CLIENTE :', Paragraph(str(client_obj.full_name.upper()), styles["narrow_a_justify"])],
#         [str(client_obj.type.abbreviation) + ' :', str(client_obj.document)],
#         ['DIRECCION :', Paragraph(str(client_address.upper()), styles["narrow_a_justify"])],
#         ['TELEFONO  :', str(client_phone)],
#         ['CORREO     :', str(client_email).upper()]
#     ]
#     C = Table(client, colWidths=[_bts * 10 / 100, _bts * 64 / 100])
#     client_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#         ('FONTNAME', (0, 0), (-1, -1), 'Narrow-a'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),  # first column
#         ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
#     ]
#     C.setStyle(TableStyle(client_style))
#     order = [
#         ['FECHA: ', str(order_obj.create_at.strftime("%d-%m-%Y"))],
#         ['ESTADO: ', str(order_obj.get_status_display()).upper()],
#         ['', ''],
#
#     ]
#     if order_obj.type == 'AL' or order_obj.type == 'TA':
#         date_init = ['INICIO: ', str(order_obj.date_init.strftime("%d-%m-%Y"))]
#         date_end = ['TERMINO: ', str(order_obj.date_end.strftime("%d-%m-%Y"))]
#         order.append(date_init)
#         order.append(date_end)
#     O = Table(order, colWidths=[_bts * 12 / 100, _bts * 14 / 100])
#     O.setStyle(TableStyle(client_style))
#     CH2 = [
#         [C, O],
#     ]
#     document_client = Table(CH2, colWidths=[_bts * 74 / 100, _bts * 26 / 100])
#     cd_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('ALIGNMENT', (0, 0), (0, -1), 'CENTER'),  # first column
#     ]
#     document_client.setStyle(TableStyle(cd_style))
#     # ------------ENCABEZADO DEL DETALLE-------------------#
#     header_detail_style = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),  # all columns
#         ('GRID', (0, 0), (-1, -1), 1, HexColor('#5f64de')),  # all columns
#         ('BACKGROUND', (0, 0), (-1, 1), HexColor('#5f64de')),
#         # Establecer el color de fondo de la segunda fila    ]
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#     ]
#     width_table = [_bts * 5 / 100, _bts * 68 / 100, _bts * 12 / 100, _bts * 15 / 100]
#     document_header_detail = Table([('Nº', 'DESCRIPCIÓN', 'CANTIDAD', 'UNIDAD MEDIDA')],
#                                    colWidths=width_table)
#     document_header_detail.setStyle(TableStyle(header_detail_style))
#
#     # -------------------DETAIL---------------------#
#     row_detail = []
#     count = 0
#     total_amount = 0
#     for d in order_obj.orderdetail_set.filter(is_state=False).order_by('id'):
#         count = count + 1
#         _product = Paragraph(
#             (str(d.product.name.upper()) + '\n' + str(d.description.upper())).replace("\n", "<br/>"),
#             styles["narrow_a_justify"])
#         _unit = str(d.unit.description.upper())
#         _quantity = str(round(decimal.Decimal(d.quantity), 2))
#         # _price = str(round(decimal.Decimal(d.price), 2))
#         # _amount = str(round(decimal.Decimal(d.quantity) * decimal.Decimal(d.price), 2))
#         row_detail.append((str(count), _product, _quantity, _unit))
#         # total_amount = total_amount + d.quantity * d.price
#     document_body_detail = Table(row_detail,
#                                  colWidths=[_bts * 5 / 100, _bts * 68 / 100, _bts * 12 / 100,
#                                             _bts * 15 / 100])
#     body_detail_style = [
#         ('GRID', (0, 0), (-1, -1), 0.1, colors.blue),
#         ('FONTNAME', (0, 0), (-1, -1), 'Narrow-a'),
#         ('FONTSIZE', (0, 0), (-1, -1), 9),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#         ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),  # three column
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # first column
#         # ('BACKGROUND', (4, 0), (4, -1), colors.blue),  # four column
#     ]
#     document_body_detail.setStyle(TableStyle(body_detail_style))
#     # -------------- Footer Detail ----------------------------
#     # footer = [
#     #     [Paragraph(
#     #         'Observaciones: ' + str(subsidiary_obj.observation_output),
#     #         styles["narrow_justify_observation"]), '            '],
#     #     [Paragraph(' ', styles["narrow_justify"]),
#     #      Paragraph(' ', styles["narrow_justify"])],
#     #     [Paragraph(' ', styles["narrow_justify"]),
#     #      Paragraph(' ', styles["narrow_justify"])],
#     #     [Paragraph(' ', styles["narrow_justify"]),
#     #      Paragraph(' ', styles["narrow_justify"])],
#     #     [Paragraph(' ', styles["narrow_justify"]),
#     #      Paragraph(' ', styles["narrow_justify"])],
#     #     [Paragraph('_____________________', styles["narrow_center"]),
#     #      Paragraph('_____________________', styles["narrow_center"])],
#     #     [Paragraph('Área Logística', styles["narrow_center"]),
#     #      Paragraph('V°B° Administración', styles["narrow_center"])]
#     # ]
#     # document_footer = Table(footer, colWidths=[_bts * 50 / 100, _bts * 50 / 100])
#     # footer_style = [
#     #     # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#     #     ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
#     #     ('FONTSIZE', (0, 0), (-1, -1), 8),
#     #     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#     #     ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
#     #     ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
#     # ]
#     # document_footer.setStyle(TableStyle(footer_style))
#     # ------------------------------------------------------------------------------------------
#     buff = io.BytesIO()
#     doc = SimpleDocTemplate(buff,
#                             pagesize=(8.3 * inch, 11.7 * inch),
#                             rightMargin=mr,
#                             leftMargin=ml,
#                             topMargin=ms,
#                             bottomMargin=mi,
#                             title=str(order_obj.get_type_display()) + "-" + str(str(order_obj.number).zfill(10)),
#
#                             )
#     dictionary = []
#     dictionary.append(document_header)
#     dictionary.append(PrintDraw(count_row=count))
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(responsible)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(client_header)
#     dictionary.append(document_client)
#     dictionary.append(Spacer(1, 16))
#     dictionary.append(document_header_detail)
#     dictionary.append(document_body_detail)
#     response = HttpResponse(content_type='application/pdf')
#     doc.build(dictionary, canvasmaker=NumberedCanvas, onFirstPage=footer_draw, onLaterPages=footer_draw)
#     response.write(buff.getvalue())
#     buff.close()
#     return response
#
#
# def document_input(request, pk=None):
#     order_obj = Order.objects.get(id=pk)
#     client_obj = order_obj.client
#     _a4 = (8.3 * inch, 11.7 * inch)
#     ml = 0.25 * inch
#     mr = 0.25 * inch
#     ms = 0.25 * inch
#     mi = 0.25 * inch
#
#     _bts = 8.3 * inch - 0.25 * inch - 0.25 * inch
#     I = Image(logo)
#     I.drawHeight = 3.00 * inch / 2.9
#     I.drawWidth = 5.6 * inch / 2.9
#     subsidiary_obj = get_subsidiary_by_user(order_obj.user)
#     client_header_style = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),  # all columns
#         ('GRID', (0, 0), (-1, -1), 1, HexColor('#5f64de')),  # all columns
#         ('BACKGROUND', (0, 0), (-1, -1), HexColor('#5f64de')),
#         # Establecer el color de fondo de la segunda fila    ]
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
#         ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 5),  # all columns
#         ('RIGHTPADDING', (-1, 0), (-1, -1), 10),  # second column
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#     ]
#     client_header = Table(
#         [('INFORMACIÓN DEL PROVEEDOR', 'DATOS DE LA ' + str(order_obj.get_type_display()).upper())],
#         colWidths=[_bts * 75 / 100, _bts * 25 / 100])
#     client_header.setStyle(TableStyle(client_header_style))
#
#     title = [
#         [Paragraph(str(subsidiary_obj.business_name), styles["narrow_b_tittle_justify"])],
#         [Paragraph(str(subsidiary_obj.address), styles["narrow_b_justify"])],
#         [Paragraph('Correo: ' + str(subsidiary_obj.email), styles['narrow_b_justify'])],
#         [Paragraph('Telefono: ' + str(subsidiary_obj.phone), styles['narrow_b_justify'])],
#     ]
#     T = Table(title)
#     title_style = [
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         # ('TEXTCOLOR', (0, 0), (-1, -1), colors.red)
#         ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#     ]
#     T.setStyle(TableStyle(title_style))
#
#     document = [
#         ['RUC ' + str(subsidiary_obj.ruc)],
#         [str(order_obj.get_type_display()).upper()],
#         [str(subsidiary_obj.serial) + ' - ' + str(str(order_obj.number).zfill(10))],
#     ]
#     D = Table(document)
#     document_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
#         ('FONTSIZE', (0, 0), (-1, -1), 13),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
#         ('SPAN', (0, 0), (0, 0))
#     ]
#     D.setStyle(TableStyle(document_style))
#     H = [
#         [I, T, D],
#     ]
#     document_header = Table(H, colWidths=[_bts * 25 / 100, _bts * 50 / 100, _bts * 25 / 100])
#     header_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # first column
#         ('SPAN', (0, 0), (0, 0)),  # first row
#         # ('LINEBELOW', (0, -1), (-1, -1), 0.5, purple, 1, None, None, 4, 1),
#         ('BACKGROUND', (2, 0), (-1, 1), HexColor('#5f64de')),  # Establecer el color de fondo de la segunda fila
#         ('LINEBEFORE', (1, 0), (-1, -1), 0.1, colors.grey),
#         # Establezca el color de la línea izquierda de la tabla en
#     ]
#     document_header.setStyle(TableStyle(header_style))
#     # ---------------------------------Datos Cliente----------------------------#
#     client_address = '-'
#     client_phone = '-'
#     client_email = '-'
#     if client_obj.address:
#         client_address = client_obj.address
#     if client_obj.telephone:
#         client_phone = client_obj.telephone
#     if client_obj.email:
#         client_email = client_obj.email
#     client = [
#         ['PROVEEDOR:', str(client_obj.full_name.upper())],
#         [str(client_obj.type.abbreviation) + ' :', str(client_obj.document)],
#         ['DIRECCION :', Paragraph(str(client_address.upper()), styles["narrow_a_justify"])],
#         ['TELEFONO  :', str(client_phone)],
#         ['CORREO     :', str(client_email).upper()]
#     ]
#     C = Table(client, colWidths=[_bts * 10 / 100, _bts * 64 / 100])
#     client_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#         ('FONTNAME', (0, 0), (-1, -1), 'Narrow-a'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),  # first column
#         ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
#     ]
#     C.setStyle(TableStyle(client_style))
#     employee_obj = Employee.objects.get(user=order_obj.user)
#     order = [
#         ['FECHA: ', str(order_obj.create_at.strftime("%d-%m-%Y"))],
#         ['ESTADO: ', str(order_obj.get_status_display()).upper()],
#         ['USUARIO: ', str(employee_obj.user.first_name).upper()],
#         ['MONEDA: ', str(order_obj.coin.description).upper()],
#         ['COMPROBANTE : ', str(order_obj.bill_number)],
#     ]
#     O = Table(order, colWidths=[_bts * 12 / 100, _bts * 14 / 100])
#     O.setStyle(TableStyle(client_style))
#     CH2 = [
#         [C, O],
#     ]
#     document_client = Table(CH2, colWidths=[_bts * 74 / 100, _bts * 26 / 100])
#     cd_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('ALIGNMENT', (0, 0), (0, -1), 'CENTER'),  # first column
#     ]
#     document_client.setStyle(TableStyle(cd_style))
#     # ------------ENCABEZADO DEL DETALLE-------------------#
#     header_detail_style = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),  # all columns
#         ('GRID', (0, 0), (-1, -1), 1, HexColor('#5f64de')),  # all columns
#         ('BACKGROUND', (0, 0), (-1, 1), HexColor('#5f64de')),
#         # Establecer el color de fondo de la segunda fila    ]
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
#         ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 5),  # all columns
#         ('RIGHTPADDING', (1, 0), (1, -1), 10),  # second column
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#         ('ALIGNMENT', (2, 0), (2, -1), 'LEFT'),  # second column
#     ]
#     width_table = [_bts * 5 / 100, _bts * 44 / 100, _bts * 12 / 100, _bts * 15 / 100,
#                    _bts * 12 / 100,
#                    _bts * 12 / 100]
#     document_header_detail = Table([('Nº', 'DESCRIPCIÓN', 'CANTIDAD', 'UND MED', 'PRECIO', 'IMPORTE')],
#                                    colWidths=width_table)
#     document_header_detail.setStyle(TableStyle(header_detail_style))
#     # ------------ENCABEZADO DEL DETALLE-------------------#
#     row_detail = []
#     # -------------------DETAIL---------------------#
#     count = 0
#     total_amount = 0
#     for d in order_obj.orderdetail_set.filter(is_state=True).order_by('id'):
#         count = count + 1
#         _product = Paragraph(
#             (str(d.product.name.upper()) + '\n' + str(d.description.upper())).replace("\n", "<br/>"),
#             styles["narrow_a_justify"])
#         _unit = str(d.unit.description.upper())
#         _quantity = str(round(decimal.Decimal(d.quantity), 2))
#         _price = str(round(decimal.Decimal(d.price), 2))
#         _amount = str(round(decimal.Decimal(d.quantity) * decimal.Decimal(d.price), 2))
#         row_detail.append((str(count), _product, _quantity, _unit, _price, _amount))
#         total_amount = total_amount + d.quantity * d.price
#     document_body_detail = Table(row_detail,
#                                  colWidths=[_bts * 5 / 100, _bts * 44 / 100, _bts * 12 / 100,
#                                             _bts * 15 / 100, _bts * 12 / 100, _bts * 12 / 100])
#     body_detail_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#7a3621')),
#         ('FONTNAME', (0, 0), (-1, -1), 'Narrow-a'),
#         ('FONTSIZE', (0, 0), (-1, -1), 9),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#         ('ALIGNMENT', (1, 0), (2, -1), 'LEFT'),  # three column
#         ('ALIGNMENT', (3, 0), (4, -1), 'CENTER'),  # three column
#         ('ALIGNMENT', (5, 0), (-1, -1), 'RIGHT'),  # three column
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # first column
#         ('RIGHTPADDING', (3, 0), (3, -1), 10),  # first column
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # all columns
#         # ('BACKGROUND', (4, 0), (4, -1), colors.blue),  # four column
#     ]
#     document_body_detail.setStyle(TableStyle(body_detail_style))
#     # -------------- Footer Detail ----------------------------
#     money = str(order_obj.coin.abbreviation)
#     total_discount = decimal.Decimal(order_obj.discount_input)
#     sub_total = (decimal.Decimal(total_amount) / decimal.Decimal(1.1800)) - total_discount
#     total_invoice = decimal.Decimal(order_obj.total_input)
#     total_igv = total_invoice - sub_total
#     if order_obj.subsidiary.is_igv:
#         total = [
#             ['GRAVADA', money + ' ' + str(round(sub_total, 2))],
#             ['DESCUENTO', money + ' ' + str(round(total_discount, 2))],
#             ['I.G.V.(18%)', money + ' ' + str(round(total_igv, 2))],
#             ['TOTAL', money + ' ' + str(round(total_invoice, 2))]
#         ]
#     else:
#         total = [
#             ['EXONERADA', money + ' ' + str(round(total_amount, 2))],
#             ['DESCUENTO', money + ' ' + str(round(total_discount, 2))],
#             ['I.G.V.(18%)', money + ' ' + str(round(decimal.Decimal(0.00), 2))],
#             ['TOTAL', money + ' ' + str(round(total_amount, 2))]
#         ]
#     TT = Table(total, colWidths=[_bts * 15 / 100, _bts * 15 / 100])
#
#     total_style = [
#         ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#         ('FONTNAME', (0, 0), (-1, 2), 'Narrow-a'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('FONTSIZE', (0, 3), (-1, -1), 11),
#         ('FONTNAME', (0, 3), (-1, -1), 'Newgot'),
#         ('TEXTCOLOR', (0, 3), (-1, -1), colors.white),
#         ('ALIGNMENT', (0, 0), (1, -1), 'LEFT'),
#         ('ALIGNMENT', (1, 0), (-1, -1), 'RIGHT'),
#         ('BACKGROUND', (0, 3), (-1, -1), HexColor('#5f64de')),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#5f64de')),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
#     ]
#     TT.setStyle(TableStyle(total_style))
#     total_letter = [
#         ['SON: ' + number_money(round(total_invoice, 2), str(order_obj.coin.description.upper())).upper()],
#         # [t_bank],
#     ]
#     TL = Table(total_letter, colWidths=[_bts * 70 / 100])
#     total_letter_style = [
#         ('RIGHTPADDING', (0, 0), (-1, -1), 10),
#         ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
#         ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),
#     ]
#     TL.setStyle(TableStyle(total_letter_style))
#
#     total_ = [
#         [TL, TT],
#     ]
#     document_total = Table(total_, colWidths=[_bts * 70 / 100, _bts * 30 / 100])
#     total_style = [
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # three column
#         ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),  # first column
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.red),
#     ]
#     document_total.setStyle(TableStyle(total_style))
#     # --------------------------------------------------------------------------------------
#     footer = [
#         [Paragraph(
#             'Observaciones: ' + str(subsidiary_obj.observation_input),
#             styles["narrow_justify_observation"]), '            '],
#         [Paragraph(' ', styles["narrow_justify"]), Paragraph(' ', styles["narrow_justify"])],
#         [Paragraph(' ', styles["narrow_justify"]),
#          Paragraph(' ', styles["narrow_justify"])],
#         [Paragraph(' ', styles["narrow_justify"]),
#          Paragraph(' ', styles["narrow_justify"])],
#         [Paragraph(' ', styles["narrow_justify"]),
#          Paragraph(' ', styles["narrow_justify"])],
#         [Paragraph('_____________________', styles["narrow_center"]),
#          Paragraph('_____________________', styles["narrow_center"])],
#         [Paragraph('Área Logística', styles["narrow_center"]),
#          Paragraph('V°B° Administración', styles["narrow_center"])]
#     ]
#     document_footer = Table(footer, colWidths=[_bts * 50 / 100, _bts * 50 / 100])
#     footer_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#         ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
#     ]
#     document_footer.setStyle(TableStyle(footer_style))
#     # ------------------------------------------------------------------------------------------
#     buff = io.BytesIO()
#     doc = SimpleDocTemplate(buff,
#                             pagesize=(8.3 * inch, 11.7 * inch),
#                             rightMargin=mr,
#                             leftMargin=ml,
#                             topMargin=ms,
#                             bottomMargin=mi,
#                             title=str(order_obj.get_type_display()) + "-" + str(str(order_obj.number).zfill(10)),
#
#                             )
#     dictionary = []
#     dictionary.append(document_header)
#     dictionary.append(InputPrint(count_row=count))
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(client_header)
#     dictionary.append(document_client)
#     dictionary.append(Spacer(1, 16))
#     dictionary.append(document_header_detail)
#     dictionary.append(document_body_detail)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(document_total)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(document_footer)
#     # dictionary.append(Spacer(1, 5))
#     # dictionary.append(Paragraph('www.jcarrillo.com', styles["Justify-Dotcirful"]))
#     response = HttpResponse(content_type='application/pdf')
#     doc.build(dictionary)
#     response.write(buff.getvalue())
#     buff.close()
#     return response
#
#
# class InputPrint(Flowable):
#     def __init__(self, width=200, height=3, count_row=None):
#         self.width = width
#         self.height = height
#         self.count_row = count_row
#
#     def wrap(self, *args):
#         """Provee el tamaño del área de dibujo"""
#         return (self.width, self.height)
#
#     def draw(self):
#         canvas = self.canv
#         canvas.saveState()
#         canvas.setLineWidth(4)
#         # canvas.setFillColor(red)
#         pie_input = "static/img/pie_input.png"
#         canvas.setFillColor(Color(0, 0, 0, alpha=0.2))
#         canvas.drawImage(watermark, 70, -550, mask='auto', width=600 / 1.5, height=600 / 1.5)
#         canvas.setFillColor(Color(0, 0.2, 0.6, alpha=0.1))
#         canvas.setStrokeGray(0.9)
#         row_d = 0
#         row_d = self.count_row
#         # canvas.setFont('Newgot', 30)
#         # canvas.setFillColorRGB(0.5, 0.5, 0.5)
#         canvas.setFillColor(Color(0, 0, 0, alpha=1))
#         canvas.drawImage(pie_input, -2, -730, mask='auto', width=830 / 1.5, height=190 / 1.5)
#         if row_d == 1:
#             d = 50 + row_d * 25
#         else:
#             d = 30 + row_d * 25
#         canvas.roundRect(-7, 1, 563, 84, 8, stroke=1, fill=0)
#         canvas.restoreState()
#
#
# def contract_service(request, pk=None):
#     order_obj = Order.objects.get(id=pk)
#     client_obj = order_obj.client
#     client_business = '-'
#     client_ruc = '-'
#     client_address = '-'
#     client_dni = '-'
#     client_name = '-'
#     client_departure = '-'
#     if client_obj.full_name:
#         client_business = client_obj.full_name
#     if client_obj.document:
#         client_ruc = client_obj.document
#     if client_obj.address:
#         client_address = client_obj.address
#     if client_obj.representative_dni:
#         client_dni = client_obj.representative_dni
#     if client_obj.representative_name:
#         client_name = client_obj.representative_name
#     if client_obj.departure:
#         client_departure = client_obj.departure
#     subsidiary_obj = get_subsidiary_by_user(order_obj.user)
#     business_name = '-'
#     business_ruc = '-'
#     business_address = '-'
#     business_representative_dni = '-'
#     business_representative_name = '-'
#     if subsidiary_obj.business_name:
#         business_name = subsidiary_obj.business_name
#     if subsidiary_obj.ruc:
#         business_ruc = subsidiary_obj.ruc
#     if subsidiary_obj.address:
#         business_address = subsidiary_obj.address
#     if subsidiary_obj.representative_dni:
#         business_representative_dni = subsidiary_obj.representative_dni
#     if subsidiary_obj.representative_name:
#         business_representative_name = subsidiary_obj.representative_name
#     A4 = (8.3 * inch, 11.7 * inch)
#     ml = 0.25 * inch
#     mr = 0.25 * inch
#     ms = 0.65 * inch
#     mi = 0.65 * inch
#     _bts = 8.3 * inch - 0.25 * inch - 0.25 * inch
#     # ...............................Title....................................
#     title = [[Paragraph('CONTRATO DE LOCACIÓN DE SERVICIOS', styles["narrow_b_tittle_center"])]]
#     title_width = Table(title, colWidths=[_bts * 82 / 100])
#     title_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#     ]
#     title_width.setStyle(TableStyle(title_style))
#     # .............................End title..................................
#     # ..............................Client....................................
#     client = [[
#         Paragraph(
#             'Conste por el presente documento, el Contrato de Locación de Servicios que celebran, de una parte, ' + str(
#                 client_business) + ' con RUC ' + str(
#                 client_ruc) + ', con domicilio para estos efectos en la ' + str(
#                 client_address) + ', representada en este acto por su Gerente General el Sr. ' + str(
#                 client_name) + ' identificado con DNI N°' + str(
#                 client_dni) + ' con Poder de representación inscrito en la Superintendencia Nacional de los Registros Públicos, Partida N°13330949 del Registro de Sociedades Mercantiles del Registro de Personas Jurídicas, Oficina Registral de Lima, a quien en adelante se le denominará como “EL COMITENTE” y de la otra parte ' + str(
#                 business_name) + ', con RUC ' + str(
#                 business_ruc) + ', con domicilio para estos efectos en la ' + str(
#                 business_address) + ', representada en este acto por su Gerente General la Sra. ' + str(
#                 business_representative_name) + ' identificada con DNI N° ' + str(
#                 business_representative_dni) + ' con Poder de representación inscrito en la Superintendencia Nacional de los Registros Públicos, Partida N° ' + str(
#                 client_departure) + ' del Registro de Sociedades Mercantiles del Registro de Personas Jurídicas, Oficina Registral de Lima, a quien en adelante se le denominará “EL LOCADOR”; en los términos y condiciones siguientes:',
#             styles["narrow_a_paragraph_justify"]),
#     ]]
#     client_width = Table(client, colWidths=[_bts * 82 / 100])
#     client_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     ]
#     client_width.setStyle(TableStyle(client_style))
#     # .............................End client..................................
#     # ...............................First.....................................
#     first = [[Paragraph('PRIMERO. - ANTECEDENTES', styles["narrow_b_tittle_justify"])]]
#     first_width = Table(first, colWidths=[_bts * 82 / 100])
#     first_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     ]
#     first_width.setStyle(TableStyle(first_style))
#     # .............................End first...................................
#     # .............................First one...................................
#     description_first = '-'
#     if order_obj.orderdetail_set.first().description:
#         description_first = order_obj.orderdetail_set.first().product.name + ', ' + order_obj.orderdetail_set.first().description
#     locator_activity = '-'
#     if client_obj.locator:
#         locator_activity = client_obj.locator
#     f = [
#         [Paragraph(
#             'EL COMITENTE, Supervisar trabajos de remodelación en ' + str(description_first).lower(),
#             styles["narrow_a_paragraph_justify"])],
#         [Paragraph(
#             'EL LOCADOR, ' + str(locator_activity),
#             styles["narrow_a_paragraph_justify"])]
#     ]
#     f_width = Table(f, colWidths=[_bts * 82 / 100])
#     f_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     ]
#     f_width.setStyle(TableStyle(f_style))
#     # .............................End first one...................................
#     # ...............................Second.....................................
#     second = [[Paragraph('SEGUNDA: OBJETO', styles["narrow_b_tittle_justify"])]]
#     second_width = Table(second, colWidths=[_bts * 82 / 100])
#     second_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     ]
#     second_width.setStyle(TableStyle(second_style))
#     # .............................End second...................................
#     # .............................Second one...................................
#     s1 = (Paragraph('Contratar los servicios de EL LOCADOR, para que se encargue de lo siguiente:',
#                     styles["narrow_a_paragraph_justify"]), '')
#     s2 = (Paragraph(
#         'EL LOCADOR, reconoce los protocolos, lo respeta y los practica, reconociendo este proceso como parte fundamental del ejercicio de sus funciones.',
#         styles["narrow_a_paragraph_justify"]), '')
#     s = [s1]
#     c = 0
#     time_contract = '-'
#     name_service = '-'
#     for i in order_obj.orderdetail_set.filter(is_state=False):
#         c = c + 1
#         time_contract = str(i.product.contract)
#         p_n = str(i.product.name).capitalize()
#         name_service = p_n
#         p_m = ' así como la implementación de ' + str(i.product.product_brand.name).lower().capitalize()
#         p_d = str(i.description).lower().capitalize() + ' durante la ejecución de la obra.'
#         s.append(('•', Paragraph(str(p_n + p_m + p_d), styles["narrow_a_paragraph_justify"])))
#     s.append(s2)
#     s_width = Table(s, colWidths=[_bts * 2 / 100, _bts * 80 / 100])
#     s_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('SPAN', (0, 0), (-1, 0)),
#         ('SPAN', (0, c + 1), (-1, c + 1)),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('VALIGN', (0, 0), (0, -1), 'TOP'),
#     ]
#     s_width.setStyle(TableStyle(s_style))
#     # .............................End second one...................................
#     # ...............................Third.....................................
#     third = [[Paragraph('TERCERA: PLAZO Y PENALIDAD', styles["narrow_b_tittle_justify"])]]
#     third_width = Table(third, colWidths=[_bts * 82 / 100])
#     third_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     ]
#     third_width.setStyle(TableStyle(third_style))
#     # .............................End third...................................
#     # .............................Third one...................................
#     t = [
#         [Paragraph(
#             'El plazo del presente contrato será de ' + str(
#                 time_contract) + ' calendarios el mismo que será contado a partir del inicio de obra.',
#             styles["narrow_a_paragraph_justify"])],
#         ['3.2', Paragraph(
#             'En el caso que EL COMITENTE incumpla con sus obligaciones de pago en un plazo no mayor a 15 días después de la entrega de la factura, deberá pagar a AL LOCADOR una penalidad equivalente al 0.5 % aplicable sobre el monto total del contrato, por cada día de atraso hasta un límite del 15% del monto total del contrato.',
#             styles["narrow_a_paragraph_justify"])],
#         ['3.3', Paragraph(
#             'Quedando facultado EL LOCADOR a suspender el servicio de ' + str(
#                 name_service) + ', dando finalidad al contrato y el reporte de la deuda a la central de riesgo INFOCORP.',
#             styles["narrow_a_paragraph_justify"])]
#     ]
#     t_width = Table(t, colWidths=[_bts * 10 / 100, _bts * 72 / 100])
#     t_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('SPAN', (0, 0), (-1, 0)),
#         ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (0, -1), 11),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP'),
#     ]
#     t_width.setStyle(TableStyle(t_style))
#     # .............................End third one...................................
#     # ...............................Fourth.....................................
#     fourth = [[Paragraph('CUARTA: FORMA DE PRESTAR EL SERVICIO', styles["narrow_b_tittle_justify"])]]
#     fourth_width = Table(fourth, colWidths=[_bts * 82 / 100])
#     fourth_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     ]
#     fourth_width.setStyle(TableStyle(fourth_style))
#     # .............................End fourth...................................
#     # .............................Fourth one...................................
#     fo = [
#         ['4.1', Paragraph(
#             'Siendo el presente contrato de naturaleza civil, queda establecido que EL LOCADOR no está sujeto a relación de dependencia ni a subordinación frente a EL COMITENTE.',
#             styles["narrow_a_paragraph_justify"])]
#     ]
#     fo_width = Table(fo, colWidths=[_bts * 10 / 100, _bts * 72 / 100])
#     fo_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (0, -1), 11),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP'),
#     ]
#     fo_width.setStyle(TableStyle(fo_style))
#     # .............................End fourth one...................................
#     # ...............................Fifth.....................................
#     fifth = [[Paragraph('QUINTA: CONTRAPRESTACIÓN, FORMA Y OPORTUNIDAD DE PAGO', styles["narrow_b_tittle_justify"])]]
#     fifth_width = Table(fifth, colWidths=[_bts * 82 / 100])
#     fifth_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     ]
#     fifth_width.setStyle(TableStyle(fifth_style))
#     # .............................End fifth...................................
#     payment_set = order_obj.payments_set.filter(status='R').all()
#     payment_row = []
#     payment_width = []
#     if payment_set.exists():
#         for p in payment_set:
#             types = p.get_payment_display()
#             amount = p.amount
#             date_payment = p.date_payment
#             payment_row.append(('•', Paragraph(str(types) + ' el '+str(current_date_format(date_payment))+' con un monto de '+str(round(amount, 2)) + ' soles', styles["narrow_a_paragraph_justify"])))
#         payment_width = Table(payment_row, colWidths=[_bts * 2 / 100, _bts * 80 / 100])
#         payment_style = [
#             # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#             # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),
#             ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#             ('VALIGN', (0, 0), (0, -1), 'TOP'),
#         ]
#         payment_width.setStyle(TableStyle(payment_style))
#
#     # .............................fifth one...................................
#     ff = [
#         [Paragraph(
#             'Las partes acuerdan que el monto de la retribución que EL COMITENTE pagará a EL LOCADOR, asciende a la cantidad de S/. ' + str(
#                 order_obj.total_output) + ' (' + str(number_money(order_obj.total_output, str(
#                 order_obj.coin.description))).capitalize() + '), donde se encuentra incluido todos los impuestos de ley, emitiendo EL LOCADOR factura por cada pago a realizarse.',
#             styles["narrow_a_paragraph_justify"])],
#         [Paragraph(
#             # 'La cantidad referida en el párrafo anterior será cancelada 15 días posteriores a la presentación de la factura.',
#             'La cantidad referida en el párrafo anterior será cancelada  en:',
#             styles["narrow_a_paragraph_justify"])],
#         [payment_width]
#     ]
#     ff_width = Table(ff, colWidths=[_bts * 82 / 100])
#     ff_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     ]
#     ff_width.setStyle(TableStyle(ff_style))
#     # .............................End fifth one...................................
#     # ...............................Sixth.....................................
#     sixth = [[Paragraph('SEXTA: OBLIGACIONES DE LAS PARTES', styles["narrow_b_tittle_justify"])]]
#     sixth_width = Table(sixth, colWidths=[_bts * 82 / 100])
#     sixth_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     ]
#     sixth_width.setStyle(TableStyle(sixth_style))
#     # .............................End sixth...................................
#     # .............................sixth one...................................
#     six = [
#         ['DEL COMITENTE', ''],
#         ['6.1', Paragraph(
#             'Se obliga a cancelar a EL LOCADOR la contraprestación, en la cantidad, forma y oportunidades pactadas en la cláusula quinta del presente contrato.',
#             styles["narrow_a_paragraph_justify"])],
#         ['6.2', Paragraph(
#             'Facilitarle a EL LOCADOR toda la documentación e información técnica que requiera, para llevar a cabo el servicio requerido.',
#             styles["narrow_a_paragraph_justify"])],
#         ['6.3', Paragraph(
#             'Proporcionar los equipos de protección colectivos y específicos para todas las áreas de trabajo.',
#             styles["narrow_a_paragraph_justify"])],
#         ['6.4', Paragraph(
#             'Participar de las reuniones de seguridad y comité de obra.',
#             styles["narrow_a_paragraph_justify"])],
#         ['6.5', Paragraph(
#             'Deberá atender las recomendaciones que EL LOCADOR realice, en un plazo no mayor a 24 horas.',
#             styles["narrow_a_paragraph_justify"])],
#         ['DEL LOCADOR', ''],
#         ['6.6', Paragraph(
#             'Se compromete a brindar el servicio dentro del plazo establecido en la cláusula tercera del presente contrato.',
#             styles["narrow_a_paragraph_justify"])],
#         ['6.7', Paragraph(
#             'Deberá asignar a un Prevensionista calificado en la obra materia del presente.',
#             styles["narrow_a_paragraph_justify"])],
#         ['6.8', Paragraph(
#             'Entregar a EL COMITENTE, el dossier de seguridad y salud.',
#             styles["narrow_a_paragraph_justify"])],
#         ['6.9', Paragraph(
#             'Participar en las coordinaciones y sustentaciones del proyecto (cuando se requiera) ante el Revisor Urbano.',
#             styles["narrow_a_paragraph_justify"])],
#         ['6.10', Paragraph(
#             'Transmitir a la gerencia los incidentes.',
#             styles["narrow_a_paragraph_justify"])],
#         ['6.11', Paragraph(
#             'Evaluar el desempeño de los trabajadores y comprobar que las actividades planteadas se están cumpliendo.',
#             styles["narrow_a_paragraph_justify"])]
#     ]
#     six_width = Table(six, colWidths=[_bts * 10 / 100, _bts * 72 / 100])
#     six_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('SPAN', (0, 0), (-1, 0)),
#         ('SPAN', (0, 6), (-1, 6)),
#         ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (0, -1), 11),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP'),
#     ]
#     six_width.setStyle(TableStyle(six_style))
#     # .............................End sixth one...................................
#     # ...............................Seventh.....................................
#     seventh = [[Paragraph('SEPTIMA: RESOLUCIÓN CONTRACTUAL', styles["narrow_b_tittle_justify"])]]
#     seventh_width = Table(seventh, colWidths=[_bts * 82 / 100])
#     seventh_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     ]
#     seventh_width.setStyle(TableStyle(seventh_style))
#     # .............................End seventh...................................
#     # .............................seventh one...................................
#     sev = [
#         ['7.1', Paragraph(
#             'De acuerdo con lo establecido en el artículo 1430° del Código Civil, en caso que EL COMITENTE, incumpla con cualquiera de las obligaciones a su cargo establecidas en la clausula sexta del presente contrato, EL LOCADOR podrá resolver el presente contrato y aplicar las penalidades que correspondan de acuerdo a ley.',
#             styles["narrow_a_paragraph_justify"])]
#     ]
#     sev_width = Table(sev, colWidths=[_bts * 10 / 100, _bts * 72 / 100])
#     sev_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (0, -1), 11),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP'),
#     ]
#     sev_width.setStyle(TableStyle(sev_style))
#     # .............................End seventh one...................................
#     # ...............................Eighth.....................................
#     eighth = [[Paragraph('OCTAVA: FUERZA MAYOR O CASO FORTUITO', styles["narrow_b_tittle_justify"])]]
#     eighth_width = Table(eighth, colWidths=[_bts * 82 / 100])
#     eighth_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     ]
#     eighth_width.setStyle(TableStyle(eighth_style))
#     # .............................End eighth...................................
#     # .............................eighth one...................................
#     ei = [
#         ['8.1', Paragraph(
#             'Las obligaciones de las partes se suspenderán por el tiempo en que la ejecución del presente contrato se encuentre impedido por causas de fuerza mayor y caso fortuito. Se entiende por fuerza mayor o caso fortuito a todos aquellos casos que no han podido preverse o que siendo previsibles, son insuperables, ocasionados por fuerzas extrañas a la voluntad y control de las partes.',
#             styles["narrow_a_paragraph_justify"])]
#     ]
#     ei_width = Table(ei, colWidths=[_bts * 10 / 100, _bts * 72 / 100])
#     ei_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (0, -1), 11),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP')
#     ]
#     ei_width.setStyle(TableStyle(ei_style))
#     # .............................End eighth one...................................
#     # ...............................Ninth.....................................
#     ninth = [[Paragraph('NOVENA: DOMICILIOS', styles["narrow_b_tittle_justify"])]]
#     ninth_width = Table(ninth, colWidths=[_bts * 82 / 100])
#     ninth_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     ]
#     ninth_width.setStyle(TableStyle(ninth_style))
#     # .............................End ninth...................................
#     # .............................ninth one...................................
#     ni = [
#         ['9.1', Paragraph(
#             'Las partes fijan como sus domicilios los indicados en la introducción del presente contrato, por lo que cualquier comunicación se tendrá por bien hecha si es dirigida a la dirección señalada en dicha introducción sin más constancia que el cargo de recepción.',
#             styles["narrow_a_paragraph_justify"])],
#         ['9.2', Paragraph(
#             'Si alguna de las partes quisiera modificar su domicilio deberá comunicar su nueva dirección a la otra, siempre dentro de la ciudad de Lima, por escrito y con cargo de recepción. El cambio surtirá efectos a los tres (03) días útiles de recibida por la otra parte.',
#             styles["narrow_a_paragraph_justify"])]
#     ]
#     ni_width = Table(ni, colWidths=[_bts * 10 / 100, _bts * 72 / 100])
#     ni_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (0, -1), 11),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP')
#     ]
#     ni_width.setStyle(TableStyle(ni_style))
#     # .............................End ninth one...................................
#     # ...............................Tenth.....................................
#     tenth = [[Paragraph('DECIMA: LEY APLICABLE Y JURISDICCIÓN', styles["narrow_b_tittle_justify"])]]
#     tenth_width = Table(tenth, colWidths=[_bts * 82 / 100])
#     tenth_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     ]
#     tenth_width.setStyle(TableStyle(tenth_style))
#     # .............................End tenth...................................
#     # .............................tenth one...................................
#     tn = [
#         ['10.1', Paragraph(
#             'En todo lo no previsto en este Contrato, será de aplicación, lo dispuesto en el D. Leg. N° 295, Código Civil y demás del sistema jurídico peruano que resulten aplicables.',
#             styles["narrow_a_paragraph_justify"])],
#         ['10.2', Paragraph(
#             'Todo litigio o controversia surgido entre las partes a partir de la fecha de suscripción del presente contrato y que no pueda ser solucionado amistosamente por ellas será resuelto mediante arbitraje de Derecho, de conformidad con los Reglamentos Arbitrales del Centro de Arbitraje de la Cámara Peruana de la Construcción, a cuyas normas, administración y decisión se someten las partes en forma incondicional, declarando conocerlas y aceptarlas en su integridad.',
#             styles["narrow_a_paragraph_justify"])]
#     ]
#     tn_width = Table(tn, colWidths=[_bts * 10 / 100, _bts * 72 / 100])
#     tn_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (0, -1), 11),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP')
#     ]
#     tn_width.setStyle(TableStyle(tn_style))
#     # .............................End tenth one...................................
#     # ..............................Footer....................................
#     foot = [[
#         Paragraph(
#             'Estando ambas partes de acuerdo con lo estipulado en el presente contrato, se firma el día ' + str(
#                 current_date_format(order_obj.create_at)) + '.',
#             styles["narrow_a_paragraph_justify"]),
#     ]]
#     foot_width = Table(foot, colWidths=[_bts * 82 / 100])
#     foot_width.setStyle(TableStyle(client_style))
#     # .............................End footer..................................
#     # ................................Firm.....................................
#     firm = [
#         [Paragraph('_____________________', styles["narrow_b_tittle_center"]),
#          Paragraph('_____________________', styles["narrow_b_tittle_center"])],
#         [Paragraph('EL COMITENTE', styles["narrow_b_tittle_center"]),
#          Paragraph('EL LOCADOR', styles["narrow_b_tittle_center"])]
#     ]
#     firm_width = Table(firm, colWidths=[_bts * 50 / 100, _bts * 50 / 100])
#     firm_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#         ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
#     ]
#     firm_width.setStyle(TableStyle(firm_style))
#     # ------------------------------------------------------------------------------------------
#     buff = io.BytesIO()
#     doc = SimpleDocTemplate(buff,
#                             pagesize=A4,
#                             rightMargin=mr,
#                             leftMargin=ml,
#                             topMargin=ms,
#                             bottomMargin=mi + 40,
#                             title="CONTRATO DE SERVICIO",
#
#                             )
#     dictionary = []
#     dictionary.append(title_width)
#     dictionary.append(Spacer(1, 15))
#     dictionary.append(client_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(first_width)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(f_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(second_width)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(s_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(third_width)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(t_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(fourth_width)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(fo_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(fifth_width)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(ff_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(sixth_width)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(six_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(seventh_width)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(sev_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(eighth_width)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(ei_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(ninth_width)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(ni_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(tenth_width)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(tn_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(foot_width)
#     dictionary.append(Spacer(1, 40))
#     dictionary.append(firm_width)
#     response = HttpResponse(content_type='application/pdf')
#     doc.build(dictionary, canvasmaker=NumberedCanvas, onFirstPage=watermark_service, onLaterPages=watermark_service)
#     response.write(buff.getvalue())
#     buff.close()
#     return response
#
#
# def watermark_service(canvas, doc):
#     canvas.saveState()
#     number = canvas._pageNumber
#
#     # num_pages = len(doc._saved_page_states)
#     if number > 0:
#         canvas.setFillColor(Color(0, 0, 0, alpha=0.4))
#         canvas.drawImage(watermark, 75, (doc.height - 370) / 2, width=400, height=400)
#         canvas.setStrokeGray(0.3)
#         # canvas.drawString(10 * cm, cm, 'Pagina ' + str(pageNumber))
#         # num_pages = len(canvas.saveState)
#         ruc = Paragraph('RUC 20608981307',
#                         styles["narrow_center"])
#         # p = Paragraph('Pagina ' + str(number) + '/' + str(10),
#         #               styles["narrow_center"])
#         footer = Paragraph("CONSULTORIA GRUPO JC S.A.C.",
#                            styles["narrow_center"])
#         wr, hr = ruc.wrap(doc.width, doc.bottomMargin)
#         wf, hf = footer.wrap(doc.width, doc.bottomMargin)
#         # w, h = p.wrap(doc.width, doc.bottomMargin)
#         ruc.drawOn(canvas, -8.1 * cm, hr)
#         footer.drawOn(canvas, cm, hf)
#         # p.drawOn(canvas, 10 * cm, h)
#         canvas.setLineWidth(2)
#         canvas.setStrokeColor(black)
#         canvas.line(15, 29, 580, 29)
#         # canvas.getPageNumber()
#         canvas.restoreState()
#
#
# def contract_rent(request, pk=None):
#     orders_obj = Order.objects.get(id=pk)
#     client_obj = orders_obj.client
#     client_business = '-'
#     client_ruc = '-'
#     client_address = '-'
#     client_dni = '-'
#     client_name = '-'
#     if client_obj.full_name:
#         client_business = client_obj.full_name
#     if client_obj.document:
#         client_ruc = client_obj.document
#     if client_obj.address:
#         client_address = client_obj.address
#     if client_obj.representative_dni:
#         client_dni = client_obj.representative_dni
#     if client_obj.representative_name:
#         client_name = client_obj.representative_name
#     subsidiary_obj = get_subsidiary_by_user(orders_obj.user)
#     business_name = '-'
#     business_ruc = '-'
#     business_address = '-'
#     business_representative_dni = '-'
#     business_representative_name = '-'
#     global name_year
#     name_year = subsidiary_obj.name_year
#     if subsidiary_obj.business_name:
#         business_name = subsidiary_obj.business_name
#     if subsidiary_obj.ruc:
#         business_ruc = subsidiary_obj.ruc
#     if subsidiary_obj.address:
#         business_address = subsidiary_obj.address
#     if subsidiary_obj.representative_dni:
#         business_representative_dni = subsidiary_obj.representative_dni
#     if subsidiary_obj.representative_name:
#         business_representative_name = subsidiary_obj.representative_name
#     # DA4 = (8.3 * inch, 11.7 * inch)
#     ml = 0.25 * inch
#     mr = 0.25 * inch
#     ms = 0.65 * inch
#     mi = 0.65 * inch
#     _bts = 8.3 * inch - 0.25 * inch - 0.25 * inch
#     d = 50
#     # ...............................Title....................................
#     title = [[Paragraph('CONTRATO N° ' + str(orders_obj.number).zfill(4) + ' – JC SAC – 2022 DE ALQUILER DE ANDAMIOS',
#                         styles["narrow_b_tittle_center"])]]
#     title_width = Table(title, colWidths=[_bts])
#     title_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('LEFTPADDING', (0, 0), (-1, -1), d),
#         ('RIGHTPADDING', (0, 0), (-1, -1), d)
#     ]
#     title_width.setStyle(TableStyle(title_style))
#     # .............................End title..................................
#     # ..............................Client....................................
#     client = [[
#         Paragraph(
#             'Conste por el presente documento el contrato de alquiler de andamios que suscribimos por parte del arrendador, la empresa, ' + str(
#                 business_name) + ' con RUC ' + str(
#                 business_ruc) + ', ubicada en ' + str(
#                 business_address) + ', la cual se encuentra representada por la Sra. ' + str(
#                 business_representative_name) + ', identificado con D.N.I. N°' + str(
#                 business_representative_dni) + '; y por parte de arrendatario ' + str(
#                 client_business) + ' identificado con R.U.C. ' + str(
#                 client_ruc) + ', con domicilio fiscal en ' + str(
#                 client_address) + ', representada en este acto por su Gerente General el Sr. ' + str(
#                 client_name) + ' identificado con DNI N° ' + str(
#                 client_dni) + ', se considera los siguientes términos y condiciones.',
#             styles["narrow_a_paragraph_justify"]),
#     ]]
#     client_width = Table(client, colWidths=[_bts])
#     client_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('LEFTPADDING', (0, 0), (-1, -1), d),
#         ('RIGHTPADDING', (0, 0), (-1, -1), d)
#     ]
#     client_width.setStyle(TableStyle(client_style))
#     # .............................End client..................................
#     # ...............................First.....................................
#     first = [['PRIMERO:', Paragraph('El arrendador del Andamio Multidireccional ofrece lo Sgt.:',
#                                     styles["narrow_a_paragraph_justify"])]]
#     first_width = Table(first, colWidths=[_bts * 18 / 100, _bts * 82 / 100])
#     first_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('LEFTPADDING', (0, 0), (0, -1), d),
#         ('RIGHTPADDING', (1, 0), (1, -1), d),
#         ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (0, -1), 11),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP')
#     ]
#     first_width.setStyle(TableStyle(first_style))
#     # .............................End first...................................
#     # ---------------------------Header Detail--------------------------------#
#     header_detail_style = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),  # all columns
#         ('GRID', (0, 0), (-1, -1), 1, HexColor('#5f64de')),  # all columns
#         ('BACKGROUND', (0, 0), (-1, 1), HexColor('#5f64de')),
#         # Establecer el color de fondo de la segunda fila    ]
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
#         # ('LEFTPADDING', (0, 0), (0, -1), d),  # first column
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 5),  # all columns
#         # ('RIGHTPADDING', (5, 0), (5, -1), d),  # second column
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#     ]
#     width_table = [_bts * 5 / 100, _bts * 30 / 100, _bts * 12 / 100, _bts * 15 / 100,
#                    _bts * 10 / 100,
#                    _bts * 10 / 100]
#     header_detail_width = Table([('Nº', 'DESCRIPCIÓN', 'CANTIDAD', 'UND MED', 'PRECIO', 'IMPORTE')],
#                                 colWidths=width_table)
#     header_detail_width.setStyle(TableStyle(header_detail_style))
#     # -----------------------------end header------------------------------------#
#     # -------------------------------DETAIL--------------------------------------#
#     row_detail_contract = []
#     count_contract = 0
#     total_amount_contract = decimal.Decimal(0.00)
#     detail_queryset = OrderDetail.objects.filter(order=orders_obj).order_by('id')
#     values = ''
#     for d in detail_queryset:
#         _product = Paragraph(
#             (str(d.product.name.upper()) + '\n' + str(d.description.upper())).replace("\n", "<br/>"),
#             styles["narrow_a_justify"])
#         _unit = str(d.unit.description.upper())
#         _quantity = str(round(decimal.Decimal(d.quantity), 2))
#         _price = str(round(decimal.Decimal(d.price), 2))
#         _amount = str(round(decimal.Decimal(d.quantity) * decimal.Decimal(d.price), 2))
#         if d.is_state:
#             values = '•'
#         else:
#             count_contract = count_contract + 1
#             values = count_contract
#             total_amount_contract = total_amount_contract + decimal.Decimal(d.quantity * d.price)
#         row_detail_contract.append((str(values), _product, _quantity, _unit, _price, _amount))
#
#     contract_detail = Table(row_detail_contract, colWidths=[_bts * 5 / 100, _bts * 30 / 100, _bts * 12 / 100,
#                                                             _bts * 15 / 100, _bts * 10 / 100, _bts * 10 / 100])
#
#     contract_detail_style = [
#         ('GRID', (0, 0), (-1, -1), 0.05, HexColor('#5f64de')),
#         ('FONTNAME', (0, 0), (-1, -1), 'Narrow-a'),
#         ('FONTSIZE', (0, 0), (-1, -1), 9),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#         ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),  # three column
#         ('ALIGNMENT', (4, 0), (5, -1), 'RIGHT'),  # three column
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # first column
#         # ('BACKGROUND', (4, 0), (4, -1), colors.blue),  # four column
#     ]
#     contract_detail.setStyle(TableStyle(contract_detail_style))
#     # -------------- Footer Detail ----------------------------
#     money = str(orders_obj.coin.abbreviation)
#     total_discount = round(decimal.Decimal(orders_obj.discount_output), 2)
#     sub_total = (decimal.Decimal(total_amount_contract) / decimal.Decimal(1.1800)) - total_discount
#     total_invoice = decimal.Decimal(orders_obj.total_output)
#     total_igv = total_invoice - sub_total
#     total = [
#         ['GRAVADA', money + ' ' + str(round(sub_total, 2))],
#         ['DESCUENTO', money + ' ' + str(round(total_discount, 2))],
#         ['I.G.V.(18%)', money + ' ' + str(round(total_igv, 2))],
#         ['TOTAL', money + ' ' + str(round(total_invoice, 2))]
#     ]
#     total_width = Table(total, colWidths=[_bts * 12 / 100, _bts * 10 / 100])
#
#     total_style = [
#         ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#         ('FONTNAME', (0, 0), (-1, 2), 'Narrow-a'),
#         ('FONTSIZE', (0, 0), (-1, -1), 9),
#         ('FONTSIZE', (0, 3), (-1, -1), 10),
#         ('FONTNAME', (0, 3), (-1, -1), 'Newgot'),
#         ('TEXTCOLOR', (0, 3), (-1, -1), colors.white),
#         ('ALIGNMENT', (0, 0), (1, -1), 'LEFT'),
#         ('ALIGNMENT', (1, 0), (-1, -1), 'RIGHT'),
#         ('BACKGROUND', (0, 3), (-1, -1), HexColor('#5f64de')),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#5f64de')),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
#     ]
#     total_width.setStyle(TableStyle(total_style))
#     # ..................................mode payment.................................
#     payment_num = 0
#     payment_detail = []
#     row_payment = [('DETALLE DE PAGOS', '', '')]
#     for p in orders_obj.payments_set.filter(status='R', subsidiary=subsidiary_obj).order_by('id'):
#         payment_num = payment_num + 1
#         payment_text = str(p.get_payment_display()).upper() + ': ' + str(payment_num)
#         if p.payment == 'C':
#             payment_text = 'CREDITO: CUOTA ' + str(payment_num)
#         payment_date = str(p.date_payment)
#         payment_amount = str(round(p.amount, 2))
#         row_payment.append((str(payment_text), payment_date, payment_amount))
#         payment_detail = Table(row_payment,
#                                colWidths=[_bts * 25 / 100, _bts * 17 / 100, _bts * 17 / 100])
#         payment_detail_style = [
#             ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#474aa1')),
#             ('FONTNAME', (0, 0), (-1, 0), 'Narrow-a'),
#             ('FONTSIZE', (0, 0), (-1, -1), 9),
#             ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#             ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
#             ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
#             ('ALIGNMENT', (1, 0), (2, -1), 'RIGHT'),  # three column
#             # ('ALIGNMENT', (3, 0), (4, -1), 'CENTER'),  # three column
#             # ('ALIGNMENT', (5, 0), (-1, -1), 'RIGHT'),  # three column
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # first column
#             # ('RIGHTPADDING', (3, 0), (3, -1), 10),  # first column
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # all columns
#             ('BACKGROUND', (0, 0), (-1, 0), HexColor('#474aa1')),  # four column
#             ('SPAN', (0, 0), (-1, 0)),  # first row
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
#         ]
#         payment_detail.setStyle(TableStyle(payment_detail_style))
#     # -----------------------accounting bank------------------------------
#     total_detail = [
#         [payment_detail, '', total_width],
#     ]
#     document_total = Table(total_detail, colWidths=[_bts * 59 / 100, _bts * 1 / 100, _bts * 22 / 100])
#     total_payment_detail_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#474aa1')),
#         ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # first column
#         ('LEFTPADDING', (0, 0), (-1, -1), 0),  # first column
#     ]
#     document_total.setStyle(TableStyle(total_payment_detail_style))
#     # .............................Detail text...................................
#
#     # .............................Condition Rent.......................................
#     condition_rent_print = []
#     condition_rent = [('CONDICIONES DE ALQUILER', '')]
#     for i in ConditionRent.objects.all():
#         description_condition = Paragraph(str(i.description), styles["narrow_a_paragraph_justify"])
#         condition_rent.append(('•', description_condition))
#     if len(condition_rent) <= 1:
#         condition_rent_print = condition_rent.append((str(''), str('')))
#     else:
#         condition_rent_print = Table(condition_rent, colWidths=[_bts * 4 / 100, _bts * 78 / 100])
#         condition_rent_style = [
#             # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#             ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#             ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#             ('FONTSIZE', (0, 0), (0, -1), 10),
#             ('ALIGNMENT', (0, 0), (0, -1), 'CENTER'),
#             ('ALIGNMENT', (0, 0), (0, 0), 'LEFT'),
#             ('VALIGN', (0, 0), (0, -1), 'TOP'),
#             ('SPAN', (0, 0), (-1, 0))
#         ]
#         condition_rent_print.setStyle(TableStyle(condition_rent_style))
#
#     # .............................Detail text...................................
#     request_text = [
#         ['REQUISITOS DE ALQUILER', ''],
#         ['•', Paragraph(
#             'Copia de DNI',
#             styles["narrow_a_paragraph_justify"])],
#         ['•', Paragraph(
#             'Vigencia de Poder',
#             styles["narrow_a_paragraph_justify"])],
#         ['•', Paragraph(
#             'Ficha RUC actualizada',
#             styles["narrow_a_paragraph_justify"])]
#     ]
#     request_text_width = Table(request_text, colWidths=[_bts * 4 / 100, _bts * 78 / 100])
#     request_text_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (0, -1), 10),
#         ('ALIGNMENT', (0, 0), (0, -1), 'CENTER'),
#         ('ALIGNMENT', (0, 0), (0, 0), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP'),
#         ('SPAN', (0, 0), (-1, 0))
#     ]
#     request_text_width.setStyle(TableStyle(request_text_style))
#     # .............................End detail text...................................
#     # .............................fin text...................................
#     note_text = [
#         ['', Paragraph(
#             'A nombre de CONSULTORIA GRUPO JC S.A.C. de usar esta forma de pago, traer el Boucher para la firma del contrato o emisión de factura de venta ',
#             styles["narrow_small_left"])],
#         ['', Paragraph(
#             'NOTA: NO SE HACEN RESERVAS, NI SEPARACIONES, TODO PEDIDO ES PAGO CONTRA ENTREGA ',
#             styles["narrow_small_left"])],
#     ]
#     note_text_width = Table(note_text, colWidths=[_bts * 4 / 100, _bts * 78 / 100])
#     note_text_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('FONTSIZE', (0, 0), (0, -1), 9),
#         ('ALIGNMENT', (0, 0), (0, -1), 'CENTER'),
#         ('ALIGNMENT', (0, 0), (0, 0), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP'),
#     ]
#     note_text_width.setStyle(TableStyle(note_text_style))
#     # .............................End fin text...................................
#     # .............................Second...................................
#     second = [
#         ['SEGUNDO:', Paragraph(
#             'El arrendatario firmara una letra de cambio previo acuerdo con el arrendador.',
#             styles["narrow_a_paragraph_justify"])]
#     ]
#     second_width = Table(second, colWidths=[_bts * 10 / 100, _bts * 72 / 100])
#     second_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (0, -1), 11),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP'),
#     ]
#     second_width.setStyle(TableStyle(second_style))
#     # .............................End second...................................
#     # .............................Third........................................
#     third = [
#         ['TERCERO:', Paragraph(
#             'El alquiler del Andamio será un lapso de ' + str(
#                 num_day(orders_obj.date_end,
#                         orders_obj.date_init)) + ' calendarios que inicia desde que el equipo sea entregado en obra en caso que el contratista no devolviera el Andamio a la fecha limite pagara sin lugar a reclamo el 2% del monto total del alquiler, por cada día que tenga en su poder.',
#             styles["narrow_a_paragraph_justify"])]
#     ]
#     third_width = Table(third, colWidths=[_bts * 10 / 100, _bts * 72 / 100])
#     third_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (0, -1), 11),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP'),
#     ]
#     third_width.setStyle(TableStyle(third_style))
#     # .............................End third...................................
#     # .............................Fourth...................................
#     fourth = [
#         ['CUARTO:', Paragraph(
#             'En caso de pérdida o deterioro de las piezas de Andamio, los arrendatarios se harán responsables según lo establecido en la cláusula de condiciones de uso y la devolución del material correspondiente.',
#             styles["narrow_a_paragraph_justify"])]
#     ]
#     fourth_width = Table(fourth, colWidths=[_bts * 10 / 100, _bts * 72 / 100])
#     fourth_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (0, -1), 11),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP'),
#     ]
#     fourth_width.setStyle(TableStyle(fourth_style))
#     # .............................End fourth...................................
#     # .............................Five...................................
#     five = [
#         ['QUINTO:', Paragraph(
#             'El presente documento tendrá validez ante cualquier autoridad judicial o policial en caso de incumplimiento de las partes estando de mutuo acuerdo firmamos el presente contrato.',
#             styles["narrow_a_paragraph_justify"])]
#     ]
#     five_width = Table(five, colWidths=[_bts * 10 / 100, _bts * 72 / 100])
#     five_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#         ('FONTNAME', (0, 0), (0, -1), 'Narrow-b'),
#         ('FONTSIZE', (0, 0), (0, -1), 11),
#         ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (0, -1), 'TOP'),
#     ]
#     five_width.setStyle(TableStyle(five_style))
#     # .............................End fourth...................................
#     # ..............................Footer......................................
#     foot = [[
#         Paragraph(
#             'Lima ' + str(current_date_format(orders_obj.create_at)),
#             styles["narrow_a_right"]),
#     ]]
#     foot_width = Table(foot, colWidths=[_bts])
#     foot_width.setStyle(TableStyle(client_style))
#     # .............................End footer..................................
#     # ................................Firm.....................................
#     firm = [
#         [Paragraph('__________________________________', styles["narrow_b_firm_center"]),
#          Paragraph('__________________________________', styles["narrow_b_firm_center"])],
#         [Paragraph('ARRENDADOR', styles["narrow_b_firm_center"]),
#          Paragraph('ARRENDATARIO', styles["narrow_b_firm_center"])],
#         [Paragraph(str(business_name), styles["narrow_b_firm_center"]),
#          Paragraph(str(client_business), styles["narrow_b_firm_center"])]
#     ]
#     firm_width = Table(firm, colWidths=[_bts * 50 / 100, _bts * 50 / 100])
#     firm_style = [
#         # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
#         ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         # ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
#         ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
#     ]
#     firm_width.setStyle(TableStyle(firm_style))
#     # ------------------------------------------------------------------------------------------
#     img = Image(letter)
#     img.drawHeight = 11.00 * inch / 2.9
#     img.drawWidth = 23.9 * inch / 2.9
#     # letter_image = add_image(letter)
#     # img = RotatedImage(letter,
#     #                    width=720, height=520)
#     # img.hAlign = 'CENTER'
#     # img.vAlign = 'TOP'
#     # img_letter = [[img]]
#     # img_letter_width = Table(img_letter, colWidths=[_bts])
#     # img_style = [
#     #     ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
#     #     # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
#     #     ('FONTSIZE', (0, 0), (-1, -1), 10),
#     #     ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
#     # ]
#     # img_letter_width.setStyle(TableStyle(img_style))
#     # image_rotate = RotatedImage(letter_image)
#     # letter_image.drawHeight = 11.00 * inch / 2.9
#     # letter_image.drawWidth = 23.6 * inch / 2.9
#     buff = io.BytesIO()
#     doc = SimpleDocTemplate(buff,
#                             pagesize=A4,
#                             rightMargin=mr,
#                             leftMargin=ml,
#                             topMargin=ms,
#                             bottomMargin=mi,
#                             title="CONTRATO DE ALQUILER",
#
#                             )
#     dictionary = []
#     dictionary.append(title_width)
#     dictionary.append(Spacer(1, 15))
#     dictionary.append(client_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(first_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(header_detail_width)
#     dictionary.append(contract_detail)
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(document_total)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(condition_rent_print)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(request_text_width)
#     dictionary.append(Spacer(1, 15))
#     dictionary.append(note_text_width)
#     dictionary.append(Spacer(1, 20))
#     dictionary.append(second_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(third_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(fourth_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(five_width)
#     dictionary.append(Spacer(1, 10))
#     dictionary.append(foot_width)
#     dictionary.append(Spacer(1, 40))
#     dictionary.append(firm_width)
#     dictionary.append(Spacer(1, 60))
#     dictionary.append(img)
#     # dictionary.append(DrawLetters(count_row=5))
#     response = HttpResponse(content_type='application/pdf')
#     doc.build(dictionary, canvasmaker=NumberedCanvas, onFirstPage=watermark_rent,
#               onLaterPages=watermark_rent)
#     response.write(buff.getvalue())
#     buff.close()
#     return response
#
#
# # def add_image(image_path):
# #     img = utils.ImageReader(image_path)
# #     img_width, img_height = img.getSize()
# #     aspect = img_height / float(img_width)
# #     my_canvas = canvas.Canvas("canvas_image.pdf",
# #                               pagesize=letter)
# #     my_canvas.saveState()
# #     my_canvas.rotate(45)
# #     my_canvas.drawImage(image_path, 150, 10,
# #                         width=100, height=(100 * aspect))
# #     my_canvas.restoreState()
# #     my_canvas.save()
#
#
# class RotatedImage(Image):
#     def wrap(self, availWidth, availHeight):
#         height, width = Image.wrap(self, availHeight, availWidth)
#         return width, height
#
#     def draw(self):
#         self.canv.rotate(45)
#         Image.draw(self)
#
#
# def watermark_rent(canvas, doc):
#     canvas.saveState()
#     number = canvas._pageNumber
#     if number > 0:
#         canvas.setFillColor(Color(0, 0, 0, alpha=0.4))
#         canvas.drawImage(watermark, 75, (doc.height - 370) / 2, width=400, height=400)
#         canvas.setStrokeGray(0.3)
#         # canvas.drawString(10 * cm, cm, 'Pagina ' + str(pageNumber))
#         ruc = Paragraph('RUC 20608981307',
#                         styles["narrow_center"])
#         year_letter = Paragraph(str(name_year),
#                                 styles["narrow_center"])
#         # p = Paragraph('Pagina ' + str(number),
#         #               styles["narrow_center"])
#         footer = Paragraph("CONSULTORIA GRUPO JC S.A.C.",
#                            styles["narrow_center"])
#         wy, hy = year_letter.wrap(doc.width, doc.bottomMargin)
#         wr, hr = ruc.wrap(doc.width, doc.bottomMargin)
#         wf, hf = footer.wrap(doc.width, doc.bottomMargin)
#         # w, h = p.wrap(doc.width, doc.bottomMargin)
#         year_letter.drawOn(canvas, cm, 81 * hy)
#         ruc.drawOn(canvas, -8.1 * cm, hr)
#         footer.drawOn(canvas, cm, hf)
#         # p.drawOn(canvas, 10 * cm, h)
#         canvas.setLineWidth(2)
#         canvas.setStrokeColor(black)
#         canvas.line(15, 29, 580, 29)
#         canvas.restoreState()
#
#
# def current_date_format(date):
#     months = (
#         "Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre",
#         "Diciembre")
#     day = date.day
#     month = months[date.month - 1]
#     year = date.year
#     if int(day) < 10:
#         return "{}{} de {} del {}".format(0, day, month, year)
#     else:
#         message = "{} de {} del {}".format(day, month, year)
#
#     return message
#
#
# def num_day(end, init):
#     n = str(end - init).replace('day,', '').replace('days,', '').replace(' ', '').replace('0:00:00', '')
#     print('valor de n=' + str(n))
#     if n == 0 or n == '':
#         n = 1
#     if int(n) == 1:
#         return "{}{} día".format(0, n)
#     elif 1 < int(n) < 10:
#         return "{}{} días".format(0, n)
#     else:
#         return "{} días".format(n)
#
#
# # ...........................................................................................................................
# class NumberedCanvas(canvas.Canvas):
#     def __init__(self, *args, **kwargs):
#         canvas.Canvas.__init__(self, *args, **kwargs)
#         self._saved_page_states = []
#
#     def showPage(self):
#         self._saved_page_states.append(dict(self.__dict__))
#         self._startPage()
#
#     def save(self):
#         """add page info to each page (page x of y)"""
#         num_pages = len(self._saved_page_states)
#         for state in self._saved_page_states:
#             self.__dict__.update(state)
#             self.draw_page_number(num_pages)
#             canvas.Canvas.showPage(self)
#         canvas.Canvas.save(self)
#
#     def draw_page_number(self, page_count):
#         self.setFont("Narrow", 11)
#         self.drawRightString(cm * 20.3, cm - 17,
#                              "Pagina %d de %d" % (self._pageNumber, page_count))

def guide(request, pk=None):
    A4 = (8.3 * inch, 11.7 * inch)
    ml = 0.25 * inch
    mr = 0.25 * inch
    ms = 0.25 * inch
    mi = 0.25 * inch
    w = 8.3 * inch - 0.25 * inch - 0.25 * inch
    order_obj = Order.objects.get(id=pk)
    subsidiary_obj = order_obj.subsidiary
    person_obj = order_obj.person
    # title_business = str(subsidiary_obj.name) + '\n' + str(subsidiary_obj.business_name) + '\n' + str(
    #     subsidiary_obj.address) + '\n RUC ' + str(
    #     subsidiary_obj.ruc)
    date = utc_to_local(order_obj.guide_date)
    date_transfer = utc_to_local(order_obj.guide_transfer)
    document_type = str(order_obj.get_add_display()).upper()
    document_number = (str(order_obj.guide_serial) + '-' + str(order_obj.guide_number).zfill(
        7 - len(str(order_obj.guide_number)))).upper()
    line = '__________________________________________________________________________________________________________________________'
    I = Image(logo)
    I.drawHeight = 3.0 * inch / 2.9
    I.drawWidth = 3.0 * inch / 2.9
    # ------------------------------------------------------------------
    business_center = [
        [Paragraph(str(subsidiary_obj.business_name), styles["narrow_b_tittle_justify"])],
        [Paragraph(str(subsidiary_obj.address), styles["narrow_b_justify"])],
        [Paragraph('Correo: ' + str(subsidiary_obj.email), styles['narrow_b_justify'])],
        [Paragraph('Telefono: ' + str(subsidiary_obj.phone), styles['narrow_b_justify'])],
    ]
    T = Table(business_center)
    title_style = [
        # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
        # ('TEXTCOLOR', (0, 0), (-1, -1), colors.red)
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ]
    T.setStyle(TableStyle(title_style))

    business_right = [
        ['RUC ' + str(subsidiary_obj.ruc)],
        [document_type],
        [document_number],
    ]
    D = Table(business_right)
    document_style = [
        # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
        ('FONTSIZE', (0, 0), (-1, -1), 13),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('SPAN', (0, 0), (0, 0))
    ]
    D.setStyle(TableStyle(document_style))
    H = [
        [I, T, D],
    ]
    document_header = Table(H, colWidths=[w * 20 / 100, w * 60 / 100, w * 20 / 100])
    header_style = [
        # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # first column
        ('SPAN', (0, 0), (0, 0)),  # first row
        # ('LINEBELOW', (0, -1), (-1, -1), 0.5, purple, 1, None, None, 4, 1),
        ('BACKGROUND', (2, 0), (-1, 1), HexColor('#0362BB')),  # Establecer el color de fondo de la segunda fila
        # ('LINEBEFORE', (1, 0), (-1, -1), 0.1, colors.grey),
        # Establezca el color de la línea izquierda de la tabla en
    ]
    document_header.setStyle(TableStyle(header_style))
    # ------------------------------------------------------------------
    pdf_person = Table(
        [('DESTINATARIO', '')] +
        [(person_obj.get_document_display() + ' EMPRESA:', person_obj.number)] +
        [('DENOMINACIÓN: ', Paragraph(person_obj.names.upper(), styles["Left-text"]))],
        colWidths=[w * 22 / 100, w * 78 / 100])
    style_person = [
        ('FONTNAME', (0, 0), (-1, -1), 'Square'),  # all columns
        ('FONTNAME', (0, 0), (-1, 0), 'Ticketing'),  # all columns
        ('FONTSIZE', (0, 0), (-1, 0), 10),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),  # all columns
        ('BOTTOMPADDING', (1, 2), (1, 2), 5),  # all columns
        ('LEFTPADDING', (0, 0), (0, -1), 2),  # first column
        ('LEFTPADDING', (1, 0), (1, -1), 2),  # first column
        ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),  # second column
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0362BB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ]
    pdf_person.setStyle(TableStyle(style_person))
    # ----------------------------------------------------------------
    pdf_transfer = Table(
        [('DATOS DEL TRASLADO', '')] +
        [('FECHA EMISIÓN:', date.strftime("%d/%m/%Y"))] +
        [('FECHA INICIO DE TRASLADO: ', date_transfer.strftime("%d/%m/%Y"))] +
        [('MOTIVO DE TRASLADO: ', order_obj.get_guide_motive_display().upper())] +
        [('MODALIDAD DE TRANSPORTE: ', 'TRANSPORTE ' + order_obj.get_guide_modality_transport_display())] +
        [('PESO BRUTO TOTAL (KGM): ', round(decimal.Decimal(order_obj.guide_weight), 2))] +
        [('NÚMERO DE BULTOS: ', round(decimal.Decimal(order_obj.guide_package), 0))],
        colWidths=[w * 22 / 100, w * 78 / 100])
    style_transfer = [
        ('FONTNAME', (0, 0), (-1, -1), 'Square'),  # all columns
        ('FONTNAME', (0, 0), (-1, 0), 'Ticketing'),  # all columns
        ('FONTSIZE', (0, 0), (-1, 0), 10),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),  # second column
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), -2),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0362BB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('TOPPADDING', (0, 0), (-1, 0), 2),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 1),
        # ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#0362BB')),  # all columns
    ]
    pdf_transfer.setStyle(TableStyle(style_transfer))
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    pdf_address = Table(
        [('DATOS DEL PUNTO DE PARTIDA Y PUNTO DE LLEGADA', '')] +
        [('PUNTO DE PARTIDA:', Paragraph(order_obj.guide_origin_address.upper(), styles["Left-text"]))] +
        [('PUNTO DE LLEGADA: ', Paragraph(order_obj.guide_destiny_address.upper(), styles["Left-text"]))],
        colWidths=[w * 22 / 100, w * 78 / 100])
    style_address = [
        ('FONTNAME', (0, 0), (-1, -1), 'Square'),  # all columns
        ('FONTNAME', (0, 0), (-1, 0), 'Ticketing'),  # all columns
        ('FONTSIZE', (0, 0), (-1, 0), 10),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),  # second column
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0362BB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        # ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#0362BB')),  # all columns
    ]
    pdf_address.setStyle(TableStyle(style_address))
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    register_mtc = ''
    if order_obj.guide_register_mtc:
        register_mtc = order_obj.guide_register_mtc

    if order_obj.guide_truck != '' and order_obj.guide_driver_dni != '' and order_obj.guide_driver_license != '' and order_obj.guide_driver_full_name != '':
        pdf_transportation = Table(
            [('DATOS DEL TRANSPORTE', '', '', '')] +
            [('TRANSPORTISTA:', Paragraph(order_obj.guide_carrier_names.upper(), styles["Left-text"]),
              'RUC: ' + order_obj.guide_carrier_document, 'Número de registro MTC: ' + str(register_mtc))] +
            [('VEHÍCULO: ', Paragraph(order_obj.guide_truck.upper(), styles["Left-text"]), '', '')] +
            [('CONDUCTOR: ',
              Paragraph('DNI: ' + str(order_obj.guide_driver_dni) + ' - ' + 'NRO LICENCIA: ' + str(
                  order_obj.guide_driver_license) + ' - ' + str(order_obj.guide_driver_full_name.upper()),
                        styles["Left-text"]), '', '')], colWidths=[w * 22 / 100, w * 40 / 100, w * 19 / 100, w * 19 / 100])
    else:
        pdf_transportation = Table(
            [('DATOS DEL TRANSPORTE', '', '', '')] +
            [('TRANSPORTISTA:', Paragraph(order_obj.guide_carrier_names.upper(), styles["Left-text"]), 'RUC: ' + order_obj.guide_carrier_document, 'NRO DE REGISTRO MTC: ' + str(register_mtc))], colWidths=[w * 22 / 100, w * 40 / 100, w * 19 / 100, w * 19 / 100])

    style_transportation = [
        ('FONTNAME', (0, 0), (-1, -1), 'Square'),  # all columns
        ('FONTNAME', (0, 0), (-1, 0), 'Ticketing'),  # all columns
        ('FONTSIZE', (0, 0), (-1, 0), 10),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),  # second column
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0362BB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        # ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#0362BB')),  # all columns
    ]
    pdf_transportation.setStyle(TableStyle(style_transportation))
    # ----------------------------------------------------------------
    style_header = [
        ('FONTNAME', (0, 0), (-1, -1), 'Ticketing'),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 9),  # all columns
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#0362BB')),  # all columns
        ('BACKGROUND', (0, 0), (-1, 1), HexColor('#0362BB')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),  # all columns
        ('TOPPADDING', (0, 0), (-1, -1), 1),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
    ]
    pdf_header = Table(
        [('CODIGO', 'DESCRIPCIÓN', 'MEDIDA', 'U/M', 'CANTIDAD')],
        colWidths=[w * 8 / 100, w * 60 / 100, w * 10 / 100, w * 10 / 100, w * 12 / 100]
    )
    pdf_header.setStyle(TableStyle(style_header))
    # -------------------------------------------------------------------
    row = []
    for d in order_obj.orderdetail_set.filter(is_invoice=True, is_state=True):
        product = Paragraph(str(d.product.name).upper(),
                            styles["Left-text"])
        measure = d.product.measure()
        code = str(d.product.code)
        unit = str(d.get_unit_display())
        quantity = round(decimal.Decimal(d.quantity), 2)
        row.append((code, product, measure, unit, str(quantity)))
    if len(row) <= 0:
        row.append(('', '', '', ''))
    pdf_detail = Table(row, colWidths=[w * 8 / 100, w * 60 / 100, w * 10 / 100, w * 10 / 100, w * 12 / 100])
    style_detail = [
        ('FONTNAME', (0, 0), (-1, -1), 'Square'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (1, 0), (1, -1), -1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#9E9E9E')),
    ]
    pdf_detail.setStyle(TableStyle(style_detail))
    # ----------------------------------------------------------------------------------------------
    pdf_observation = 'OBSERVACIÓN: ' + str(order_obj.guide_description)
    pdf_document_related = f'DOCUMENTOS RELACIONADOS: {order_obj.get_doc_display()} {order_obj.bill_serial}-{order_obj.bill_number}'
    # -----------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------
    code_qr = 'https://4soluciones.pse.pe/20600854535'

    qr_left = [
        [Paragraph('Representación impresa de la ' + str(order_obj.get_add_display()).upper() +
                   ' REMITENTE ELECTRÓNICA, para ver el documento visita',
                   styles["narrow_left"])],
        [Paragraph('https://www.tuf4ct.com/cpe/', styles["narrow_left"])],
        # [Paragraph(
        #     'Emitido mediante un PROVEEDOR Autorizado por la SUNAT mediante Resolución de Intendencia No.034-005-0005315',
        #     styles["narrow_left"])],
        [Paragraph('', styles["narrow_left"])],
        [Paragraph('', styles["narrow_left"])],
    ]

    # pdf_link_uno = 'Representación impresa de la ' + str(
    #     order_obj.get_add_display()).upper() + ' REMITENTE ELECTRÓNICA, para ver el documento visita'
    # pdf_link_dos = 'https://4soluciones.pse.pe/20600854535'
    # pdf_link_tres = 'Emitido mediante un PROVEEDOR Autorizado por la SUNAT mediante Resolución de Intendencia No.034-005-0005315'
    # -----------------------------------------------------------------------------------------------
    qr_l = Table(qr_left, colWidths=[w * 80 / 100])

    style_qr1 = [
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    qr_l.setStyle(TableStyle(style_qr1))

    qr_row = [
        [qr_l, get_qr(code_qr)],
    ]
    qr_table = Table(qr_row, colWidths=[w * 80 / 100, w * 20 / 100])
    style_qr = [
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.9, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    qr_table.setStyle(TableStyle(style_qr))

    counter = order_obj.orderdetail_set.filter(is_state=True).count()
    buff = io.BytesIO()

    doc = SimpleDocTemplate(buff,
                            pagesize=A4,
                            rightMargin=mr,
                            leftMargin=ml,
                            topMargin=ms,
                            bottomMargin=mi,
                            title=document_number
                            )
    pdf = []
    # pdf.append(I)
    # pdf.append(Spacer(1, 3))
    # pdf.append(Paragraph(title_business.upper().replace("\n", "<br />"), styles["CenterNewgotBold"]))
    # pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(document_header)
    pdf.append(DrawInvoice(count_row=counter))
    # pdf.append(Paragraph(document_type, styles["CenterNewgotBoldGuideNumber"]))
    # pdf.append(Spacer(1, 3))
    # pdf.append(Paragraph(document_number, styles["CenterNewgotBoldGuideNumber"]))
    pdf.append(Spacer(1, 5))
    # pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(pdf_person)
    pdf.append(pdf_transfer)
    pdf.append(pdf_address)
    pdf.append(pdf_transportation)
    pdf.append(Spacer(1, 3))
    pdf.append(pdf_header)
    pdf.append(pdf_detail)
    pdf.append(Spacer(1, 5))
    # pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(Paragraph(pdf_observation.upper(), styles["narrow_justify_observation"]))
    pdf.append(Spacer(1, 2))
    pdf.append(Paragraph(pdf_document_related.upper(), styles["narrow_justify_observation"]))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(Spacer(1, 7))
    pdf.append(qr_table)
    # pdf.append(Paragraph(pdf_link_uno, styles["LeftNewgotBold"]))
    # pdf.append(Paragraph(pdf_link_dos, styles["LeftNewgotBold"]))
    # pdf.append(Paragraph(pdf_link_tres, styles["LeftNewgotBold"]))
    # pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(Spacer(1, 2))
    pdf.append(Paragraph("www.4soluciones.net", styles["CenterNewgotBold"]))
    doc.build(pdf)
    response = HttpResponse(content_type='application/pdf')
    response.write(buff.getvalue())
    buff.close()
    return response


class DrawInvoice(Flowable):
    def __init__(self, width=200, height=3, count_row=None):
        self.width = width
        self.height = height
        self.count_row = count_row

    def wrap(self, *args):
        """Provee el tamaño del área de dibujo"""
        return (self.width, self.height)

    def draw(self):
        canvas = self.canv
        canvas.saveState()

        canvas.setStrokeGray(0.9)
        # canvas.setFillColor(Color(0, 0, 0, alpha=1))
        canvas.setLineWidth(3)
        canvas.roundRect(-7, 1, 563, 84.5, 8, stroke=1, fill=0)
        canvas.restoreState()
