# from django.contrib.sites import requests
import requests
import html

from django.db.models import Max
from django.http import JsonResponse
from http import HTTPStatus
from .models import *
import math
from django.contrib.auth.models import User
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
import datetime
from django.db import DatabaseError, IntegrityError
from django.core import serializers

from ..sales.models import Order, OrderDetail, Product


def send_sunat(pk=None):
    order_obj = Order.objects.get(id=int(pk))
    person_obj = order_obj.person
    subsidiary_obj = order_obj.subsidiary
    date = order_obj.bill_date.strftime("%d-%m-%Y")
    payment_set = Payments.objects.filter(order=order_obj)

    items = []
    description = 'Acuerdo de pago'
    payment = 'Contado'
    if payment_set.exists():
        payment_obj = payment_set.last()
        code = ''
        if payment_obj.code_operation:
            code = 'OP: ' + str(payment_obj.code_operation)
        payment = str(payment_obj.get_payment_display()) + code
        j = 1
        for c in payment_set.filter(credit=True):
            credit = {
                "cuota": j,
                "fecha_de_pago": c.date_payment.strftime("%d-%m-%Y"),
                "importe": c.amount
            }
            items.append(credit)
            j = j + 1
    index = 1
    sub_total = 0
    total = 0
    igv_total = 0

    details = OrderDetail.objects.filter(order=order_obj, is_invoice=True, is_state=True)
    if order_obj.condition == 'PA':
        details = OrderDetail.objects.filter(order=order_obj, is_invoice=True, operation='S')

    for d in details:
        amount_igv = d.quantity * d.price
        amount_sin_igv = amount_igv / decimal.Decimal(1.1800)
        price_igv = d.price
        price_sin_igv = price_igv / decimal.Decimal(1.1800)
        item_igv = amount_igv - amount_sin_igv
        sub_total = sub_total + amount_sin_igv
        total = total + amount_igv
        igv_total = igv_total + item_igv
        # amount = d.quantity * d.price
        # amount_igv = amount * decimal.Decimal(1.1800)
        # item_igv = amount_igv - amount
        # price_igv = d.price * decimal.Decimal(1.1800)
        # sub_total = sub_total + amount
        # total = total + amount_igv
        # igv_total = igv_total + item_igv
        item = {
            "item": index,
            "unidad_de_medida": str(d.unit),
            "codigo": str(d.product.code),
            "codigo_producto_sunat": "10000000",
            "descripcion": d.product.name + " " + d.product.measure(),
            "cantidad": float(round(d.quantity, 4)),
            # "valor_unitario": float(round((d.price), 2)),
            "valor_unitario": float(round(price_sin_igv, 6)),
            # "precio_unitario": float(round(price_igv, 2)),
            "precio_unitario": float(round(price_igv, 4)),
            "descuento": "",
            "subtotal": float(round(amount_sin_igv, 4)),
            "tipo_de_igv": 1,
            "igv": float(round(item_igv, 4)),
            # "total": float(round(amount_igv, 2)),
            "total": float(round(amount_igv, 4)),
            "anticipo_regularizacion": 'false',
            "anticipo_documento_serie": "",
            "anticipo_documento_numero": "",
        }
        items.append(item)
        index = index + 1
    client_document = '00000000'
    client_type = '1'
    client_names = 'CLIENTES VARIOS'
    client_address = '-'
    client_email = ''
    client_id = ''
    if person_obj:
        client_id = person_obj.id
        client_document = person_obj.number
        client_type = person_obj.document
        client_names = person_obj.names
        client_address = person_obj.address
        client_email = person_obj.email
    if client_document == '0':
        client_document = '00000000'
        client_type = '1'
    elif client_document == '1':
        client_document = '1'
        client_type = '-'
    elif client_document == str(client_id):
        client_type = '-'
    params = {
        "operacion": "generar_comprobante",
        "tipo_de_comprobante": int(order_obj.doc),
        "serie": str(order_obj.bill_serial),
        "numero": int(order_obj.bill_number),
        "sunat_transaction": 1,
        "cliente_tipo_de_documento": str(client_type),
        "cliente_numero_de_documento": client_document,
        "cliente_denominacion": client_names,
        "cliente_direccion": client_address,
        "cliente_email": client_email,
        "cliente_email_1": "",
        "cliente_email_2": "",
        "fecha_de_emision": date,
        "fecha_de_vencimiento": "",
        "moneda": 1,
        "tipo_de_cambio": "",
        "porcentaje_de_igv": 18.00,
        "descuento_global": "",
        "total_descuento": "",
        "total_anticipo": "",
        "total_gravada": float(sub_total),
        "total_inafecta": "",
        "total_exonerada": "",
        "total_igv": float(igv_total),
        "total_gratuita": "",
        "total_otros_cargos": "",
        "total": float(total),
        "percepcion_tipo": "",
        "percepcion_base_imponible": "",
        "total_percepcion": "",
        "total_incluido_percepcion": "",
        "retencion_tipo": "",
        "retencion_base_imponible": "",
        "total_retencion": "",
        "total_impuestos_bolsas": "",
        "detraccion": 'false',
        "observaciones": "",
        "documento_que_se_modifica_tipo": "",
        "documento_que_se_modifica_serie": "",
        "documento_que_se_modifica_numero": "",
        "tipo_de_nota_de_credito": "",
        "tipo_de_nota_de_debito": "",
        "enviar_automaticamente_a_la_sunat": 'true',
        "enviar_automaticamente_al_cliente": 'false',
        "condiciones_de_pago": str(description),
        "medio_de_pago": str(payment),
        "placa_vehiculo": "",
        "orden_compra_servicio": "",
        "formato_de_pdf": "",
        "generado_por_contingencia": "",
        "bienes_region_selva": "",
        "servicios_region_selva": "",
        "items": items,
    }
    # print(params)
    url = str(subsidiary_obj.url)
    authorization = str(subsidiary_obj.token)
    headers = {
        "Authorization": authorization,
        "Content-Type": 'application/json'
    }
    response = requests.post(url, json=params, headers=headers)

    if response.status_code == 200:
        # print(response.status_code)
        result = response.json()
        order_obj.bill_type = result.get("tipo_de_comprobante")
        order_obj.status = 'E'
        order_obj.bill_status = result.get("aceptada_por_sunat")
        order_obj.bill_description = result.get("sunat_description")
        order_obj.bill_enlace_pdf = result.get("enlace_del_pdf")
        order_obj.bill_qr = result.get("cadena_para_codigo_qr")
        order_obj.bill_hash = result.get("codigo_hash")
        order_obj.save()
        context = {
            'success': True,
            'message': 'OK',
            'code_hash': result.get("codigo_hash"),
        }
    else:
        # print("Error " + str(response.status_code))
        result = response.json()
        context = {
            'success': False,
            'errors': result.get("errors"),
            'codigo': result.get("codigo"),
        }
        if context.get('errors') == 'Este documento ya existe en [PSE.PE]' and context.get('codigo') == 23:
            params_consult = {}
            if order_obj.doc == '1':
                params_consult = {
                    "operacion": "consultar_comprobante",
                    "tipo_de_comprobante": 1,
                    "serie": order_obj.bill_serial,
                    "numero": order_obj.bill_number
                }
            elif order_obj.doc == '2':
                params_consult = {
                    "operacion": "consultar_comprobante",
                    "tipo_de_comprobante": 2,
                    "serie": order_obj.bill_serial,
                    "numero": order_obj.bill_number
                }
            response_consult = requests.post(url, json=params_consult, headers=headers)
            if response_consult.status_code == 200:
                result_consult = response_consult.json()
                order_obj.bill_type = result_consult.get("tipo_de_comprobante")
                order_obj.status = 'E'
                order_obj.bill_status = result_consult.get("aceptada_por_sunat")
                order_obj.bill_description = result_consult.get("sunat_description")
                order_obj.bill_enlace_pdf = result_consult.get("enlace_del_pdf")
                order_obj.bill_qr = result_consult.get("cadena_para_codigo_qr")
                order_obj.bill_hash = result_consult.get("codigo_hash")
                order_obj.save()
                context = {
                    'success': True,
                    'message': 'OK',
                    'code_hash': result_consult.get("codigo_hash"),
                }
    return context


