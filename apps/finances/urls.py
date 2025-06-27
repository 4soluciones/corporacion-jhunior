from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required

from .views_pdf import guide_return

urlpatterns = [

    path('orders_supplier_list/', login_required(orders_supplier_list), name='orders_supplier_list'),
    path('get_orders_purchased/', login_required(get_orders_purchased), name='get_orders_purchased'),
    path('get_order_purchased_by_id/', login_required(get_order_purchased_by_id), name='get_order_purchased_by_id'),
    path('credit_note_supplier_save/', login_required(credit_note_supplier_save), name='credit_note_supplier_save'),
    path('credit_note_supplier_review/', login_required(credit_note_supplier_review), name='credit_note_supplier_review'),
    path('purchase_review/', login_required(purchase_review), name='purchase_review'),
    path('annul_credit_note_by_id/', login_required(annul_credit_note_by_id), name='annul_credit_note_by_id'),

    path('modal_guide/', login_required(modal_guide), name='modal_guide'),
    path('guide_return_save/', login_required(guide_return_save), name='guide_return_save'),
    path('guide_return/<int:pk>/', login_required(guide_return), name='guide_return'),
]
