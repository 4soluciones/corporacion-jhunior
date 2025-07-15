from http import HTTPStatus
from django.db.models import Min, Max, Sum, Count, Q, Prefetch, F
from django.db.models.functions import Coalesce
from django.forms import model_to_dict
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import json
import decimal
import time
from django.db.models import Q
import pytz
import requests
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.template import loader
from datetime import datetime, timedelta
import datetime
from django.db import DatabaseError, IntegrityError
from django.core import serializers
from django.views.generic import ListView

from apps import sales
from apps.accounting.api_FACT import send_sunat_4_fact, send_credit_note_fact
from apps.accounting.models import Casing, Payments, MoneyChange
from apps.accounting.sunat import send_sunat, credit_note, cancelsunat, query_apis_net_money, send_sunat_to_cancel, \
    credit_note_by_parts, credit_note_pending
from apps.hrm.models import Subsidiary, Person
from apps.sales.models import Order, OrderDetail, Product, Kardex
from apps.sales.views import input_stock, output_stock, kardex_ouput, kardex_initial, kardex_input
from apps.user.models import User


class CasingList(ListView):
    model = Casing
    template_name = 'accounting/casing_list.html'

    def get_context_data(self, **kwargs):
        casing_set = Casing.objects.all().order_by('id')
        context = {
            'casing_set': casing_set
        }
        return context


def modal_casing(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        casing_obj = None
        if pk and pk != '0':
            casing_obj = Casing.objects.get(id=int(pk))
        t = loader.get_template('accounting/casing.html')
        c = ({
            'casing_obj': casing_obj,
            'type_set': Casing._meta.get_field('type').choices,
            'subsidiary_set': Subsidiary.objects.all()
        })
        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
        })


@csrf_exempt
def casing_save(request):
    if request.method == 'POST':
        casing = request.POST.get('casing', '')
        types = request.POST.get('type', '')
        subsidiary = request.POST.get('subsidiary', '')
        subsidiary_obj = None
        if subsidiary:
            subsidiary_obj = Subsidiary.objects.get(id=int(subsidiary))
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        initial = request.POST.get('initial', '')
        pk = None
        if casing != '0' and casing != '':
            pk = int(casing)
        casing_obj, created = Casing.objects.update_or_create(
            id=pk,
            defaults={
                "type": types,
                "subsidiary": subsidiary_obj,
                "name": name.upper(),
                "description": description.upper(),
                "initial": decimal.Decimal(initial)
            })
        if created:
            return JsonResponse({
                'success': True,
                'message': 'Se registro con exito'
            }, status=HTTPStatus.OK)
        else:
            return JsonResponse({
                'success': True,
                'message': 'Se actualizo con exito'
            }, status=HTTPStatus.OK)


def get_total_money(casing_obj=None):
    total = []
    subsidiary_obj = casing_obj.subsidiary
    if casing_obj.type == 'C':
        aperture_set = Payments.objects.filter(casing=casing_obj, subsidiary=subsidiary_obj,
                                               payment='E', type='A', operation='R')
        if aperture_set:
            aperture_obj = aperture_set.last()
            total_aperture = aperture_obj.amount
            payment_set = Payments.objects.filter(subsidiary=subsidiary_obj, group=aperture_obj.group)
            total_entry = payment_set.filter(casing=casing_obj, payment='E', type='I').aggregate(
                r=Coalesce(Sum('amount'), decimal.Decimal(0))).get('r')
            total_egress = payment_set.filter(casing=casing_obj, payment='E', type='E').aggregate(
                r=Coalesce(Sum('amount'), decimal.Decimal(0))).get('r')
        else:
            total_aperture = casing_obj.initial
            total_entry = decimal.Decimal(0.00)
            total_egress = decimal.Decimal(0.00)
        subtotal_cash = total_entry - total_egress
        total_cash = total_aperture + subtotal_cash
        c_total = {
            'total_aperture': round(total_aperture, 4),
            'total_cash_entry': round(total_entry, 4),
            'total_cash_egress': round(total_egress, 4),
            'total_cash': round(subtotal_cash, 4),
            'total': round(total_cash, 4)
        }
        total.append(c_total)
    elif casing_obj.type == 'B':
        total_init = casing_obj.initial
        payment_set = Payments.objects.filter(subsidiary=subsidiary_obj, casing=casing_obj, payment='D')
        if payment_set:
            total_entry = payment_set.filter(type='I').aggregate(r=Coalesce(Sum('amount'), decimal.Decimal(0))).get('r')
            total_egress = payment_set.filter(type='E').aggregate(r=Coalesce(Sum('amount'), decimal.Decimal(0))).get(
                'r')
        else:
            total_entry = decimal.Decimal(0.00)
            total_egress = decimal.Decimal(0.00)
        subtotal_cash = total_entry - total_egress
        total_cash = total_init + subtotal_cash
        t_total = {
            'total_aperture': round(total_init, 4),
            'total_cash_entry': round(total_entry, 4),
            'total_cash_egress': round(total_egress, 4),
            'total_cash': round(subtotal_cash, 4),
            'total': round(total_cash, 4)
        }
        total.append(t_total)
    return total


def open_casing(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        if pk:
            casing_obj = Casing.objects.get(id=int(pk))
            user_id = request.user.id
            user_obj = User.objects.get(id=int(user_id))
            subsidiary_obj = user_obj.subsidiary
            my_date = datetime.datetime.now()
            date_now = my_date.strftime("%Y-%m-%d")
            tpl = loader.get_template('accounting/open.html')
            context = ({
                'date_now': date_now,
                'casing_obj': casing_obj,
                'total': round(get_total_open(casing_obj, subsidiary_obj), 4)
            })
            return JsonResponse({
                'success': True,
                'grid': tpl.render(context, request),
            }, status=HTTPStatus.OK, content_type="application/json")
        else:
            return JsonResponse({
                'success': False,
                'message': 'Problemas con la caja',
            }, status=HTTPStatus.OK)


def get_total_open(casing_obj=None, subsidiary_obj=None):
    try:
        opening_obj = Payments.objects.filter(casing=casing_obj, subsidiary=subsidiary_obj, type='A').last()
    except Payments.DoesNotExist:
        opening_obj = None

    if opening_obj is not None:
        closing_set = Payments.objects.filter(casing=casing_obj, subsidiary=subsidiary_obj, type='C',
                                              group=opening_obj.id)
        if closing_set:
            closing_obj = closing_set.last()
            return round(closing_obj.amount, 4)
        else:
            return casing_obj.get_total()
    else:
        return round(casing_obj.initial, 4)


@csrf_exempt
def opening(request):
    if request.method == 'POST':
        try:
            _date = request.POST.get('date-aperture', '')
            _pk = request.POST.get('id-casing', '')
            casing_obj = Casing.objects.get(id=int(_pk))
            _amount = request.POST.get('amount-aperture', '')
            user_id = request.user.id
            user_obj = User.objects.get(id=int(user_id))
            subsidiary_obj = user_obj.subsidiary
            payment_obj = Payments(
                type='A',
                payment='E',
                operation='R',
                description='Apertura de caja',
                amount=decimal.Decimal(_amount),
                coin='1',
                change_coin=1,
                date_payment=_date,
                user=user_obj,
                subsidiary=subsidiary_obj,
                casing=casing_obj
            )
            payment_obj.save()
            payment_obj.group = payment_obj.id
            payment_obj.save()
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e),
            }, status=HTTPStatus.OK)
        return JsonResponse({
            'success': True,
            'message': 'Caja aperturada con exito',
        }, status=HTTPStatus.OK)


