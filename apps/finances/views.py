import decimal
import json
from http import HTTPStatus

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader
from datetime import datetime, timedelta
import datetime

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from apps import accounting
from apps.accounting.api_FACT import send_guide_return_fact
from apps.accounting.sunat import send_guide, send_guide_return
from apps.hrm.models import Person
from apps.sales.models import Order, OrderDetail, Product, Presentation
from apps.sales.views import output_stock, input_stock


def orders_supplier_list(request):
    if request.method == 'GET':
        date_time = datetime.datetime.now()
        date = date_time.date()
        supplier_set = Person.objects.filter(type='P')
        return render(request, 'finances/order_supplier_list.html', {
            'date': date,
            'supplier_set': supplier_set,
        })


def get_quantity_returned_by_guide(guide_id, product_id):
    quantity_returned = ''
    detail_set = OrderDetail.objects.filter(order_id=guide_id, product_id=product_id)
    if detail_set.exists():
        detail_obj = detail_set.last()
        quantity_returned = detail_obj.quantity
    return quantity_returned


def get_order_purchased_by_id(request):
    if request.method == 'GET':
        order_id = request.GET.get('orderID', '')
        order_obj = Order.objects.get(id=int(order_id))
        guide_id = order_obj.order_set.last().id
        guide_obj = Order.objects.get(id=int(guide_id))
        date_time = datetime.datetime.now()
        date = date_time.date()

        detail_dict = []
        for d in order_obj.orderdetail_set.all():
            item = {
                'id': d.id,
                'product_id': d.product.id,
                'product_code': d.product.code,
                'product_name': d.product.name,
                'product_with': d.product.width,
                'product_length': d.product.length,
                'product_height': d.product.height,
                'unit': d.unit,
                'price': d.price,
                'quantity': d.quantity,
                'quantity_niu': d.quantity_niu,
                'quantity_purchased': d.quantity,
                'quantity_returned': get_quantity_returned_by_guide(guide_id, d.product.id),
                'amount': d.amount
            }
            detail_dict.append(item)

        tpl = loader.get_template('finances/order_detail_form.html')
        context = ({
            'order_obj': order_obj,
            'guide_id': guide_id,
            'guide_obj': guide_obj,
            'detail_dict': detail_dict,
            'date': date,
        })
        # serialized_obj = serializers.serialize('json', [order_obj, ])
        dict_obj = model_to_dict(order_obj)
        serialized_obj = json.dumps(dict_obj, cls=DjangoJSONEncoder)
        # serialized_detail_set = serializers.serialize('json', order_obj.orderdetail_set.all())
        serialized_detail_set = [{
            'detailID': detail.id,
            'productID': detail.product.id,
            'productName': detail.product.name,
            'productCode': detail.product.code,
            'price': float(detail.price),
            'quantityPurchased': float(detail.quantity),
            'quantityNiu': detail.quantity_niu,
            'unit': detail.unit,
            'isCreditNote': False,
            'quantityReturned': 0,
            'newSubtotal': 0,
        } for detail in order_obj.orderdetail_set.all()]

        return JsonResponse({
            'form': tpl.render(context, request),
            # 'serialized_obj': serialized_obj,
            'serialized_obj': serialized_obj,
            # 'serialized_detail_set': json.loads(serialized_detail_set),
            'serialized_detail_set': serialized_detail_set,
            'orderTotal': order_obj.get_purchase_total(),
            'date': date.strftime("%Y-%m-%d"),
        }, status=HTTPStatus.OK, content_type="application/json")


def get_orders_purchased(request):
    if request.method == 'GET':
        supplier_id = request.GET.get('supplier', '')
        init = request.GET.get('init', '')
        end = request.GET.get('end', '')
        # print('supplier_id', supplier_id)

        order_set = Order.objects.filter(create_at__range=(init, end), type='C', doc='1',
                                         person__id=(supplier_id)).distinct('id')

        tpl = loader.get_template('finances/order_supplier_grid.html')
        context = ({
            'order_set': order_set.order_by('-id')
        })
        return JsonResponse({
            'grid': tpl.render(context, request),
        }, status=HTTPStatus.OK, content_type="application/json")


