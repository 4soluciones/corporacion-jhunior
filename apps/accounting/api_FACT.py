import requests

from .format_to_dates import utc_to_local
from .models import *
from django.db.models import Max
from datetime import datetime
import datetime

from .sunat import number_note
from ..sales.models import Order, OrderDetail, Product

GRAPHQL_URL = "https://ng.tuf4ctur4.net.pe/graphql"
# GRAPHQL_URL = "http://192.168.1.80:9050/graphql"

tokens = {
    "20614357194": "gAAAAABoXwfF4kUG3BWN1Ac2tbOyH2YLxHklwr9lGDwmqTndA_nQzv_wjE-LOS0cV1rvMHHCed6fDpOYtsZXJtGA42xWtS0O2g==",
}


def send_sunat_4_fact(order_id):  # FACTURA Y BOLETA 4 FACT
    order_obj = Order.objects.get(id=int(order_id))
    person_obj = order_obj.person
    serial = str(order_obj.bill_serial)
    correlative = int(order_obj.bill_number)
    register_date = order_obj.bill_date
    formatdate = order_obj.bill_date.strftime("%Y-%m-%d")
    hour_date = register_date.strftime("%H:%M:%S")

    items = []
    index = 1
    sub_total = 0
    total = 0
    igv_total = 0
    _base_total_v = 0
    _base_amount_v = 0
    _igv = 0

    type_document_code = order_obj.doc

    if order_obj.doc == '2':
        type_document_code = '03'
    if order_obj.doc == '1':
        type_document_code = '01'

    details = OrderDetail.objects.filter(order=order_obj, is_invoice=True, is_state=True)
    if order_obj.condition == 'PA':
        details = OrderDetail.objects.filter(order=order_obj, is_invoice=True, operation='S')

    for d in details:
        # base_total = d.quantity_sold * d.price_unit  # 5 * 20 = 100
        # base_amount = base_total / decimal.Decimal(1.1800)  # 100 / 1.18 = 84.75
        # igv = base_total - base_amount  # 100 - 84.75 = 15.25
        # sub_total = sub_total + base_amount
        # total = total + base_total
        # igv_total = igv_total + igv
        # _base_amount_v = float(round((base_amount / d.quantity_sold), 6))

        amount_igv = d.quantity * d.price
        amount_sin_igv = amount_igv / decimal.Decimal(1.1800)
        price_igv = d.price
        price_sin_igv = price_igv / decimal.Decimal(1.1800)
        item_igv = round(amount_igv, 4) - round(amount_sin_igv, 4)
        sub_total = sub_total + round(amount_sin_igv, 4)
        total = total + amount_igv
        igv_total = igv_total + item_igv
        product_name = str(d.product.name).replace('"', "'")
        product_measure = str(d.product.measure()).replace('"', "'")

        item = {
            "index": str(index),
            "codigoUnidad": str(d.unit),
            "codigoProducto": str(d.product.code),
            "codigoSunat": "10000000",
            "producto": product_name + " " + product_measure,
            "cantidad": float(round(d.quantity, 4)),
            "precioBase": float(round(price_sin_igv, 6)),
            "tipoIgvCodigo": "10"
        }
        items.append(item)

    items_graphql = ", ".join(
        f"""{{  
               producto: "{item['producto']}", 
               cantidad: {item['cantidad']}, 
               precioBase: {item['precioBase']}, 
               codigoSunat: "{item['codigoSunat']}",
               codigoProducto: "{item['codigoProducto']}",
               codigoUnidad: "{item['codigoUnidad']}",                                            
               tipoIgvCodigo: "{item['tipoIgvCodigo']}" 
        }}"""
        for item in items
    )

    items_graphql = f"[{items_graphql}]"

    client_number = '00000000'
    client_names = 'CLIENTES VARIOS'
    client_address = '-'
    client_document = '-'
    # client_id = ''
    if person_obj:
        # client_id = person_obj.id
        client_number = person_obj.number
        client_names = str(person_obj.names).replace('"', "'")
        client_address = str(person_obj.address).replace('"', "'")
        client_document = str(person_obj.document).replace('"', "'")
    if client_number == '0':
        client_number = '00000000'
        client_document = '1'
    elif client_number == '1':
        client_number = '00000000'
        client_document = '1'
    # elif client_number == str(client_id):
    #     client_type = '-'

    graphql_query = f"""
    mutation RegisterSale  {{
        registerSale(            
            cliente: {{
                razonSocialNombres: "{client_names}",
                numeroDocumento: "{client_number}",
                codigoTipoEntidad: {client_document},
                clienteDireccion: "{client_address}"
            }},
            venta: {{
                serie: "{serial}",
                numero: "{correlative}",
                fechaEmision: "{formatdate}",
                horaEmision: "{hour_date}",
                fechaVencimiento: "",
                monedaId: 1,                
                formaPagoId: 1,
                totalGravada: {float(round(sub_total, 2))},
                totalDescuentoGlobalPorcentaje: 0,
                totalDescuentoGlobal: 0,
                totalIgv: {float(round(igv_total, 2))},
                totalExonerada: 0,
                totalInafecta: 0,
                totalImporte: {float(round(total, 2))},
                totalAPagar: {float(round(total, 2))},
                tipoDocumentoCodigo: "{type_document_code}",
                nota: ""
            }},
            items: {items_graphql}
        ) {{
            message
            success
            operationId
        }}
    }}
    """
    # print(graphql_query)

    token = tokens.get("20614357194", "ID no encontrado")

    HEADERS = {
        "Content-Type": "application/json",
        "token": token
    }

    try:
        response = requests.post(GRAPHQL_URL, json={"query": graphql_query}, headers=HEADERS)
        response.raise_for_status()

        result = response.json()

        success = result.get("data", {}).get("registerSale", {}).get("success")

        if success:
            operation_id = result.get("data", {}).get("registerSale", {}).get("operationId")
            order_obj.invoice_id = int(operation_id)
            order_obj.bill_type = order_obj.doc
            order_obj.status = 'E'
            order_obj.bill_status = 'True'
            order_obj.bill_description = f'La Factura numero {serial}-{correlative}, ha sido aceptado'
            order_obj.bill_enlace_pdf = f'https://ng.tuf4ctur4.net.pe/operations/print_invoice/{operation_id}/'
            # order_obj.bill_enlace_pdf = f'http://192.168.1.80:9050/operations/print_invoice/{operation_id}/'
            order_obj.bill_qr = ''
            order_obj.bill_hash = ''
            order_obj.save()
            return {
                "success": success,
                "message": result.get("data", {}).get("registerSale", {}).get("message"),
                "operationId": result.get("data", {}).get("registerSale", {}).get("operationId"),
                "serie": serial,
                "numero": correlative,
                "tipo_de_comprobante": "1",
            }
        else:
            # Maneja el caso en que la operación no fue exitosa
            return {
                "success": False,
                "message": "La operación no fue exitosa, revise la venta e informe a Sistemas",
            }

    except requests.exceptions.RequestException as e:
        return {"error": f"Error en la solicitud: {str(e)}"}
    except ValueError:
        return {"error": "La respuesta no es un JSON válido"}


