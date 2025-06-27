from django.contrib import admin

# Register your models here.
from apps.sales.models import Brand, Family

admin.site.register(Brand)
admin.site.register(Family)