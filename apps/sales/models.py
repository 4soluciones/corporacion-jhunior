import decimal
from django.db import models
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Adjust
from apps.accounting.models import Payments
from apps.hrm.models import Person, Subsidiary


class Product(models.Model):
    TYPE_CHOICES = (('A', 'ARMADO'), ('P', 'PIEZA'))
    id = models.AutoField(primary_key=True)
    code = models.CharField('Codigo', max_length=20, null=True, blank=True)
    name = models.CharField('Nombre', max_length=300, null=True, blank=True)
    description = models.CharField('Descripción', max_length=300, null=True, blank=True)
    family = models.ForeignKey('Family', on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField('Tipo Producto', max_length=1, choices=TYPE_CHOICES, default='P')

    # photo = models.ImageField(upload_to='product/',
    #                           default='product/product0.jpg', blank=True)
    # photo_thumbnail = ImageSpecField([Adjust(contrast=1.2, sharpness=1.1), ResizeToFill(
    #     100, 100)], source='photo', format='JPEG', options={'quality': 90})
    is_state = models.BooleanField('Estado', default=True)
    width = models.CharField('Ancho', max_length=100, null=True, blank=True)
    length = models.CharField('Largo', max_length=100, null=True, blank=True)
    height = models.CharField('Alto', max_length=100, null=True, blank=True)
    store = models.CharField('Alamacen', max_length=100, null=True, blank=True)
    minimum = models.DecimalField('Stock Minimo', max_digits=30, decimal_places=4, default=0)
    stock = models.DecimalField('Stock Producto', max_digits=30, decimal_places=4, default=0)
    relation = models.CharField('Codigo Relacional', max_length=100, null=True, blank=True)
    is_discount = models.BooleanField('Descuento', default=False)
    invoice_stock = models.DecimalField('Invoice Stock', max_digits=30, decimal_places=4, default=0)

    def __str__(self):
        return str(self.name)

    def valued_total(self):
        if self.stock:
            presenting_set = Presentation.objects.filter(product=self, unit='NIU', quantity=decimal.Decimal(1.0000),
                                                         quantity_niu=1)
            if presenting_set.exists():
                price = presenting_set.first().price
                return round(self.stock * decimal.Decimal(price), 4)
            else:
                return decimal.Decimal(0.0000)
        else:
            return decimal.Decimal(0.0000)

    def price_unit(self):
        if self.presentation_set:
            presenting_set = Presentation.objects.filter(product=self, unit='NIU', quantity=decimal.Decimal(1.0000),
                                                         quantity_niu=1)
            if presenting_set.exists():
                price = presenting_set.first().price
                return round(price, 4)
            else:
                return decimal.Decimal(0.0000)
        else:
            return decimal.Decimal(0.0000)

    def measure(self):
        if self.width:
            width = str(self.width.strip())
        else:
            width = ''
        if self.length:
            self.length = (self.length).strip()
            if self.length != 'NULL' and self.length != 'NONE' and self.length != '' and len(self.length) > 0:
                length = ' x ' + str(self.length.strip())
            else:
                length = ''
        else:
            length = ''
        if self.height:
            self.height = (self.height).strip()
            if self.height != 'NULL' and self.height != 'NONE' and self.height != '' and len(self.height) > 0:
                height = ' x ' + str(self.height.strip())
            else:
                height = ''
        else:
            height = ''

        return str(width) + str(length) + str(height)

    def complete_name(self):
        return self.name + ' ' + self.measure()

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'


class Presentation(models.Model):
    UNIT_CHOICES = (('NIU', 'UNIDAD'), ('KGM', 'KILO'), ('BG', 'BOLSA'), ('BX', 'CAJA'))
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    unit = models.CharField('Unidad', max_length=3, choices=UNIT_CHOICES, default='NIU')
    price = models.DecimalField('Precio de Venta', max_digits=10, decimal_places=4, default=0)
    quantity = models.DecimalField('Cantidad Minima', max_digits=10, decimal_places=4, default=0)
    quantity_niu = models.IntegerField('Cantidad Unidades', default=1)
    is_elderly = models.BooleanField('Precio Mayor', default=False)
    is_corporate = models.BooleanField('Venta Corporativa', default=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Presentación'
        verbose_name_plural = 'Presentaciones'


# class ProductDetail(models.Model):
#     id = models.AutoField(primary_key=True)
#     input = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='input')
#     output = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='output')
#
#     def __str__(self):
#         return str(self.output.name)
#
#     class Meta:
#         verbose_name = 'Detalle Producto'
#         verbose_name_plural = 'Detalle Productos'


class Family(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Nombre Familia', max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Familia'
        verbose_name_plural = 'Familias'


class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Nombre Marca', max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'


# class Unit(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField('Abreviatura', max_length=5, unique=True)
#     description = models.CharField('Descripción', max_length=100, unique=True)
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name = 'Unidad'
#         verbose_name_plural = 'Unidades'


class Order(models.Model):
    TYPE_CHOICES = (('T', 'COTIZACIÓN'), ('V', 'VENTA'), ('C', 'COMPRA'))
    COIN_CHOICES = (('1', 'SOLES'), ('2', 'DOLARES'))
    MOTIVE_CHOICES = (('01', 'VENTA'), ('14', 'VENTA SUJETA A CONFIRMACION DEL COMPRADOR'), ('02', 'COMPRA'),
                      ('04', 'TRASLADO ENTRE ESTABLECIMIENTOS DE LA MISMA EMPRESA'),
                      ('18', 'TRASLADO EMISOR ITINERANTE CP'),
                      ('08', 'IMPORTACION'), ('09', 'EXPORTACION'), ('13', 'OTROS'), ('06', 'DEVOLUCION'),)
    DOC_CHOICES = (('0', 'ORDEN'), ('1', 'FACTURA ELECTRÓNICA'), ('2', 'BOLETA ELECTRÓNICA'), ('3', 'NOTA DE CREDITO'),
                   ('4', 'NOTA DE DEBITO'), ('5', 'GUIA DE REMISION'))
    ADD_CHOICES = (('N', 'NINGUNA'), ('G', 'GUIA DE REMISIÓN'))
    MODALITY_TRANSPORT_CHOICES = (('1', 'PUBLICO'), ('2', 'PRIVADO'))
    STATUS_CHOICES = (
        ('P', 'PENDIENTE'), ('R', 'REALIZADA'), ('E', 'EMITIDO'), ('A', 'ANULADA'), ('N', 'NOTA DE CREDITO'),
        ('G', 'GUIA DE REMISION'))
    CONDITION_CHOICES = (('R', 'REALIZADO'), ('PA', 'PENDIENTE ANULACION'), ('A', 'ANULADA'))
    id = models.AutoField(primary_key=True)
    type = models.CharField('TIPO', max_length=1, choices=TYPE_CHOICES, default='T')
    doc = models.CharField('Documento', max_length=1, choices=DOC_CHOICES, default='0')
    add = models.CharField('Adicionales', max_length=1, choices=ADD_CHOICES, default='N')
    number = models.IntegerField(verbose_name='CORRELATIVO', null=True, blank=True)
    correlative = models.IntegerField(verbose_name='CORRELATIVO', null=True, blank=True)
    status = models.CharField('ESTADO', max_length=1, choices=STATUS_CHOICES, default='P')
    total = models.DecimalField('TOTAL', max_digits=30, decimal_places=6, default=0)
    total_discount = models.DecimalField('DESCUENTO', max_digits=30, decimal_places=4, default=0)
    coin = models.CharField('TIPO', max_length=1, choices=COIN_CHOICES, default='1')
    change = models.DecimalField('CAMBIO DE MONEDA', max_digits=30, decimal_places=4, default=1)
    create_at = models.DateField(null=True, blank=True)
    update_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True, blank=True)
    person = models.ForeignKey(Person, verbose_name='CLIENTE/PROVEEDOR',
                               on_delete=models.SET_NULL, null=True, blank=True)
    quotation = models.IntegerField(verbose_name='COTIZACION', null=True, blank=True)
    is_igv = models.BooleanField('IGV', default=True)
    date_document = models.DateField(null=True, blank=True)
    invoice_number = models.CharField('Numero Factura', max_length=50, null=True, blank=True)
    invoice_date = models.DateField("Fecha Ingreso", null=True, blank=True)
    license_plate = models.CharField('Placa', max_length=50, null=True, blank=True)
    paid = models.DecimalField('PAGADO', max_digits=30, decimal_places=4, default=0)
    bill_serial = models.CharField(max_length=50, null=True, blank=True, default='-')
    bill_type = models.CharField('TIPO', max_length=2, null=True, blank=True)
    bill_number = models.IntegerField(verbose_name='CORRELATIVO', null=True, blank=True)
    bill_status = models.CharField('Sunat Status', max_length=5, null=True, blank=True)
    bill_description = models.CharField('Sunat descripcion', max_length=500, null=True, blank=True)
    bill_enlace_pdf = models.CharField('Sunat Enlace Pdf', max_length=500, null=True, blank=True)
    bill_date = models.DateTimeField(null=True, blank=True)
    bill_qr = models.CharField('Codigo QR', max_length=500, null=True, blank=True)
    bill_hash = models.CharField('Codigo Hash', max_length=500, null=True, blank=True)
    subsidiary = models.ForeignKey(Subsidiary, on_delete=models.CASCADE, null=True, blank=True)

    note_serial = models.CharField(max_length=50, null=True, blank=True, default='-')
    note_type = models.CharField('TIPO', max_length=2, null=True, blank=True)
    note_number = models.IntegerField(verbose_name='CORRELATIVO', null=True, blank=True)
    note_status = models.CharField('Sunat Status', max_length=5, null=True, blank=True)
    note_description = models.CharField('Sunat descripcion', max_length=500, null=True, blank=True)
    note_enlace_pdf = models.CharField('Sunat Enlace Pdf', max_length=500, null=True, blank=True)
    note_date = models.DateField(null=True, blank=True)
    note_qr = models.CharField('Codigo QR', max_length=500, null=True, blank=True)
    note_hash = models.CharField('Codigo Hash', max_length=500, null=True, blank=True)
    note_total = models.DecimalField('Total Nota Credito', max_digits=30, decimal_places=6, default=0)

    guide_modality_transport = models.CharField('Modalidad de transporte guia', max_length=1,
                                                choices=MODALITY_TRANSPORT_CHOICES, default='1')
    guide_serial = models.CharField(max_length=50, null=True, blank=True, default='-')
    guide_type = models.CharField('TIPO', max_length=2, null=True, blank=True)
    guide_number = models.IntegerField(verbose_name='CORRELATIVO', null=True, blank=True)
    guide_motive = models.CharField('Motivo Guia', max_length=2, choices=MOTIVE_CHOICES, default='1')
    guide_status = models.CharField('Sunat Status', max_length=5, null=True, blank=True)
    guide_description = models.CharField('Sunat descripcion', max_length=500, default='-')
    guide_enlace_pdf = models.CharField('Sunat Enlace Pdf', max_length=500, null=True, blank=True)
    guide_date = models.DateTimeField(null=True, blank=True)
    guide_qr = models.CharField('Codigo QR', max_length=500, null=True, blank=True)
    guide_hash = models.CharField('Codigo Hash', max_length=500, null=True, blank=True)
    guide_origin = models.CharField('Ubigeo Origen', max_length=10, null=True, blank=True)
    guide_destiny = models.CharField('Ubigeo Destino', max_length=10, null=True, blank=True)
    guide_transfer = models.DateTimeField(null=True, blank=True)
    guide_truck = models.CharField('Vehiculo', max_length=50, null=True, blank=True)
    guide_driver_name = models.CharField('Nombre conductor', max_length=100, null=True, blank=True)
    guide_driver_lastname = models.CharField('Apellido conductor', max_length=100, null=True, blank=True)
    guide_driver_dni = models.CharField('Documento conductor', max_length=15, null=True, blank=True)
    guide_driver_license = models.CharField('Licencia conductor', max_length=15, null=True, blank=True)
    guide_driver_full_name = models.CharField('Nombre Completo conductor', max_length=100, null=True, blank=True)
    guide_package = models.DecimalField('Bulto', max_digits=30, decimal_places=4, default=0)
    guide_weight = models.DecimalField('Peso', max_digits=30, decimal_places=4, default=0)
    guide_carrier_document = models.CharField('Numero documento transportista', max_length=11, null=True, blank=True)
    guide_carrier_names = models.CharField('Razon social transportista', max_length=200, null=True, blank=True)
    guide_origin_address = models.CharField('Direccion Origen', max_length=200, null=True, blank=True)
    guide_destiny_address = models.CharField('Direccion Origen', max_length=200, null=True, blank=True)
    parent_order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True)
    condition = models.CharField('Condition', max_length=2, choices=CONDITION_CHOICES, default='R')
    guide_register_mtc = models.CharField('Registro MTC', max_length=200, null=True, blank=True)
    invoice_id = models.IntegerField(default=0)
    guide_id = models.IntegerField(default=0)
    note_id = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)

    def total_payment(self):
        if self.type == 'V':
            amount = Payments.objects.filter(order=self, operation='O', type='I').exclude(payment='C').aggregate(
                r=Coalesce(Sum('amount'), decimal.Decimal('0'))).get('r')
            return round(amount, 4)
        elif self.type == 'C':
            amount = Payments.objects.filter(order__id=self.id, operation='O', type='E').exclude(
                payment='C').aggregate(
                r=Coalesce(Sum('amount'), 0)).get('r')
            return round(amount, 4)

    def payment_invoice(self):
        if self.type == 'V':
            amount = Payments.objects.filter(order=self, operation='O', type='I', credit=False).exclude(
                payment='C').aggregate(
                r=Coalesce(Sum('amount'), decimal.Decimal('0'))).get('r')
            return round(amount, 4)

    def invoice_total(self):
        if self.type == 'V':
            total = decimal.Decimal(0.00)
            for d in OrderDetail.objects.filter(order=self, is_state=True, is_invoice=True):
                total = total + decimal.Decimal(d.amount())
            return round(total, 4)

    def total_debt(self):
        total_payment = self.total_payment()
        total = self.total
        t = decimal.Decimal(total) - decimal.Decimal(total_payment)
        return round(t, 4)

    def get_code(self):
        if self.type == 'C' and self.doc == '1':
            code = str(self.create_at.year)[2:] + str(self.create_at.month).zfill(2) + str(self.correlative).zfill(3)
            return code
        else:
            return '-'

    def get_purchase_total(self):
        if self.type == 'C':
            total = decimal.Decimal(0.00)
            for d in OrderDetail.objects.filter(order=self):
                total = total + decimal.Decimal(d.amount())
            return round(total, 4)

    def get_purchase_igv(self):
        if self.type == 'C':
            base = self.get_purchase_total()
            igv = base * 0.18
            return round(igv, 4)

    def get_purchase_base_plus_igv(self):
        if self.type == 'C':
            base = self.get_purchase_total()
            igv = self.get_purchase_igv()
            total = base + igv
            return round(total, 4)

    def sum_total(self):
        response = 0
        if OrderDetail.objects.filter(order__id=self.pk, is_state=True, is_invoice=True).exists():
            for s in OrderDetail.objects.filter(order__id=self.pk, is_state=True, is_invoice=True):
                response = response + s.amount()
        return response

    def sum_total_purchase(self):
        response = 0
        if OrderDetail.objects.filter(order__id=self.pk, is_state=True).exists():
            for s in OrderDetail.objects.filter(order__id=self.pk, is_state=True):
                response = response + s.amount()
        return response

    def sum_total_annulled(self):
        response = 0
        if OrderDetail.objects.filter(order__id=self.pk, is_state=False, is_invoice=False).exists():
            for s in OrderDetail.objects.filter(order__id=self.pk, is_state=False, is_invoice=False):
                response = response + s.amount()
        return response

    def validate_bill_date(self):
        import datetime
        my_date = datetime.datetime.now()
        # date_now = my_date.strftime("%Y-%m-%d")
        flag = False
        if my_date.date() > self.bill_date.date():
            flag = True
        return flag

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Ordenes'