def close_cash(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        if pk:
            casing_obj = Casing.objects.get(id=int(pk))
            dates = datetime.datetime.now()
            date_now = dates.strftime("%Y-%m-%d")
            tpl = loader.get_template('accounting/close.html')
            context = ({
                'date_now': date_now,
                'casing_obj': casing_obj,
                'total': get_total_money(casing_obj=casing_obj)
            })
            return JsonResponse({
                'success': True,
                'grid': tpl.render(context, request),
            }, status=HTTPStatus.OK, content_type="application/json")
        else:
            return JsonResponse({
                'success': False,
                'message': 'Problemas con la caja',
            }, status=HTTPStatus.OK)


@csrf_exempt
def closing(request):
    if request.method == 'POST':
        _date = request.POST.get('date-closing', '')
        _pk = request.POST.get('id-casing-close', '')
        _amount = request.POST.get('total-cash', '')
        if _amount:
            _amount = decimal.Decimal(_amount)
        else:
            _amount = decimal.Decimal(0.00)
        if _pk:
            casing_obj = Casing.objects.get(id=int(_pk))
        else:
            return JsonResponse({
                'success': False,
                'message': 'Caja no especificada',
            }, status=HTTPStatus.OK)
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = user_obj.subsidiary
        payment_obj = Payments(
            type='C',
            payment='E',
            operation='R',
            description='Cierre de caja',
            amount=decimal.Decimal(_amount),
            coin='1',
            change_coin=1,
            date_payment=_date,
            user=user_obj,
            subsidiary=subsidiary_obj,
            casing=casing_obj,
            # group=get_group(cash_obj=casing_obj)
        )
        payment_obj.save()
        return JsonResponse({
            'success': True,
            'pk': payment_obj.id,
            'message': 'Caja cerrada con exito',
        }, status=HTTPStatus.OK)


# def get_group(cash_obj=None):
#     if cash_obj is not None:
#         if cash_obj.type == 'C':
#             aperture_obj = Payments.objects.filter(casing=cash_obj,
#                                                    subsidiary=cash_obj.subsidiary,
#                                                    type='A').last()
#             group = aperture_obj.group
#         else:
#             group = 0
#         return int(group)
#     else:
#         return 0


def payable(request):
    if request.method == 'GET':
        order_set = Order.objects.filter(status='R', payments__order__isnull=True,
                                         type__in=['V', 'C']).order_by('id')
        return render(request, 'accounting/payable_list.html', {
            'order_set': order_set
        })


def payment_order(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        if pk:
            user_id = request.user.id
            user_obj = User.objects.get(id=int(user_id))
            subsidiary_obj = user_obj.subsidiary
            my_date = datetime.datetime.now()
            date_now = my_date.strftime("%Y-%m-%d")
            order_obj = Order.objects.get(id=int(pk))
            casing_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj, type='C').values('id',
                                                                                                            'name')
            bank_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj, type='B').values('id',
                                                                                                          'name')
            tpl = loader.get_template('accounting/payment_order.html')
            context = ({
                'date_now': date_now,
                'order_obj': order_obj,
                'payment_set': Payments._meta.get_field('payment').choices,
                'casing_set': casing_set,
                'bank_set': bank_set,
                'document_set': Person._meta.get_field('document').choices
            })
            return JsonResponse({
                'grid': tpl.render(context, request),
            }, status=HTTPStatus.OK, content_type="application/json")
        else:
            return JsonResponse({
                'success': False,
                'message': 'Orden desconocida',
            }, status=HTTPStatus.OK)


def get_validate_casing(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        if pk:
            casing_obj = Casing.objects.get(id=int(pk))
            status = False
            message = ''
            if casing_obj.get_status() == 'A':
                status = True
                message = 'Caja disponible'
            elif casing_obj.get_status() == 'C':
                status = False
                message = 'Necesita aperturar la caja'
            return JsonResponse({
                'success': status,
                'message': str(message),
            }, status=HTTPStatus.OK)


def number_invoice(subsidiary=None, document=None):
    number = Order.objects.filter(subsidiary=subsidiary, doc=document).aggregate(
        r=Coalesce(Max('bill_number'), 0)).get('r')
    return number + 1


def number_guide(subsidiary=None, document=None):
    number = Order.objects.filter(subsidiary=subsidiary, add=document).aggregate(
        r=Coalesce(Max('guide_number'), 0)).get('r')
    return number + 1


@csrf_exempt
def payment_save(request):
    if request.method == 'POST':
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        payment_json = request.POST.get('payment', '')
        data = json.loads(payment_json)
        order = data["order"]
        person = data["person"]
        date = data["date"]
        document = data["voucher"]
        total = data["total"]
        total_invoice = data["total_invoice"]
        total_paid = data["total_paid"]
        total_refund = data["total_refund"]
        if total_paid:
            total_paid = decimal.Decimal(total_paid)
        else:
            total_paid = decimal.Decimal(0.00)
        if total_invoice:
            total_invoice = decimal.Decimal(total_invoice)
        else:
            total_invoice = decimal.Decimal(0.00)
        if total:
            total = decimal.Decimal(total)
        if order:
            order_obj = Order.objects.get(id=int(order))
            # parent_order_obj = None
            # if order_obj.parent_order:
            #     parent_order_obj = Order.objects.get(id=int(order_obj.parent_order.id))
            #     if order_obj.total > parent_order_obj.total:

            if order_obj.bill_hash and (
                    document == '1' or document == '2') and order_obj.total == order_obj.total_payment():
                return JsonResponse({
                    'success': False,
                    'message': 'La orden ya tiene comprobante registrado'
                }, status=HTTPStatus.OK)
            else:
                user_id = request.user.id
                user_obj = User.objects.get(id=user_id)
                subsidiary_obj = user_obj.subsidiary
                for d in data['Detail']:
                    date_payment = d['date']
                    if date_payment:
                        type_payment = d['type']
                        if type_payment:
                            casing = d['casing']
                            if casing:
                                state = False
                                if type_payment == 'C':
                                    state = True
                                    casing_obj = None
                                else:
                                    casing_obj = Casing.objects.get(id=int(casing))
                                amount = d['amount']
                                if amount:
                                    amount = decimal.Decimal(amount)
                                    code = d['code']
                                    t = ''
                                    if order_obj.type == 'V':
                                        t = 'I'
                                    elif order_obj.type == 'C':
                                        t = 'E'
                                    else:
                                        t = 'I'
                                    pk = d['pk']
                                    py = None
                                    if pk != '0' and pk != '':
                                        py = int(pk)
                                        payment_obj = Payments.objects.get(id=py)
                                        payment_obj.order = order_obj
                                        payment_obj.type = t
                                        payment_obj.payment = type_payment
                                        payment_obj.operation = 'O'
                                        payment_obj.description = str(order_obj.get_type_display())
                                        payment_obj.code_operation = code
                                        if total_refund and amount > total:
                                            amount = amount - decimal.Decimal(total_refund)
                                        payment_obj.amount = amount
                                        payment_obj.coin = order_obj.coin
                                        payment_obj.change_coin = order_obj.change
                                        payment_obj.date_payment = date_payment
                                        payment_obj.user = user_obj
                                        payment_obj.subsidiary = subsidiary_obj
                                        payment_obj.casing = casing_obj
                                        payment_obj.credit = state
                                        payment_obj.save()
                                    else:
                                        if validate_payment(order=order_obj, amount=amount):
                                            payment_create = {
                                                'order': order_obj,
                                                'type': t,
                                                'payment': type_payment,
                                                'operation': 'O',
                                                'description': str(order_obj.get_type_display()),
                                                'code_operation': code,
                                                'amount': amount,
                                                'coin': order_obj.coin,
                                                'change_coin': order_obj.change,
                                                'date_payment': date_payment,
                                                'user': user_obj,
                                                'subsidiary': subsidiary_obj,
                                                'casing': casing_obj,
                                                'credit': state,
                                                # 'group': get_group(cash_obj=casing_obj)
                                            }
                                            payment_obj = Payments.objects.create(**payment_create)
                                            payment_obj.save()
                                            # if order_obj.doc == '1' or order_obj.doc == '2':
                                            #     for d in order_obj.orderdetail_set.filter(is_state=True,
                                            #                                               is_invoice=True):
                                            #         kardex_set = Kardex.objects.filter(product=d.product)
                                            #         if kardex_set.exists():
                                            #             kardex_ouput(product=d.product, quantity=d.quantity,
                                            #                          order_detail_obj=d,
                                            #                          type_document=str('0' + order_obj.doc),
                                            #                          type_operation='01')
                                            #         else:
                                            #             kardex_initial(product=d.product, stock=d.quantity,
                                            #                            price_unit=d.price, order_detail_obj=d)
                                else:
                                    return JsonResponse({
                                        'success': False,
                                        'message': 'No se especifico el monto'
                                    }, status=HTTPStatus.OK)
                            else:
                                return JsonResponse({
                                    'success': False,
                                    'message': 'No se especifico la cuenta'
                                }, status=HTTPStatus.OK)
                        else:
                            return JsonResponse({
                                'success': False,
                                'message': 'No se especifico la modalidad de pago'
                            }, status=HTTPStatus.OK)

                    else:
                        return JsonResponse({
                            'success': False,
                            'message': 'No se especifico la fecha'
                        }, status=HTTPStatus.OK)
                if order_obj.type == 'V' and order_obj.bill_enlace_pdf == None:
                    serial = ''
                    if document == '1':
                        serial = 'FF' + str(subsidiary_obj.serial)
                        if order_obj.bill_number:
                            correlative = order_obj.bill_number
                        else:
                            correlative = number_invoice(subsidiary=subsidiary_obj, document=document)
                        subtotal = total_invoice / decimal.Decimal(1.1800)
                        igv = total_invoice - subtotal
                        client_document = ''
                        client_name = ''
                        if order_obj.person:
                            client_document = order_obj.person.document
                            client_name = order_obj.person.number
                        qr = str(subsidiary_obj.ruc) + '|' + str(document.zfill(1)) + '|' + serial + '|' + str(
                            correlative).zfill(6 - len(str(correlative))) + '|' + str(round(igv, 4)) + '|' + str(
                            round(total_invoice, 4)) + '|' + str(
                            datetime.datetime.strptime(date, '%Y-%m-%d').strftime("%d/%m/%Y")) + '|' + str(
                            client_document) + '|' + str(client_name) + '|'
                    elif document == '2':
                        serial = 'BB' + str(subsidiary_obj.serial)
                        if order_obj.bill_number:
                            correlative = order_obj.bill_number
                        else:
                            correlative = number_invoice(subsidiary=subsidiary_obj, document=document)
                        subtotal = total_invoice / decimal.Decimal(1.1800)
                        igv = total_invoice - subtotal
                        client_document = ''
                        client_name = ''
                        if order_obj.person:
                            client_document = order_obj.person.document
                            client_name = order_obj.person.number
                        qr = str(subsidiary_obj.ruc) + '|' + str(document.zfill(1)) + '|' + serial + '|' + str(
                            correlative).zfill(6 - len(str(correlative))) + '|' + str(round(igv, 4)) + '|' + str(
                            round(total_invoice, 4)) + '|' + str(
                            datetime.datetime.strptime(date, '%Y-%m-%d').strftime("%d/%m/%Y")) + '|' + str(
                            client_document) + '|' + str(client_name) + '|'
                    elif document == '0':
                        if order_obj.bill_number:
                            return JsonResponse({
                                'success': False,
                                'pk': order_obj.id,
                                'message': 'No puede convertir un comprobante a ticket',
                                'number': order_obj.number
                            }, status=HTTPStatus.OK)
                        else:
                            serial = None
                            correlative = None
                            date = None
                            qr = None
                    else:
                        return JsonResponse({
                            'success': True,
                            'pk': order_obj.id,
                            'number': order_obj.number
                        }, status=HTTPStatus.OK)
                    order_obj.paid = total_paid
                    order_obj.doc = document
                    order_obj.bill_serial = serial
                    order_obj.bill_type = document
                    order_obj.bill_number = correlative
                    order_obj.bill_date = date
                    order_obj.bill_qr = qr
                    order_obj.save()
                    return JsonResponse({
                        'success': True,
                        'pk': order_obj.id,
                        'number': order_obj.number,
                        'hatch': user_obj.user_work,
                    }, status=HTTPStatus.OK)
                else:
                    return JsonResponse({
                        'success': True,
                        'pk': order_obj.id,
                        'message': 'Pagos registrados',
                        'number': order_obj.number,
                        'type_doc': order_obj.doc
                    }, status=HTTPStatus.OK)
        else:
            return JsonResponse({
                'success': False,
                'message': 'No se identifico la orden'
            }, status=HTTPStatus.OK)


def validate_payment(order=None, amount=0):
    if order:
        total_payment_plus_amount = (
                decimal.Decimal(round(round(float(order.total_payment()), 3), 2)) + decimal.Decimal(
            amount)).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_UP)
        order_total = decimal.Decimal(order.sum_total()).quantize(decimal.Decimal('0.00'),
                                                                  rounding=decimal.ROUND_HALF_UP)
        if total_payment_plus_amount <= order_total:
            order.total = order.sum_total()
            order.save()
            return True
        else:
            return False
    else:
        return False