def send_credit_note_fact(pk, details, motive):
    order_obj = Order.objects.get(id=int(pk))
    serial = str(order_obj.bill_serial)[0] + "N01"
    correlative = number_note(serial, 'N')
    person_obj = order_obj.person
    date_voucher = datetime.datetime.now().strftime("%d-%m-%Y")
    items = []
    index = 1
    sub_total = 0
    total = 0
    total_discount = decimal.Decimal(order_obj.total_discount)
    for d in details:
        if d['quantityReturned']:
            product_id = int(d['productID'])
            product_obj = Product.objects.get(id=product_id)
            description = str(str(product_obj.name).upper() + ' ' + str(product_obj.measure())).replace('"', "'")
            total_item_igv = decimal.Decimal(d['quantityReturned']) * decimal.Decimal(d['price'])
            price_igv = decimal.Decimal(d['price'])
            price_sin_igv = price_igv / decimal.Decimal(1.1800)
            total_item_sin_igv = total_item_igv / decimal.Decimal(1.1800)
            igv_item = total_item_igv - total_item_sin_igv
            total = total + total_item_igv
            sub_total = sub_total + total_item_sin_igv

            item = {
                "index": str(index),
                "codigoUnidad": str(d['unit']),
                "codigoProducto": str(product_obj.code),
                "codigoSunat": "10000000",
                "producto": description,
                "cantidad": round(float(d['quantityReturned']), 4),
                "precioBase": round(price_sin_igv, 6),
                "tipoIgvCodigo": "10"
            }
            items.append(item)

    items_graphql = ", ".join(
        f"""{{  
                   producto: "{item['producto']}", 
                   cantidad: {item['cantidad']}, 
                   precioBase: {item['precioBase']}, 
                   codigoSunat: "{item['codigoSunat']}",
                   codigoProducto: "{item['codigoProducto']}",
                   codigoUnidad: "{item['codigoUnidad']}",                                            
                   tipoIgvCodigo: "{item['tipoIgvCodigo']}" 
            }}"""
        for item in items
    )

    items_graphql = f"[{items_graphql}]"

    client_type = person_obj.document
    client_names = str(person_obj.names).replace('"', "'")
    client_document = person_obj.number
    client_address = str(person_obj.address).replace('"', "'")
    total_engraved = decimal.Decimal(sub_total - total_discount)
    total_invoice = total_engraved * decimal.Decimal(1.1800)
    total_igv = total_invoice - total_engraved

    formatdate = datetime.datetime.now().strftime("%Y-%m-%d")
    hour_date = datetime.datetime.now().strftime("%H:%M:%S")

    type_document_code = order_obj.doc

    if order_obj.doc == '2':
        type_document_code = '03'
    if order_obj.doc == '1':
        type_document_code = '01'

    graphql_query = f"""
        mutation RegisterCreditNote  {{
            registerCreditNote(            
                client: {{
                    razonSocialNombres: "{client_names}",
                    numeroDocumento: "{client_document}",
                    codigoTipoEntidad: {client_type},
                    clienteDireccion: "{client_address}"
                }},
                creditNote: {{
                    serie: "{serial}",
                    numero: "{correlative}",
                    fechaEmision: "{formatdate}",
                    horaEmision: "{hour_date}",
                    fechaVencimiento: "{formatdate}",
                    monedaId: 1,                
                    formaPagoId: 1,
                    totalGravada: {float(total_engraved)},
                    totalDescuentoGlobalPorcentaje: 0,
                    totalDescuentoGlobal: 0,
                    totalIgv: {float(total_igv)},
                    totalExonerada: 0,
                    totalInafecta: 0,
                    totalImporte: {float(round(total_invoice, 2))},
                    totalAPagar: {float(round(total_invoice, 2))},
                    tipoDocumentoCodigo: "07",
                    nota: "",
                    motiveCreditNote: "{motive}"
                }},
                relatedDocuments: {{
                    serial: "{str(order_obj.bill_serial)}"      
                    number: "{str(order_obj.bill_number)}"      
                    codeTypeDocument: "{str(type_document_code)}"      
                }},
                items: {items_graphql}
            ) {{
                message
                error
                operationId
            }}
        }}
        """
    # print(graphql_query)

    token = tokens.get("20614357194", "ID no encontrado")

    HEADERS = {
        "Content-Type": "application/json",
        "token": token
    }

    try:
        response = requests.post(GRAPHQL_URL, json={"query": graphql_query}, headers=HEADERS)
        response.raise_for_status()

        result = response.json()

        success = not result.get("data", {}).get("registerCreditNote", {}).get("error")

        if success:
            operation_id = result.get("data", {}).get("registerCreditNote", {}).get("operationId")
            order_obj.status = 'N'
            order_obj.note_serial = str(serial)
            order_obj.note_type = '3'
            order_obj.note_number = correlative
            order_obj.note_status = 'True'
            order_obj.note_description = f'La Nota de Crédito numero {serial}-{correlative}, ha sido aceptado'
            order_obj.note_enlace_pdf = f'https://ng.tuf4ctur4.net.pe/operations/print_credit_note/{operation_id}/'
            # order_obj.note_enlace_pdf = f'http://192.168.1.80:9050/operations/print_credit_note/{operation_id}/'
            order_obj.note_date = datetime.datetime.now().strftime("%Y-%m-%d")
            # order_obj.note_qr = '20614357194|07|FN01|000163|14.49|95.00|26/04/2025|6|20322628642|58wxWwjO/laYkdbvU5WQVrsEFNDCH2oOY5FCtnLQf6I=|'
            # order_obj.note_hash = result.get("codigo_hash")
            order_obj.note_total = total_invoice
            order_obj.note_id = int(operation_id)
            order_obj.save()
            # return {
            #     "success": success,
            #     "message": result.get("data", {}).get("registerCreditNote", {}).get("message"),
            #     "operationId": result.get("data", {}).get("registerCreditNote", {}).get("operationId"),
            #     "serie": serial,
            #     "numero": correlative,
            #     "tipo_de_comprobante": "3",
            # }
            return {
                "success": success,
                'tipo_de_comprobante': '3',
                "message": result.get("data", {}).get("registerCreditNote", {}).get("message"),
                'serie': str(serial),
                'numero': correlative,
                'enlace_del_pdf': f'https://ng.tuf4ctur4.net.pe/operations/print_credit_note/{operation_id}/'
            }
        else:
            return {
                "success": False,
                "message": "La operación no fue exitosa, revise la venta e informe a Sistemas",
                "error": result.get("data", {}).get("registerCreditNote", {}).get("error"),
            }

    except requests.exceptions.RequestException as e:
        return {"error": f"Error en la solicitud: {str(e)}"}
    except ValueError:
        return {"error": "La respuesta no es un JSON válido"}