class OrderDetail(models.Model):
    OPERATION_CHOICES = (('E', 'Entrada'), ('S', 'Salida'))
    UNIT_CHOICES = (('NIU', 'UNIDAD'), ('KGM', 'KILO'), ('BG', 'BOLSA'), ('BX', 'CAJA'))
    id = models.AutoField(primary_key=True)
    operation = models.CharField('Operación', max_length=1, choices=OPERATION_CHOICES, default='E', )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField('Cantidad', max_digits=10, decimal_places=4, default=0)
    quantity_niu = models.IntegerField('Cantidad afectada en unidades', default=0)
    quantity_remaining = models.DecimalField('Cantidad restante en unidades', max_digits=30, decimal_places=4,
                                             default=0)
    price = models.DecimalField('Precio', max_digits=10, decimal_places=6, default=0)
    unit = models.CharField('Unidad', max_length=3, choices=UNIT_CHOICES, default='NIU')
    is_state = models.BooleanField('Estado', default=True)
    is_invoice = models.BooleanField('Facturado', default=False)
    is_considered = models.BooleanField('Considerado', default=True)
    create_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    def amount(self):
        return round(self.quantity * self.price, 6)

    def amount_without_igv(self):
        amount = (decimal.Decimal(self.quantity) * decimal.Decimal(self.price)) / decimal.Decimal(1.18)
        return round(amount, 6)

    def balance_remaining(self):
        return round(self.quantity_remaining * self.price, 6)

    def total_initial(self):
        return round(decimal.Decimal(self.previous()) * decimal.Decimal(self.product.price_unit()), 6)

    def remaining(self):
        entry = OrderDetail.objects.filter(operation='E', id__lte=self.id, is_state=True).aggregate(
            r=Coalesce(Sum('quantity'), 0)).get('r')
        return round(entry, 4)

    def previous(self):
        if self.quantity_niu and self.quantity_remaining:
            if self.order.type == 'V':
                return round(self.quantity_niu + self.quantity_remaining, 4)
            elif self.order.type == 'C':
                return round(self.quantity_remaining - self.quantity_niu, 4)
            else:
                return round(0, 4)
        else:
            return round(0, 4)

    def cancel(self):
        if self.quantity_remaining:
            if self.order.type == 'V':
                return self.quantity_remaining - self.quantity_niu
            elif self.order.type == 'C':
                return self.quantity_remaining + self.quantity_niu
            else:
                return 0
        else:
            return 0

    class Meta:
        verbose_name = 'Detalle orden'
        verbose_name_plural = 'Detalles de orden'