def invoice_list(request):
    if request.method == 'GET':
        date_time = datetime.datetime.now()
        date = date_time.date()
        order_set = Order.objects.filter(doc='1', status='R', bill_description=None,
                                         type='V', bill_enlace_pdf=None, bill_number__gt=0).order_by('bill_number')
        return render(request, 'accounting/invoice_list.html', {
            'order_set': order_set
        })


def get_type_invoice(request):
    if request.method == 'GET':
        types = request.GET.get('type', '')
        if types:
            order_set = Order.objects.filter(doc=types, status='R', type='V', bill_enlace_pdf=None,
                                             bill_number__gt=0).order_by(
                'bill_number')
            tpl = loader.get_template('accounting/invoice_grid_list.html')
            context = ({
                'order_set': order_set
            })
            return JsonResponse({
                'grid': tpl.render(context, request),
            }, status=HTTPStatus.OK, content_type="application/json")


def get_pending_invoices_to_canceled(request):
    if request.method == 'GET':
        status = request.GET.get('status', '')
        if status:
            order_set = Order.objects.filter(doc__in=['1', '2'], status='E', condition='PA',
                                             type='V', bill_number__gt=0).order_by(
                'bill_number')
            tpl = loader.get_template('accounting/invoice_grid_list.html')
            context = ({
                'order_set': order_set
            })
            return JsonResponse({
                'grid': tpl.render(context, request),
            }, status=HTTPStatus.OK, content_type="application/json")


def invoice_sunat(request):
    if request.method == 'GET':
        pk = request.GET.get('o', '')
        if pk != '0' and pk != '':
            time.sleep(2)
            # r = send_sunat(pk)
            r = send_sunat_4_fact(pk)
            # if r.get('code_hash'):
            if r.get('success'):
                return JsonResponse({
                    'success': True,
                    'message': r.get('message'),
                }, status=HTTPStatus.OK)
            else:
                return JsonResponse({
                    'success': False,
                    'code': r.get('codigo'),
                    'error': r.get('errors'),
                    'message': r.get('message'),
                }, status=HTTPStatus.OK)


def invoice_cancel_sunat(request):
    if request.method == 'GET':
        pk = request.GET.get('o', '')
        if pk != '0' and pk != '':
            time.sleep(2)
            r = cancelsunat(pk)
            if r.get('enlace'):
                return JsonResponse({
                    'success': True,
                    'message': 'El Comprobante Electrónico ' + str(r.get('serial')) + '-' + str(r.get('number')) +
                               ' fue anulado correctamente',
                }, status=HTTPStatus.OK)
            else:
                return JsonResponse({
                    'success': False,
                    'code': r.get('codigo'),
                    'error': r.get('errors'),
                }, status=HTTPStatus.OK)


def send_receipt_sunat(request):
    if request.method == 'GET':
        pk = request.GET.get('order_id', '')
        if pk != '0' and pk != '':
            time.sleep(1)
            r = send_sunat_to_cancel(pk)
            if r.get('success'):
                return JsonResponse({
                    'success': True,
                    'message': 'La Boleta Electronica ' + r.get('serial') + r.get('number') +
                               'Fue enviada correctamente, espere 24 horas para Anularla',
                }, status=HTTPStatus.OK)
            else:
                return JsonResponse({
                    'success': False,
                    'code': r.get('codigo'),
                    'error': r.get('errors'),
                }, status=HTTPStatus.OK)


def send_receipt_cancel(request):
    if request.method == 'GET':
        pk = request.GET.get('order_id', '')
        if pk != '0' and pk != '':
            time.sleep(1)
            c = cancelsunat(pk)
            if c.get('success'):
                return JsonResponse({
                    'success': True,
                    'message': 'La Boleta Electronica ' + c.get('serial') + c.get('number') +
                               'Fue anulada',
                }, status=HTTPStatus.OK)
            else:
                return JsonResponse({
                    'success': False,
                    'code': c.get('codigo'),
                    'error': c.get('errors'),
                }, status=HTTPStatus.OK)


def invoice_sunat_and_cancel(request):
    if request.method == 'GET':
        pk = request.GET.get('order_id', '')
        message_one = ''
        if pk != '0' and pk != '':
            time.sleep(1)
            r = send_sunat_to_cancel(pk)
            if r.get('success'):
                message_one = 'La Factura ' + str(r.get('serial')) + '-' + str(
                    r.get('number')) + ' se envio correctamente'
            time.sleep(1)
            c = cancelsunat(pk)
            if c.get('enlace'):
                message_two = 'La Factura ' + str(r.get('serial')) + '-' + str(
                    r.get('number')) + ' se anulo correctamente'
                return JsonResponse({
                    'success': True,
                    'message': message_one,
                    'messageTwo': message_two,
                }, status=HTTPStatus.OK)
            else:
                return JsonResponse({
                    'success': False,
                    'code': r.get('codigo'),
                    'error': r.get('errors'),
                    'codeA': c.get('codigo'),
                    'errorA': c.get('errors'),
                }, status=HTTPStatus.OK)


