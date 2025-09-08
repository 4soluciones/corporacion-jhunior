from django.db.models import Sum
from django.db.models.functions import Coalesce
from reportlab.lib.colors import black, blue, red, Color, green, HexColor, purple, white
from reportlab.lib.pagesizes import letter, landscape, A4, A5, C7
from reportlab.pdfgen import canvas
import io
import pdfkit
import decimal
import reportlab
from django.contrib.auth.models import User
from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape, A5, portrait, letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Spacer, Image, Flowable
from reportlab.platypus import Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import qr
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.units import cm, inch
from reportlab.rl_settings import defaultPageSize
from corporacion_jhunior import settings
from apps.sales.number_letters import numero_a_letras, numero_a_moneda, number_money
import io
from django.conf import settings
import datetime
from datetime import datetime

from ..accounting.models import Casing, Payments
from ..accounting.zone import utc_to_local
from ..sales.models import Order

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
styles.add(ParagraphStyle(name='CenterNewgotBoldInvoiceNumber', alignment=TA_CENTER, leading=11, fontName='Newgot',
                          fontSize=11))
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
styles.add(ParagraphStyle(name='narrow_a_justify', alignment=TA_JUSTIFY, leading=10, fontName='Narrow-b', fontSize=9))
styles.add(ParagraphStyle(name='narrow_b_justify', alignment=TA_JUSTIFY, leading=11, fontName='Narrow-b', fontSize=10))
styles.add(
    ParagraphStyle(name='narrow_b_tittle_justify', alignment=TA_JUSTIFY, leading=12, fontName='Narrow-b', fontSize=12))
styles.add(ParagraphStyle(name='narrow_b_left', alignment=TA_LEFT, leading=9, fontName='Narrow-b', fontSize=8))
styles.add(ParagraphStyle(name='narrow_c_justify', alignment=TA_JUSTIFY, leading=10, fontName='Narrow-c', fontSize=10))
styles.add(ParagraphStyle(name='narrow_d_justify', alignment=TA_JUSTIFY, leading=10, fontName='Narrow-d', fontSize=10))
styles.add(ParagraphStyle(name='narrow_a_right', alignment=TA_RIGHT, leading=11, fontName='Narrow-b', fontSize=11))

style = styles["Normal"]

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

logo = "static/assets/pdfimg/logo_corporation.png"
watermark = "static/assets/images/img/agua.jpg"


def invoice(request, pk=None):
    order_set = Order.objects.filter(number=pk, type='V')
    order_obj = order_set.first()
    subsidiary_obj = order_obj.subsidiary
    person_obj = order_obj.person
    user_obj = order_obj.user
    w = 2.83 * inch - 4 * 0.05 * inch
    title_business = str(subsidiary_obj.business_name) + '\n' + str(
        subsidiary_obj.address) + '\n RUC ' + str(
        subsidiary_obj.ruc) + '\n TELF. ' + str(subsidiary_obj.phone)
    date = utc_to_local(order_obj.update_at)
    document_type = str(order_obj.get_doc_display()).upper()
    document_number = (str(order_obj.bill_serial) + '-' + str(order_obj.bill_number).zfill(
        7 - len(str(order_obj.bill_number)))).upper()
    license_plate = '-'
    if order_obj.license_plate:
        license_plate = order_obj.license_plate
    line = '--------------------------------------------------------------'
    I = Image(logo)
    I.drawHeight = 4.0 * inch / 2.9
    I.drawWidth = 5.0 * inch / 2.9
    # ------------------------------------------------------------------
    pdf_user = Table(
        [('USUARIO: ', Paragraph(user_obj.first_name.upper(), styles["narrow_b_left"]))] +
        [('FECHA: ',
          date.strftime("%d/%m/%Y") + '  HORA: ' + str(utc_to_local(order_obj.update_at).strftime('%H:%M:%S')))] +
        [('PLACA: ', str(license_plate))] +
        [('ORDEN Nº: ', str(order_obj.number).zfill(6 - len(str(order_obj.number))))],
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
    pdf_person = Table(
        [('CLIENTE: ', Paragraph(person_obj.names.upper(), styles["narrow_b_left"]))] +
        [(person_obj.get_document_display() + ':', Paragraph(person_obj.number, styles["narrow_b_left"]))] +
        [('DIRECCIÓN: ', Paragraph(person_obj.address.upper(), styles["narrow_b_left"]))],
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
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#9E9E9E')),  # all columns
        ('BACKGROUND', (0, 0), (-1, 1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),  # all columns
        ('TOPPADDING', (0, 0), (-1, -1), 1),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
    ]
    pdf_header = Table(
        [('DESCRIPCIÓN', 'CANT', 'P/U', 'TOTAL')],
        colWidths=[w * 53 / 100, w * 13 / 100, w * 16 / 100, w * 18 / 100]
    )
    pdf_header.setStyle(TableStyle(style_header))
    # -------------------------------------------------------------------
    row = []
    total = round(decimal.Decimal(0.00), 4)
    sub_total_without_igv = decimal.Decimal(0.00)
    order_condition = order_obj.condition
    if order_condition == 'R':
        details = order_obj.orderdetail_set.filter(is_invoice=True, is_state=True)
    elif order_condition == 'A' or order_condition == 'PA':
        details = order_obj.orderdetail_set.filter(is_invoice=False, is_state=False)
    else:
        details = order_obj.orderdetail_set.filter(is_invoice=True, is_state=True)
    for d in details:
        product = Paragraph(str(d.product.code) + ' ' + str(d.product.name).upper() + ' ' + str(
            d.product.measure() + ' ' + str(d.unit)),
                            styles["narrow_b_left"])
        price = round(decimal.Decimal(d.price), 4)
        quantity = round(decimal.Decimal(d.quantity), 4)
        amount = round(decimal.Decimal(d.quantity * d.price), 4)
        row.append((product, str(round(quantity, 2)), str(price), str(amount)))
        sub_total_without_igv += amount / decimal.Decimal(1.18)
        total = total + amount
    if len(row) <= 0:
        row.append(('', '', '', ''))
    pdf_detail = Table(row, colWidths=[w * 53 / 100, w * 13 / 100, w * 16 / 100, w * 18 / 100])
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
    payment_sum = Payments.objects.filter(payment__in=['E', 'D'], order=order_obj).aggregate(
        r=Coalesce(Sum('amount'), 0)).get('r')
    total_turn = decimal.Decimal(0.00)
    if order_obj.paid > payment_sum:
        total_turn = decimal.Decimal(order_obj.paid) - decimal.Decimal(payment_sum)

    total_with_igv = round(sub_total_without_igv * decimal.Decimal(1.18), 2)

    totals = [
        ['GRAVADA', 'S/. ' + str(round(sub_total_without_igv, 2))],
        # ['DESCUENTO', str(round(decimal.Decimal(0.00), 2))],
        ['IGV 18.00%',
         'S/. ' + str(round(decimal.Decimal(total_with_igv) - decimal.Decimal(sub_total_without_igv), 2))],
        ['TOTAL', 'S/. ' + str(round(decimal.Decimal(total_with_igv), 2))],
        # ['TOTAL PAGADO', 'S/. ' + str(round(decimal.Decimal(order_obj.payment_invoice()), 2))]
        ['TOTAL PAGADO', 'S/. ' + str(round(decimal.Decimal(order_obj.paid), 2))],
        ['TOTAL VUELTO', 'S/. ' + str(round(total_turn, 2))]
    ]

    total_right = Table(totals, colWidths=[w * 40 / 100, w * 25 / 100])

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
    pdf_total = Table(total_table, colWidths=[w * 35 / 100, w * 65 / 100])
    total_style = [
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # three column
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),  # first column
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.red),
    ]
    pdf_total.setStyle(TableStyle(total_style))

    pdf_total_letter = 'SON: ' + str(
        number_money(round(decimal.Decimal(order_obj.total), 2), str(order_obj.get_coin_display())))
    # ----------------------------------------------------------------------------------------------
    payment = [['FORMAS DE PAGO', order_obj.payments_set.first().get_payment_display().upper(),
                round(decimal.Decimal(total_with_igv), 2)]]
    # for p in Payments.objects.filter(order=order_obj):
    #     payment.append(
    #         ['PAGO ' + str(p.get_payment_display()).upper(), 'S/. ' + str(round(decimal.Decimal(p.amount), 2)), ''])

    pdf_payment = Table(payment, colWidths=[w * 40 / 100, w * 30 / 100, w * 30 / 100])
    payment_style = [
        ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),  # three column
        ('ALIGNMENT', (1, 0), (2, -1), 'RIGHT'),  # three column
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),  # first column
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        # ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#9E9E9E')),
    ]
    pdf_payment.setStyle(TableStyle(payment_style))
    # -----------------------------------------------------------------------------------------------
    pdf_link_uno = 'Representación impresa de la ' + str(
        order_obj.get_doc_display()).upper() + ', para ver el documento visita'
    pdf_link_dos = 'https://www.tuf4ct.com/cpe'
    pdf_link_tres = 'Emitido mediante un PROVEEDOR Autorizado por la SUNAT'
    # -----------------------------------------------------------------------------------------------
    style_qr = [
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),   # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # first column
        ('TOPPADDING', (0, 0), (-1, -1), -10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), -10),
    ]
    datatable = str(order_obj.bill_qr)
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
    pdf.append(I)
    pdf.append(Spacer(1, 3))
    pdf.append(Paragraph(title_business.upper().replace("\n", "<br />"), styles["CenterNewgotBold"]))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
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
    pdf.append(pdf_payment)
    # pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    # pdf.append(pdf_qr)
    # pdf.append(Spacer(1, -3))
    pdf.append(Spacer(1, -3))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(Paragraph(pdf_link_uno, styles["LeftNewgotBold"]))
    pdf.append(Paragraph(pdf_link_dos, styles["LeftNewgotBold"]))
    pdf.append(Paragraph(pdf_link_tres, styles["LeftNewgotBold"]))

    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(Paragraph("NO SE ACEPTAN CAMBIOS NI DEVOLUCIONES", styles["CenterNewgotBold"]))
    doc.build(pdf)
    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="pago_{}.pdf"'.format(order_obj.number)
    response.write(buff.getvalue())
    buff.close()
    return response


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


