import decimal

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Adjust

from apps.sales.models import Order


class User(AbstractUser):
    TYPE_CHOICES = (('A', 'ADMINISTRADOR'), ('V', 'VENTA'), ('C', 'CAJA'))
    document = models.CharField('Documento', max_length=15, null=True, blank=True)
    phone = models.CharField('Celular', max_length=12, null=True, blank=True)
    birth_date = models.DateField('Fecha de nacimiento', null=True, blank=True)
    address = models.CharField('Direccion', max_length=200, null=True, blank=True)
    subsidiary = models.ForeignKey('hrm.Subsidiary', on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ImageField(upload_to='employee/',
                              default='employee/employee0.jpg', blank=True)
    photo_thumbnail = ImageSpecField([Adjust(contrast=1.2, sharpness=1.1), ResizeToFill(
        100, 100)], source='photo', format='JPEG', options={'quality': 90})
    user_work = models.CharField('Ventanilla', max_length=5, null=True, blank=True)
    type = models.CharField('CARGO', max_length=1, choices=TYPE_CHOICES, default='V')
    is_authorization = models.BooleanField('Autorización', default=False)

    def total_order(self):
        total = Order.objects.filter(user=self, type='V')
        n = total.count()
        return n

    def sum_order(self):
        total = Order.objects.filter(user=self, type='V').aggregate(
            r=Coalesce(Sum('total'), decimal.Decimal('0'))).get('r')
        return round(total, 4)
