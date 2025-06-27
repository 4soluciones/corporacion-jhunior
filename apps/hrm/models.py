from django.db import models


class Subsidiary(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    serial = models.CharField(max_length=4, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=45, null=True, blank=True)
    email = models.EmailField(max_length=45, null=True, blank=True)
    ruc = models.CharField('RUC', max_length=11, null=True, blank=True)
    business_name = models.CharField('Razón social', max_length=100, null=True, blank=True)
    representative_name = models.CharField(max_length=100, null=True, blank=True)
    representative_dni = models.CharField(max_length=45, null=True, blank=True)
    url = models.CharField(max_length=500, null=True, blank=True)
    token = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'


class Person(models.Model):
    TYPE_CHOICES = (
        ('C', 'Cliente'), ('P', 'Proveedor'))
    DOCUMENT_CHOICES = (
        ('1', 'DNI'), ('6', 'RUC'))
    id = models.AutoField(primary_key=True)
    type = models.CharField('Cliente - Proveedor', max_length=1, choices=TYPE_CHOICES, default='C', db_index=True)
    document = models.CharField('Tipo Documento', max_length=1, choices=DOCUMENT_CHOICES, default='1')
    number = models.CharField('Numero documento', max_length=15, null=True, blank=True, db_index=True)
    names = models.CharField('Nombres y Apellidos', max_length=200, null=True, blank=True, db_index=True)
    phone = models.CharField(max_length=15, null=True, blank=True, db_index=True)
    email = models.EmailField('Correo', max_length=100, null=True, blank=True)
    address = models.CharField('Direccion', max_length=200, null=True, blank=True, db_index=True)
    license = models.CharField('Licencia de conducir', max_length=15, null=True, blank=True)
    is_enabled = models.BooleanField(default=True, db_index=True)
    discount = models.ForeignKey('hrm.Discount', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.names)

    class Meta:
        verbose_name = 'Cliente - Proveedor'
        verbose_name_plural = 'Clientes - Proveedores'
        indexes = [
            models.Index(fields=['type', 'is_enabled']),
            models.Index(fields=['names', 'number']),
        ]


class Discount(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.DecimalField('Descuento (%)', max_digits=5, decimal_places=2, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.value}%"