class Kardex(models.Model):
    OPERATION_CHOICES = (('E', 'Entrada'), ('S', 'Salida'), ('C', 'Inventario inicial'))
    TYPE_DOCUMENT = (('00', 'OTROS'), ('01', 'FACTURA'), ('03', 'BOLETA DE VENTA'), ('07', 'NOTE DE CREDITO'),
                     ('08', 'NOTA DE DEBITO'), ('09', 'GUIA DE REMISION'))
    TYPE_OPERATION = (('01', 'VENTA'), ('02', 'COMPRA'), ('05', 'DEVOLUCION RECIBIDA'), ('06', 'DEVOLUCION ENTREGADA'),
                      ('11', 'TRANSFERENCIA ENTRE ALMACENES'), ('12', 'RETIRO'), ('13', 'MERMAS'),
                      ('16', 'SALDO INICIAL'), ('09', 'DONACION'), ('99', 'OTROS'))
    id = models.AutoField(primary_key=True)
    operation = models.CharField('operación', max_length=1, choices=OPERATION_CHOICES, default='C')
    type_document = models.CharField('Tipo de documento', max_length=2, choices=TYPE_DOCUMENT, default='00')
    type_operation = models.CharField('Tipo de operación', max_length=2, choices=TYPE_OPERATION, default='99')
    quantity = models.DecimalField('Cantidad', max_digits=10, decimal_places=2, default=0)
    price_unit = models.DecimalField('Precio unitario', max_digits=30, decimal_places=15, default=0)
    price_total = models.DecimalField('Precio total', max_digits=30, decimal_places=15, default=0)
    remaining_quantity = models.DecimalField('Cantidad restante', max_digits=10, decimal_places=2, default=0)
    remaining_price = models.DecimalField(
        'Precio restante', max_digits=30, decimal_places=15, default=0)
    remaining_price_total = models.DecimalField(
        'Precio total restante', max_digits=30, decimal_places=15, default=0)
    order_detail = models.ForeignKey('OrderDetail', on_delete=models.SET_NULL, null=True, blank=True)
    create_at = models.DateTimeField(null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Registro de Kardex'
        verbose_name_plural = 'Registros de Kardex'
