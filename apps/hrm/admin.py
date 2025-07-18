from django.contrib import admin

from .models import Subsidiary, Person


class SubsidiaryAdmin(admin.ModelAdmin):
    fields = ['name', 'serial', 'address', 'phone', 'ruc', 'business_name',
              'legal_representative_name', 'legal_representative_dni']
    ordering = ('id',)


admin.site.register(Subsidiary, SubsidiaryAdmin)


admin.site.register(Person)
