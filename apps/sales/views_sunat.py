from datetime import datetime
import decimal
import html
import requests
from django.db.models import Max
from http import HTTPStatus
from .models import *
from typing import List, Optional
import logging
import requests


class ApisNetPe:
    BASE_URL = "https://api.apis.net.pe"

    def __init__(self, token: str = None) -> None:
        self.token = token

    def _get(self, path: str, params: dict):

        url = f"{self.BASE_URL}{path}"

        headers = {
            "Authorization": self.token,
            "Referer": "https://apis.net.pe/api-tipo-cambio.html"
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                if data.get('tipoDocumento') == '1':
                    context = {
                        'success': True,
                        'nombres': data.get('nombres'),
                        'paterno': data.get('apellidoPaterno'),
                        'materno': data.get('apellidoMaterno'),
                        'direccion': data.get('direccion')
                    }
                    return context
                elif data.get('tipoDocumento') == '6':
                    context = {
                        'success': True,
                        'razon_social': data.get('nombre'),
                        'ruc': data.get('numeroDocumento'),
                        'direccion_completa': data.get('direccion')
                    }
                    return context
                elif data.get('precioVenta'):
                    context = {
                        'success': True,
                        'compra': data.get('precioCompra'),
                        'venta': data.get('precioVenta'),
                        'moneda': data.get('moneda')
                    }
                    return context
            else:
                context = {
                    'success': False
                }
                return context
        elif response.status_code == 422:
            logging.warning(f"{response.url} - parámetro inválido")
            logging.warning(response.text)
        elif response.status_code == 403:
            logging.warning(f"{response.url} - IP bloqueada")
        elif response.status_code == 429:
            logging.warning(f"{response.url} - Muchas solicitudes agregan retraso")
        elif response.status_code == 401:
            logging.warning(f"{response.url} - Token no válido o limitado")
        else:
            logging.warning(f"{response.url} - Server Error status_code={response.status_code}")
        return None

    # def _get_person_api(self, path: str, params: dict):
    #     url = 'https://api.apis.net.pe/v1/dni?numero=' + params.get('numero')
    #
    #     headers = {
    #         "Content-Type": 'application/json',
    #         "Authorization": 'Bearer apis-token-1685.amWUXQRSlBEjqsVJYTy0zH-jDSGL5Mmy'
    #     }
    #     response = requests.get(url, headers=headers)
    #
    #     if response.status_code == 200:
    #         result = response.json()
    #
    #         context = {
    #             'success': True,
    #             'nombre': result.get("nombre"),
    #             'tipoDocumento': result.get("tipoDocumento"),
    #             'numeroDocumento': result.get('numeroDocumento'),
    #             'apellidoPaterno': result.get('apellidoPaterno'),
    #             'apellidoMaterno': result.get('apellidoMaterno'),
    #             'nombres': result.get('nombres'),
    #             'direccion': result.get('direccion'),
    #         }
    #     else:
    #         result = response.status_code
    #         context = {
    #             'errors': True
    #         }
    #     return context

    def get_person(self, dni: str) -> Optional[dict]:
        url = 'https://api.apis.net.pe/v2/dni?numero=' + dni

        headers = {
            "Content-Type": 'application/json',
            "Authorization": 'Bearer apis-token-1685.amWUXQRSlBEjqsVJYTy0zH-jDSGL5Mmy'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()

            context = {
                'success': True,
                'nombre': result.get("nombre"),
                'tipoDocumento': result.get("tipoDocumento"),
                'numeroDocumento': result.get('numeroDocumento'),
                'apellidoPaterno': result.get('apellidoPaterno'),
                'apellidoMaterno': result.get('apellidoMaterno'),
                'nombres': result.get('nombres'),
                'direccion': result.get('direccion'),
            }
        else:
            result = response.status_code
            context = {
                'errors': True
            }
        return context
    # return self._get_person_api("/v2/dni", {"numero": dni})

    def get_company(self, ruc: str) -> Optional[dict]:
        url = 'https://api.apis.net.pe/v1/ruc?numero=' + ruc

        headers = {
            "Content-Type": 'application/json',
            "Authorization": 'Bearer apis-token-1685.amWUXQRSlBEjqsVJYTy0zH-jDSGL5Mmy'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()

            context = {
                'success': True,
                'nombre': result.get("nombre"),
                'tipoDocumento': result.get("tipoDocumento"),
                'numeroDocumento': result.get('numeroDocumento'),
                'apellidoPaterno': result.get('apellidoPaterno'),
                'apellidoMaterno': result.get('apellidoMaterno'),
                'nombres': result.get('nombres'),
                'direccion': result.get('direccion'),
            }
        else:
            result = response.status_code
            context = {
                'errors': True
            }
        return context
        # return self._get("/v2/ruc", {"numero": ruc})

def get_exchange_rate(self, date: str) -> dict:
    return self._get("/v2/tipo-cambio-sunat", {"fecha": date})


def get_exchange_rate_today(self) -> dict:
    return self._get("/v2/tipo-cambio-sunat", {})


def get_exchange_rate_for_month(self, month: int, year: int) -> List[dict]:
    return self._get("/v2/tipo-cambio-sunat", {"month": month, "year": year})
# def search_api_peru(nro_doc, type_document):
#     context = {}
#     if type_document == 'DNI':
#         url = 'https://apiperu.dev/api/dni/{}'.format(nro_doc)
#         headers = {
#             "Content-Type": 'application/json',
#             'authorization': 'Bearer 738943dbc8ef22fd4ebb49caa36883e99baf9c4f2170f437537e2341bd7a725d',
#         }
#         r = requests.get(url, headers=headers)
#
#         if r.status_code == 200:
#             result = r.json()
#             if result.get('success'):
#                 data = result.get('data')
#                 context = {
#                     'success': True,
#                     'nombres': data.get('nombres'),
#                     'paterno': data.get('apellido_paterno'),
#                     'materno': data.get('apellido_materno'),
#                     'direccion': data.get('domicilio_direccion')
#                 }
#             else:
#                 context = {
#                     'success': False
#                 }
#         else:
#             context = {
#                 'success': False,
#                 'errors': 'Datos invalidos en reniec',
#             }
#
#     if type_document == 'RUC':
#         url = 'https://apiperu.dev/api/ruc/{}'.format(nro_doc)
#         headers = {
#             "Content-Type": 'application/json',
#             'authorization': 'Bearer 738943dbc8ef22fd4ebb49caa36883e99baf9c4f2170f437537e2341bd7a725d',
#         }
#         r = requests.get(url, headers=headers)
#
#         if r.status_code == 200:
#             result = r.json()
#             if result.get('success'):
#                 data = result.get('data')
#                 context = {
#                     'success': True,
#                     'ruc': data.get('ruc'),
#                     'direccion': data.get('direccion'),
#                     'direccion_completa': data.get('direccion_completa'),
#                     'razon_social': data.get('nombre_o_razon_social'),
#                 }
#             else:
#                 context = {
#                     'success': False,
#                     'message': result.get('message')
#                 }
#         else:
#             context = {
#                 'success': False,
#                 'errors': 'Datos invalidos en sunat',
#             }
#     return context
#
#
# class ApisNetPe:
#     BASE_URL = "https://api.apis.net.pe"
#
#     def __init__(self, token: str = None) -> None:
#         self.token = token
#
#     def _get(self, path: str, params: dict):
#
#         url = f"{self.BASE_URL}{path}"
#
#         headers = {
#             "Authorization": self.token,
#             "Referer": "https://apis.net.pe/api-tipo-cambio.html"
#         }
#
#         response = requests.get(url, headers=headers, params=params)
#         if response.status_code == 200:
#             data = response.json()
#             if data:
#                 if data.get('tipoDocumento') == '1':
#                     context = {
#                         'success': True,
#                         'nombres': data.get('nombres'),
#                         'paterno': data.get('apellidoPaterno'),
#                         'materno': data.get('apellidoMaterno'),
#                         'direccion': data.get('direccion')
#                     }
#                 elif data.get('tipoDocumento') == '6':
#                     context = {
#                         'success': True,
#                         'razon_social': data.get('nombre'),
#                         'ruc': data.get('numeroDocumento'),
#                         'direccion_completa': data.get('direccion')
#                     }
#             else:
#                 context = {
#                     'success': False
#                 }
#             return context
#         elif response.status_code == 422:
#             logging.warning(f"{response.url} - parámetro inválido")
#             logging.warning(response.text)
#         elif response.status_code == 403:
#             logging.warning(f"{response.url} - IP bloqueada")
#         elif response.status_code == 429:
#             logging.warning(f"{response.url} - Muchas solicitudes agregan retraso")
#         elif response.status_code == 401:
#             logging.warning(f"{response.url} - Token no válido o limitado")
#         else:
#             logging.warning(f"{response.url} - Server Error status_code={response.status_code}")
#         return None
#
#     def get_person(self, dni: str) -> Optional[dict]:
#         return self._get("/v1/dni", {"numero": dni})
#
#     def get_company(self, ruc: str) -> Optional[dict]:
#         return self._get("/v1/ruc", {"numero": ruc})
#
#     def get_exchange_rate(self, date: str) -> dict:
#         return self._get("/v1/tipo-cambio-sunat", {"fecha": date})
#
#     def get_exchange_rate_today(self) -> dict:
#         return self._get("/v1/tipo-cambio-sunat", {})
#
#     def get_exchange_rate_for_month(self, month: int, year: int) -> List[dict]:
#         return self._get("/v1/tipo-cambio-sunat", {"month": month, "year": year})
#
#
# def get_bill_number(serial=None, type=None):
#     bill = 1
#     correlative = Bill.objects.filter(serial=serial, type=str(type)).aggregate(r=Coalesce(Max('number'), 0)).get(
#         'r')
#     if correlative:
#         bill = bill + correlative
#         return bill
#     else:
#         return bill
#
#
# def voucher_igv(pk, date=None, types=None, detraction=False, percentage=0):
#     order_obj = Order.objects.get(id=int(pk))
#     payment_set = Payments.objects.filter(order=order_obj)
#     subsidiary_obj = order_obj.subsidiary
#     serial = types + str(subsidiary_obj.serial)
#     type_number = ''
#     if types == 'F':
#         type_number = 1
#     elif types == 'B':
#         type_number = 2
#     number = get_bill_number(serial, type_number)
#     detail_set = OrderDetail.objects.filter(order=order_obj)
#     client_obj = order_obj.client
#     date_voucher = datetime.now().strftime("%d-%m-%Y")
#     date_order = order_obj.create_at
#     if date:
#         date_voucher = (datetime.strptime(date, '%Y-%m-%d')).strftime("%d-%m-%Y")
#     else:
#         date_voucher = date_order.strftime("%d-%m-%Y")
#     items = []
#     index = 1
#     sub_total = 0
#     total = 0
#     total_discount = decimal.Decimal(order_obj.discount_output)
#     for d in detail_set.filter(operation='S', is_state=False):
#         total_item_igv = d.quantity * d.price
#         price_item_igv = d.price
#         price_item_sin_igv = d.price / decimal.Decimal(1.1800)
#         total_item_sin_igv = total_item_igv / decimal.Decimal(1.1800)
#         igv_item = total_item_igv - total_item_sin_igv
#         total = total + total_item_igv
#         sub_total = sub_total + total_item_sin_igv
#         item = {
#             "item": index,  # index para los detalles
#             "unidad_de_medida": str(d.unit.name),  # NIU viene del nubefact NIU=PRODUCTO
#             "codigo": str(d.product.code),  # codigo del producto opcional
#             "codigo_producto_sunat": "10000000",  # codigo del producto excel-sunat
#             "descripcion": str(d.product.name),
#             "cantidad": float(round(d.quantity, 2)),
#             "valor_unitario": float(round(price_item_sin_igv, 2)),  # valor unitario sin IGV
#             "precio_unitario": float(round(price_item_igv, 2)),  # valor unitario con IGV
#             "descuento": "",
#             "subtotal": float(round(total_item_sin_igv, 2)),  # total sin igv
#             # resultado del valor unitario por la cantidad menos el descuento
#             "tipo_de_igv": 1,  # operacion onerosa
#             "igv": float(round(igv_item, 2)),
#             "total": float(round(total_item_igv, 2)),  # total con igv
#             "anticipo_regularizacion": 'false',
#             "anticipo_documento_serie": "",
#             "anticipo_documento_numero": "",
#         }
#         items.append(item)
#         index = index + 1
#     client_type = client_obj.type.id
#     client_names = client_obj.full_name
#     client_document = client_obj.document
#     client_address = client_obj.address
#     client_email = client_obj.email
#     coin = ''
#     change = ''
#     if order_obj.coin.id == 'PEN':
#         coin = 1
#     elif order_obj.coin.id == 'US$':
#         coin = 2
#         change = float(round(decimal.Decimal(order_obj.change), 2))
#     payment_obj = payment_set.last()
#     payment_description = ""
#     credits = []
#     if payment_obj.payment == 'C':
#         payment_description = 'PAGO AL CREDITO'
#         j = 0
#         for c in payment_set.filter(credit=True).order_by('id'):
#             quota = {
#                 "cuota": j,
#                 "fecha_de_pago": c.date_payment.strftime("%d-%m-%Y"),
#                 "importe": float(round(c.amount, 2))
#             }
#             credits.append(quota)
#             j = j + 1
#     elif payment_obj.payment == 'D':
#         payment_description = 'PAGO EN DEPOSITO' + ' CODIGO OPERACIÓN: ' + str(payment_obj.code_operation)
#     else:
#         payment_description = 'PAGO EN EFECTIVO'
#     total_engraved = decimal.Decimal(sub_total - total_discount)
#     total_invoice = total_engraved * decimal.Decimal(1.1800)
#     total_igv = total_invoice - total_engraved
#     params = {
#         "operacion": "generar_comprobante",
#         "tipo_de_comprobante": type_number,
#         "serie": str(serial),
#         "numero": number,
#         "sunat_transaction": 1,
#         "cliente_tipo_de_documento": int(client_type),
#         "cliente_numero_de_documento": client_document,
#         "cliente_denominacion": client_names,
#         "cliente_direccion": client_address,
#         "cliente_email": client_email,
#         "cliente_email_1": "",
#         "cliente_email_2": "",
#         "fecha_de_emision": date_voucher,
#         "fecha_de_vencimiento": "",
#         "moneda": coin,
#         "tipo_de_cambio": change,
#         "porcentaje_de_igv": 18.00,
#         "descuento_global": float(round(total_discount, 2)),
#         "total_descuento": float(round(total_discount, 2)),
#         "total_anticipo": "",
#         "total_gravada": float(round(total_engraved, 2)),
#         "total_inafecta": "",
#         "total_exonerada": "",
#         "total_igv": float(round(total_igv, 2)),
#         "total_gratuita": "",
#         "total_otros_cargos": "",
#         "total": float(round(total_invoice, 2)),
#         "percepcion_tipo": "",
#         "percepcion_base_imponible": "",
#         "total_percepcion": "",
#         "total_incluido_percepcion": "",
#         "total_impuestos_bolsas": "",
#         "detraccion": detraction,
#         "detraccion_porcentaje": float(percentage),
#         "observaciones": "",
#         "documento_que_se_modifica_tipo": "",
#         "documento_que_se_modifica_serie": "",
#         "documento_que_se_modifica_numero": "",
#         "tipo_de_nota_de_credito": "",
#         "tipo_de_nota_de_debito": "",
#         "enviar_automaticamente_a_la_sunat": 'true',
#         "enviar_automaticamente_al_cliente": 'false',
#         "condiciones_de_pago": "",
#         "medio_de_pago": str(payment_description),
#         "placa_vehiculo": "",
#         "orden_compra_servicio": "",
#         "formato_de_pdf": "",
#         "generado_por_contingencia": "",
#         "bienes_region_selva": "",
#         "servicios_region_selva": "",
#         "items": items,
#         "venta_al_credito": credits,
#     }
#     _url = subsidiary_obj.url
#     _authorization = subsidiary_obj.token
#     url = _url
#     headers = {
#         "Authorization": _authorization,
#         "Content-Type": 'application/json'
#     }
#     response = requests.post(url, json=params, headers=headers)
#
#     if response.status_code == 200:
#         result = response.json()
#         context = {
#             'tipo_de_comprobante': result.get("tipo_de_comprobante"),
#             'serie': result.get("serie"),
#             'numero': result.get("numero"),
#             'aceptada_por_sunat': result.get("aceptada_por_sunat"),
#             'sunat_description': result.get("sunat_description"),
#             'enlace_del_pdf': result.get("enlace_del_pdf"),
#             'cadena_para_codigo_qr': result.get("cadena_para_codigo_qr"),
#             'codigo_hash': result.get("codigo_hash"),
#             'params': params
#         }
#     else:
#         result = response.json()
#         context = {
#             'errors': result.get("errors"),
#             'codigo': result.get("codigo"),
#         }
#     return context
#
#
# def cancel_sunat(pk: int):
#     if pk:
#         bill_obj = Bill.objects.get(id=int(pk))
#         subsidiary_obj = bill_obj.order.subsidiary
#         params = {
#             "operacion": "generar_anulacion",
#             "tipo_de_comprobante": str(bill_obj.type),
#             "serie": str(bill_obj.serial),
#             "numero": str(bill_obj.number),
#             "motivo": "ERROR DEL SISTEMA",
#             "codigo_unico": ""
#         }
#         _url = subsidiary_obj.url
#         _authorization = subsidiary_obj.token
#         url = _url
#         headers = {
#             "Authorization": _authorization,
#             "Content-Type": 'application/json'
#         }
#         response = requests.post(url, json=params, headers=headers)
#
#         if response.status_code == 200:
#             result = response.json()
#             context = {
#                 'numero': result.get("numero"),
#                 'enlace': result.get("enlace"),
#                 'sunat_ticket_numero': result.get("sunat_ticket_numero"),
#                 'aceptada_por_sunat': result.get("aceptada_por_sunat"),
#                 'enlace_del_pdf': result.get("enlace_del_pdf"),
#                 'params': params
#             }
#         else:
#             result = response.json()
#             context = {
#                 'errors': result.get("errors"),
#                 'codigo': result.get("codigo"),
#             }
#         return context
#
#
# def credit_note(pk):
#     if pk:
#         bill_obj = Bill.objects.get(id=int(pk))
#         order_obj = bill_obj.order
#         subsidiary_obj = order_obj.subsidiary
#         serial = bill_obj.serial
#         type_number = 3
#         number = get_bill_number(serial, type_number)
#         detail_set = OrderDetail.objects.filter(order=order_obj)
#         client_obj = order_obj.client
#         date_voucher = datetime.now().strftime("%d-%m-%Y")
#         date_order = order_obj.create_at
#         items = []
#         index = 1
#         sub_total = 0
#         total = 0
#         total_discount = decimal.Decimal(order_obj.discount_output)
#         for d in detail_set.filter(operation='S', is_state=False):
#             total_item_igv = d.quantity * d.price
#             price_item_igv = d.price
#             price_item_sin_igv = d.price / decimal.Decimal(1.1800)
#             total_item_sin_igv = total_item_igv / decimal.Decimal(1.1800)
#             igv_item = total_item_igv - total_item_sin_igv
#             total = total + total_item_igv
#             sub_total = sub_total + total_item_sin_igv
#             item = {
#                 "item": index,  # index para los detalles
#                 "unidad_de_medida": str(d.unit.name),  # NIU viene del nubefact NIU=PRODUCTO
#                 "codigo": str(d.product.code),  # codigo del producto opcional
#                 "codigo_producto_sunat": "10000000",  # codigo del producto excel-sunat
#                 "descripcion": str(d.product.name),
#                 "cantidad": float(round(d.quantity, 2)),
#                 "valor_unitario": float(round(price_item_sin_igv, 2)),  # valor unitario sin IGV
#                 "precio_unitario": float(round(price_item_igv, 2)),  # valor unitario con IGV
#                 "descuento": "",
#                 "subtotal": float(round(total_item_sin_igv, 2)),  # total sin igv
#                 # resultado del valor unitario por la cantidad menos el descuento
#                 "tipo_de_igv": 1,  # operacion onerosa
#                 "igv": float(round(igv_item, 2)),
#                 "total": float(round(total_item_igv, 2)),  # total con igv
#                 "anticipo_regularizacion": 'false',
#                 "anticipo_documento_serie": "",
#                 "anticipo_documento_numero": "",
#             }
#             items.append(item)
#             index = index + 1
#         client_type = client_obj.type.id
#         client_names = client_obj.full_name
#         client_document = client_obj.document
#         client_address = client_obj.address
#         client_email = client_obj.email
#         coin = ''
#         change = ''
#         if order_obj.coin.id == 'PEN':
#             coin = 1
#         elif order_obj.coin.id == 'US$':
#             coin = 2
#             change = float(round(decimal.Decimal(order_obj.change), 2))
#
#         total_engraved = decimal.Decimal(sub_total - total_discount)
#         total_invoice = total_engraved * decimal.Decimal(1.1800)
#         total_igv = total_invoice - total_engraved
#         params = {
#             "operacion": "generar_comprobante",
#             "tipo_de_comprobante": type_number,
#             "serie": str(serial),
#             "numero": number,
#             "sunat_transaction": 1,
#             "cliente_tipo_de_documento": int(client_type),
#             "cliente_numero_de_documento": client_document,
#             "cliente_denominacion": client_names,
#             "cliente_direccion": client_address,
#             "cliente_email": client_email,
#             "cliente_email_1": "",
#             "cliente_email_2": "",
#             "fecha_de_emision": date_voucher,
#             "fecha_de_vencimiento": "",
#             "moneda": coin,
#             "tipo_de_cambio": change,
#             "porcentaje_de_igv": 18.00,
#             "descuento_global": float(round(total_discount, 2)),
#             "total_descuento": float(round(total_discount, 2)),
#             "total_anticipo": "",
#             "total_gravada": float(round(total_engraved, 2)),
#             "total_inafecta": "",
#             "total_exonerada": "",
#             "total_igv": float(round(total_igv, 2)),
#             "total_gratuita": "",
#             "total_otros_cargos": "",
#             "total": float(round(total_invoice, 2)),
#             "percepcion_tipo": "",
#             "percepcion_base_imponible": "",
#             "total_percepcion": "",
#             "total_incluido_percepcion": "",
#             "total_impuestos_bolsas": "",
#             "detraccion": "false",
#             "detraccion_porcentaje": "",
#             "observaciones": "",
#             "documento_que_se_modifica_tipo": str(bill_obj.type),
#             "documento_que_se_modifica_serie": str(bill_obj.serial),
#             "documento_que_se_modifica_numero": str(bill_obj.number),
#             "tipo_de_nota_de_credito": 1,
#             "tipo_de_nota_de_debito": "",
#             "enviar_automaticamente_a_la_sunat": 'true',
#             "enviar_automaticamente_al_cliente": 'false',
#             "condiciones_de_pago": "",
#             "medio_de_pago": "",
#             "placa_vehiculo": "",
#             "orden_compra_servicio": "",
#             "formato_de_pdf": "",
#             "generado_por_contingencia": "",
#             "bienes_region_selva": "",
#             "servicios_region_selva": "",
#             "items": items,
#             "venta_al_credito": "",
#         }
#         url = subsidiary_obj.url
#         _authorization = subsidiary_obj.token
#         headers = {"Authorization": _authorization, "Content-Type": 'application/json'}
#         response = requests.post(url, json=params, headers=headers)
#
#         if response.status_code == 200:
#             result = response.json()
#             context = {
#                 'tipo_de_comprobante': result.get("tipo_de_comprobante"),
#                 'serie': result.get("serie"),
#                 'numero': result.get("numero"),
#                 'aceptada_por_sunat': result.get("aceptada_por_sunat"),
#                 'sunat_description': result.get("sunat_description"),
#                 'enlace_del_pdf': result.get("enlace_del_pdf"),
#                 'cadena_para_codigo_qr': result.get("cadena_para_codigo_qr"),
#                 'codigo_hash': result.get("codigo_hash"),
#                 'params': params
#             }
#         else:
#             result = response.json()
#             context = {
#                 'errors': result.get("errors"),
#                 'codigo': result.get("codigo"),
#             }
#         return context