def credit_note_supplier_save(request):
    if request.method == 'POST':
        credit_note_json = request.POST.get('creditNote', '')
        guide_id = request.POST.get('guideID', '')
        data = json.loads(credit_note_json)
        credit_note_invoice_number = data['creditNoteInvoiceNumber']
        credit_note_date_document = data['creditNoteDateDocument']
        credit_note_invoice_date = data['creditNoteInvoiceDate']
        credit_note_date = data['creditNoteDate']
        # new_total = data['newTotal']
        # new_igv = data['newIgv']
        # new_base = data['newBase']

        guide_obj = Order.objects.get(id=int(guide_id))
        purchase_obj = Order.objects.get(id=int(data['id']))

        guide_obj.status = 'N'
        guide_obj.doc = '3'
        guide_obj.user = request.user
        guide_obj.invoice_number = credit_note_invoice_number
        guide_obj.date_document = credit_note_date_document
        guide_obj.invoice_date = credit_note_invoice_date
        guide_obj.note_date = credit_note_date
        guide_obj.save()

        purchase_obj.status = 'N'
        purchase_obj.save()

        # credit_note_obj = Order(
        #     type=purchase_obj.type,
        #     status="N",
        #     doc='3',
        #     # total=decimal.Decimal(new_total),
        #     coin=purchase_obj.coin,
        #     change=purchase_obj.change,
        #     create_at=datetime.datetime.now().date(),
        #     user=request.user,
        #     person=purchase_obj.person,
        #     subsidiary=purchase_obj.subsidiary,
        #     is_igv=purchase_obj.is_igv,
        #     invoice_number=credit_note_invoice_number,
        #     date_document=credit_note_date_document,
        #     invoice_date=credit_note_invoice_date,
        #     note_date=credit_note_date,
        #     parent_order=purchase_obj
        # )
        # credit_note_obj.save()

        # for d in data['details']:
        #     detail_id = int(d['detailID'])
        #     product_id = int(d['productID'])
        #     quantity_purchased = decimal.Decimal(d['quantityPurchased'])
        #     quantity_returned = decimal.Decimal(d['quantityReturned'])
        #     quantity_niu = decimal.Decimal(d['quantityNiu'])
        #     price = decimal.Decimal(d['price'])
        #     is_credit_note = bool(d['isCreditNote'])
        #     unit = str(d['unit'])
        #
        #     units = decimal.Decimal(quantity_returned)
        #     if unit == 'KGM':
        #         quantity_minimum = quantity_niu / quantity_purchased
        #         units = round(decimal.Decimal(quantity_returned) * decimal.Decimal(quantity_minimum), 4)
        #     if is_credit_note:
        #         product_obj = Product.objects.get(id=product_id)
        #         order_detail_obj = OrderDetail(
        #             operation='S',
        #             order=credit_note_obj,
        #             product=product_obj,
        #             quantity=quantity_returned,
        #             quantity_niu=int(units),
        #             price=price,
        #             unit=unit,
        #             is_state=True,
        #             is_invoice=False
        #         )
        #         order_detail_obj.save()
        #         output_stock(order_detail_obj)

        # purchase_obj.status = 'N'
        # purchase_obj.save()

        return JsonResponse({
            'success': True,
            'message': 'Proceso realizado Codigo'
        }, status=HTTPStatus.OK)

    return JsonResponse({'message': 'Error de peticion.'}, status=HTTPStatus.BAD_REQUEST)


def credit_note_supplier_review(request):
    if request.method == 'GET':
        credit_note_id = request.GET.get('creditNoteID', '')
        credit_note_obj = Order.objects.get(id=int(credit_note_id))
        date_time = datetime.datetime.now()
        date = date_time.date()
        tpl = loader.get_template('finances/credit_note_detail_form.html')
        context = ({
            'credit_note_obj': credit_note_obj,
            'date': date,
        })

        return JsonResponse({
            'form': tpl.render(context, request),
            'creditNoteID': credit_note_obj.id,
            'creditNoteTotal': credit_note_obj.get_purchase_total(),
            'creditNoteIsIgv': credit_note_obj.is_igv,
            'date': date.strftime("%Y-%m-%d"),
        }, status=HTTPStatus.OK, content_type="application/json")


def annul_credit_note_by_id(request):
    if request.method == 'POST':
        credit_note_id = request.POST.get('creditNoteID', '')
        credit_note_obj = Order.objects.get(id=int(credit_note_id))
        credit_note_obj.status = 'A'
        credit_note_obj.save()
        for d in credit_note_obj.orderdetail_set.all():
            input_stock(d)
        return JsonResponse({
            'message': 'Proceso realizado'
        }, status=HTTPStatus.OK, content_type="application/json")
    return JsonResponse({'message': 'Error de peticion.'}, status=HTTPStatus.BAD_REQUEST)