@csrf_exempt
def generate_guide(request):
    if request.method == 'POST':
        payment_json = request.POST.get('payment', '')
        data = json.loads(payment_json)
        order = data["order"]
        date = data["date"]
        document = data["voucher"]
        total = data["total"]
        if total:
            total = decimal.Decimal(total)
        if order:
            order_obj = Order.objects.get(id=int(order))
            if order_obj.bill_hash and (document == '1' or document == '2'):
                return JsonResponse({
                    'success': False,
                    'message': 'La orden ya tiene comprobante registrado'
                }, status=HTTPStatus.OK)
            else:
                user_id = request.user.id
                user_obj = User.objects.get(id=user_id)
                subsidiary_obj = user_obj.subsidiary
                for d in data['Detail']:
                    date_payment = d['date']
                    if date_payment:
                        type_payment = d['type']
                        if type_payment:
                            casing = d['casing']
                            if casing:
                                state = False
                                if type_payment == 'C':
                                    state = True
                                    casing_obj = None
                                else:
                                    casing_obj = Casing.objects.get(id=int(casing))
                                amount = d['amount']
                                if amount:
                                    amount = decimal.Decimal(amount)
                                    code = d['code']
                                    t = ''
                                    if order_obj.type == 'V':
                                        t = 'I'
                                    elif order_obj.type == 'C':
                                        t = 'E'
                                    else:
                                        t = 'I'
                                    pk = d['pk']
                                    py = None
                                    if pk != '0' and pk != '':
                                        py = int(pk)
                                    payment_obj, payment_create = Payments.objects.update_or_create(
                                        id=py,
                                        defaults={
                                            'order': order_obj,
                                            'type': t,
                                            'payment': type_payment,
                                            'operation': 'O',
                                            'description': str(order_obj.get_type_display()),
                                            'code_operation': code,
                                            'amount': amount,
                                            'coin': order_obj.coin,
                                            'change_coin': order_obj.change,
                                            'date_payment': date_payment,
                                            'user': user_obj,
                                            'subsidiary': subsidiary_obj,
                                            'casing': casing_obj,
                                            'credit': state,
                                            # 'group': get_group(cash_obj=casing_obj)
                                        })
                                else:
                                    return JsonResponse({
                                        'success': False,
                                        'message': 'No se especifico el monto'
                                    }, status=HTTPStatus.OK)
                            else:
                                return JsonResponse({
                                    'success': False,
                                    'message': 'No se especifico la cuenta'
                                }, status=HTTPStatus.OK)
                        else:
                            return JsonResponse({
                                'success': False,
                                'message': 'No se especifico la modalidad de pago'
                            }, status=HTTPStatus.OK)

                    else:
                        return JsonResponse({
                            'success': False,
                            'message': 'No se especifico la fecha'
                        }, status=HTTPStatus.OK)
                if document != '0' and order_obj.type == 'V':
                    serial = ''
                    if document == '1':
                        serial = 'F' + str(subsidiary_obj.serial)
                    elif document == '2':
                        serial = 'B' + str(subsidiary_obj.serial)
                    correlative = number_invoice(subsidiary=subsidiary_obj, document=document)
                    subtotal = total / decimal.Decimal(1.1800)
                    igv = total - subtotal
                    qr = str(subsidiary_obj.ruc) + '|' + str(document.zfill(1)) + '|' + serial + '|' + str(
                        correlative).zfill(6 - len(str(correlative))) + '|' + str(round(igv, 4)) + '|' + str(
                        round(total, 4)) + '|' + str(
                        datetime.datetime.strptime(date, '%Y-%m-%d').strftime("%d/%m/%Y")) + '|' + str(
                        order_obj.person.document) + '|' + str(order_obj.person.number) + '|'
                    order_obj.doc = document
                    order_obj.bill_serial = serial
                    order_obj.bill_type = document
                    order_obj.bill_number = correlative
                    order_obj.bill_date = date
                    order_obj.bill_qr = qr
                    order_obj.save()
                    return JsonResponse({
                        'success': True,
                        'pk': order_obj.id
                    }, status=HTTPStatus.OK)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Pagos registrados'
                    }, status=HTTPStatus.OK)
        else:
            return JsonResponse({
                'success': False,
                'message': 'No se identifico la orden'
            }, status=HTTPStatus.OK)


def orders_person_list(request):
    if request.method == 'GET':
        return render(request, 'accounting/order_person_list.html', {
            'document_type': Person._meta.get_field('document')
        })


def orders_person(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        number = request.GET.get('number', '')
        order_set = []
        if pk:
            person_obj = Person.objects.get(id=int(pk))
        elif number:
            person_set = Person.objects.filter(number=number)
            person_obj = person_set.first()
        order_set = Order.objects.filter(person=person_obj, type='V').order_by('number')

        tpl = loader.get_template('accounting/orders_person_grid.html')
        context = ({
            'order_set': order_set
        })
        return JsonResponse({
            'success': True,
            'number': person_obj.number,
            'names': person_obj.names,
            'grid': tpl.render(context, request),
        }, status=HTTPStatus.OK, content_type="application/json")


def are_all_products_returned(order_id):
    details = OrderDetail.objects.filter(order_id=order_id)
    outputs = details.filter(operation='S').values('product_id').annotate(total_salida=Sum('quantity'))
    inputs = details.filter(operation='E').values('product_id').annotate(total_entrada=Sum('quantity'))

    input_dict = {e['product_id']: e['total_entrada'] for e in inputs}

    for out in outputs:
        product_id = out['product_id']
        quantity_out = out['total_salida']
        quantity_in = input_dict.get(product_id, 0)

        if quantity_out < quantity_in:
            return False

    return True


def get_order_by_number(request):
    if request.method == 'GET':
        number = request.GET.get('order', '')
        if number:
            order_set = Order.objects.filter(number=int(number), type='V')
            check_quantity_product = are_all_products_returned(order_set.last().id)
            tpl = loader.get_template('accounting/orders_person_grid.html')
            context = ({
                'order_set': order_set,
                'check_quantity_product': check_quantity_product
            })
            if order_set.exists():
                return JsonResponse({
                    'success': True,
                    'grid': tpl.render(context, request),
                }, status=HTTPStatus.OK, content_type="application/json")
            else:
                return JsonResponse({
                    'success': False,
                    'grid': tpl.render(context, request),
                    'message': 'No existe ninguna orden'
                }, status=HTTPStatus.OK, content_type="application/json")


def modal_payment(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        if pk:
            user_id = request.user.id
            user_obj = User.objects.get(id=int(user_id))
            subsidiary_obj = user_obj.subsidiary
            my_date = datetime.datetime.now()
            date_now = my_date.strftime("%Y-%m-%d")
            order_obj = Order.objects.get(id=int(pk))
            payment_set = Payments.objects.filter(order=order_obj)
            casing_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj, type='C').values('id',
                                                                                                            'name')
            bank_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj, type='B').values('id',
                                                                                                          'name')
            tpl = loader.get_template('accounting/payment.html')
            context = ({
                'date_now': date_now,
                'order_obj': order_obj,
                'type_payment_set': Payments._meta.get_field('payment').choices,
                'casing_set': casing_set,
                'bank_set': bank_set,
                'document_set': Person._meta.get_field('document').choices,
                'payment_set': payment_set
            })
            return JsonResponse({
                'grid': tpl.render(context, request),
            }, status=HTTPStatus.OK, content_type="application/json")
        else:
            return JsonResponse({
                'success': False,
                'message': 'Orden desconocida',
            }, status=HTTPStatus.OK)


def modal_payment_show(request):
    if request.method == 'GET':
        n = request.GET.get('n', '')
        if n:
            user_id = request.user.id
            user_obj = User.objects.get(id=int(user_id))
            subsidiary_obj = user_obj.subsidiary
            my_date = datetime.datetime.now()
            date_now = my_date.strftime("%Y-%m-%d")
            order_set = Order.objects.filter(number=n, type='V')
            if order_set.exists():
                order_obj = order_set.first()
                payment_set = Payments.objects.filter(order=order_obj)
                casing_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj, type='C').values('id',
                                                                                                                'name')
                bank_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj, type='B').values('id',
                                                                                                              'name')
                tpl = loader.get_template('accounting/payment.html')
                context = ({
                    'date_now': date_now,
                    'order_obj': order_obj,
                    'type_payment_set': Payments._meta.get_field('payment').choices,
                    'casing_set': casing_set,
                    'bank_set': bank_set,
                    'document_set': Person._meta.get_field('document').choices,
                    'payment_set': payment_set
                })
                return JsonResponse({
                    'grid': tpl.render(context, request),
                }, status=HTTPStatus.OK, content_type="application/json")
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No se encontro ninguna orden con ese numero',
                }, status=HTTPStatus.OK)

        else:
            return JsonResponse({
                'success': False,
                'message': 'Orden desconocida',
            }, status=HTTPStatus.OK)


