import decimal
from datetime import datetime
from http import HTTPStatus

from django.db.models import Prefetch, Subquery, OuterRef, Sum, F
from django.db.models.functions import Coalesce
from django.template import loader
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.db import models

from apps.hrm.models import Subsidiary, Person, Discount
from apps.sales.models import Order, OrderDetail
from apps.user.models import User


class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        pk = self.request.user.id
        current_date = datetime.now()
        current_month = current_date.month
        last_month = current_month - 1
        current_year = current_date.year
        user_set = User.objects.filter(type__in=['V', 'C', 'A'], is_active=True)
        users_dict = []
        for u in user_set:

            total_count_day = Order.objects.filter(
                create_at=current_date.date(),
                type='V',
                user=u,
                payments__isnull=False,
                orderdetail__operation='S',
                orderdetail__is_state=True,
                orderdetail__is_invoice=True,
            ).prefetch_related('payments_set', 'orderdetail_set').distinct('id').count()

            total_count_month = Order.objects.filter(
                create_at__month=current_month,
                type='V',
                user=u,
                payments__isnull=False,
                orderdetail__operation='S',
                orderdetail__is_state=True,
                orderdetail__is_invoice=True,
            ).prefetch_related('payments_set', 'orderdetail_set').distinct('id').count()

            total_day = Order.objects.filter(
                create_at=current_date.date(),
                type='V',
                user=u,
                payments__isnull=False,
            ).prefetch_related('payments_set', 'orderdetail_set').annotate(
                sum_details=Subquery(OrderDetail.objects.filter(order=OuterRef('pk'), operation='S', is_state=True,
                                                                is_invoice=True).annotate(
                    subtotal=Coalesce('quantity', 0) * Coalesce('price', 0)
                ).values('order').annotate(
                    sum_details=Sum('subtotal')).values('sum_details'))
            ).distinct().aggregate(total=Sum('sum_details'))

            total_current_month = Order.objects.filter(
                create_at__month=current_month,
                type='V',
                user=u,
                payments__isnull=False,
            ).prefetch_related('payments_set', 'orderdetail_set').annotate(
                sum_details=Subquery(OrderDetail.objects.filter(order=OuterRef('pk'), operation='S', is_state=True,
                                                                is_invoice=True).annotate(
                    subtotal=Coalesce('quantity', 0) * Coalesce('price', 0)
                ).values('order').annotate(
                    sum_details=Sum('subtotal')).values('sum_details'))
            ).distinct().aggregate(total=Sum('sum_details'))

            # total_year = Order.objects.filter(
            #     create_at__year=current_year,
            #     type='V',
            #     user=u,
            #     payments__isnull=False,
            # ).prefetch_related('payments_set', 'orderdetail_set').annotate(
            #     sum_details=Subquery(OrderDetail.objects.filter(order=OuterRef('pk')).annotate(
            #         subtotal=Coalesce('quantity', 0) * Coalesce('price', 0)
            #     ).values('order').annotate(
            #         sum_details=Sum('subtotal')).values('sum_details'))
            # ).distinct().aggregate(total=Sum('sum_details'))

            total_day = total_day['total']
            if total_day is not None:
                float_total_day = float(total_day)
            else:
                float_total_day = 0

            total_current_month = total_current_month['total']
            if total_current_month is not None:
                float_total_current_month = float(total_current_month)
            else:
                float_total_current_month = 0

            # total_year = total_year['total']
            # if total_year is not None:
            #     float_total_year = float(total_year)
            # else:
            #     float_total_year = 0

            item = {
                'user': u.username,
                'total_day': '{:,}'.format(round(decimal.Decimal(float_total_day), 2)),
                'total_current_month': '{:,}'.format(round(decimal.Decimal(float_total_current_month), 2)),
                # 'total_year': '{:,}'.format(round(decimal.Decimal(float_total_year), 2)),
                'total_count_day': total_count_day,
                'total_count_month': total_count_month,
            }
            users_dict.append(item)
        # print(users_dict)

        total_all_month = Order.objects.filter(
            create_at__month=current_month,
            type='V',
            payments__isnull=False,
        ).prefetch_related('payments_set', 'orderdetail_set').annotate(
            sum_details=Subquery(OrderDetail.objects.filter(order=OuterRef('pk'), operation='S', is_state=True,
                                                            is_invoice=True).annotate(
                subtotal=Coalesce('quantity', 0) * Coalesce('price', 0)
            ).values('order').annotate(
                sum_details=Sum('subtotal')).values('sum_details'))
        ).distinct().aggregate(total=Sum('sum_details'))

        total_month = total_all_month['total']
        if total_month is not None:
            float_total_all_month = float(total_month)
        else:
            float_total_all_month = 0

        context = {
            'current': current_date,
            'user_dict': users_dict,
            'current_date': current_date,
            'current_year': current_year,
            'current_month': current_month,
            'month': get_month(current_month),
            'total_all_month': '{:,}'.format(round(decimal.Decimal(float_total_all_month), 2)),
            'v': User.objects.filter(type='V').count(),
            'c': User.objects.filter(type='C').count(),
            'a': User.objects.filter(type='A').count()
        }
        return context