def purchase_review(request):
    if request.method == 'GET':
        purchase_id = request.GET.get('purchaseID', '')
        purchase_obj = Order.objects.get(id=int(purchase_id))
        date_time = datetime.datetime.now()
        date = date_time.date()
        tpl = loader.get_template('finances/purchase_detail_form.html')
        context = ({
            'purchase_obj': purchase_obj,
            'date': date,
        })

        return JsonResponse({
            'form': tpl.render(context, request),
            'purchaseTotal': purchase_obj.get_purchase_total(),
            'purchaseIsIgv': purchase_obj.is_igv,
            'date': date.strftime("%Y-%m-%d"),
        }, status=HTTPStatus.OK, content_type="application/json")


def modal_guide(request):
    if request.method == 'GET':
        order_id = request.GET.get('pk', '')
        if order_id:
            order_obj = Order.objects.get(id=int(order_id))
            date_time = datetime.datetime.now()
            date = date_time.date()
            tpl = loader.get_template('finances/guide_return_supplier.html')
            c = ({
                'order_obj': order_obj,
                'date_now': date.strftime("%Y-%m-%d"),
                'guide_motive_set': Order._meta.get_field('guide_motive').choices,
                'guide_modality_set': Order._meta.get_field('guide_modality_transport').choices
            })
            dict_obj = model_to_dict(order_obj)
            serialized_obj = json.dumps(dict_obj, cls=DjangoJSONEncoder)
            serialized_detail_set = [{
                'detailID': detail.id,
                'productID': detail.product.id,
                'productName': detail.product.name,
                'productCode': detail.product.code,
                'price': float(detail.price),
                'quantityPurchased': float(detail.quantity),
                'quantityNiu': detail.quantity_niu,
                'unit': detail.unit,
                'isCreditNote': False,
                'quantityReturned': 0,
                'newSubtotal': 0,
            } for detail in order_obj.orderdetail_set.all()]
            return JsonResponse({
                'form': tpl.render(c, request),
                'serialized_obj': serialized_obj,
                'serialized_detail_set': serialized_detail_set,
                'orderTotal': order_obj.get_purchase_total(),
                'date': date.strftime("%Y-%m-%d"),
            }, status=HTTPStatus.OK, content_type="application/json")