def cancel_recipe(request):
    if request.method == 'GET':
        order = request.GET.get('pk', '')
        # date = datetime.datetime.now()
        if order:
            order_obj = Order.objects.get(id=int(order))
            if order_obj.status == 'E' and order_obj.bill_enlace_pdf:
                # order_obj.status = 'A'
                # order_obj.save()
                # difference = date - timedelta(days=7)
                # date_seven = difference.date()
                # date_invoice = order_obj.bill_date.date()
                # if date_seven > date_invoice:
                nc = credit_note(order)
                if nc.get('numero'):
                    order_detail_set = order_obj.orderdetail_set.filter(is_state=True)
                    for d in order_detail_set:
                        d.is_state = False
                        d.save()
                        if order_obj.type == 'V':
                            new_order_detail = {
                                "operation": 'E',
                                "order": order_obj,
                                "product": d.product,
                                "quantity": decimal.Decimal(d.quantity),
                                "quantity_niu": decimal.Decimal(d.quantity_niu),
                                "price": decimal.Decimal(round(d.price, 6)),
                                "unit": d.unit,
                                "is_state": False,
                                "is_invoice": False
                            }
                            new_order_detail_obj = OrderDetail.objects.create(**new_order_detail)
                            new_order_detail_obj.save()
                            input_stock(order_detail_obj=new_order_detail_obj)
                        elif order_obj.type == 'C':
                            new_order_detail = {
                                "operation": 'S',
                                "order": order_obj,
                                "product": d.product,
                                "quantity": decimal.Decimal(d.quantity),
                                "quantity_niu": int(d.quantity_niu),
                                "price": decimal.Decimal(round(d.price, 6)),
                                "unit": d.unit,
                                "is_state": False,
                                "is_invoice": False
                            }
                            new_order_detail_obj = OrderDetail.objects.create(**new_order_detail)
                            new_order_detail_obj.save()
                            output_stock(order_detail_obj=new_order_detail_obj)
                    return JsonResponse({
                        'success': True,
                        'number': order_obj.id,
                        'message': 'Nota de credito generada',
                    }, status=HTTPStatus.OK)
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Codigo: ' + str(nc.get('codigo')) + 'Error: ' + str(nc.get('errors')),
                        'detail': nc.get('detail')
                    }, status=HTTPStatus.OK)
            elif order_obj.status == 'E' and order_obj.bill_qr and order_obj.condition == 'PA':
                nc = credit_note_pending(order)
                if nc.get('numero'):
                    return JsonResponse({
                        'success': True,
                        'number': order_obj.id,
                        'message': 'Nota de credito generada',
                    }, status=HTTPStatus.OK)
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Codigo: ' + str(nc.get('codigo')) + 'Error: ' + str(nc.get('errors')),
                        'detail': nc.get('detail')
                    }, status=HTTPStatus.OK)
                # else:
                #     a = cancelsunat(order)
                #     if a.get('numero'):
                #         order_detail_set = order_obj.orderdetail_set.filter(is_state=True)
                #         for d in order_detail_set:
                #             d.is_state = False
                #             d.save()
                #             if order_obj.type == 'V':
                #                 new_order_detail = {
                #                     "operation": 'E',
                #                     "order": order_obj,
                #                     "product": d.product,
                #                     "quantity": decimal.Decimal(d.quantity),
                #                     "quantity_niu": int(d.quantity_niu),
                #                     "price": decimal.Decimal(round(d.price, 6)),
                #                     "unit": d.unit,
                #                     "is_state": False,
                #                     "is_invoice": False
                #                 }
                #                 new_order_detail_obj = OrderDetail.objects.create(**new_order_detail)
                #                 new_order_detail_obj.save()
                #                 input_stock(order_detail_obj=new_order_detail_obj)
                #             elif order_obj.type == 'C':
                #                 new_order_detail = {
                #                     "operation": 'S',
                #                     "order": order_obj,
                #                     "product": d.product,
                #                     "quantity": decimal.Decimal(d.quantity),
                #                     "quantity_niu": int(d.quantity_niu),
                #                     "price": decimal.Decimal(round(d.price, 6)),
                #                     "unit": d.unit,
                #                     "is_state": False,
                #                     "is_invoice": False
                #                 }
                #                 new_order_detail_obj = OrderDetail.objects.create(**new_order_detail)
                #                 new_order_detail_obj.save()
                #                 output_stock(order_detail_obj=new_order_detail_obj)
                #         return JsonResponse({
                #             'success': True,
                #             'number': order_obj.number,
                #             'message': 'Comprobante Anulado',
                #         }, status=HTTPStatus.OK)
                #     else:
                #         return JsonResponse({
                #             'success': False,
                #             'message': 'Codigo: ' + str(a.get('codigo')) + 'Error: ' + str(a.get('errors')),
                #         }, status=HTTPStatus.OK)
            elif order_obj.status == 'R':
                order_obj.status = 'A'
                order_obj.bill_number = None
                order_obj.bill_serial = None
                order_obj.bill_qr = None
                order_obj.bill_date = None
                order_obj.bill_hash = None
                order_obj.bill_type = None
                order_obj.bill_status = None
                order_obj.bill_enlace_pdf = None
                order_obj.save()
                order_detail_set = order_obj.orderdetail_set.filter(is_state=True)
                for d in order_detail_set:
                    d.is_state = False
                    d.save()
                    if order_obj.type == 'V':
                        new_order_detail = {
                            "operation": 'E',
                            "order": order_obj,
                            "product": d.product,
                            "quantity": decimal.Decimal(d.quantity),
                            "quantity_niu": int(d.quantity_niu),
                            "price": decimal.Decimal(round(d.price, 6)),
                            "unit": d.unit,
                            "is_state": False,
                            "is_invoice": False
                        }
                        new_order_detail_obj = OrderDetail.objects.create(**new_order_detail)
                        new_order_detail_obj.save()
                        input_stock(order_detail_obj=new_order_detail_obj)
                    elif order_obj.type == 'C':
                        new_order_detail = {
                            "operation": 'S',
                            "order": order_obj,
                            "product": d.product,
                            "quantity": decimal.Decimal(d.quantity),
                            "quantity_niu": int(d.quantity_niu),
                            "price": decimal.Decimal(round(d.price, 6)),
                            "unit": d.unit,
                            "is_state": False,
                            "is_invoice": False
                        }
                        new_order_detail_obj = OrderDetail.objects.create(**new_order_detail)
                        new_order_detail_obj.save()
                        output_stock(order_detail_obj=new_order_detail_obj)
                return JsonResponse({
                    'success': True,
                    'number': order_obj.number,
                    'message': 'Orden anulado correctamente',
                }, status=HTTPStatus.OK)
            elif order_obj.status == 'A' or order_obj.status == 'N':
                return JsonResponse({
                    'success': True,
                    'number': order_obj.number,
                    'message': 'La orden se encuentra anulada',
                }, status=HTTPStatus.OK)
            else:
                return JsonResponse({
                    'success': False,
                    'number': order_obj.number,
                    'message': 'Ocurrio un problema',
                }, status=HTTPStatus.OK)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Orden sin identificar',
            }, status=HTTPStatus.OK)