def send_guide_fact(pk=None):
    guide_obj = Order.objects.get(id=pk)
    date_transfer = guide_obj.guide_transfer
    date = guide_obj.guide_date
    subsidiary_obj = guide_obj.subsidiary
    person_obj = guide_obj.person
    # Get client information

    client_type_document = person_obj.document
    client_nro_document = person_obj.number
    client_names = str(person_obj.names).replace('"', "'")
    client_address = str(person_obj.address).replace('"', "'")

    if guide_obj.guide_motive == '04':
        client_type_document = '6'
        client_nro_document = subsidiary_obj.ruc
        client_names = str(subsidiary_obj.business_name.upper()).replace('"', "'")
        client_address = str(subsidiary_obj.address.upper()).replace('"', "'")

    # Format dates
    formatdate = date.strftime("%Y-%m-%d")
    formatdate_hour = date.strftime("%H:%M")
    formatdate_transfer = date_transfer.strftime("%Y-%m-%d")

    # Get items
    items = []
    for d in OrderDetail.objects.filter(order=guide_obj, is_invoice=True, is_state=True):
        quantity_sent = decimal.Decimal(d.quantity)
        base_total = quantity_sent * d.price
        base_amount = base_total / decimal.Decimal(1.1800)
        description = str(str(d.product.name).upper() + ' ' + str(d.product.measure())).replace('"', "'")

        item = {
            "producto": description,
            "cantidad": float(quantity_sent),
            "precioBase": float(round(base_amount / quantity_sent, 6)),
            "codigoSunat": "10000000",
            "codigoProducto": str(d.product.code) if d.product.code else "0000",
            "codigoUnidad": "NIU",
            "tipoIgvCodigo": "10"
        }
        items.append(item)

    # Format items for GraphQL
    items_graphql = ", ".join(
        f"""{{
               producto: "{item['producto']}",
               cantidad: {item['cantidad']},
               precioBase: {item['precioBase']},
               codigoSunat: "{item['codigoSunat']}",
               codigoProducto: "{item['codigoProducto']}",
               codigoUnidad: "{item['codigoUnidad']}",
               tipoIgvCodigo: "{item['tipoIgvCodigo']}"
        }}"""
        for item in items
    )
    items_graphql = f"[{items_graphql}]"

    # Determine guide mode and reason
    guide_mode = "01" if guide_obj.guide_modality_transport == "1" else "02"
    guide_reason = guide_obj.guide_motive
    observation = guide_obj.guide_description.replace('\n', '').replace('\r', '')

    type_document_code = guide_obj.doc

    if guide_obj.doc == '2':
        type_document_code = '03'
    if guide_obj.doc == '1':
        type_document_code = '01'

    # Build GraphQL mutation
    graphql_query = f"""
    mutation RegisterGuide {{
        registerGuide(
            client: {{
                razonSocialNombres: "{client_names}",
                numeroDocumento: "{client_nro_document}",
                codigoTipoEntidad: {client_type_document},
                clienteDireccion: "{client_address}",
                clienteTelefono: "{person_obj.phone if person_obj.phone else ''}"
            }},
            guide: {{
                serial: "{guide_obj.guide_serial}",
                number: "{guide_obj.guide_number}",
                guideModeTransfer: "{guide_mode}",
                guideReasonTransfer: "{guide_reason}",
                note: "{observation}",
                emitDate: "{formatdate}",
                emitHour: "{formatdate_hour}"
            }},
            transportation: {{
                transferDate: "{formatdate_transfer}",
                totalWeight: "{guide_obj.guide_weight}",
                quantityPackages: "{guide_obj.guide_package}"
            }},
            points: {{
                guideOriginSerial: "",
                guideOriginAddress: "{guide_obj.guide_origin_address}",
                guideOriginDistrictId: "{guide_obj.guide_origin}",
                guideArrivalSerial: "",
                guideArrivalAddress: "{guide_obj.guide_destiny_address}",
                guideArrivalDistrictId: "{guide_obj.guide_destiny}"
            }},
            carrier: {{
                transportationCompanyDocumentType: "6",
                transportationCompanyDocumentNumber: "{guide_obj.guide_carrier_document}",
                transportationCompanyNames: "{guide_obj.guide_carrier_names}",
                transportationCompanyMtcRegistrationNumber: "",
                mainDriverDocumentNumber: "{guide_obj.guide_driver_dni}",
                mainDriverNames: "{guide_obj.guide_driver_full_name.upper()}",
                mainDriverLicense: "{guide_obj.guide_driver_license.upper()}",
                mainVehicleLicensePlate: "{guide_obj.guide_truck}"
            }},
            items: {items_graphql},
            relatedDocuments: {{
                tipoDocumentoCodigo: "{type_document_code}",
                serie: "{str(guide_obj.bill_serial)}",
                numero: "{str(guide_obj.bill_number)}",
                fechaEmision: "{formatdate}"
            }}
        ) {{
            message
            error
            operationId
        }}
    }}
    """
    # print(graphql_query)

    token = tokens.get("20614357194", "ID no encontrado")

    HEADERS = {
        "Content-Type": "application/json",
        "token": token
    }

    try:
        response = requests.post(GRAPHQL_URL, json={"query": graphql_query}, headers=HEADERS)
        response.raise_for_status()

        result = response.json()

        success = not result.get("data", {}).get("registerGuide", {}).get("error")

        if success:
            operation_id = result.get("data", {}).get("registerGuide", {}).get("operationId")
            guide_obj.guide_id = operation_id
            guide_obj.save()
            return {
                "success": success,
                "message": result.get("data", {}).get("registerGuide", {}).get("message"),
                "operationId": result.get("data", {}).get("registerGuide", {}).get("operationId"),
                "serie": guide_obj.guide_serial,
                "numero": guide_obj.guide_number,
            }
        else:
            return {
                "success": False,
                "message": result.get("data", {}).get("registerGuide", {}).get("message"),
                "error": result.get("data", {}).get("registerGuide", {}).get("error"),
            }

    except requests.exceptions.RequestException as e:
        return {"error": f"Error en la solicitud: {str(e)}"}
    except ValueError:
        return {"error": "La respuesta no es un JSON válido"}


