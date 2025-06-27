from django.core.serializers import serialize
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework import generics
# from django_filters.rest_framework import FilterSet, filters
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
# import rest_framework_filters as filters
# import django_filters
from rest_framework.views import APIView
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import api_view
import json
from json import JSONEncoder

from apps.accounting.models import Payments
from apps.sales.models import Order, OrderDetail
import decimal
import pytz

from apps.sales.number_letters import number_money


def utc_to_local(utc_dt):
    local_tz = pytz.timezone('America/Bogota')
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)


@api_view(['GET'])
def get_ticket_sale(request, orderNumber):
    try:
        order_obj = Order.objects.get(number=orderNumber)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':

        names = '-'
        client_document_type = ''
        client_number = ''

        if order_obj.person:
            names = order_obj.person.names
            client_document_type = order_obj.person.get_document_display()
            client_number = order_obj.person.number

        order_dict = {
            'type': order_obj.get_type_display(),
            'numberID': order_obj.number,
            'userName': order_obj.user.first_name.upper(),
            'date': order_obj.update_at.strftime("%d/%m/%Y"),
            'time': utc_to_local(order_obj.update_at).strftime("%H:%M:%S"),
            'clientName': names.upper(),
            'clientDocumentType': client_document_type,
            'clientDocumentNumber': client_number,
            'total': str(
                decimal.Decimal(order_obj.sum_total()).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_DOWN))
            # 'total': str(
            #     decimal.Decimal(order_obj.total).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_DOWN)),
        }
        # print(order_dict)
        return Response(order_dict)


@api_view(['GET'])
def get_payment_cash(request, orderNumber):
    order_obj = None
    try:
        order_set = Order.objects.filter(number=orderNumber)
        if order_set.exists():
            order_obj = order_set.last()
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':

        names = '-'
        client_document_type_display = '-'
        client_number = '-'
        client_address = '-'
        total_turn = decimal.Decimal(0.00)
        type_sale = 'TICKET'
        type_sale_id = 'T'
        serial = '-'
        correlative = '-'
        payment = 'SIN PAGO'
        license_plate = '-'
        client_document_type = '-'

        subsidiary_obj = order_obj.subsidiary

        title_business = subsidiary_obj.business_name
        title_address = subsidiary_obj.address
        title_ruc = subsidiary_obj.ruc
        title_phone = subsidiary_obj.phone

        payment_sum = Payments.objects.filter(payment__in=['E', 'D'], order=order_obj.number).aggregate(
            r=Coalesce(Sum('amount'), 0)).get('r')

        pdf_total_letter = 'SON: ' + str(
            number_money(round(decimal.Decimal(order_obj.total), 4), str(order_obj.get_coin_display())))

        if order_obj.payments_set.exists():
            payment = order_obj.payments_set.first().get_payment_display().upper()

        if order_obj.license_plate:
            license_plate = order_obj.license_plate

        if order_obj.paid > order_obj.total:
            total_turn = round(decimal.Decimal(order_obj.paid) - decimal.Decimal(order_obj.total), 2)

        if order_obj.doc == '1':
            type_sale_id = 'F'
            type_sale = 'FACTURA ELECTRÓNICA'
        elif order_obj.doc == '2':
            type_sale = 'BOLETA ELECTRÓNICA'
            type_sale_id = 'B'

        if order_obj.person:
            names = order_obj.person.names
            client_document_type_display = order_obj.person.get_document_display()
            client_document_type = order_obj.person.document
            client_number = order_obj.person.number
            client_address = order_obj.person.address

        if order_obj.doc == '1' or order_obj.doc == '2':

            if client_document_type == '1':
                serial = order_obj.bill_serial
                correlative = str(order_obj.bill_number).zfill(7 - len(str(order_obj.bill_number))).upper()
            elif client_document_type == '6':
                serial = order_obj.bill_serial
                correlative = str(order_obj.bill_number).zfill(7 - len(str(order_obj.bill_number))).upper()

        order = {
            'typeSale': type_sale,
            'typeSaleID': type_sale_id,
            'serial': serial,
            'correlative': correlative,
            'titleBusiness': title_business,
            'titleAddress': title_address,
            'titleRuc': title_ruc,
            'titlePhone': title_phone,
            'numberID': order_obj.number,
            'clientName': names,
            'licensePlate': license_plate,
            'clientDocumentType': client_document_type_display,
            'clientDocumentNumber': client_number,
            'clientAddress': client_address,
            'userName': order_obj.user.first_name.upper(),
            'date': order_obj.update_at.strftime("%d/%m/%Y"),
            'time': utc_to_local(order_obj.update_at).strftime("%H:%M:%S"),
            'engraved': 0,
            'igv': 0,
            'total': 0,
            'totalPayment': str(
                decimal.Decimal(order_obj.paid).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_DOWN)),
            'totalTurned': str(
                decimal.Decimal(total_turn).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_DOWN)),
            'totalTurned2': str(decimal.Decimal(total_turn)),
            'numberToLetter': pdf_total_letter.upper(),
            'payment': payment,
            'orderDetailDict': []
        }

        total = round(decimal.Decimal(0.00), 4)

        for d in order_obj.orderdetail_set.filter(is_state=True).order_by('id'):
            order_detail_dict = {
                'productName': d.product.code + " " + d.product.name.upper() + " " + d.product.measure() + " " + d.unit,
                'quantity': str(
                    decimal.Decimal(d.quantity).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_DOWN)),
                'unit': str(d.get_unit_display()),
                'price': str(
                    decimal.Decimal(d.price).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_DOWN)),
                'total': str(
                    decimal.Decimal(d.amount()).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_DOWN)),
            }
            total = total + d.amount()
            engraved = (decimal.Decimal(total) / decimal.Decimal(1.1800)).quantize(decimal.Decimal('0.00'),
                                                                                   rounding=decimal.ROUND_HALF_DOWN)
            igv = (decimal.Decimal(total) - decimal.Decimal(total) / decimal.Decimal(1.1800)).quantize(
                decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_DOWN)
            total = (decimal.Decimal(total)).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_DOWN)

            order.get('orderDetailDict').append(order_detail_dict)
            order['engraved'] = str(engraved)
            order['igv'] = str(igv)
            order['total'] = str(total)

        return Response(order)