def modal_credit_note(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        if pk:
            my_date = datetime.datetime.now()
            date_now = my_date.strftime("%Y-%m-%d")
            order_obj = Order.objects.get(id=int(pk))
            details = []
            details_all = order_obj.orderdetail_set.all()
            inputs = details_all.filter(operation='E').values('product_id').annotate(total_entrada=Sum('quantity'))
            outputs = details_all.filter(operation='S').values('product_id').annotate(total_salida=Sum('quantity'))
            input_dict = {e['product_id']: e['total_entrada'] for e in inputs}
            output_dict = {e['product_id']: e['total_salida'] for e in outputs}
            for d in order_obj.orderdetail_set.filter(operation='S'):
                product_id = d.product.id
                quantity_sold = output_dict.get(product_id, 0)
                quantity_returned = input_dict.get(product_id, 0)
                quantity_pending = quantity_sold - quantity_returned
                item = {
                    'id': d.id,
                    'operation': d.operation,
                    'quantity': d.quantity,
                    'quantity_pending': str(quantity_pending),
                    'quantity_niu': d.quantity_niu,
                    'quantity_remaining': d.quantity_remaining,
                    'price': d.price,
                    'unit': d.unit,
                    'product_id': d.product.id,
                    'product_name': d.product.name,
                    'product_code': d.product.code,
                    'product_width': d.product.width,
                    'product_length': d.product.length,
                    'product_height': d.product.height,
                    'amount': d.amount()
                }
                details.append(item)

            tpl = loader.get_template('accounting/modal_credit_note.html')
            context = ({
                'date_now': date_now,
                'order_obj': order_obj,
                'details': details,
            })
            dict_obj = model_to_dict(order_obj)
            serialized_obj = json.dumps(dict_obj, cls=DjangoJSONEncoder)
            serialized_detail_set = [{
                'detailID': detail.id,
                'productID': detail.product.id,
                'productName': detail.product.name,
                'productCode': detail.product.code,
                'price': float(detail.price),
                'quantitySold': float(detail.quantity),
                'quantityNiu': detail.quantity_niu,
                'unit': detail.unit,
                'isCreditNote': False,
                'quantityReturned': 0,
                'newSubtotal': 0,
            } for detail in order_obj.orderdetail_set.all()]
            return JsonResponse({
                'grid': tpl.render(context, request),
                'serialized_obj': serialized_obj,
                'serialized_detail_set': serialized_detail_set,
                'orderTotal': order_obj.total,
            }, status=HTTPStatus.OK, content_type="application/json")
        else:
            return JsonResponse({
                'success': False,
                'message': 'Orden desconocida',
            }, status=HTTPStatus.OK)


def cash_page(request):
    if request.method == 'GET':
        return render(request, 'accounting/cash_page.html', {
            'document_type': Person._meta.get_field('document'),
        })


def cash_order(request):
    if request.method == 'GET':
        n = request.GET.get('n', '')
        if n:
            user_id = request.user.id
            user_obj = User.objects.get(id=int(user_id))
            subsidiary_obj = user_obj.subsidiary
            my_date = datetime.datetime.now()
            date_now = my_date.strftime("%Y-%m-%d")
            order_set = Order.objects.filter(number=n, type='V')
            if order_set.exists():
                order_obj = order_set.first()
                order_detail_set = OrderDetail.objects.filter(order=order_obj, is_state=True)
                if order_detail_set.exists():
                    payment_set = Payments.objects.filter(order=order_obj)
                    casing_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj, type='C').values(
                        'id',
                        'name')
                    bank_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj, type='B').values('id',
                                                                                                                  'name')
                    tpl = loader.get_template('accounting/cash_page_grid.html')
                    context = ({
                        'date_now': date_now,
                        'order_obj': order_obj,
                        'type_payment_set': Payments._meta.get_field('payment').choices,

                        'bank_set': bank_set,
                        'document_set': Person._meta.get_field('document').choices,
                        'payment_set': payment_set,
                        'casing_set': casing_set,
                        'total_order': order_obj.invoice_total()
                    })
                    return JsonResponse({
                        'grid': tpl.render(context, request),
                    }, status=HTTPStatus.OK, content_type="application/json")
                else:
                    data = {'error': "No hay operaciones registradas"}
                    response = JsonResponse(data)
                    response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                    return response

            else:
                data = {'error': "No se encontro ninguna orden con ese numero"}
                response = JsonResponse(data)
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response
        else:
            return JsonResponse({
                'success': False,
                'message': 'Orden desconocida',
            }, status=HTTPStatus.OK)


def payments(request):
    if request.method == 'GET':
        user_id = request.user.id
        user_obj = User.objects.get(id=int(user_id))
        subsidiary_obj = user_obj.subsidiary
        my_date = datetime.datetime.now()
        date_now = my_date.strftime("%Y-%m-%d")
        casing_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj, type='C').values('id',
                                                                                                        'name')
        bank_set = Casing.objects.filter(is_enabled=True, subsidiary=subsidiary_obj, type='B').values('id',
                                                                                                      'name')

        user_dict = []
        user_set = User.objects.filter(type='V', is_active=True).order_by('id')
        for u in user_set:
            auth = 'No autorizado'
            if u.is_authorization:
                auth = 'Autorizado'
            user_item = {
                'user_id': u.id,
                'user_name': u.username.upper(),
                'auth': auth,
                'auth_boolean': u.is_authorization,
            }
            user_dict.append(user_item)

        return render(request, 'accounting/payments.html', {
            'date_now': date_now,
            'type_payment_set': Payments._meta.get_field('payment').choices,
            'casing_set': casing_set,
            'bank_set': bank_set,
            # 'user_set': User.objects.filter(type='V', is_active=True),
            'user_set': user_dict
        })


def search_order(request):
    if request.method == 'GET':
        order = request.GET.get('order', '')
        if order:
            order_set = Order.objects.filter(number=order, type='V')
            if order_set.exists():
                order_obj = order_set.first()
                if order_obj.status == 'A' or order_obj.status == 'D':
                    return JsonResponse({
                        'success': False,
                        'message': 'Orden Anulada, busquela en el Reporte de Ordenes',
                    }, status=HTTPStatus.OK)

                client = ''
                client_document = ''
                client_names = ''
                client_address = ''
                if order_obj.person:
                    person = order_obj.person
                    client = person.id
                    client_document = person.number
                    client_names = person.names
                    client_address = person.address
                payment_set = Payments.objects.filter(order=order_obj).order_by('id')
                payment = serializers.serialize('json', payment_set)
                detail_set = OrderDetail.objects.filter(order=order_obj, is_state=True).order_by('id')
                detail = []
                my_date = datetime.datetime.now()
                date_invoice = my_date.strftime("%Y-%m-%d")
                parent_order_total = ''
                parent_order_id = ''
                payment_order_parent_id = ''
                parent_order_number = ''
                difference = 0
                order_total = order_obj.sum_total()
                if order_obj.parent_order:
                    parent_order_obj = Order.objects.get(id=int(order_obj.parent_order.id))
                    if parent_order_obj.condition == 'A' or parent_order_obj.condition == 'PA':
                        parent_order_total = parent_order_obj.sum_total_annulled()
                    else:
                        parent_order_total = parent_order_obj.sum_total()
                    parent_order_id = parent_order_obj.id
                    parent_order_number = parent_order_obj.number
                    if Payments.objects.filter(order_id=parent_order_id).exists():
                        payment_order_parent_id = Payments.objects.filter(order_id=parent_order_id).last().id
                    difference = order_total - parent_order_total
                    # if parent_order_total > order_total:
                    #     difference = parent_order_total - order_total
                    # else:
                    #     difference = parent_order_total - order_total
                if order_obj.bill_date:
                    date_invoice = order_obj.bill_date.strftime("%Y-%m-%d")
                if detail_set.exists():
                    for d in detail_set:
                        det = {
                            'pk': d.id,
                            'name': d.product.name,
                            'unit': d.get_unit_display(),
                            'measure': d.product.measure(),
                            'quantity': d.quantity,
                            'price': d.price,
                            'amount': d.amount(),
                            'is_i': d.is_invoice
                        }
                        detail.append(det)
                    return JsonResponse({
                        'success': True,
                        'order': order_obj.id,
                        'doc': order_obj.doc,
                        'date': date_invoice,
                        'paid': order_obj.paid,
                        'invoice': order_obj.invoice_total(),
                        'd': detail,
                        'p': payment,
                        'c': client,
                        'document': client_document,
                        'names': client_names,
                        'address': client_address,
                        'total': order_obj.total,
                        'user': order_obj.user.first_name.upper(),
                        # 'parent_order_obj': model_to_dict(parent_order_obj)
                        'parent_order_total': parent_order_total,
                        'parent_order_id': parent_order_id,
                        'parent_order_number': parent_order_number,
                        'payment_order_parent_id': payment_order_parent_id,
                        'difference': difference
                    }, status=HTTPStatus.OK)
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Orden no encontrada',
                    }, status=HTTPStatus.OK)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No se encontro ninguna orden con ese numero',
                }, status=HTTPStatus.OK)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Ingrese un numero valido',
            }, status=HTTPStatus.OK)