@csrf_exempt
def guide_return_save(request):
    if request.method == 'POST':
        order = request.POST.get('id-order', '')
        if order:
            purchase_obj = Order.objects.get(id=int(order))

            details = request.POST.get('details', '')
            details_data = json.loads(details)

            # description = 'FACTURA ELECTRONICA: ' + str(purchase_obj.invoice_number)

            date_issue = request.POST.get('issue', '')
            date_transfer = request.POST.get('transfer', '')

            motive = request.POST.get('motive', '')
            truck = request.POST.get('truck', '')

            driver_name = request.POST.get('driver-names', '')
            driver_last_name = request.POST.get('driver-lastname', '')

            driver_dni = request.POST.get('driver-dni', '')
            driver_license = request.POST.get('driver-license', '')

            guide_carrier_document = request.POST.get('guide_carrier_document', '')
            guide_carrier_names = request.POST.get('guide_carrier_names', '')

            guide_origin_address = request.POST.get('subsidiary-address', '')
            guide_destiny_address = request.POST.get('person-address', '')

            origin = request.POST.get('origin', '')
            modality_transport = request.POST.get('modality_transport', '')
            destiny = request.POST.get('destiny', '')
            weight = request.POST.get('weight', 0)
            lumps = request.POST.get('lumps', 0)

            new_total = request.POST.get('new-total', 0)

            # if request.POST.get('observation', '') != '':
            #     description = str(request.POST.get('observation', '')) + '\n' + description

            description = str(request.POST.get('observation', ''))

            subsidiary_obj = purchase_obj.subsidiary
            serial = 'T0' + str(subsidiary_obj.serial)
            correlative = accounting.views.number_guide(subsidiary=subsidiary_obj, document='G')

            guide_obj = Order(
                type=purchase_obj.type,
                status='G',
                doc='5',
                total=decimal.Decimal(new_total),
                coin=purchase_obj.coin,
                change=purchase_obj.change,
                create_at=datetime.datetime.now().date(),
                user=request.user,
                person=purchase_obj.person,
                subsidiary=purchase_obj.subsidiary,
                is_igv=purchase_obj.is_igv,

                guide_serial=serial,
                add='G',
                guide_description=description,
                guide_type=7,
                guide_number=correlative,
                guide_date=date_issue,
                guide_transfer=date_transfer,
                guide_motive=motive,
                guide_truck=truck,
                guide_driver_name=driver_name,
                guide_driver_lastname=driver_last_name,
                guide_driver_full_name=driver_name + ' ' + driver_last_name,
                guide_driver_dni=driver_dni,
                guide_driver_license=driver_license,
                guide_origin=origin,
                guide_destiny=destiny,
                guide_carrier_document=guide_carrier_document,
                guide_modality_transport=modality_transport,
                guide_carrier_names=guide_carrier_names,
                guide_origin_address=guide_origin_address,
                guide_destiny_address=guide_destiny_address,
                guide_weight=decimal.Decimal(weight),
                guide_package=decimal.Decimal(lumps),

                parent_order=purchase_obj
            )
            guide_obj.save()

            for d in details_data:
                # detail_id = int(d['detailID'])
                if d['quantityReturned']:
                    quantity_returned = decimal.Decimal(d['quantityReturned'])
                    product_id = int(d['productID'])
                    quantity_purchased = decimal.Decimal(d['quantityPurchased'])
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
                        operation='S',
                        order=guide_obj,
                        product=product_obj,
                        quantity=quantity_returned,
                        quantity_niu=int(units),
                        price=price,
                        unit=unit,
                        is_state=True,
                        is_invoice=True
                    )
                    order_detail_obj.save()
                    output_stock(order_detail_obj)

            # order_obj.guide_serial = serial
            # order_obj.add = 'G'
            # order_obj.guide_description = description
            # order_obj.guide_type = 7
            # order_obj.guide_number = correlative
            # order_obj.guide_date = date_issue
            # order_obj.guide_transfer = date_transfer
            # order_obj.guide_motive = motive
            # order_obj.guide_truck = truck
            # order_obj.guide_driver_name = driver_name
            # order_obj.guide_driver_lastname = driver_last_name
            # order_obj.guide_driver_full_name = driver_name + ' ' + driver_last_name
            # order_obj.guide_driver_dni = driver_dni
            # order_obj.guide_driver_license = driver_license
            # order_obj.guide_origin = origin
            # order_obj.guide_destiny = destiny
            # order_obj.guide_carrier_document = guide_carrier_document
            # order_obj.guide_modality_transport = modality_transport
            # order_obj.guide_carrier_names = guide_carrier_names
            #
            # order_obj.guide_origin_address = guide_origin_address
            # order_obj.guide_destiny_address = guide_destiny_address

            # if weight:
            #     order_obj.guide_weight = decimal.Decimal(weight)
            # if lumps:
            #     order_obj.guide_package = decimal.Decimal(lumps)
            # order_obj.save()

            # r = send_guide_return(guide_obj.id)
            r = send_guide_return_fact(guide_obj.id)
            if r.get('success'):
                purchase_obj.status = 'G'
                purchase_obj.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Guia generada Correctamente',
                    'pk': guide_obj.id
                }, status=HTTPStatus.OK)
            else:
                objects_to_delete = OrderDetail.objects.filter(order=guide_obj)
                objects_to_delete.delete()
                guide_obj.delete()
                # order_obj.guide_serial = '-'
                # order_obj.add = 'N'
                # order_obj.guide_description = '-'
                # order_obj.guide_type = ''
                # order_obj.guide_number = None
                # order_obj.guide_date = None
                # order_obj.guide_transfer = None
                # order_obj.guide_motive = '01'
                # order_obj.guide_truck = ''
                # order_obj.guide_driver_name = ''
                # order_obj.guide_driver_lastname = ''
                # order_obj.guide_driver_full_name = ''
                # order_obj.guide_driver_dni = ''
                # order_obj.guide_driver_license = ''
                # order_obj.guide_origin = ''
                # order_obj.guide_destiny = ''
                # order_obj.guide_carrier_document = ''
                # order_obj.guide_modality_transport = '1'
                # order_obj.guide_carrier_names = ''
                # order_obj.guide_origin_address = ''
                # order_obj.guide_destiny_address = ''
                # order_obj.guide_weight = decimal.Decimal(0.0000)
                # order_obj.guide_package = decimal.Decimal(0.0000)
                # order_obj.save()
                return JsonResponse({
                    'success': False,
                    'message': r.get('errors'),
                }, status=HTTPStatus.OK)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Orden no identificada'
            }, status=HTTPStatus.OK)