def send_guide_return_fact(pk=None):
    guide_obj = Order.objects.get(id=pk)
    date_transfer = guide_obj.guide_transfer
    date = guide_obj.guide_date
    subsidiary_obj = guide_obj.subsidiary
    person_obj = guide_obj.person
    # Get client information

    client_type_document = person_obj.document
    client_nro_document = person_obj.number
    client_names = str(person_obj.names).replace('"', "'")
    client_address = str(person_obj.address).replace('"', "'")

    if guide_obj.guide_motive == '04':
        client_type_document = '6'
        client_nro_document = subsidiary_obj.ruc
        client_names = str(subsidiary_obj.business_name.upper()).replace('"', "'")
        client_address = str(subsidiary_obj.address.upper()).replace('"', "'")

    # Format dates
    formatdate = date.strftime("%Y-%m-%d")
    formatdate_hour = date.strftime("%H:%M")
    formatdate_transfer = date_transfer.strftime("%Y-%m-%d")

    invoice_number = guide_obj.parent_order.invoice_number
    serial_purchase, correlative_purchase = invoice_number.split('-')
    date_purchase = guide_obj.parent_order.invoice_date.strftime("%Y-%m-%d")
    # print(person_obj.phone)
    # Get items
    items = []
    for d in OrderDetail.objects.filter(order=guide_obj):
        quantity_sent = decimal.Decimal(d.quantity)
        base_total = quantity_sent * d.price
        base_amount = base_total / decimal.Decimal(1.1800)
        description = str(str(d.product.name).upper() + ' ' + str(d.product.measure())).replace('"', "'")

        item = {
            "producto": description,
            "cantidad": float(quantity_sent),
            "precioBase": float(round(base_amount / quantity_sent, 6)),
            "codigoSunat": "10000000",
            "codigoProducto": str(d.product.code) if d.product.code else "0000",
            "codigoUnidad": "NIU",
            "tipoIgvCodigo": "10"
        }
        items.append(item)

    # Format items for GraphQL
    items_graphql = ", ".join(
        f"""{{
               producto: "{item['producto']}",
               cantidad: {item['cantidad']},
               precioBase: {item['precioBase']},
               codigoSunat: "{item['codigoSunat']}",
               codigoProducto: "{item['codigoProducto']}",
               codigoUnidad: "{item['codigoUnidad']}",
               tipoIgvCodigo: "{item['tipoIgvCodigo']}"
        }}"""
        for item in items
    )
    items_graphql = f"[{items_graphql}]"

    # Determine guide mode and reason
    guide_mode = "01" if guide_obj.guide_modality_transport == "1" else "02"
    guide_reason = guide_obj.guide_motive
    observation = guide_obj.guide_description.replace('\n', '').replace('\r', '')
    # Build GraphQL mutation
    graphql_query = f"""
    mutation RegisterGuide {{
        registerGuide(
            client: {{
                razonSocialNombres: "{client_names}",
                numeroDocumento: "{client_nro_document}",
                codigoTipoEntidad: {client_type_document},
                clienteDireccion: "{client_address}",
                clienteTelefono: "{person_obj.phone if person_obj and person_obj.phone and person_obj.phone != 'None' else ''}"
            }},
            guide: {{
                serial: "{guide_obj.guide_serial}",
                number: "{guide_obj.guide_number}",
                guideModeTransfer: "{guide_mode}",
                guideReasonTransfer: "{guide_reason}",
                note: "{observation}",
                emitDate: "{formatdate}",
                emitHour: "{formatdate_hour}"
            }},
            transportation: {{
                transferDate: "{formatdate_transfer}",
                totalWeight: "{guide_obj.guide_weight}",
                quantityPackages: "{guide_obj.guide_package}"
            }},
            points: {{
                guideOriginSerial: "",
                guideOriginAddress: "{guide_obj.guide_origin_address}",
                guideOriginDistrictId: "{guide_obj.guide_origin}",
                guideArrivalSerial: "",
                guideArrivalAddress: "{guide_obj.guide_destiny_address}",
                guideArrivalDistrictId: "{guide_obj.guide_destiny}"
            }},
            carrier: {{
                transportationCompanyDocumentType: "6",
                transportationCompanyDocumentNumber: "{guide_obj.guide_carrier_document}",
                transportationCompanyNames: "{guide_obj.guide_carrier_names}",
                transportationCompanyMtcRegistrationNumber: "",
                mainDriverDocumentNumber: "{guide_obj.guide_driver_dni}",
                mainDriverNames: "{guide_obj.guide_driver_full_name.upper()}",
                mainDriverLicense: "{guide_obj.guide_driver_license.upper()}",
                mainVehicleLicensePlate: "{guide_obj.guide_truck}"
            }},
            items: {items_graphql},
            relatedDocuments: {{
                tipoDocumentoCodigo: "01",
                serie: "{str(serial_purchase)}",
                numero: "{str(correlative_purchase)}",
                fechaEmision: "{date_purchase}"
            }}
        ) {{
            message
            error
            operationId
        }}
    }}
    """
    # print(graphql_query)

    token = tokens.get("20614357194", "ID no encontrado")

    HEADERS = {
        "Content-Type": "application/json",
        "token": token
    }

    try:
        response = requests.post(GRAPHQL_URL, json={"query": graphql_query}, headers=HEADERS)
        response.raise_for_status()

        result = response.json()

        success = not result.get("data", {}).get("registerGuide", {}).get("error")

        if success:
            operation_id = result.get("data", {}).get("registerGuide", {}).get("operationId")
            guide_obj.guide_id = operation_id
            guide_obj.guide_status = True
            guide_obj.bill_enlace_pdf = f'https://ng.tuf4ctur4.net.pe/operations/print_guide/{operation_id}/'
            guide_obj.save()
            return {
                "success": success,
                "message": result.get("data", {}).get("registerGuide", {}).get("message"),
                "operationId": result.get("data", {}).get("registerGuide", {}).get("operationId"),
                "serie": guide_obj.guide_serial,
                "numero": guide_obj.guide_number,
            }
        else:
            return {
                "success": False,
                "message": result.get("data", {}).get("registerGuide", {}).get("message"),
                "error": result.get("data", {}).get("registerGuide", {}).get("error"),
            }

    except requests.exceptions.RequestException as e:
        return {"error": f"Error en la solicitud: {str(e)}"}
    except ValueError:
        return {"error": "La respuesta no es un JSON válido"}