def delete_payment(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        if pk:
            payment_obj = Payments.objects.get(id=int(pk))
            payment_obj.delete()

            return JsonResponse({
                'success': True,
                'message': 'Pago eliminado correctamente',
            }, status=HTTPStatus.OK)
        else:
            return JsonResponse({
                'success': False,
                'message': 'No se logro indetificar el detalle',
            }, status=HTTPStatus.OK)


def close_casing(request):
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        my_date = datetime.datetime.now().strftime("%Y-%m-%d")
        t = loader.get_template('accounting/modal_casing.html')
        c = ({
            'my_date': my_date
        })
        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
        })


def get_users_by_date(request):
    if request.method == 'GET':
        init = request.GET.get('init', '')
        end = request.GET.get('end', '')
        total_s = decimal.Decimal(0.0000)
        t_f = decimal.Decimal(0.00)
        t_b = decimal.Decimal(0.00)
        t_t = decimal.Decimal(0.00)
        t_p = decimal.Decimal(0.00)
        t_n = decimal.Decimal(0.00)
        user_dic = []
        if init and end:
            user_set = User.objects.filter(type__in=['V', 'C', 'A'], is_active=True)
            order_set = Order.objects.filter(create_at__range=(init, end), type='V', condition='R').exclude(status__in=['A', 'PA'])
            total_s = order_set.aggregate(r=Coalesce(Sum('total'), decimal.Decimal('0'))).get('r')
            # total_without_note = order_set.aggregate(r=Coalesce(Sum(F('total') - Coalesce(F('note_total'), decimal.Decimal('0'))), decimal.Decimal('0'))).get('r')
            total_f = order_set.filter(doc='1', payments__isnull=False).distinct('id').values('id', 'total')
            # total_f = order_set.filter(doc='1', payments__isnull=False).distinct('id').values('id', total_rest=F(
            #     'total') - Coalesce(F('note_total'), decimal.Decimal('0')))
            for i in total_f:
                # t_f += decimal.Decimal(i['total_rest'])
                t_f += decimal.Decimal(i['total'])
            total_b = order_set.filter(doc='2', payments__isnull=False).distinct('id').values('id', 'total')
            # total_b = order_set.filter(doc='2', payments__isnull=False).distinct('id').values('id', total_rest=F(
            #     'total') - Coalesce(F('note_total'), decimal.Decimal('0')))
            for i in total_b:
                t_b += decimal.Decimal(i['total'])
                # t_b += decimal.Decimal(i['total_rest'])
            total_t = order_set.filter(doc='0', payments__isnull=False).distinct('id').values('id', 'total')
            for i in total_t:
                t_t += decimal.Decimal(i['total'])
            total_p = order_set.filter(payments__isnull=True).distinct('id').values('id', 'total')
            for i in total_p:
                t_p += decimal.Decimal(i['total'])
            total_n = order_set.filter(doc__in=['1', '2'], status='N', payments__isnull=False).distinct('id').values('id', 'total')
            for i in total_n:
                t_n += decimal.Decimal(i['total'])

            total_cancel = Order.objects.filter(create_at__range=(init, end), type='V', status__in=['A', 'PA']).aggregate(r=Coalesce(Sum('total'), decimal.Decimal('0'))).get('r')

            for u in user_set:
                o = order_set.filter(user=u, payments__isnull=False).distinct()
                quantity = o.count()
                # total = o.aggregate(r=Coalesce(Sum('total'), decimal.Decimal('0'))).get('r')
                total = o.aggregate(r=Coalesce(Sum(F('total') - Coalesce(F('note_total'), decimal.Decimal('0'))),
                                               decimal.Decimal('0'))).get('r')
                dic = {
                    'pk': u.id,
                    'username': u.first_name,
                    'quantity': quantity,
                    'total': '{:,}'.format(round(decimal.Decimal(round(total, 4)), 2)),
                }
                user_dic.append(dic)

            tpl = loader.get_template('accounting/users_grid_list.html')
            context = ({
                'user_dic': user_dic,
                'total_s': '{:,}'.format(round(decimal.Decimal(total_s - t_p - t_n), 2)),
                'total_f': '{:,}'.format(round(decimal.Decimal(t_f), 2)),
                'total_b': '{:,}'.format(round(decimal.Decimal(t_b), 2)),
                'total_t': '{:,}'.format(round(decimal.Decimal(t_t), 2)),
                'total_p': '{:,}'.format(round(decimal.Decimal(t_p), 2)),
                'total_n': '{:,}'.format(round(decimal.Decimal(t_n), 2)),
                'total_cancel': '{:,}'.format(round(decimal.Decimal(total_cancel), 2)),
            })
            return JsonResponse({
                'grid': tpl.render(context, request),
            }, status=HTTPStatus.OK, content_type="application/json")


def get_orders_by_user(request):
    if request.method == 'GET':
        u = request.GET.get('u', '')
        init = request.GET.get('init', '')
        end = request.GET.get('end', '')
        if u:
            user_obj = User.objects.get(id=int(u))
            order_set = Order.objects.filter(user=user_obj, create_at__range=(init, end), type='V').order_by('number')
            tpl = loader.get_template('accounting/orders_user_grid_list.html')
            context = ({
                'order_set': order_set
            })
            return JsonResponse({
                'grid': tpl.render(context, request),
            }, status=HTTPStatus.OK, content_type="application/json")


def casing_report(request):
    if request.method == 'GET':
        my_date = datetime.datetime.now().strftime("%Y-%m-%d")
        t = loader.get_template('accounting/cash_report.html')
        c = ({
            'my_date': my_date
        })
        return JsonResponse({
            'success': True,
            'form': t.render(c, request),
        })


@csrf_exempt
def get_order_list(request):
    if request.method == 'POST':
        r = request.POST.get('rd', '')
        init = request.POST.get('date-init', '')
        end = request.POST.get('date-end', '')
        if r == '0':
            order_set = Order.objects.filter(create_at__range=(init, end), type='V')
        elif r == '1':
            order_set = Order.objects.filter(create_at__range=(init, end), type='V', doc='1',
                                             payments__isnull=False).distinct('id')
        elif r == '2':
            order_set = Order.objects.filter(create_at__range=(init, end), type='V', doc='2',
                                             payments__isnull=False).distinct('id')
        elif r == '3':
            order_set = Order.objects.filter(create_at__range=(init, end), type='V', doc='0',
                                             payments__isnull=False).distinct('id')
        elif r == '4':
            order_set = Order.objects.filter(create_at__range=(init, end), type='V', payments__isnull=True).distinct(
                'id')
        else:
            order_set = []
        t = decimal.Decimal(0.00)
        if order_set.exists():
            # total = order_set.aggregate(r=Coalesce(Sum('total'), 0)).get('r')
            # t_p = decimal.Decimal(0.00)
            for i in order_set.values('id', 'total'):
                t += decimal.Decimal(i['total'])
            # for i in order_set.values('id', 'total'):
            #     t += decimal.Decimal(i['total'])
            order_set = order_set.order_by('id')
        tpl = loader.get_template('accounting/table_order.html')
        context = ({
            'order_set': order_set,
            'total': round(t, 4),
        })
        return JsonResponse({
            'success': True,
            'grid': tpl.render(context, request),
        }, status=HTTPStatus.OK, content_type="application/json")


def get_order_detail(request):
    if request.method == 'GET':
        o = request.GET.get('o', '')
        if o:
            order_obj = Order.objects.get(id=int(o))
            detail_set = OrderDetail.objects.filter(order=order_obj, is_state=True)
            tpl = loader.get_template('accounting/table_order_detail.html')
            context = ({
                'detail_set': detail_set
            })
            return JsonResponse({
                'grid': tpl.render(context, request),
            }, status=HTTPStatus.OK, content_type="application/json")


def invoice_issued(request):
    if request.method == 'GET':
        date_time = datetime.datetime.now()
        date = date_time.date()
        order_set = Order.objects.filter(create_at=date, type='V', doc='0',
                                         payments__isnull=False).distinct('id', 'number').order_by('number')
        order_set_total = Order.objects.filter(create_at=date, type='V', payments__isnull=False).distinct('id',
                                                                                                          'number').order_by(
            'number')
        total_t = order_set_total.values('id', 'total')
        t_t = decimal.Decimal(0.00)
        for i in total_t:
            t_t += decimal.Decimal(i['total'])
        return render(request, 'accounting/invoice_issued.html', {
            'order_set': order_set.order_by('-id'),
            'date': date,
            't_t': t_t
        })