def send_guide(pk=None):
    order_obj = Order.objects.get(id=pk)
    date_transfer = order_obj.guide_transfer
    date = order_obj.guide_date
    subsidiary_obj = order_obj.subsidiary
    person_obj = order_obj.person
    client_type_document = person_obj.document
    client_nro_document = person_obj.number
    client_names = person_obj.names
    client_address = person_obj.address
    client_email = person_obj.email

    if order_obj.guide_motive == '04':
        client_type_document = '6'
        client_nro_document = subsidiary_obj.ruc
        client_names = subsidiary_obj.business_name.upper()
        client_address = subsidiary_obj.address.upper()
        client_email = subsidiary_obj.email

    items = []
    for d in OrderDetail.objects.filter(order=order_obj, is_invoice=True, is_state=True):
        quantity_sent = decimal.Decimal(d.quantity)
        item = {
            "unidad_de_medida": str(d.unit),
            "codigo": str(d.product.code),
            "descripcion": str(d.product.name),
            "cantidad": float(round(quantity_sent, 2))
        }
        items.append(item)
    # new_issue = datetime.datetime.strptime(date, "%Y-%m-%d")
    formatdate = date.strftime("%d-%m-%Y")
    # new_transfer = datetime.datetime.strptime(date_transfer, "%Y-%m-%d")
    formatdate1 = date_transfer.strftime("%d-%m-%Y")
    type_of_transport = ''
    carrier_document_type = ''
    if order_obj.guide_modality_transport == '1':
        type_of_transport = '01'
        carrier_document_type = '6'
    elif order_obj.guide_modality_transport == '2':
        type_of_transport = '02'
        carrier_document_type = '1'

    params = {
        "operacion": "generar_guia",
        "tipo_de_comprobante": 7,
        "serie": str(order_obj.guide_serial),
        "numero": str(order_obj.guide_number),
        "cliente_tipo_de_documento": client_type_document,
        "cliente_numero_de_documento": client_nro_document,
        "cliente_denominacion": client_names,
        "cliente_direccion": client_address,
        "cliente_email": client_email,
        "cliente_email_1": "",
        "cliente_email_2": "",
        "fecha_de_emision": formatdate,
        "observaciones": order_obj.guide_description,
        "motivo_de_traslado": str(order_obj.guide_motive),
        "peso_bruto_total": float(order_obj.guide_weight),
        "numero_de_bultos": int(order_obj.guide_package),
        "peso_bruto_unidad_de_medida": "KGM",
        "tipo_de_transporte": str(type_of_transport),  # '01'=publico, '02'=privado
        "fecha_de_inicio_de_traslado": formatdate1,

        "transportista_documento_tipo": carrier_document_type,
        "transportista_documento_numero": str(order_obj.guide_carrier_document),
        "transportista_denominacion": str(order_obj.guide_carrier_names),

        "transportista_placa_numero": str(order_obj.guide_truck),
        "conductor_documento_tipo": '1',
        "conductor_documento_numero": str(order_obj.guide_driver_dni),
        "conductor_denominacion": str(order_obj.guide_driver_full_name),
        "conductor_nombre": str(order_obj.guide_driver_name),
        "conductor_apellidos": str(order_obj.guide_driver_lastname),
        "conductor_numero_licencia": str(order_obj.guide_driver_license),
        "punto_de_partida_ubigeo": str(order_obj.guide_origin),
        "punto_de_partida_direccion": str(order_obj.guide_origin_address),
        "punto_de_llegada_ubigeo": str(order_obj.guide_destiny),
        "punto_de_llegada_direccion": str(order_obj.guide_destiny_address),
        "enviar_automaticamente_a_la_sunat": "true",
        "enviar_automaticamente_al_cliente": "false",
        "codigo_unico": "",
        "formato_de_pdf": "",
        "items": items
    }
    url = str(subsidiary_obj.url)
    authorization = str(subsidiary_obj.token)
    headers = {
        "Authorization": authorization,
        "Content-Type": 'application/json'
    }
    response = requests.post(url, json=params, headers=headers)

    if response.status_code == 200:
        result = response.json()

        context = {
            'success': True,
            "tipo_de_comprobante": result.get("tipo_de_comprobante"),
            "serie": result.get("serie"),
            "numero": result.get("numero"),
            "enlace": result.get("enlace"),
            "aceptada_por_sunat": result.get("aceptada_por_sunat"),
            "sunat_description": result.get("sunat_description"),
            "sunat_note": result.get("sunat_note"),
            "sunat_responsecode": result.get("sunat_responsecode"),
            "sunat_soap_error": result.get("sunat_soap_error"),
            "pdf_zip_base64": result.get("pdf_zip_base64"),
            "xml_zip_base64": result.get("xml_zip_base64"),
            "cdr_zip_base64": result.get("cdr_zip_base64"),
            "enlace_del_pdf": result.get("enlace_del_pdf"),
            "enlace_del_xml": result.get("enlace_del_xml"),
            "enlace_del_cdr": result.get("enlace_del_cdr")
        }
        order_obj.guide_status = True
        order_obj.guide_enlace_pdf = result.get("enlace_del_xml")
        order_obj.save()
    else:
        print("Error " + str(response.status_code) + str(response.text))
        result = response.json()
        context = {
            'success': False,
            'errors': result.get("errors"),
            'codigo': result.get("codigo"),
        }
    return context


