from http import HTTPStatus
from django.contrib.auth.hashers import make_password
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView
from django.views.generic.edit import FormView
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect, JsonResponse
from .forms import FormLogin
from django.shortcuts import render, redirect
from django.template import loader
from django.conf import settings
from django.core.mail import send_mail

from .models import User
from ..hrm.models import Subsidiary


class Login(FormView):
    template_name = 'login.html'
    form_class = FormLogin
    success_url = reverse_lazy('home')

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(Login, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(Login, self).form_valid(form)


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/accounts/login/')


def users_list(request):
    if request.method == 'GET':
        user_set = User.objects.all()
        return render(request, 'user/user_list.html', {
            'user_set': user_set,
        })


class UserList(ListView):
    model = User
    template_name = 'user/user_list.html'


def user_create(request):
    if request.method == 'GET':
        subsidiary_set = Subsidiary.objects.all()
        return render(request, 'user/user.html', {
            'subsidiary_set': subsidiary_set,
            'type_set': User._meta.get_field('type').choices
        })


def user_update(request, pk):
    if request.method == 'GET':
        if pk:
            user_obj = User.objects.get(id=int(pk))
            subsidiary_set = Subsidiary.objects.all()
            return render(request, 'user/user.html', {
                'user_obj': user_obj,
                'subsidiary_set': subsidiary_set,
                'type_set': User._meta.get_field('type').choices
            })


@csrf_exempt
def user_save(request):
    if request.method == 'POST':
        user = request.POST.get('user', '')
        document = request.POST.get('document', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        birth_date = request.POST.get('birth_date', '')
        username = request.POST.get('username', '')
        address = request.POST.get('address', '')
        subsidiary = request.POST.get('subsidiary', None)
        types = request.POST.get('type', None)
        if subsidiary:
            subsidiary_obj = Subsidiary.objects.get(id=int(subsidiary))
        else:
            subsidiary_obj = None
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        is_state = request.POST.get('defaultCheck3', False)
        if is_state == 'on':
            is_state = True
        try:
            photo = request.FILES['photo']
        except Exception:
            photo = 'employee/employee0.jpg'
        password = request.POST.get('password', '')
        if password == '':
            return JsonResponse({
                'success': False,
                'message': 'Ingrese una contraseña valida'
            }, status=HTTPStatus.OK)
        pk = None
        if user != '0':
            pk = int(user)
        obj, created = User.objects.update_or_create(
            id=pk,
            defaults={
                "subsidiary": subsidiary_obj,
                "document": document,
                "email": email,
                "phone": phone,
                "birth_date": birth_date,
                "address": address,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": is_state,
                "username": username,
                "password": make_password(password),
                "photo": photo,
                "type": types
            })
        if obj:
            # return redirect('user:users', pk=obj.id) retorna un paramaetro del al forma 'user:users/pk'
            # return redirect('user:users')
            # return HttpResponseRedirect('/user/users/')
            return JsonResponse({
                'success': True,
                'message': 'proceso exitoso'
            }, status=HTTPStatus.OK)
        else:
            return JsonResponse({
                'success': False,
                'message': 'problemas en el proceso'
            }, status=HTTPStatus.OK)


def authorization(request):
    if request.method == 'GET':
        u = request.GET.get('u')
        if u != "0" and u != '':
            v = True
            user_obj = User.objects.get(id=int(u))
            if user_obj.is_authorization:
                user_obj.is_authorization = False
            else:
                user_obj.is_authorization = True
            user_obj.save()
            if user_obj.is_authorization:
                message = 'Autorizado - ' + str(user_obj.username.upper())
                v = True
            else:
                message = 'Desautorizado - ' + str(user_obj.username.upper())
                v = False
            return JsonResponse({
                'status': True,
                'value': v,
                'message': message,
                'userName': user_obj.username,
                'userAuth': v
            })
        else:
            return JsonResponse({
                'status': False,
                'message': 'Especifique el usuario'
            })