def get_order_type(request):
    if request.method == 'GET':
        v = request.GET.get('v', '')
        init = request.GET.get('init', '')
        end = request.GET.get('end', '')
        all_orders = []
        if init and end:
            if v == '0':  # TICKETS
                order_set = Order.objects.filter(create_at__range=(init, end),
                                                 type='V', doc='0',
                                                 payments__isnull=False).select_related('user', 'person',
                                                                                        'subsidiary').prefetch_related(
                    Prefetch(
                        'payments_set', queryset=Payments.objects.select_related('casing')
                    )
                )

            elif v == '1':  # FACTURAS
                order_set = Order.objects.filter(create_at__range=(init, end), type='V', doc='1',
                                                 payments__isnull=False).distinct('id')
            elif v == '2':  # BOLETAS
                order_set = Order.objects.filter(create_at__range=(init, end), type='V', doc='2',
                                                 payments__isnull=False).distinct('id')
            elif v == '3':  # PENDIENTES
                order_set = Order.objects.filter(create_at__range=(init, end), type='V',
                                                 payments__isnull=True).distinct('id')
            elif v == '4':  # TODOS
                order_set = Order.objects.filter(create_at__range=(init, end), type='V').order_by('-number')

                for order in order_set:
                    if order.condition in ['PA', 'A']:
                        condition = 'ANULADA'
                    else:
                        if order.status == 'N':
                            condition = 'EMITIDO'
                        else:
                            condition = order.get_status_display()

                    order_data = {
                        'id': order.id,
                        'type': order.type,
                        'number': order.number,
                        'doc_display': order.get_doc_display(),
                        'bill_serial': order.bill_serial or '',
                        'bill_number': order.bill_number or '',
                        'condition': condition,
                        'create_at': order.create_at.strftime('%d-%m-%Y'),
                        'payment_display': order.payments_set.first().get_payment_display() if order.payments_set.exists() else '',
                        'person_names': order.person.names if order.person else '',
                        'total': str(order.total),
                    }
                    all_orders.append(order_data)

                    if order.doc == '1' and order.status == 'N':
                        order_data_status_n = order_data.copy()
                        order_data_status_n['doc_display'] = 'NOTA DE CREDITO'
                        order_data_status_n['total'] = f"-{order.total}"
                        order_data_status_n['note_serial'] = order.note_serial
                        order_data_status_n['note_number'] = str(order.note_number).zfill(4)
                        order_data_status_n['bill_serial'] = ''
                        order_data_status_n['bill_number'] = ''
                        order_data_status_n['condition'] = 'NOTA DE CREDITO'
                        all_orders.append(order_data_status_n)

            elif v == '5':  # COTIZACIONES
                order_set = Order.objects.filter(create_at__range=(init, end), type='T').order_by('number')
            else:
                order_set = []
            tpl = loader.get_template('accounting/invoice_issued_grid.html')
            context = ({
                'order_set': order_set.order_by('id'),
                'orders_dict': all_orders,
                'type_search': v
            })
            return JsonResponse({
                'grid': tpl.render(context, request),
            }, status=HTTPStatus.OK, content_type="application/json")


def get_type_change(request):
    if request.method == 'GET':
        date = request.GET.get('date', '')
        # mydate = datetime.datetime.now()
        # formatdate = mydate.strftime("%Y-%m-%d")
        money_change_set = MoneyChange.objects.filter(search_date=date)

        if money_change_set.exists():
            money_change_obj = money_change_set.first()
            sell = money_change_obj.sell
            buy = money_change_obj.buy
            money = 'USD'

            return JsonResponse({'sales': sell, 'money': money},
                                status=HTTPStatus.OK)
        else:
            r = query_apis_net_money(date)

            if r.get('fecha_busqueda') == date:
                sell = round(r.get('venta'), 3)
                buy = round(r.get('compra'), 3)
                money = r.get('moneda')
                search_date = r.get('fecha_busqueda')
                sunat_date = r.get('fecha_sunat')

                money_change_obj = MoneyChange(
                    search_date=search_date,
                    sunat_date=sunat_date,
                    sell=sell,
                    buy=buy
                )
                money_change_obj.save()

            else:
                data = {'error': 'NO EXISTE TIPO DE CAMBIO'}
                response = JsonResponse(data)
                response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                return response

        return JsonResponse({'sales': sell, 'money': money},
                            status=HTTPStatus.OK)

    return JsonResponse({'message': 'Error de peticion.'}, status=HTTPStatus.BAD_REQUEST)


@csrf_exempt
def save_credit_note(request):
    if request.method == 'POST':
        order = request.POST.get('id-order', '')
        motive = request.POST.get('motive-credit-note', '')
        if order:
            order_obj = Order.objects.get(id=int(order))
            details = request.POST.get('details', '')
            details_data = json.loads(details)
            if order_obj.status == 'E' and order_obj.bill_enlace_pdf:
                # nc = credit_note_by_parts(order, details_data)
                nc = send_credit_note_fact(order, details_data, motive)
                if nc.get('numero'):
                    # nc = 'nc'
                    # if nc:
                    for d in details_data:
                        if d['quantityReturned']:

                            detail_id = d['detailID']
                            detail_order_obj = OrderDetail.objects.get(id=int(detail_id))
                            detail_order_obj.is_state = False
                            detail_order_obj.save()

                            quantity_returned = decimal.Decimal(d['quantityReturned'])
                            product_id = int(d['productID'])
                            quantity_purchased = decimal.Decimal(d['quantitySold'])
                            unit = str(d['unit'])
                            quantity_niu = decimal.Decimal(d['quantityNiu'])
                            price = decimal.Decimal(d['price'])
                            # is_credit_note = bool(d['isCreditNote'])
                            units = decimal.Decimal(quantity_returned)
                            if unit == 'KGM':
                                quantity_minimum = quantity_niu / quantity_purchased
                                units = round(decimal.Decimal(quantity_returned) * decimal.Decimal(quantity_minimum), 4)

                            product_obj = Product.objects.get(id=product_id)
                            order_detail_obj = OrderDetail(
                                operation='E',
                                order=order_obj,
                                product=product_obj,
                                quantity=quantity_returned,
                                quantity_niu=int(units),
                                price=price,
                                unit=unit,
                                is_state=False,
                                is_invoice=False
                            )
                            order_detail_obj.save()
                            kardex_set = Kardex.objects.filter(product=order_detail_obj.product)
                            input_stock(order_detail_obj)
                            # if kardex_set.exists():
                            #     kardex_input(product=order_detail_obj.product, quantity=order_detail_obj.quantity,
                            #                  total_cost=order_detail_obj.amount(), order_detail_obj=order_detail_obj,
                            #                  type_document='07', type_operation='06')

                    return JsonResponse({
                        'success': True,
                        'number': order_obj.number,
                        'enlace': nc.get('enlace_del_pdf'),
                        'message': 'Nota de credito generada',
                    }, status=HTTPStatus.OK)
                    # if order_obj.type == 'V':
                    #     new_order_detail = {
                    #         "operation": 'E',
                    #         "order": order_obj,
                    #         "product": d.product,
                    #         "quantity": decimal.Decimal(d.quantity),
                    #         "quantity_niu": decimal.Decimal(d.quantity_niu),
                    #         "price": decimal.Decimal(round(d.price, 6)),
                    #         "unit": d.unit,
                    #         "is_state": False,
                    #         "is_invoice": False
                    #     }
                    #     new_order_detail_obj = OrderDetail.objects.create(**new_order_detail)
                    #     new_order_detail_obj.save()
                    #     input_stock(order_detail_obj=new_order_detail_obj)
            else:
                return JsonResponse({
                    'success': False,
                    'number': order_obj.number,
                    'message': 'Orden sin comprobante electronico',
                }, status=HTTPStatus.OK)


def deposit_report(request):
    if request.method == 'GET':
        date_time = datetime.datetime.now()
        date = date_time.date()
        return render(request, 'accounting/deposit_report.html', {
            'date': date,
        })


def get_report_deposit(request):
    if request.method == 'GET':
        v = request.GET.get('v', '')
        init = request.GET.get('init', '')
        end = request.GET.get('end', '')

        payment_set = Payments.objects.filter(payment='D', order__create_at__range=(init, end), order__type='V',
                                              order__doc__in=['0', '1', '2']).exclude(
            order__status__in=['A', 'PA']).distinct('id')
        # order_set = Order.objects.filter(create_at__range=(init, end), type='V', doc='0',
        #                                  payments__isnull=False).distinct('id')

        tpl = loader.get_template('accounting/deposit_report_grid.html')
        context = ({
            'payment_set': payment_set.order_by('-id')
        })
        return JsonResponse({
            'grid': tpl.render(context, request),
        }, status=HTTPStatus.OK, content_type="application/json")