def send_sunat_to_cancel(pk=None):
    order_obj = Order.objects.get(id=int(pk))
    person_obj = order_obj.person
    subsidiary_obj = order_obj.subsidiary
    date = order_obj.bill_date.strftime("%d-%m-%Y")
    payment_set = Payments.objects.filter(order=order_obj)

    items = []
    description = 'Acuerdo de pago'
    payment = 'Contado'
    if payment_set.exists():
        payment_obj = payment_set.last()
        code = ''
        if payment_obj.code_operation:
            code = 'OP: ' + str(payment_obj.code_operation)
        payment = str(payment_obj.get_payment_display()) + code
        j = 1
        for c in payment_set.filter(credit=True):
            credit = {
                "cuota": j,
                "fecha_de_pago": c.date_payment.strftime("%d-%m-%Y"),
                "importe": c.amount
            }
            items.append(credit)
            j = j + 1
    index = 1
    sub_total = 0
    total = 0
    igv_total = 0
    for d in OrderDetail.objects.filter(order=order_obj, is_invoice=True, operation='S'):
        amount_igv = d.quantity * d.price
        amount_sin_igv = amount_igv / decimal.Decimal(1.1800)
        price_igv = d.price
        price_sin_igv = price_igv / decimal.Decimal(1.1800)
        item_igv = amount_igv - amount_sin_igv
        sub_total = sub_total + amount_sin_igv
        total = total + amount_igv
        igv_total = igv_total + item_igv
        # amount = d.quantity * d.price
        # amount_igv = amount * decimal.Decimal(1.1800)
        # item_igv = amount_igv - amount
        # price_igv = d.price * decimal.Decimal(1.1800)
        # sub_total = sub_total + amount
        # total = total + amount_igv
        # igv_total = igv_total + item_igv
        item = {
            "item": index,
            "unidad_de_medida": str(d.unit),
            "codigo": str(d.product.code),
            "codigo_producto_sunat": "10000000",
            "descripcion": d.product.name + " " + d.product.measure(),
            "cantidad": float(round(d.quantity, 4)),
            # "valor_unitario": float(round((d.price), 2)),
            "valor_unitario": float(round(price_sin_igv, 6)),
            # "precio_unitario": float(round(price_igv, 2)),
            "precio_unitario": float(round(price_igv, 4)),
            "descuento": "",
            "subtotal": float(round(amount_sin_igv, 4)),
            "tipo_de_igv": 1,
            "igv": float(round(item_igv, 4)),
            # "total": float(round(amount_igv, 2)),
            "total": float(round(amount_igv, 4)),
            "anticipo_regularizacion": 'false',
            "anticipo_documento_serie": "",
            "anticipo_documento_numero": "",
        }
        items.append(item)
        index = index + 1
    client_document = '00000000'
    client_type = '1'
    client_names = 'CLIENTES VARIOS'
    client_address = '-'
    client_email = ''
    client_id = ''
    if person_obj:
        client_id = person_obj.id
        client_document = person_obj.number
        client_type = person_obj.document
        client_names = person_obj.names
        client_address = person_obj.address
        client_email = person_obj.email
    if client_document == '0':
        client_document = '00000000'
        client_type = '1'
    elif client_document == '1':
        client_document = '1'
        client_type = '-'
    elif client_document == str(client_id):
        client_type = '-'
    params = {
        "operacion": "generar_comprobante",
        "tipo_de_comprobante": int(order_obj.doc),
        "serie": str(order_obj.bill_serial),
        "numero": int(order_obj.bill_number),
        "sunat_transaction": 1,
        "cliente_tipo_de_documento": str(client_type),
        "cliente_numero_de_documento": client_document,
        "cliente_denominacion": client_names,
        "cliente_direccion": client_address,
        "cliente_email": client_email,
        "cliente_email_1": "",
        "cliente_email_2": "",
        "fecha_de_emision": date,
        "fecha_de_vencimiento": "",
        "moneda": 1,
        "tipo_de_cambio": "",
        "porcentaje_de_igv": 18.00,
        "descuento_global": "",
        "total_descuento": "",
        "total_anticipo": "",
        "total_gravada": float(sub_total),
        "total_inafecta": "",
        "total_exonerada": "",
        "total_igv": float(igv_total),
        "total_gratuita": "",
        "total_otros_cargos": "",
        "total": float(total),
        "percepcion_tipo": "",
        "percepcion_base_imponible": "",
        "total_percepcion": "",
        "total_incluido_percepcion": "",
        "retencion_tipo": "",
        "retencion_base_imponible": "",
        "total_retencion": "",
        "total_impuestos_bolsas": "",
        "detraccion": 'false',
        "observaciones": "",
        "documento_que_se_modifica_tipo": "",
        "documento_que_se_modifica_serie": "",
        "documento_que_se_modifica_numero": "",
        "tipo_de_nota_de_credito": "",
        "tipo_de_nota_de_debito": "",
        "enviar_automaticamente_a_la_sunat": 'true',
        "enviar_automaticamente_al_cliente": 'false',
        "condiciones_de_pago": str(description),
        "medio_de_pago": str(payment),
        "placa_vehiculo": "",
        "orden_compra_servicio": "",
        "formato_de_pdf": "",
        "generado_por_contingencia": "",
        "bienes_region_selva": "",
        "servicios_region_selva": "",
        "items": items,
    }
    print(params)
    url = str(subsidiary_obj.url)
    authorization = str(subsidiary_obj.token)
    headers = {
        "Authorization": authorization,
        "Content-Type": 'application/json'
    }
    response = requests.post(url, json=params, headers=headers)

    if response.status_code == 200:
        print(response.status_code)
        result = response.json()
        order_obj.bill_type = result.get("tipo_de_comprobante")
        # order_obj.status = 'E'
        order_obj.bill_status = result.get("aceptada_por_sunat")
        order_obj.bill_description = result.get("sunat_description")
        order_obj.bill_enlace_pdf = result.get("enlace_del_pdf")
        order_obj.bill_qr = result.get("cadena_para_codigo_qr")
        order_obj.bill_hash = result.get("codigo_hash")
        order_obj.save()
        context = {
            'success': True,
            'message': 'OK',
            'serial': order_obj.bill_serial,
            'number': order_obj.bill_number
        }
    else:
        print("Error " + str(response.status_code))
        result = response.json()
        context = {
            'success': False,
            'errors': result.get("errors"),
            'codigo': result.get("codigo"),
        }
    return context


