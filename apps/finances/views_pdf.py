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
from ..sales.models import Order
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


def guide_return(request, pk=None):
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
    pdf_transportation = Table(
        [('DATOS DEL TRANSPORTE', '')] +
        [('TRANSPORTISTA:', Paragraph(order_obj.guide_carrier_names.upper(), styles["Left-text"]))] +
        [('VEHÍCULO: ', Paragraph(order_obj.guide_truck.upper(), styles["Left-text"]))] +
        [('CONDUCTOR: ',
          Paragraph('DNI: ' + str(order_obj.guide_driver_dni) + ' - ' + 'NRO LICENCIA: ' + str(
              order_obj.guide_driver_license) + ' - ' + str(order_obj.guide_driver_full_name.upper()),
                    styles["Left-text"]))],
        colWidths=[w * 22 / 100, w * 78 / 100])
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
    for d in order_obj.orderdetail_set.filter(is_invoice=True):
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
    # -----------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------
    code_qr = 'https://4soluciones.pse.pe/20600854535'

    qr_left = [
        [Paragraph('Representación impresa de la ' + str(order_obj.get_add_display()).upper() +
                   ' REMITENTE ELECTRÓNICA, para ver el documento visita',
                   styles["narrow_left"])],
        [Paragraph('https://4soluciones.pse.pe/' + str(subsidiary_obj.ruc), styles["narrow_left"])],
        [Paragraph(
            'Emitido mediante un PROVEEDOR Autorizado por la SUNAT mediante Resolución de Intendencia No.034-005-0005315',
            styles["narrow_left"])],
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