def ticket(request, pk=None):
    order_set = Order.objects.filter(number=pk, type='V')
    order_obj = order_set.first()
    subsidiary_obj = order_obj.subsidiary
    person_obj = order_obj.person
    user_obj = order_obj.user
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
        colWidths=[w * 53 / 100, w * 13 / 100, w * 16 / 100, w * 18 / 100]
    )
    pdf_header.setStyle(TableStyle(style_header))
    # -------------------------------------------------------------------
    row = []
    total = round(decimal.Decimal(0.00), 4)
    for d in order_obj.orderdetail_set.filter(is_invoice=True, is_state=True):
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
    pdf_detail = Table(row, colWidths=[w * 53 / 100, w * 13 / 100, w * 16 / 100, w * 18 / 100])
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
        # ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#9E9E9E')),
    ]
    pdf_detail.setStyle(TableStyle(style_detail))
    # --------------------------------------------------------------------------
    payment_sum = Payments.objects.filter(payment__in=['E', 'D'], order=order_obj).aggregate(
        r=Coalesce(Sum('amount'), 0)).get('r')
    total_turn = decimal.Decimal(0.00)
    if order_obj.paid > payment_sum:
        total_turn = round(decimal.Decimal(order_obj.paid) - decimal.Decimal(payment_sum), 2)
    totals = [
        # ['GRAVADA', 'S/. ' + str(round(decimal.Decimal(total) / decimal.Decimal(1.1800), 4))],
        # ['DESCUENTO', str(round(decimal.Decimal(0.00), 2))],
        # ['IGV 18.00%',
        #  'S/. ' + str(round(decimal.Decimal(total) - decimal.Decimal(total) / decimal.Decimal(1.1800), 4))],
        ['TOTAL',
         'S/. ' + str(decimal.Decimal(total).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_DOWN))],
        # ['TOTAL PAGADO', 'S/. ' + str(round(decimal.Decimal(order_obj.payment_invoice()), 2))]
        ['TOTAL PAGADO', 'S/. ' + str(
            decimal.Decimal(order_obj.paid).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_DOWN))],
        ['TOTAL VUELTO',
         'S/. ' + str(decimal.Decimal(total_turn).quantize(decimal.Decimal('0.5'), rounding=decimal.ROUND_HALF_UP))]
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
    payment = [['FORMAS DE PAGO', order_obj.payments_set.first().get_payment_display().upper(),
                round(decimal.Decimal(order_obj.total), 4)]]
    # for p in Payments.objects.filter(order=order_obj):
    #     payment.append(
    #         ['PAGO ' + str(p.get_payment_display()).upper(), 'S/. ' + str(round(decimal.Decimal(p.amount), 2)), ''])

    pdf_payment = Table(payment, colWidths=[w * 40 / 100, w * 30 / 100, w * 30 / 100])
    payment_style = [
        ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),  # three column
        ('ALIGNMENT', (1, 0), (2, -1), 'RIGHT'),  # three column
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),  # first column
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        # ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#9E9E9E')),
    ]
    pdf_payment.setStyle(TableStyle(payment_style))
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
    pdf.append(pdf_payment)
    # pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    # pdf.append(pdf_qr)
    # pdf.append(Spacer(1, -3))
    pdf.append(Spacer(1, -3))
    pdf.append(Paragraph(line, styles["CenterNewgotBold"]))
    pdf.append(Paragraph("NO SE ACEPTAN CAMBIOS NI DEVOLUCIONES", styles["CenterNewgotBold"]))
    doc.build(pdf)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pago_{}.pdf"'.format(order_obj.number)
    response.write(buff.getvalue())
    buff.close()
    return response