class SubsidiaryList(ListView):
    model = Subsidiary
    template_name = 'hrm/subsidiary_list.html'


def subsidiary_create(request):
    if request.method == 'GET':
        return render(request, 'hrm/subsidiary.html', {})


def subsidiary_update(request, pk):
    if request.method == 'GET':
        if pk:
            subsidiary_obj = Subsidiary.objects.get(id=int(pk))
            return render(request, 'hrm/subsidiary.html', {
                'subsidiary_obj': subsidiary_obj,
            })


@csrf_exempt
def subsidiary_save(request):
    if request.method == 'POST':
        subsidiary = request.POST.get('subsidiary', '')
        serial = request.POST.get('serial', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        name = request.POST.get('name', '')
        ruc = request.POST.get('ruc', '')
        business_name = request.POST.get('business_name', '')
        address = request.POST.get('address', '')
        representative_name = request.POST.get('representative_name', '')
        representative_dni = request.POST.get('representative_dni', '')
        pk = None
        if subsidiary != '0':
            pk = int(subsidiary)
        obj, created = Subsidiary.objects.update_or_create(
            id=pk,
            defaults={
                "name": name,
                "serial": serial,
                "phone": phone,
                "email": email,
                "ruc": ruc,
                "business_name": business_name,
                "address": address,
                "representative_name": representative_name,
                "representative_dni": representative_dni
            })
        if obj:
            return JsonResponse({
                'success': True,
                'message': 'proceso exitoso'
            }, status=HTTPStatus.OK)
        else:
            return JsonResponse({
                'success': False,
                'message': 'problemas en el proceso'
            }, status=HTTPStatus.OK)


class PersonList(ListView):
    model = Person
    template_name = 'hrm/person_list.html'
    paginate_by = 50  # Mostrar 50 registros por página
    ordering = ['id']  # Ordenamiento por defecto

    def get_queryset(self):
        queryset = self.model.objects.all().values('id',
                                                   'type',
                                                   'document',
                                                   'number',
                                                   'names',
                                                   'phone',
                                                   'address',
                                                   'is_enabled',
                                                   'discount__value')
        
        # Filtro por búsqueda
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                models.Q(names__icontains=search) |
                models.Q(number__icontains=search) |
                models.Q(address__icontains=search) |
                models.Q(phone__icontains=search)
            )
        
        # Filtro por tipo
        person_type = self.request.GET.get('type', '')
        if person_type:
            queryset = queryset.filter(type=person_type)
        
        # Filtro por estado
        is_enabled = self.request.GET.get('enabled', '')
        if is_enabled == 'true':
            queryset = queryset.filter(is_enabled=True)
        elif is_enabled == 'false':
            queryset = queryset.filter(is_enabled=False)
        
        return queryset.order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['selected_type'] = self.request.GET.get('type', '')
        context['selected_enabled'] = self.request.GET.get('enabled', '')
        context['type_choices'] = Person._meta.get_field('type').choices
        return context


