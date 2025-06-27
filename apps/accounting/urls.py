from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required
from .api import *

from .views_pdf import invoice, ticket, pdf, quotation_pdf

urlpatterns = [
    path('casing/', login_required(CasingList.as_view()), name='casing'),
    path('casing_save/', login_required(casing_save), name='casing_save'),
    path('modal_casing/', login_required(modal_casing), name='modal_casing'),
    path('open_casing/', login_required(open_casing), name='open_casing'),
    path('opening/', login_required(opening), name='opening'),
    path('close_casing/', login_required(close_casing), name='close_casing'),
    path('closing/', login_required(closing), name='closing'),

    path('payable/', login_required(payable), name='payable'),
    path('payment_order/', login_required(payment_order), name='payment_order'),
    path('validate_casing/', login_required(get_validate_casing), name='validate_casing'),
    path('payment_save/', login_required(payment_save), name='payment_save'),
    path('invoice/<int:pk>/', login_required(invoice), name='invoice'),
    path('pdf/<int:pk>/', login_required(pdf), name='pdf'),
    path('quotation_pdf/<int:pk>/', login_required(quotation_pdf), name='quotation_pdf'),
    path('ticket/<int:pk>/', login_required(ticket), name='ticket'),
    path('invoice_list/', login_required(invoice_list), name='invoice_list'),
    path('invoice_issued/', login_required(invoice_issued), name='invoice_issued'),
    path('get_order_type/', login_required(get_order_type), name='get_order_type'),
    path('cancel_recipe/', login_required(cancel_recipe), name='cancel_recipe'),
    path('get_type_invoice/', login_required(get_type_invoice), name='get_type_invoice'),
    path('get_pending_invoices_to_canceled/', login_required(get_pending_invoices_to_canceled), name='get_pending_invoices_to_canceled'),
    path('invoice_sunat/', login_required(invoice_sunat), name='invoice_sunat'),

    path('orders_person_list/', login_required(orders_person_list), name='orders_person_list'),
    path('cash_page/', login_required(cash_page), name='cash_page'),
    path('orders_person/', login_required(orders_person), name='orders_person'),
    path('get_order_by_number/', login_required(get_order_by_number), name='get_order_by_number'),
    path('modal_payment/', login_required(modal_payment), name='modal_payment'),
    path('modal_payment_show/', login_required(modal_payment_show), name='modal_payment_show'),

    path('cash_page/', login_required(cash_page), name='cash_page'),
    path('cash_order/', login_required(cash_order), name='cash_order'),
    path('close_casing/', login_required(close_casing), name='close_casing'),
    path('get_users_by_date/', login_required(get_users_by_date), name='get_users_by_date'),
    path('get_orders_by_user/', login_required(get_orders_by_user), name='get_orders_by_user'),
    path('casing_report/', login_required(casing_report), name='casing_report'),
    path('get_order_list/', login_required(get_order_list), name='get_order_list'),
    path('get_order_detail/', login_required(get_order_detail), name='get_order_detail'),

    path('payments/', login_required(payments), name='payments'),
    path('delete_payment/', login_required(delete_payment), name='delete_payment'),
    path('search_order/', login_required(search_order), name='search_order'),

    # APIS
    path('api/v1/get_ticket_sale/<int:orderNumber>', get_ticket_sale),
    path('api/v1/get_payment_cash/<int:orderNumber>', get_payment_cash),
    path('api/v1/get_close_cash/<str:start_date>/<str:end_date>', get_close_cash),
    path('get_type_change/', login_required(get_type_change), name='get_type_change'),

    # SEND AND CANCEL
    path('invoice_sunat_and_cancel/', login_required(invoice_sunat_and_cancel), name='invoice_sunat_and_cancel'),
    path('send_receipt_sunat/', login_required(send_receipt_sunat), name='send_receipt_sunat'),
    path('send_receipt_cancel/', login_required(send_receipt_cancel), name='send_receipt_cancel'),
    path('invoice_cancel_sunat/', login_required(invoice_cancel_sunat), name='invoice_cancel_sunat'),

    # CREDIT NOTE
    path('modal_credit_note/', login_required(modal_credit_note), name='modal_credit_note'),
    path('save_credit_note/', login_required(save_credit_note), name='save_credit_note'),

    # DEPOSIT REPORT
    path('deposit_report/', login_required(deposit_report), name='deposit_report'),
    path('get_report_deposit/', login_required(get_report_deposit), name='get_report_deposit'),
    path('send_sunat_4_fact/<int:order_id>', send_sunat_4_fact),
]