@api_view(['GET'])
def get_close_cash(request, start_date, end_date):
    if request.method == 'GET':

        order_set = Order.objects.filter(create_at__range=(start_date, end_date), type='V', condition='R').exclude(status__in=['A', 'PA'])
        total_s = order_set.aggregate(
            r=Coalesce(Sum('total'), decimal.Decimal('0'))).get('r')
        total_f = order_set.filter(doc='1', payments__isnull=False).distinct('id').values('id', 'total')
        t_f = decimal.Decimal(0.00)
        for i in total_f:
            t_f += decimal.Decimal(i['total'])
        total_b = order_set.filter(doc='2', payments__isnull=False).distinct('id').values('id', 'total')
        t_b = decimal.Decimal(0.00)
        for i in total_b:
            t_b += decimal.Decimal(i['total'])
        total_t = order_set.filter(doc='0', payments__isnull=False).distinct('id').values('id', 'total')
        t_t = decimal.Decimal(0.00)
        for i in total_t:
            t_t += decimal.Decimal(i['total'])
        total_p = order_set.filter(payments__isnull=True).distinct('id').values('id', 'total')
        t_p = decimal.Decimal(0.00)
        for i in total_p:
            t_p += decimal.Decimal(i['total'])
        total_n = order_set.filter(doc='1', status='N', payments__isnull=False).distinct('id').values('id', 'total')
        t_n = decimal.Decimal(0.00)
        for i in total_n:
            t_n += decimal.Decimal(i['total'])

        cash_close_dict = {
            'start_date': str(start_date),
            'end_date': str(end_date),
            'total_sale': round(total_s - t_p - t_n, 2),
            'total_bills': round(t_f, 2),
            'total_receipt': round(t_b, 2),
            'total_ticket': round(t_t, 2),
            'total_pending': round(t_p, 2)
        }

        return Response(cash_close_dict)