def person_create(request):
    if request.method == 'GET':
        return render(request, 'hrm/person.html', {
            'type_set': Person._meta.get_field('type').choices,
            'document_set': Person._meta.get_field('document').choices,
            'discount_set': Discount.objects.all().order_by('value')
        })


def person_update(request, pk):
    if request.method == 'GET':
        if pk:
            person_obj = Person.objects.get(id=int(pk))
            return render(request, 'hrm/person.html', {
                'person_obj': person_obj,
                'type_set': Person._meta.get_field('type').choices,
                'document_set': Person._meta.get_field('document').choices,
                'discount_set': Discount.objects.all().order_by('value')
            })


@csrf_exempt
def person_save(request):
    if request.method == 'POST':
        person = request.POST.get('person', '')
        types = request.POST.get('type', '')
        number = request.POST.get('number', '')
        names = request.POST.get('names', '')
        document = request.POST.get('document', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        discount_id = request.POST.get('discount', '')
        is_enabled = request.POST.get('defaultCheck3', False)
        if is_enabled == 'on':
            is_enabled = True
        
        # Procesar descuento
        discount = None
        if discount_id and discount_id != '0':
            try:
                discount = Discount.objects.get(id=int(discount_id))
            except Discount.DoesNotExist:
                pass
        
        pk = None
        if person != '0':
            pk = int(person)
        update, created = Person.objects.update_or_create(
            id=pk,
            defaults={
                "type": types,
                "document": document,
                "number": number,
                "email": email,
                "phone": phone,
                "names": names,
                "address": address,
                "is_enabled": is_enabled,
                "discount": discount,
            })
        return redirect('hrm:persons')


@csrf_exempt
def update_person(request):
    if request.method == 'POST':
        pk = request.POST.get('pk', '')
        if pk != '' and pk != '0':
            person_obj = Person.objects.get(id=int(pk))
            number = request.POST.get('number', '').strip()
            names = request.POST.get('names', '')

            if names == 'CLIENTES VARIOS':
                return JsonResponse({
                    'success': True,
                    'message': 'CLIENTES VARIOS',
                    'pk': person_obj.id,
                }, status=HTTPStatus.OK)

            if number == '' or number == None:
                return JsonResponse({
                    'success': False,
                    'message': 'Ingrese un numero de documento valido'
                }, status=HTTPStatus.OK)

            if names == '' or names == None:
                return JsonResponse({
                    'success': False,
                    'message': 'Ingrese nombres/razon social valida'
                }, status=HTTPStatus.OK)
            address = request.POST.get('address', '')
            if address:
                address = address.strip()
            phone = request.POST.get('phone', '')
            email = request.POST.get('email', '')
            person_obj.names = names
            person_obj.number = number
            person_obj.email = email
            person_obj.address = address
            person_obj.phone = phone
            person_obj.save()
            return JsonResponse({
                'success': True,
                'message': 'Datos actualizados correctamente',
                'pk': person_obj.id,
            }, status=HTTPStatus.OK)


@csrf_exempt
def insert_person(request):
    if request.method == 'POST':
        pk = request.POST.get('pk', '')
        if pk == '0':
            number = request.POST.get('number', '').strip()
            names = request.POST.get('names', '')
            address = request.POST.get('address', '')
            new_person = {
                'names': names,
                'address': address
            }
            person_obj = Person.objects.create(**new_person)
            person_obj.save()
            if person_obj:
                person_obj.number = person_obj.id
                person_obj.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Cliente creado correctamente',
                    'pk': person_obj.id,
                }, status=HTTPStatus.OK)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No se logro crear el cliente'
                }, status=HTTPStatus.OK)


def get_person(request):
    if request.method == 'GET':
        search = request.GET.get('search')
        person = []
        if search:
            person_set = Person.objects.filter(names__icontains=search)
            for p in person_set:
                person.append({
                    'pk': p.id,
                    'document': p.document,
                    'number': p.number,
                    'names': p.names,
                    'phone': p.phone,
                    'email': p.email,
                    'address': p.address
                })
        return JsonResponse({
            'status': True,
            'person': person
        })


def get_month(month):
    names_months = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }
    month_name = names_months[month]

    return month_name