def cancelsunat(pk: int):
    if pk:
        order_obj = Order.objects.get(id=int(pk))
        subsidiary_obj = order_obj.subsidiary
        params = {
            "operacion": "generar_anulacion",
            "tipo_de_comprobante": str(order_obj.doc),
            "serie": str(order_obj.bill_serial),
            "numero": str(order_obj.bill_number),
            "motivo": "ERROR DE LLENADO",
            "codigo_unico": ""
        }
        url = subsidiary_obj.url
        _authorization = subsidiary_obj.token
        headers = {
            "Authorization": _authorization,
            "Content-Type": 'application/json'
        }
        response = requests.post(url, json=params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            order_obj.status = 'A'
            order_obj.condition = 'A'
            order_obj.save()
            context = {
                'serial': order_obj.bill_serial,
                'number': order_obj.bill_number,
                'enlace': result.get("enlace"),
                'sunat_ticket_numero': result.get("sunat_ticket_numero"),
                'aceptada_por_sunat': result.get("aceptada_por_sunat"),
                'enlace_del_pdf': result.get("enlace_del_pdf"),
                'params': params
            }
        else:
            result = response.json()
            context = {
                'errors': result.get("errors"),
                'codigo': result.get("codigo"),
            }
        return context


def number_note(serial=None, document=None):
    number = Order.objects.filter(note_serial=serial, status=document).aggregate(
        r=Coalesce(Max('note_number'), 0)).get('r')
    return number + 1


def credit_note(pk):
    if pk:
        order_obj = Order.objects.get(id=int(pk))
        subsidiary_obj = order_obj.subsidiary
        serial = str(order_obj.bill_serial)[0] + "N01"
        type_number = 3
        number = number_note(serial, 'N')
        person_obj = order_obj.person
        date_voucher = datetime.datetime.now().strftime("%d-%m-%Y")
        date_order = order_obj.create_at
        items = []
        index = 1
        sub_total = 0
        total = 0
        total_discount = decimal.Decimal(order_obj.total_discount)
        for d in OrderDetail.objects.filter(order=order_obj, is_invoice=True, is_state=True):
            total_item_igv = d.quantity * d.price
            price_item_igv = d.price
            price_item_sin_igv = d.price / decimal.Decimal(1.1800)
            total_item_sin_igv = total_item_igv / decimal.Decimal(1.1800)
            igv_item = total_item_igv - total_item_sin_igv
            total = total + total_item_igv
            sub_total = sub_total + total_item_sin_igv
            item = {
                "item": index,  # index para los detalles
                "unidad_de_medida": str(d.unit),  # NIU viene del nubefact NIU=PRODUCTO
                "codigo": str(d.product.code),  # codigo del producto opcional
                "codigo_producto_sunat": "10000000",  # codigo del producto excel-sunat
                "descripcion": str(d.product.name),
                "cantidad": float(round(d.quantity, 3)),
                "valor_unitario": float(round(price_item_sin_igv, 3)),  # valor unitario sin IGV
                "precio_unitario": float(round(price_item_igv, 3)),  # valor unitario con IGV
                "descuento": "",
                "subtotal": float(round(total_item_sin_igv, 3)),  # total sin igv
                # resultado del valor unitario por la cantidad menos el descuento
                "tipo_de_igv": 1,  # operacion onerosa
                "igv": float(round(igv_item, 3)),
                "total": float(round(total_item_igv, 3)),  # total con igv
                "anticipo_regularizacion": 'false',
                "anticipo_documento_serie": "",
                "anticipo_documento_numero": "",
            }
            items.append(item)
            index = index + 1
        client_type = person_obj.document
        client_names = person_obj.names
        client_document = person_obj.number
        client_address = person_obj.address
        client_email = person_obj.email
        total_engraved = decimal.Decimal(sub_total - total_discount)
        total_invoice = total_engraved * decimal.Decimal(1.1800)
        total_igv = total_invoice - total_engraved
        params = {
            "operacion": "generar_comprobante",
            "tipo_de_comprobante": type_number,
            "serie": str(serial),
            "numero": number,
            "sunat_transaction": 1,
            "cliente_tipo_de_documento": int(client_type),
            "cliente_numero_de_documento": client_document,
            "cliente_denominacion": client_names,
            "cliente_direccion": client_address,
            "cliente_email": client_email,
            "cliente_email_1": "",
            "cliente_email_2": "",
            "fecha_de_emision": date_voucher,
            "fecha_de_vencimiento": "",
            "moneda": order_obj.coin,
            "tipo_de_cambio": "",
            "porcentaje_de_igv": 18.00,
            "descuento_global": float(round(total_discount, 3)),
            "total_descuento": float(round(total_discount, 3)),
            "total_anticipo": "",
            "total_gravada": float(round(total_engraved, 3)),
            "total_inafecta": "",
            "total_exonerada": "",
            "total_igv": float(round(total_igv, 3)),
            "total_gratuita": "",
            "total_otros_cargos": "",
            "total": float(round(total_invoice, 3)),
            "percepcion_tipo": "",
            "percepcion_base_imponible": "",
            "total_percepcion": "",
            "total_incluido_percepcion": "",
            "total_impuestos_bolsas": "",
            "detraccion": "",
            "detraccion_porcentaje": "",
            "observaciones": "",
            "documento_que_se_modifica_tipo": str(order_obj.doc),
            "documento_que_se_modifica_serie": str(order_obj.bill_serial),
            "documento_que_se_modifica_numero": str(order_obj.bill_number),
            "tipo_de_nota_de_credito": 6,
            "tipo_de_nota_de_debito": "",
            "enviar_automaticamente_a_la_sunat": 'true',
            "enviar_automaticamente_al_cliente": 'false',
            "condiciones_de_pago": "",
            "medio_de_pago": "",
            "placa_vehiculo": "",
            "orden_compra_servicio": "",
            "formato_de_pdf": "",
            "generado_por_contingencia": "",
            "bienes_region_selva": "",
            "servicios_region_selva": "",
            "items": items,
            "venta_al_credito": "",
        }
        # print(params)
        url = subsidiary_obj.url
        _authorization = subsidiary_obj.token
        headers = {"Authorization": _authorization, "Content-Type": 'application/json'}
        response = requests.post(url, json=params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            order_obj.status = 'N'
            order_obj.note_serial = str(serial)
            order_obj.note_type = result.get("tipo_de_comprobante")
            order_obj.note_number = number
            order_obj.note_status = result.get("aceptada_por_sunat")
            order_obj.note_description = result.get("sunat_description")
            order_obj.note_enlace_pdf = result.get("enlace_del_pdf")
            order_obj.note_date = datetime.datetime.now().strftime("%Y-%m-%d")
            order_obj.note_qr = result.get("cadena_para_codigo_qr")
            order_obj.note_hash = result.get("codigo_hash")
            order_obj.condition = 'A'
            order_obj.save()
            context = {
                'tipo_de_comprobante': result.get("tipo_de_comprobante"),
                'serie': result.get("serie"),
                'numero': result.get("numero"),
                'aceptada_por_sunat': result.get("aceptada_por_sunat"),
                'sunat_description': result.get("sunat_description"),
                'enlace_del_pdf': result.get("enlace_del_pdf"),
                'cadena_para_codigo_qr': result.get("cadena_para_codigo_qr"),
                'codigo_hash': result.get("codigo_hash"),
                'params': params
            }
        else:
            result = response.json()
            context = {
                'errors': str(result.get("errors")),
                'codigo': result.get("codigo"),
                'detail': params
            }
        return context


def query_apis_net_money(date):
    context = {}

    url = 'https://api.apis.net.pe/v1/tipo-cambio-sunat?fecha={}'.format(date)
    headers = {
        "Content-Type": 'application/json',
        'authorization': 'Bearer apis-token-3244.1KWBKUSrgYq6HNht68arg8LNsId9vVLm',
    }

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        result = r.json()

        context = {
            'success': True,
            'fecha_busqueda': result.get('fecha'),
            'fecha_sunat': result.get('fecha'),
            'venta': result.get('venta'),
            'compra': result.get('compra'),
            'origen': result.get('origen'),
            'moneda': result.get('moneda'),
        }
    else:
        result = r.json()
        context = {
            'status': False,
            'errors': '400 Bad Request',
        }

    return context


def send_guide_return(pk=None):
    order_obj = Order.objects.get(id=pk)
    date_transfer = order_obj.guide_transfer
    date = order_obj.guide_date
    subsidiary_obj = order_obj.subsidiary
    person_obj = order_obj.person
    client_type_document = person_obj.document
    client_nro_document = person_obj.number
    client_names = person_obj.names
    client_address = person_obj.address
    client_email = person_obj.email

    if order_obj.guide_motive == '04':
        client_type_document = '6'
        client_nro_document = subsidiary_obj.ruc
        client_names = subsidiary_obj.business_name.upper()
        client_address = subsidiary_obj.address.upper()
        client_email = subsidiary_obj.email

    items = []
    for d in OrderDetail.objects.filter(order=order_obj):
        quantity_sent = decimal.Decimal(d.quantity)
        item = {
            "unidad_de_medida": str(d.unit),
            "codigo": str(d.product.code),
            "descripcion": str(d.product.name),
            "cantidad": float(round(quantity_sent, 2))
        }
        items.append(item)
    # new_issue = datetime.datetime.strptime(date, "%Y-%m-%d")
    formatdate = date.strftime("%d-%m-%Y")
    # new_transfer = datetime.datetime.strptime(date_transfer, "%Y-%m-%d")
    formatdate1 = date_transfer.strftime("%d-%m-%Y")
    type_of_transport = ''
    carrier_document_type = ''
    if order_obj.guide_modality_transport == '1':
        type_of_transport = '01'
        carrier_document_type = '6'
    elif order_obj.guide_modality_transport == '2':
        type_of_transport = '02'
        carrier_document_type = '1'

    params = {
        "operacion": "generar_guia",
        "tipo_de_comprobante": 7,
        "serie": str(order_obj.guide_serial),
        "numero": str(order_obj.guide_number),
        "cliente_tipo_de_documento": client_type_document,
        "cliente_numero_de_documento": client_nro_document,
        "cliente_denominacion": client_names,
        "cliente_direccion": client_address,
        "cliente_email": client_email,
        "cliente_email_1": "",
        "cliente_email_2": "",
        "fecha_de_emision": formatdate,
        "observaciones": order_obj.guide_description,
        "motivo_de_traslado": str(order_obj.guide_motive),
        "peso_bruto_total": float(order_obj.guide_weight),
        "numero_de_bultos": int(order_obj.guide_package),
        "peso_bruto_unidad_de_medida": "KGM",
        "tipo_de_transporte": str(type_of_transport),  # '01'=publico, '02'=privado
        "fecha_de_inicio_de_traslado": formatdate1,

        "transportista_documento_tipo": carrier_document_type,
        "transportista_documento_numero": str(order_obj.guide_carrier_document),
        "transportista_denominacion": str(order_obj.guide_carrier_names),

        "transportista_placa_numero": str(order_obj.guide_truck),
        "conductor_documento_tipo": '1',
        "conductor_documento_numero": str(order_obj.guide_driver_dni),
        "conductor_denominacion": str(order_obj.guide_driver_full_name),
        "conductor_nombre": str(order_obj.guide_driver_name),
        "conductor_apellidos": str(order_obj.guide_driver_lastname),
        "conductor_numero_licencia": str(order_obj.guide_driver_license),
        "punto_de_partida_ubigeo": str(order_obj.guide_origin),
        "punto_de_partida_direccion": str(order_obj.guide_origin_address),
        "punto_de_llegada_ubigeo": str(order_obj.guide_destiny),
        "punto_de_llegada_direccion": str(order_obj.guide_destiny_address),
        "enviar_automaticamente_a_la_sunat": "true",
        "enviar_automaticamente_al_cliente": "false",
        "codigo_unico": "",
        "formato_de_pdf": "",
        "items": items
    }
    url = str(subsidiary_obj.url)
    authorization = str(subsidiary_obj.token)
    headers = {
        "Authorization": authorization,
        "Content-Type": 'application/json'
    }
    response = requests.post(url, json=params, headers=headers)

    if response.status_code == 200:
        result = response.json()

        context = {
            'success': True,
            "tipo_de_comprobante": result.get("tipo_de_comprobante"),
            "serie": result.get("serie"),
            "numero": result.get("numero"),
            "enlace": result.get("enlace"),
            "aceptada_por_sunat": result.get("aceptada_por_sunat"),
            "sunat_description": result.get("sunat_description"),
            "sunat_note": result.get("sunat_note"),
            "sunat_responsecode": result.get("sunat_responsecode"),
            "sunat_soap_error": result.get("sunat_soap_error"),
            "pdf_zip_base64": result.get("pdf_zip_base64"),
            "xml_zip_base64": result.get("xml_zip_base64"),
            "cdr_zip_base64": result.get("cdr_zip_base64"),
            "enlace_del_pdf": result.get("enlace_del_pdf"),
            "enlace_del_xml": result.get("enlace_del_xml"),
            "enlace_del_cdr": result.get("enlace_del_cdr")
        }
        order_obj.guide_status = True
        order_obj.guide_enlace_pdf = result.get("enlace_del_xml")
        order_obj.save()
    else:
        print("Error " + str(response.status_code) + str(response.text))
        result = response.json()
        context = {
            'success': False,
            'errors': result.get("errors"),
            'codigo': result.get("codigo"),
        }
    return context


def credit_note_by_parts(pk, details):
    if pk:
        order_obj = Order.objects.get(id=int(pk))
        subsidiary_obj = order_obj.subsidiary
        serial = str(order_obj.bill_serial)[0] + "N01"
        type_number = 3
        number = number_note(serial, 'N')
        person_obj = order_obj.person
        date_voucher = datetime.datetime.now().strftime("%d-%m-%Y")
        date_order = order_obj.create_at
        items = []
        index = 1
        sub_total = 0
        total = 0
        total_discount = decimal.Decimal(order_obj.total_discount)
        for d in details:
            if d['quantityReturned']:
                product_id = int(d['productID'])
                product_obj = Product.objects.get(id=product_id)
                total_item_igv = decimal.Decimal(d['quantityReturned']) * decimal.Decimal(d['price'])
                price_item_igv = decimal.Decimal(d['price'])
                price_item_sin_igv = decimal.Decimal(d['price']) / decimal.Decimal(1.1800)
                total_item_sin_igv = total_item_igv / decimal.Decimal(1.1800)
                igv_item = total_item_igv - total_item_sin_igv
                total = total + total_item_igv
                sub_total = sub_total + total_item_sin_igv
                description = str(str(product_obj.name).upper() + ' ' + str(product_obj.measure()))
                item = {
                    "item": index,  # index para los detalles
                    "unidad_de_medida": str(d['unit']),  # NIU viene del nubefact NIU=PRODUCTO
                    "codigo": str(product_obj.code),  # codigo del producto opcional
                    "codigo_producto_sunat": "10000000",  # codigo del producto excel-sunat
                    "descripcion": description,
                    "cantidad": float(round(decimal.Decimal(d['quantityReturned']), 4)),
                    "valor_unitario": float(round(price_item_sin_igv, 4)),  # valor unitario sin IGV
                    "precio_unitario": float(round(price_item_igv, 4)),  # valor unitario con IGV
                    "descuento": "",
                    "subtotal": float(round(total_item_sin_igv, 4)),  # total sin igv
                    # resultado del valor unitario por la cantidad menos el descuento
                    "tipo_de_igv": 1,  # operacion onerosa
                    "igv": float(round(igv_item, 4)),
                    "total": float(round(total_item_igv, 4)),  # total con igv
                    "anticipo_regularizacion": 'false',
                    "anticipo_documento_serie": "",
                    "anticipo_documento_numero": "",
                }
                items.append(item)
                index = index + 1
        client_type = person_obj.document
        client_names = person_obj.names
        client_document = person_obj.number
        client_address = person_obj.address
        client_email = person_obj.email
        total_engraved = decimal.Decimal(sub_total - total_discount)
        total_invoice = total_engraved * decimal.Decimal(1.1800)
        total_igv = total_invoice - total_engraved
        params = {
            "operacion": "generar_comprobante",
            "tipo_de_comprobante": type_number,
            "serie": str(serial),
            "numero": number,
            "sunat_transaction": 1,
            "cliente_tipo_de_documento": int(client_type),
            "cliente_numero_de_documento": client_document,
            "cliente_denominacion": client_names,
            "cliente_direccion": client_address,
            "cliente_email": client_email,
            "cliente_email_1": "",
            "cliente_email_2": "",
            "fecha_de_emision": date_voucher,
            "fecha_de_vencimiento": "",
            "moneda": order_obj.coin,
            "tipo_de_cambio": "",
            "porcentaje_de_igv": 18.00,
            "descuento_global": float(round(total_discount, 3)),
            "total_descuento": float(round(total_discount, 3)),
            "total_anticipo": "",
            "total_gravada": float(round(total_engraved, 3)),
            "total_inafecta": "",
            "total_exonerada": "",
            "total_igv": float(round(total_igv, 3)),
            "total_gratuita": "",
            "total_otros_cargos": "",
            "total": float(round(total_invoice, 3)),
            "percepcion_tipo": "",
            "percepcion_base_imponible": "",
            "total_percepcion": "",
            "total_incluido_percepcion": "",
            "total_impuestos_bolsas": "",
            "detraccion": "",
            "detraccion_porcentaje": "",
            "observaciones": "",
            "documento_que_se_modifica_tipo": str(order_obj.doc),
            "documento_que_se_modifica_serie": str(order_obj.bill_serial),
            "documento_que_se_modifica_numero": str(order_obj.bill_number),
            "tipo_de_nota_de_credito": 6,
            "tipo_de_nota_de_debito": "",
            "enviar_automaticamente_a_la_sunat": 'true',
            "enviar_automaticamente_al_cliente": 'false',
            "condiciones_de_pago": "",
            "medio_de_pago": "",
            "placa_vehiculo": "",
            "orden_compra_servicio": "",
            "formato_de_pdf": "",
            "generado_por_contingencia": "",
            "bienes_region_selva": "",
            "servicios_region_selva": "",
            "items": items,
            "venta_al_credito": "",
        }
        print(params)
        url = subsidiary_obj.url
        _authorization = subsidiary_obj.token
        headers = {"Authorization": _authorization, "Content-Type": 'application/json'}
        response = requests.post(url, json=params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            order_obj.status = 'N'
            order_obj.note_serial = str(serial)
            order_obj.note_type = result.get("tipo_de_comprobante")
            order_obj.note_number = number
            order_obj.note_status = result.get("aceptada_por_sunat")
            order_obj.note_description = result.get("sunat_description")
            order_obj.note_enlace_pdf = result.get("enlace_del_pdf")
            order_obj.note_date = datetime.datetime.now().strftime("%Y-%m-%d")
            order_obj.note_qr = result.get("cadena_para_codigo_qr")
            order_obj.note_hash = result.get("codigo_hash")
            order_obj.note_total = total_invoice
            order_obj.save()
            context = {
                'tipo_de_comprobante': result.get("tipo_de_comprobante"),
                'serie': result.get("serie"),
                'numero': result.get("numero"),
                'aceptada_por_sunat': result.get("aceptada_por_sunat"),
                'sunat_description': result.get("sunat_description"),
                'enlace_del_pdf': result.get("enlace_del_pdf"),
                'cadena_para_codigo_qr': result.get("cadena_para_codigo_qr"),
                'codigo_hash': result.get("codigo_hash"),
                'params': params
            }
        else:
            result = response.json()
            context = {
                'errors': str(result.get("errors")),
                'codigo': result.get("codigo"),
                'detail': params
            }
        return context


def credit_note_pending(pk):
    if pk:
        order_obj = Order.objects.get(id=int(pk))
        subsidiary_obj = order_obj.subsidiary
        serial = str(order_obj.bill_serial)[0] + "N01"
        type_number = 3
        number = number_note(serial, 'N')
        person_obj = order_obj.person
        date_voucher = datetime.datetime.now().strftime("%d-%m-%Y")
        date_order = order_obj.create_at
        items = []
        index = 1
        sub_total = 0
        total = 0
        total_discount = decimal.Decimal(order_obj.total_discount)
        for d in OrderDetail.objects.filter(order=order_obj, is_invoice=True, operation='S'):
            total_item_igv = d.quantity * d.price
            price_item_igv = d.price
            price_item_sin_igv = d.price / decimal.Decimal(1.1800)
            total_item_sin_igv = total_item_igv / decimal.Decimal(1.1800)
            igv_item = total_item_igv - total_item_sin_igv
            total = total + total_item_igv
            sub_total = sub_total + total_item_sin_igv
            item = {
                "item": index,  # index para los detalles
                "unidad_de_medida": str(d.unit),  # NIU viene del nubefact NIU=PRODUCTO
                "codigo": str(d.product.code),  # codigo del producto opcional
                "codigo_producto_sunat": "10000000",  # codigo del producto excel-sunat
                "descripcion": str(d.product.name),
                "cantidad": float(round(d.quantity, 3)),
                "valor_unitario": float(round(price_item_sin_igv, 3)),  # valor unitario sin IGV
                "precio_unitario": float(round(price_item_igv, 3)),  # valor unitario con IGV
                "descuento": "",
                "subtotal": float(round(total_item_sin_igv, 3)),  # total sin igv
                # resultado del valor unitario por la cantidad menos el descuento
                "tipo_de_igv": 1,  # operacion onerosa
                "igv": float(round(igv_item, 3)),
                "total": float(round(total_item_igv, 3)),  # total con igv
                "anticipo_regularizacion": 'false',
                "anticipo_documento_serie": "",
                "anticipo_documento_numero": "",
            }
            items.append(item)
            index = index + 1
        client_type = person_obj.document
        client_names = person_obj.names
        client_document = person_obj.number
        client_address = person_obj.address
        client_email = person_obj.email
        total_engraved = decimal.Decimal(sub_total - total_discount)
        total_invoice = total_engraved * decimal.Decimal(1.1800)
        total_igv = total_invoice - total_engraved
        params = {
            "operacion": "generar_comprobante",
            "tipo_de_comprobante": type_number,
            "serie": str(serial),
            "numero": number,
            "sunat_transaction": 1,
            "cliente_tipo_de_documento": int(client_type),
            "cliente_numero_de_documento": client_document,
            "cliente_denominacion": client_names,
            "cliente_direccion": client_address,
            "cliente_email": client_email,
            "cliente_email_1": "",
            "cliente_email_2": "",
            "fecha_de_emision": date_voucher,
            "fecha_de_vencimiento": "",
            "moneda": order_obj.coin,
            "tipo_de_cambio": "",
            "porcentaje_de_igv": 18.00,
            "descuento_global": float(round(total_discount, 3)),
            "total_descuento": float(round(total_discount, 3)),
            "total_anticipo": "",
            "total_gravada": float(round(total_engraved, 3)),
            "total_inafecta": "",
            "total_exonerada": "",
            "total_igv": float(round(total_igv, 3)),
            "total_gratuita": "",
            "total_otros_cargos": "",
            "total": float(round(total_invoice, 3)),
            "percepcion_tipo": "",
            "percepcion_base_imponible": "",
            "total_percepcion": "",
            "total_incluido_percepcion": "",
            "total_impuestos_bolsas": "",
            "detraccion": "",
            "detraccion_porcentaje": "",
            "observaciones": "",
            "documento_que_se_modifica_tipo": str(order_obj.doc),
            "documento_que_se_modifica_serie": str(order_obj.bill_serial),
            "documento_que_se_modifica_numero": str(order_obj.bill_number),
            "tipo_de_nota_de_credito": 6,
            "tipo_de_nota_de_debito": "",
            "enviar_automaticamente_a_la_sunat": 'true',
            "enviar_automaticamente_al_cliente": 'false',
            "condiciones_de_pago": "",
            "medio_de_pago": "",
            "placa_vehiculo": "",
            "orden_compra_servicio": "",
            "formato_de_pdf": "",
            "generado_por_contingencia": "",
            "bienes_region_selva": "",
            "servicios_region_selva": "",
            "items": items,
            "venta_al_credito": "",
        }
        print(params)
        url = subsidiary_obj.url
        _authorization = subsidiary_obj.token
        headers = {"Authorization": _authorization, "Content-Type": 'application/json'}
        response = requests.post(url, json=params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            order_obj.status = 'N'
            order_obj.note_serial = str(serial)
            order_obj.note_type = result.get("tipo_de_comprobante")
            order_obj.note_number = number
            order_obj.note_status = result.get("aceptada_por_sunat")
            order_obj.note_description = result.get("sunat_description")
            order_obj.note_enlace_pdf = result.get("enlace_del_pdf")
            order_obj.note_date = datetime.datetime.now().strftime("%Y-%m-%d")
            order_obj.note_qr = result.get("cadena_para_codigo_qr")
            order_obj.note_hash = result.get("codigo_hash")
            order_obj.condition = 'A'
            order_obj.save()
            context = {
                'tipo_de_comprobante': result.get("tipo_de_comprobante"),
                'serie': result.get("serie"),
                'numero': result.get("numero"),
                'aceptada_por_sunat': result.get("aceptada_por_sunat"),
                'sunat_description': result.get("sunat_description"),
                'enlace_del_pdf': result.get("enlace_del_pdf"),
                'cadena_para_codigo_qr': result.get("cadena_para_codigo_qr"),
                'codigo_hash': result.get("codigo_hash"),
                'params': params
            }
        else:
            result = response.json()
            context = {
                'errors': str(result.get("errors")),
                'codigo': result.get("codigo"),
                'detail': params
            }
        return context