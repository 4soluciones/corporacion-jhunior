import decimal
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from apps.hrm.models import Subsidiary


class Casing(models.Model):
    TYPE_CHOICES = (('C', 'CAJA EFECTIVO'), ('B', 'CUENTA BANCARIA'))
    id = models.AutoField(primary_key=True)
    name = models.CharField('Nombre', max_length=50)
    description = models.CharField('Descripción', max_length=100, null=True, blank=True)
    type = models.CharField('Tipo', max_length=1, choices=TYPE_CHOICES)
    initial = models.DecimalField(max_digits=10, decimal_places=4, default='0')
    is_enabled = models.BooleanField(default=True)
    subsidiary = models.ForeignKey(Subsidiary, on_delete=models.SET_NULL, null=True, blank=True)
    create_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_status(self):
        status = 'C'
        payment_set = Payments.objects.filter(casing__id=self.id, type__in=['A', 'C'],
                                              subsidiary=self.subsidiary)
        if payment_set:
            status = payment_set.last().type
        return status

    def get_total(self):
        from apps.accounting.views import get_total_money
        total = get_total_money(casing_obj=self)
        t = decimal.Decimal(0.00)
        if total:
            t = total[0].get('total')
        return t

    def total(self):
        payment_set = Payments.objects.filter(subsidiary=self.subsidiary, casing=self)
        t = decimal.Decimal(0.00)
        if payment_set.exists():
            total_i = payment_set.filter(type='I').aggregate(
                r=Coalesce(Sum('amount'), decimal.Decimal(0.00))).get('r')
            total_e = payment_set.filter(type='E').aggregate(
                r=Coalesce(Sum('amount'), decimal.Decimal(0.00))).get('r')
            t = total_i - total_e
        return t

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'


class Payments(models.Model):
    TYPE_CHOICES = (('I', 'INGRESO'), ('E', 'EGRESO'), ('A', 'APERTURA'), ('C', 'CIERRE'))
    PAYMENT_CHOICES = (('E', 'EFECTIVO'), ('D', 'DEPOSITO'), ('C', 'CREDITO'))
    OPERATION_CHOICES = (
        ('O', 'ORDEN'), ('S', 'SALIDA'), ('E', 'ENTRADA'), ('T', 'TRANSFERENCIA'),
        ('R', 'APERTURA/CIERRE'), ('R', 'REEMBOLSO'), ('F', 'FALTANTE'))
    COIN_CHOICES = (('1', 'SOLES'), ('2', 'DOLARES'), ('3', 'EUROS'))
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey('sales.Order', on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField('Tipo', max_length=1, choices=TYPE_CHOICES)
    payment = models.CharField('Pago', max_length=1, choices=PAYMENT_CHOICES)
    operation = models.CharField('Operacion', max_length=1, choices=OPERATION_CHOICES)
    code_operation = models.CharField('Codigo de operacion', max_length=50, null=True, blank=True)
    description = models.CharField('Descripcion de la operacion', max_length=250, default='-')
    amount = models.DecimalField('Monto', max_digits=10, decimal_places=4, default=0)
    coin = models.CharField('Moneda', max_length=1, choices=COIN_CHOICES, default='1')
    change_coin = models.DecimalField('Valor de cambio', max_digits=10, decimal_places=4, default=1)
    date_payment = models.DateField(null=True, blank=True)
    create_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('user.User', verbose_name='Usuario', on_delete=models.CASCADE, null=True, blank=True)
    subsidiary = models.ForeignKey(Subsidiary, verbose_name='Sede', on_delete=models.SET_NULL, null=True, blank=True)
    casing = models.ForeignKey(Casing, verbose_name='Caja/Cuenta', on_delete=models.SET_NULL, null=True, blank=True)
    group = models.IntegerField('Grupo', default=0)
    credit = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    # def get_debt(self):
    #     total = Payments.objects.filter(order=self.order, status='R', operation='O').aggregate(
    #         r=Coalesce(Sum('amount'), 0)).get('r')
    #     return round(total, 2)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'


class MoneyChange(models.Model):
    id = models.AutoField(primary_key=True)
    search_date = models.DateField('Fecha de busqueda', null=True, blank=True)
    sunat_date = models.DateField('Fecha de sunat', null=True, blank=True)
    sell = models.DecimalField('Venta', max_digits=10, decimal_places=4, default=0)
    buy = models.DecimalField('Compra', max_digits=10, decimal_places=4, default=0)

    def __str__(self):
        return str(self.id)