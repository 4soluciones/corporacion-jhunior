from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

from .views_excel import ReportProduct, reportkardex, StockMin, purchase_excel, export_product_filter, \
    report_kardex_cont, kardex_excel
from .views_pdf import ticket, guide, logistic, quotation

urlpatterns = [
    path('products/', login_required(ProductList.as_view()), name='products'),
    path('product_save/', login_required(product_save), name='product_save'),
    path('modal_product/', login_required(modal_product), name='modal_product'),
    path('update_product/', login_required(update_product), name='update_product'),
    path('get_search_product/', login_required(get_search_product), name='get_search_product'),

    path('brands/', login_required(BrandList.as_view()), name='brands'),
    path('modal_brand/', login_required(modal_brand), name='modal_brand'),
    path('brand_save/', login_required(brand_save), name='brand_save'),

    path('familys/', login_required(FamilyList.as_view()), name='familys'),
    path('modal_family/', login_required(modal_family), name='modal_family'),
    path('family_save/', login_required(family_save), name='family_save'),

    path('modal_presenting/', login_required(modal_presenting), name='modal_presenting'),
    path('presentation_save/', login_required(presentation_save), name='presentation_save'),
    path('get_presentation/', login_required(get_presentation), name='get_presentation'),
    path('update_presentation/', login_required(update_presentation), name='update_presentation'),
    path('delete_presentation/', login_required(delete_presentation), name='delete_presentation'),

    path('get_store/', login_required(get_store), name='get_store'),
    path('store_save/', login_required(store_save), name='store_save'),

    path('sales/', login_required(SalesList.as_view()), name='sales'),
    path('search_product/', login_required(search_product), name='search_product'),
    path('delete_order_detail/', login_required(delete_order_detail), name='delete_order_detail'),
    path('get_prices/', login_required(get_prices), name='get_prices'),
    path('get_products/', login_required(get_products), name='get_products'),
    path('order_save/', login_required(order_save), name='order_save'),
    path('quotation_save/', login_required(quotation_save), name='quotation_save'),
    path('get_person_by_document/', login_required(get_person_by_document), name='get_person_by_document'),
    path('update_order_detail/', login_required(update_order_detail), name='update_order_detail'),
    path('ticket/<int:pk>/', login_required(ticket), name='ticket'),
    path('quotation/<int:pk>/', login_required(quotation), name='quotation'),
    path('get_order/', login_required(get_order), name='get_order'),
    path('get_search_product_code/', login_required(get_search_product_code), name='get_search_product_code'),

    path('purchase/', login_required(PurchaseList.as_view()), name='purchase'),
    path('get_product_purchase/', login_required(get_product_purchase), name='get_product_purchase'),
    path('get_purchase_by_date/', login_required(get_purchase_by_date), name='get_purchase_by_date'),
    path('get_purchase/', login_required(get_purchase), name='get_purchase'),
    path('purchase_list/', login_required(purchase_list), name='purchase_list'),
    path('valid_unit/', login_required(valid_unit), name='valid_unit'),
    path('purchase_save/', login_required(purchase_save), name='purchase_save'),
    path('pass_purchase/', login_required(pass_purchase), name='pass_purchase'),
    path('cancel_purchase/', login_required(cancel_purchase), name='cancel_purchase'),
    path('get_change/', login_required(get_change), name='get_change'),

    path('modal_kardex/', login_required(modal_kardex), name='modal_kardex'),
    path('get_kardex/', login_required(get_kardex), name='get_kardex'),
    path('get_search_product_other/', login_required(get_search_product_other), name='get_search_product_other'),
    path('get_product_all/', login_required(get_product_all), name='get_product_all'),

    path('sales_list/', login_required(sales_list), name='sales_list'),
    path('get_sales_detail/', login_required(get_sales_detail), name='get_sales_detail'),
    path('modal_guide/', login_required(modal_guide), name='modal_guide'),
    path('modal_kardex_accounting/', login_required(modal_kardex_accounting), name='modal_kardex_accounting'),
    path('guide_save/', login_required(guide_save), name='guide_save'),
    path('guide/<int:pk>/', login_required(guide), name='guide'),
    path('logistic/<int:pk>/', login_required(logistic), name='logistic'),
    path('reportproduct/', ReportProduct.as_view(), name='reportproduct'),
    path('export_product/', login_required(export_product), name='export_product'),
    path('get_kardex_table/', login_required(get_kardex_table), name='get_kardex_table'),
    path('stockmin/', StockMin.as_view(), name='stockmin'),
    path('reportkardex/<str:init>/<str:end>/<int:pk>/', login_required(reportkardex), name='reportkardex'),
    path('report_kardex_cont/<str:init>/<str:end>/<int:pk>/', login_required(report_kardex_cont), name='report_kardex_cont'),
    path('purchase_excel/<str:init>/<str:end>/', login_required(purchase_excel), name='purchase_excel'),
    path('export_product_filter/<str:c1>/<str:c2>/<str:c3>/<str:c4>/<str:array_id>/', login_required(export_product_filter), name='export_product_filter'),

    path('graphic_user/', login_required(graphic_user), name='graphic_user'),
    path('graphic_sales/', login_required(graphic_sales), name='graphic_sales'),
    path('graphic_month/', login_required(graphic_month), name='graphic_month'),

    # Corporate_sale
    path('sales_corporate/', login_required(SalesListCorporate.as_view()), name='sales_corporate'),

    # Cancel Order
    path('cancel_order/', login_required(cancel_order), name='cancel_order'),
    path('get_last_order/', login_required(get_last_order), name='get_last_order'),

    # New Kardex
    path('get_kardex_by_product/', login_required(get_kardex_by_product), name='get_kardex_by_product'),
    path('kardex_excel/<str:month_year>/', login_required(kardex_excel), name='kardex_excel'),

    # TEST FUNCTIONS BACKUP
    path('recalculate_credit_note/', login_required(recalculate_credit_note), name='recalculate_credit_note'),
    path('update_invoice_stock_product/', login_required(update_invoice_stock_product), name='update_invoice_stock_product'),
    path('fill_kardex_invoice/', login_required(fill_kardex_invoice), name='fill_kardex_invoice'),

    # TEST SOCKET
    path('test_socket/', login_required(test_socket), name='test_socket'),

]