def pdf(request, pk=None):
    order_obj = Order.objects.get(id=pk)
    client_obj = order_obj.person
    subsidiary_obj = order_obj.subsidiary

    ml = 0.25 * inch
    mr = 0.25 * inch
    ms = 0.25 * inch
    mi = 0.25 * inch

    _bts = 8.3 * inch - 0.25 * inch - 0.25 * inch
    I = Image(logo)
    I.drawHeight = 3.00 * inch / 2.9
    I.drawWidth = 4.0 * inch / 2.9
    title = [
        [Paragraph(str(subsidiary_obj.business_name), styles["narrow_b_tittle_justify"])],
        [Paragraph(str(subsidiary_obj.address), styles["narrow_b_justify"])],
        [Paragraph('CORREO: ' + str(subsidiary_obj.email).upper(), styles['narrow_b_justify'])],
        [Paragraph('TELEFONO: ' + str(subsidiary_obj.phone).upper(), styles['narrow_b_justify'])],
    ]
    C = Table(title)
    c_style = [
        # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
        # ('TEXTCOLOR', (0, 0), (-1, -1), colors.red)
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ]
    C.setStyle(TableStyle(c_style))
    detail_set = []
    type_document = '-'
    if order_obj.type == 'V':
        if order_obj.status == 'N':
            detail_set = order_obj.orderdetail_set.filter(is_state=False, operation='S')
        else:
            detail_set = order_obj.orderdetail_set.filter(is_state=True)
        type_document = str(order_obj.get_doc_display())
    elif order_obj.type == 'T':
        detail_set = order_obj.orderdetail_set.filter(is_state=False)
        type_document = str(order_obj.get_type_display())

    if order_obj.bill_number:
        number_invoice = str(order_obj.bill_serial) + ' - ' + str(order_obj.bill_number).zfill(10)
    else:
        number_invoice = 'Nº ' + str(order_obj.number).zfill(10)
    header_r = [
        ['RUC ' + str(subsidiary_obj.ruc)],
        [type_document.upper()],
        [number_invoice],
    ]
    D = Table(header_r)
    d_style = [
        # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
        ('FONTSIZE', (0, 0), (-1, -1), 13),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('SPAN', (0, 0), (0, 0))
    ]
    D.setStyle(TableStyle(d_style))
    H = [
        [I, C, D],
    ]
    H_header = Table(H, colWidths=[_bts * 25 / 100, _bts * 50 / 100, _bts * 25 / 100])
    header_style = [
        # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # first column
        ('SPAN', (0, 0), (0, 0)),  # first row
        # ('LINEBELOW', (0, -1), (-1, -1), 0.5, purple, 1, None, None, 4, 1),
        ('BACKGROUND', (2, 0), (-1, 1), HexColor('#474aa1')),  # Establecer el color de fondo de la segunda fila
        ('LINEBEFORE', (1, 0), (-1, -1), 0.1, colors.lightgrey),
        # Establezca el color de la línea izquierda de la tabla en
    ]
    H_header.setStyle(TableStyle(header_style))
    # ---------------------------------Datos Cliente----------------------------#
    client_names = '-'
    client_address = '-'
    client_phone = '-'
    client_email = '-'
    document_type = 'DOCUMENTO'
    document_number = '-'
    if client_obj:
        if client_obj.names:
            client_names = client_obj.names
        if client_obj.address:
            client_address = client_obj.address
        if client_obj.phone:
            client_phone = client_obj.phone
        if client_obj.email:
            client_email = client_obj.email
        if client_obj.document:
            document_type = str(client_obj.get_document_display())
        if client_obj.number:
            document_number = str(client_obj.number)
    client = [
        ['CLIENTE:', client_names],
        [document_type + ':', document_number],
        ['DIRECCION:', Paragraph(str(client_address.upper()), styles["narrow_a_justify"])],
        ['TELEFONO:', str(client_phone)],
        ['CORREO:', str(client_email).upper()]
    ]
    client_header = Table(client, colWidths=[_bts * 10 / 100, _bts * 64 / 100])
    client_style = [
        # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),  # first column
        ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
    ]
    client_header.setStyle(TableStyle(client_style))
    order = [
        ['FECHA: ', str(order_obj.create_at.strftime("%d-%m-%Y"))],
        ['USUARIO: ', str(order_obj.user.username).upper()],
        ['PLACA: ', str(order_obj.license_plate)],
        ['ORDEN Nº: ', str(order_obj.number)]
    ]
    order_row = Table(order, colWidths=[_bts * 12 / 100, _bts * 14 / 100])
    order_row.setStyle(TableStyle(client_style))
    client_order = [
        [client_header, order_row],
    ]
    client_order_row = Table(client_order, colWidths=[_bts * 74 / 100, _bts * 26 / 100])
    co_style = [
        # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (0, -1), 'CENTER'),  # first column
    ]
    client_order_row.setStyle(TableStyle(co_style))
    # ------------ENCABEZADO DEL DETALLE-------------------#
    header_detail_style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),  # all columns
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#474aa1')),  # all columns
        ('BACKGROUND', (0, 0), (-1, 1), HexColor('#474aa1')),
        # Establecer el color de fondo de la segunda fila    ]
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
    ]
    width_table = [_bts * 5 / 100, _bts * 7 / 100, _bts * 42 / 100, _bts * 10 / 100, _bts * 12 / 100,
                   _bts * 12 / 100,
                   _bts * 12 / 100]
    document_header_detail = Table([('Nº', 'CODIGO', 'DESCRIPCIÓN', 'CANTIDAD', 'UND/MED', 'PRECIO', 'IMPORTE')],
                                   colWidths=width_table)
    document_header_detail.setStyle(TableStyle(header_detail_style))

    # -------------------DETAIL---------------------#
    row_detail = []
    count = 0
    total_amount = 0

    for d in detail_set.order_by('id'):
        count = count + 1
        _code = str(d.product.code)
        _product = Paragraph((str(d.product.name.upper()) + '\n' + str(d.product.measure())).replace("\n", "<br/>"),
                             styles["narrow_a_justify"])
        _unit = str(d.get_unit_display())
        _quantity = str(round(decimal.Decimal(d.quantity), 2))
        _price = str(round(decimal.Decimal(d.price), 4))
        _amount = str(round(decimal.Decimal(d.quantity) * decimal.Decimal(d.price), 4))
        row_detail.append((str(count), _code, _product, _quantity, _unit, _price, _amount))
        total_amount = total_amount + d.quantity * d.price
        document_body_detail = Table(row_detail,
                                     colWidths=[_bts * 5 / 100, _bts * 7 / 100, _bts * 42 / 100, _bts * 10 / 100,
                                                _bts * 12 / 100,
                                                _bts * 12 / 100,
                                                _bts * 12 / 100])
        body_detail_style = [
            # ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#7a3621')),
            ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
            ('ALIGNMENT', (0, 0), (4, -1), 'CENTER'),  # all column
            ('ALIGNMENT', (2, 0), (2, -1), 'LEFT'),  # three column
            ('ALIGNMENT', (5, 0), (-1, -1), 'RIGHT'),  # three column
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # first column
            ('RIGHTPADDING', (3, 0), (3, -1), 10),  # first column
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # all columns
            # ('BACKGROUND', (4, 0), (4, -1), colors.blue),  # four column
        ]
        document_body_detail.setStyle(TableStyle(body_detail_style))
        # -------------- Footer Detail ----------------------------
    money = str(order_obj.get_coin_display())
    total_discount = decimal.Decimal(order_obj.total_discount)
    sub_total = (decimal.Decimal(total_amount) / decimal.Decimal(1.1800)) - total_discount
    total_invoice = decimal.Decimal(total_amount)
    total_igv = total_invoice - sub_total
    total = []
    if order_obj.doc == '1' or order_obj.doc == '2':
        total.append(['GRAVADA', 'S/.', str(round(sub_total, 4))])
        total.append(['DESCUENTO', 'S/.', str(round(total_discount, 4))])
        total.append(['I.G.V.(18%)', 'S/.', str(round(total_igv, 4))])
        total.append(['TOTAL', 'S/.', str(round(total_invoice, 4))])
    else:
        total.append(['TOTAL', 'S/.', str(round(total_invoice, 4))])

    TT = Table(total, colWidths=[_bts * 12 / 100, _bts * 5 / 100, _bts * 13 / 100])
    total_style = [
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        # ('FONTSIZE', (0, 3), (-1, -1), 11),
        # ('FONTNAME', (0, 3), (-1, -1), 'Newgot'),
        # ('TEXTCOLOR', (0, 3), (-1, -1), colors.white),
        ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
        ('ALIGNMENT', (1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # ('BACKGROUND', (0, 3), (-1, -1), HexColor('#474aa1')),
        # # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#474aa1')),
        ('LINEBEFORE', (2, 0), (-1, -1), 0.5, colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]
    TT.setStyle(TableStyle(total_style))
    total_letter = [
        ['IMPORTE EN LETRAS: ' + number_money(round(total_invoice, 2), money).upper()],
    ]
    TL = Table(total_letter, colWidths=[_bts * 70 / 100])
    total_letter_style = [
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),
    ]
    TL.setStyle(TableStyle(total_letter_style))
    total_ = [
        [TL, TT],
    ]
    document_total = Table(total_, colWidths=[_bts * 70 / 100, _bts * 30 / 100])
    total_style = [
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # three column
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),  # first column
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.red),
    ]
    document_total.setStyle(TableStyle(total_style))
    # ....................... QR ........................................
    qr_left = []
    if order_obj.bill_qr:
        code_qr = str(order_obj.bill_qr)
        qr_left = [
            [Paragraph('Representación impresa de la FACTURA ELECTRÓNICA, para ver el documento visita',
                       styles["narrow_left"])],
            [Paragraph('https://www.tuf4ct.com/cpe ', styles["narrow_left"])],
            [Paragraph(
                'Emitido mediante un PROVEEDOR Autorizado por la SUNAT',
                styles["narrow_left"])],
            [Paragraph('', styles["narrow_left"])],
            [Paragraph('', styles["narrow_left"])],
        ]
    else:
        code_qr = str(order_obj.number)
        qr_left = [[Paragraph('Representación impresa de la ' + str(order_obj.get_type_display()),
                              styles["narrow_left"])], ]

    qr_l = Table(qr_left, colWidths=[_bts * 80 / 100])

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
    qr_table = Table(qr_row, colWidths=[_bts * 80 / 100, _bts * 20 / 100])
    style_qr = [
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.9, HexColor('#474aa1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    qr_table.setStyle(TableStyle(style_qr))
    # ..................................mode payment.................................
    payment_num = 0
    row_payment = [('N°', 'FORMA PAGO', 'FECHA', 'MONEDA', 'TOTAL')]
    for p in order_obj.payments_set.filter(subsidiary=subsidiary_obj).order_by('id'):
        if p.payment == 'C':
            # Si es pago a crédito, recorrer las cuotas del modelo PaymentFees
            payment_fees = p.paymentfees_set.all().order_by('id')
            for fee in payment_fees:
                payment_num = payment_num + 1
                payment_text = 'CREDITO: CUOTA ' + str(payment_num)
                payment_date = str(fee.date) if fee.date else str(p.date_payment)
                payment_amount = str(round(fee.amount, 2))
                row_payment.append((str(payment_num), str(payment_text), payment_date, money, payment_amount))
        else:
            # Para otros tipos de pago, mantener la lógica original
            payment_num = payment_num + 1
            payment_text = str(p.get_payment_display()).upper()
            payment_date = str(p.date_payment)
            payment_amount = str(round(p.amount, 2))
            row_payment.append((str(payment_num), str(payment_text), payment_date, money, payment_amount))
    payment_detail = Table(row_payment,
                           colWidths=[_bts * 10 / 100, _bts * 35 / 100, _bts * 15 / 100, _bts * 15 / 100,
                                      _bts * 25 / 100])
    payment_detail_style = [
        ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#474aa1')),
        ('FONTNAME', (0, 0), (-1, 0), 'Narrow-b'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
        ('ALIGNMENT', (4, 1), (4, -1), 'RIGHT'),  # three column
        # ('ALIGNMENT', (3, 0), (4, -1), 'CENTER'),  # three column
        # ('ALIGNMENT', (5, 0), (-1, -1), 'RIGHT'),  # three column
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # first column
        # ('RIGHTPADDING', (3, 0), (3, -1), 10),  # first column
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # all columns
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#474aa1')),  # four column
        # ('SPAN', (0, 0), (-1, 0)),  # first row
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ]
    payment_detail.setStyle(TableStyle(payment_detail_style))
    # --------------------------------------------------------------------------------------
    footer = [
        [payment_detail],
    ]
    document_footer = Table(footer, colWidths=[_bts * 100 / 100])
    footer_style = [
        # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
    ]
    document_footer.setStyle(TableStyle(footer_style))
    # .......................... FORMA DE PAGO .................................................

    # ------------------------------------------------------------------------------------------
    buff = io.BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=(8.3 * inch, 11.7 * inch),
                            rightMargin=mr,
                            leftMargin=ml,
                            topMargin=ms,
                            bottomMargin=mi,
                            title=str(order_obj.get_doc_display()) + "-" + str(number_invoice),

                            )
    dictionary = []
    dictionary.append(H_header)
    dictionary.append(DrawInvoice(count_row=count))
    dictionary.append(Spacer(1, 10))
    dictionary.append(client_order_row)
    dictionary.append(Spacer(1, 16))
    dictionary.append(document_header_detail)
    dictionary.append(document_body_detail)
    dictionary.append(Spacer(1, 5))
    dictionary.append(document_total)
    dictionary.append(Spacer(1, 5))
    dictionary.append(qr_table)
    dictionary.append(Spacer(1, 5))
    if order_obj.type == 'V':
        dictionary.append(document_footer)
    dictionary.append(Spacer(1, 5))
    response = HttpResponse(content_type='application/pdf')
    doc.build(dictionary, canvasmaker=NumberedCanvas, onFirstPage=add_draw, onLaterPages=add_draw)
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
        canvas.setLineWidth(3.5)
        canvas.setStrokeGray(0.9)
        canvas.setFillColor(Color(0, 0, 0, alpha=1))
        canvas.roundRect(-7, 1, 563, 90, 8, stroke=1, fill=0)
        canvas.restoreState()


def num_day(end, init):
    n = str(end - init).replace('day,', '').replace('days,', '').replace(' ', '').replace('0:00:00', '')
    print('valor de n=' + str(n))
    if n == 0 or n == '':
        n = 1
    if int(n) == 1:
        return "{}{} día".format(0, n)
    elif 1 < int(n) < 10:
        return "{}{} días".format(0, n)
    else:
        return "{} días".format(n)


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Narrow", 11)
        self.drawRightString(cm * 20.3, cm - 17,
                             "Pagina %d de %d" % (self._pageNumber, page_count))


def add_draw(canvas, doc):
    canvas.saveState()
    pageNumber = canvas._pageNumber
    if pageNumber > 0:
        canvas.setFillColor(Color(0, 0, 0, alpha=0.4))
        canvas.drawImage(watermark, (doc.width - 350) / 2, (doc.height - 350) / 2, width=350, height=350)
        canvas.setStrokeGray(0.9)
        # canvas.drawString(10 * cm, cm, 'Pagina ' + str(pageNumber))
        # p = Paragraph('Pagina ' + str(pageNumber),
        #               styles["narrow_center"])
        footer1 = Paragraph("NO SE ACEPTAN CAMBIOS NI DEVOLUCIONES",
                            styles["narrow_center_pie"])
        # footer4 = Paragraph("NOTAS",
        #                     styles["narrow_center_pie"])
        footer5 = Paragraph("www.4soluciones.net",
                            styles["narrow_center_pie"])
        w1, h1 = footer1.wrap(doc.width, doc.bottomMargin)
        # w4, h4 = footer4.wrap(doc.width, doc.bottomMargin)
        w5, h5 = footer5.wrap(doc.width, doc.bottomMargin)
        # w, h = p.wrap(doc.width, doc.bottomMargin)
        footer1.drawOn(canvas, doc.leftMargin, h1 + 10)
        # footer4.drawOn(canvas, doc.leftMargin, h4 + 9)
        footer5.drawOn(canvas, doc.leftMargin, h5)
        # p.drawOn(canvas, 10 * cm, h)
        canvas.setLineWidth(1)
        canvas.setStrokeColor(black)
        # canvas.line(15, 75, 580, 75)
        canvas.line(15, 30, 580, 30)
        # canvas.setFont('Times-Roman', 9)
        # canvas.setLineWidth(4)
        # canvas.setFillColor(Color(0, 0, 0, alpha=1))
        # canvas.setStrokeGray(0.9)
        # canvas.roundRect(18, 730, 563, 90, 8, stroke=1, fill=0)
        canvas.restoreState()


def quotation_pdf(request, pk=None):
    order_obj = Order.objects.get(id=pk)
    client_obj = order_obj.person
    subsidiary_obj = order_obj.subsidiary

    ml = 0.25 * inch
    mr = 0.25 * inch
    ms = 0.25 * inch
    mi = 0.25 * inch

    _bts = 8.3 * inch - 0.25 * inch - 0.25 * inch
    I = Image(logo)
    I.drawHeight = 3.00 * inch / 2.9
    I.drawWidth = 4.0 * inch / 2.9
    title = [
        [Paragraph(str(subsidiary_obj.business_name), styles["narrow_b_tittle_justify"])],
        [Paragraph(str(subsidiary_obj.address), styles["narrow_b_justify"])],
        [Paragraph('CORREO: ' + str(subsidiary_obj.email).upper(), styles['narrow_b_justify'])],
        [Paragraph('TELEFONO: ' + str(subsidiary_obj.phone).upper(), styles['narrow_b_justify'])],
    ]
    C = Table(title)
    c_style = [
        # ('GRID', (0, 3), (0, 3), 0.9, colors.red),
        # ('TEXTCOLOR', (0, 0), (-1, -1), colors.red)
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ]
    C.setStyle(TableStyle(c_style))
    detail_set = []
    type_document = '-'
    if order_obj.type == 'V':
        detail_set = order_obj.orderdetail_set.filter(is_state=True)
        type_document = str(order_obj.get_doc_display())
    elif order_obj.type == 'T':
        detail_set = order_obj.orderdetail_set.filter(is_state=False)
        type_document = str(order_obj.get_type_display())
    number_invoice = '-'
    # if order_obj.bill_number:
    #     number_invoice = str(order_obj.bill_serial) + ' - ' + str(order_obj.bill_number).zfill(10)
    # else:
    number_invoice = 'Nº ' + str(order_obj.number).zfill(10)
    header_r = [
        ['RUC ' + str(subsidiary_obj.ruc)],
        ['COTIZACIÓN'],
        [number_invoice],
    ]
    D = Table(header_r)
    d_style = [
        # ('GRID', (0, 0), (-1, -1), 0.9, colors.red),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
        ('FONTSIZE', (0, 0), (-1, -1), 13),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('SPAN', (0, 0), (0, 0))
    ]
    D.setStyle(TableStyle(d_style))
    H = [
        [I, C, D],
    ]
    H_header = Table(H, colWidths=[_bts * 25 / 100, _bts * 50 / 100, _bts * 25 / 100])
    header_style = [
        # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # first column
        ('SPAN', (0, 0), (0, 0)),  # first row
        # ('LINEBELOW', (0, -1), (-1, -1), 0.5, purple, 1, None, None, 4, 1),
        ('BACKGROUND', (2, 0), (-1, 1), HexColor('#d44c4c')),  # Establecer el color de fondo de la segunda fila
        ('LINEBEFORE', (1, 0), (-1, -1), 0.1, colors.lightgrey),
        # Establezca el color de la línea izquierda de la tabla en
    ]
    H_header.setStyle(TableStyle(header_style))
    # ---------------------------------Datos Cliente----------------------------#
    order_document_tittle = [['COTIZACIÓN ' + str(number_invoice) + ' - ' + str(order_obj.create_at.year)]]
    order_document = Table(order_document_tittle, colWidths=[_bts * 100 / 100])
    order_document_style = [
        # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
    ]
    order_document.setStyle(TableStyle(order_document_style))
    client_names = '-'
    client_address = '-'
    client_phone = '-'
    client_email = '-'
    document_type = 'DOCUMENTO'
    document_number = '-'
    if client_obj:
        if client_obj.names:
            client_names = client_obj.names
        if client_obj.address:
            client_address = client_obj.address
        if client_obj.phone:
            client_phone = client_obj.phone
        if client_obj.email:
            client_email = client_obj.email
        if client_obj.document:
            document_type = str(client_obj.get_document_display())
        if client_obj.number:
            document_number = str(client_obj.number)
    client = [
        ['FECHA          :', str(order_obj.create_at.strftime("%d-%m-%Y"))],
        ['EMPRESA     :', client_names],
        ['DIRECCION  :', Paragraph(str(client_address.upper()), styles["narrow_a_justify"])]
    ]
    client_header = Table(client, colWidths=[_bts * 10 / 100, _bts * 64 / 100])
    client_style = [
        # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),  # first column
        ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
    ]
    client_header.setStyle(TableStyle(client_style))
    order = [
        [document_type + '              :', document_number],
        ['CORREO     :', str(client_email).upper()],
        ['TELEFONO :', str(client_phone)],
        ['USUARIO :', str(order_obj.user.first_name.upper())]
    ]
    order_row = Table(order, colWidths=[_bts * 12 / 100, _bts * 14 / 100])
    order_row.setStyle(TableStyle(client_style))
    client_order = [
        [client_header, order_row],
    ]
    client_order_row = Table(client_order, colWidths=[_bts * 74 / 100, _bts * 26 / 100])
    co_style = [
        # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (0, -1), 'CENTER'),  # first column
    ]
    client_order_row.setStyle(TableStyle(co_style))
    # ------------DESCRIPCION------------------------------#
    order_document_body = [[Paragraph(
        'Tengo el agrado de dirigirme a Ud. Con la finalidad de  saludarlos muy cordialmente, de la misma manera aprovecho la oportunidad para presentarle nuestra mejor oferta por lo siguiente:',
        styles["Justify_a4"])]]
    order_doc_body = Table(order_document_body, colWidths=[_bts * 100 / 100])
    order_doc_body_style = [
        # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),  # first column
    ]
    order_doc_body.setStyle(TableStyle(order_doc_body_style))
    # ------------ENCABEZADO DEL DETALLE-------------------#
    header_detail_style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),  # all columns
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#d44c4c')),  # all columns
        ('BACKGROUND', (0, 0), (-1, 1), HexColor('#d44c4c')),
        # Establecer el color de fondo de la segunda fila    ]
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),  # all columns
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
    ]
    width_table = [_bts * 5 / 100, _bts * 7 / 100, _bts * 10 / 100, _bts * 12 / 100,
                   _bts * 42 / 100,
                   _bts * 12 / 100,
                   _bts * 12 / 100]
    document_header_detail = Table([('Nº', 'CODIGO', 'CANTIDAD', 'UND/MED', 'DESCRIPCIÓN', 'PRECIO', 'IMPORTE')],
                                   colWidths=width_table)
    document_header_detail.setStyle(TableStyle(header_detail_style))

    # -------------------DETAIL---------------------#
    row_detail = []
    count = 0
    total_amount = 0

    for d in detail_set.order_by('id'):
        count = count + 1
        _code = str(d.product.code)
        _product = Paragraph((str(d.product.name.upper()) + '\n' + str(d.product.measure())).replace("\n", "<br/>"),
                             styles["narrow_a_justify"])
        _unit = str(d.get_unit_display())
        _quantity = str(round(decimal.Decimal(d.quantity), 2))
        _price = str(round(decimal.Decimal(d.price), 4))
        _amount = str(round(decimal.Decimal(d.quantity) * decimal.Decimal(d.price), 4))
        row_detail.append((str(count), _code, _quantity, _unit, _product, _price, _amount))
        total_amount = total_amount + d.quantity * d.price
        document_body_detail = Table(row_detail,
                                     colWidths=[_bts * 5 / 100, _bts * 7 / 100, _bts * 10 / 100, _bts * 12 / 100,
                                                _bts * 42 / 100,
                                                _bts * 12 / 100,
                                                _bts * 12 / 100])
        body_detail_style = [
            # ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#7a3621')),
            ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
            ('ALIGNMENT', (0, 0), (4, -1), 'CENTER'),  # all column
            ('ALIGNMENT', (4, 0), (4, -1), 'LEFT'),  # three column
            ('ALIGNMENT', (5, 0), (-1, -1), 'RIGHT'),  # three column
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # first column
            ('RIGHTPADDING', (3, 0), (3, -1), 10),  # first column
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # all columns
            # ('BACKGROUND', (4, 0), (4, -1), colors.blue),  # four column
        ]
        document_body_detail.setStyle(TableStyle(body_detail_style))
        # -------------- Footer Detail ----------------------------
    money = str(order_obj.get_coin_display())
    total_discount = decimal.Decimal(order_obj.total_discount)
    sub_total = (decimal.Decimal(total_amount) / decimal.Decimal(1.1800)) - total_discount
    total_invoice = decimal.Decimal(total_amount)
    total_igv = total_invoice - sub_total
    total = []
    # if order_obj.doc == '1' or order_obj.doc == '2':
    #     total.append(['SUBTOTAL', 'S/.', str(round(sub_total, 4))])
    #     total.append(['DESCUENTO', 'S/.', str(round(total_discount, 4))])
    #     total.append(['I.G.V.(18%)', 'S/.', str(round(total_igv, 4))])
    #     total.append(['TOTAL', 'S/.', str(round(total_invoice, 4))])
    # else:
    total.append(['SUBTOTAL', 'S/.', str(round(sub_total, 4))])
    total.append(['I.G.V.(18%)', 'S/.', str(round(total_igv, 4))])
    total.append(['TOTAL', 'S/.', str(round(total_invoice, 4))])

    TT = Table(total, colWidths=[_bts * 12 / 100, _bts * 5 / 100, _bts * 13 / 100])
    total_style = [
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('FONTNAME', (0, 0), (-1, -1), 'Newgot'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        # ('FONTSIZE', (0, 3), (-1, -1), 11),
        # ('FONTNAME', (0, 3), (-1, -1), 'Newgot'),
        # ('TEXTCOLOR', (0, 3), (-1, -1), colors.white),
        ('ALIGNMENT', (0, 0), (0, -1), 'LEFT'),
        ('ALIGNMENT', (1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # ('BACKGROUND', (0, 3), (-1, -1), HexColor('#474aa1')),
        # # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#474aa1')),
        ('LINEBEFORE', (2, 0), (-1, -1), 0.5, colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]
    TT.setStyle(TableStyle(total_style))
    total_letter = [
        ['IMPORTE EN LETRAS: ' + number_money(round(total_invoice, 2), money).upper()],
    ]
    TL = Table(total_letter, colWidths=[_bts * 70 / 100])
    total_letter_style = [
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('FONTNAME', (0, 0), (-1, -1), 'Narrow-b'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),
    ]
    TL.setStyle(TableStyle(total_letter_style))
    total_ = [
        [TL, TT],
    ]
    document_total = Table(total_, colWidths=[_bts * 70 / 100, _bts * 30 / 100])
    total_style = [
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # three column
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),  # first column
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.red),
    ]
    document_total.setStyle(TableStyle(total_style))
    # ....................... QR ........................................
    qr_left = []
    # if order_obj.bill_qr:
    #     code_qr = str(order_obj.bill_qr)
    #     qr_left = [
    #         [Paragraph('Representación impresa de la FACTURA ELECTRÓNICA, para ver el documento visita',
    #                    styles["narrow_left"])],
    #         [Paragraph('https://4soluciones.pse.pe/' + str(subsidiary_obj.ruc), styles["narrow_left"])],
    #         [Paragraph(
    #             'Emitido mediante un PROVEEDOR Autorizado por la SUNAT mediante Resolución de Intendencia No.034-005-0005315',
    #             styles["narrow_left"])],
    #         [Paragraph('', styles["narrow_left"])],
    #         [Paragraph('', styles["narrow_left"])],
    #     ]
    # else:
    code_qr = str(order_obj.number)
    qr_left = [[Paragraph('Tiempo de Entrega	: INMEDIATO ',
                          styles["narrow_left"])],
               [Paragraph('Presupuesto Válido	: 03 días',
                          styles["narrow_left"])],
               [Paragraph('Precios expresados en	: Soles',
                          styles["narrow_left"])],
               [Paragraph('Forma de Pago		: Contado',
                          styles["narrow_left"])],
               ]

    qr_l = Table(qr_left, colWidths=[_bts * 80 / 100])

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
    qr_table = Table(qr_row, colWidths=[_bts * 80 / 100, _bts * 20 / 100])
    style_qr = [
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
        # ('GRID', (0, 0), (-1, -1), 0.9, HexColor('#474aa1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    qr_table.setStyle(TableStyle(style_qr))
    # ...............................................................................
    foot_left = [[Paragraph('CTA. CORPORACION PERNOS JUNIOR S.R.L.',
                            styles["narrow_left"])],
                 [Paragraph('Banco de Crédito en Soles: 405-7222645-0-17',
                            styles["narrow_left"])],
                 [Paragraph('CCI: 002 405 007222645017 98',
                            styles["narrow_left"])],
                 [Paragraph('',
                            styles["narrow_left"])],
                 ]

    foot_left_detail = Table(foot_left, colWidths=[_bts * 50 / 100])
    foot_right = [[Paragraph('CTA. CORPORACION PERNOS JUNIOR S.R.L.',
                             styles["narrow_center"])],
                  [Paragraph('RUC: 20614357194',
                             styles["narrow_center"])],
                  [Paragraph('Av. El Sol N° 767 Urb. Las Mercedes (Interseccion con la Av. Circunvalación)',
                             styles["narrow_center"])],
                  [Paragraph('051 622543 - 946413793',
                             styles["narrow_center"])],
                  ]

    foot_right_detail = Table(foot_right, colWidths=[_bts * 50 / 100])
    foot_detail = [
        [foot_left_detail, foot_right_detail],
    ]
    foot_detail_table = Table(foot_detail, colWidths=[_bts * 50 / 100, _bts * 50 / 100])
    style_foot_detail_table = [
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
        # ('GRID', (0, 0), (-1, -1), 0.9, HexColor('#474aa1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    foot_detail_table.setStyle(TableStyle(style_foot_detail_table))
    # ..................................mode payment.................................
    payment_num = 0
    # row_payment = [('N°', 'FORMA PAGO', 'FECHA', 'MONEDA', 'TOTAL')]
    # for p in order_obj.payments_set.filter(subsidiary=subsidiary_obj).order_by('id'):
    #     payment_num = payment_num + 1
    #     payment_text = str(p.get_payment_display()).upper()
    #     if p.payment == 'C':
    #         payment_text = 'CREDITO: CUOTA ' + str(payment_num)
    #     payment_date = str(p.date_payment)
    #     payment_amount = str(round(p.amount, 2))
    #     row_payment.append((str(payment_num), str(payment_text), payment_date, money, payment_amount))
    # payment_detail = Table(row_payment,
    #                        colWidths=[_bts * 10 / 100, _bts * 35 / 100, _bts * 15 / 100, _bts * 15 / 100,
    #                                   _bts * 25 / 100])
    # payment_detail_style = [
    #     ('GRID', (0, 0), (-1, -1), 0.1, HexColor('#474aa1')),
    #     ('FONTNAME', (0, 0), (-1, 0), 'Narrow-b'),
    #     ('FONTSIZE', (0, 0), (-1, -1), 9),
    #     ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    #     ('LEFTPADDING', (0, 0), (0, -1), 10),  # first column
    #     ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),  # all column
    #     ('ALIGNMENT', (4, 1), (4, -1), 'RIGHT'),  # three column
    #     # ('ALIGNMENT', (3, 0), (4, -1), 'CENTER'),  # three column
    #     # ('ALIGNMENT', (5, 0), (-1, -1), 'RIGHT'),  # three column
    #     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # first column
    #     # ('RIGHTPADDING', (3, 0), (3, -1), 10),  # first column
    #     ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # all columns
    #     ('BACKGROUND', (0, 0), (-1, 0), HexColor('#474aa1')),  # four column
    #     # ('SPAN', (0, 0), (-1, 0)),  # first row
    #     ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    # ]
    # payment_detail.setStyle(TableStyle(payment_detail_style))
    # --------------------------------------------------------------------------------------
    # footer = [
    #     [payment_detail],
    # ]
    # document_footer = Table(footer, colWidths=[_bts * 100 / 100])
    # footer_style = [
    #     # ('GRID', (0, 0), (-1, -1), 0.9, colors.blue),  # all columns
    #     ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # all columns
    #     ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
    # ]
    # document_footer.setStyle(TableStyle(footer_style))
    # .......................... FORMA DE PAGO .................................................

    # ------------------------------------------------------------------------------------------
    buff = io.BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=(8.3 * inch, 11.7 * inch),
                            rightMargin=mr,
                            leftMargin=ml,
                            topMargin=ms,
                            bottomMargin=mi,
                            title=str(order_obj.get_doc_display()) + "-" + str(number_invoice),

                            )
    dictionary = []
    dictionary.append(H_header)
    dictionary.append(DrawInvoice(count_row=count))
    dictionary.append(Spacer(1, 10))
    dictionary.append(order_document)
    dictionary.append(Spacer(1, 10))
    dictionary.append(client_order_row)
    dictionary.append(Spacer(1, 10))
    dictionary.append(order_doc_body)
    dictionary.append(Spacer(1, 16))
    dictionary.append(document_header_detail)
    dictionary.append(document_body_detail)
    dictionary.append(Spacer(1, 5))
    dictionary.append(document_total)
    dictionary.append(Spacer(1, 5))
    dictionary.append(qr_table)
    dictionary.append(Spacer(1, 5))
    dictionary.append(foot_detail_table)
    dictionary.append(Spacer(1, 5))
    # if order_obj.type == 'V':
    #     dictionary.append(document_footer)
    dictionary.append(Spacer(1, 5))
    response = HttpResponse(content_type='application/pdf')
    doc.build(dictionary, canvasmaker=NumberedCanvas, onFirstPage=add_foot_pie, onLaterPages=add_foot_pie)
    response.write(buff.getvalue())
    buff.close()
    return response


def add_foot_pie(canvas, doc):
    canvas.saveState()
    pageNumber = canvas._pageNumber
    if pageNumber > 0:
        canvas.setFillColor(Color(0, 0, 0, alpha=0.4))
        canvas.drawImage(watermark, (doc.width - 350) / 2, (doc.height - 350) / 2, width=350, height=350)
        canvas.setStrokeGray(0.9)
        # canvas.drawString(10 * cm, cm, 'Pagina ' + str(pageNumber))
        # p = Paragraph('Pagina ' + str(pageNumber),
        #               styles["narrow_center"])
        footer1 = Paragraph("Venta de Materiales de Ajuste y Sujeción",
                            styles["narrow_center_pie"])
        # footer4 = Paragraph("NOTAS",
        #                     styles["narrow_center_pie"])
        footer5 = Paragraph("www.4soluciones.net",
                            styles["narrow_center_pie"])
        w1, h1 = footer1.wrap(doc.width, doc.bottomMargin)
        # w4, h4 = footer4.wrap(doc.width, doc.bottomMargin)
        w5, h5 = footer5.wrap(doc.width, doc.bottomMargin)
        # w, h = p.wrap(doc.width, doc.bottomMargin)
        footer1.drawOn(canvas, doc.leftMargin, h1 + 10)
        # footer4.drawOn(canvas, doc.leftMargin, h4 + 9)
        footer5.drawOn(canvas, doc.leftMargin, h5)
        # p.drawOn(canvas, 10 * cm, h)
        canvas.setLineWidth(1)
        canvas.setStrokeColor(black)
        # canvas.line(15, 75, 580, 75)
        canvas.line(15, 30, 580, 30)
        # canvas.setFont('Times-Roman', 9)
        # canvas.setLineWidth(4)
        # canvas.setFillColor(Color(0, 0, 0, alpha=1))
        # canvas.setStrokeGray(0.9)
        # canvas.roundRect(18, 730, 563, 90, 8, stroke=1, fill=0)
        canvas.restoreState()
