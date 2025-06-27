"""jhunior URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.hrm.views import Home
from apps.user.views import Login, logout_user
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="AVENTURA API",
        default_version='v1',
        description="Documentación ventura",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('docs/', schema_view.with_ui('swagger',
                                                    cache_timeout=0), name='schema-swagger-ui'),
                  path('redocs/', schema_view.with_ui('redoc',
                                                      cache_timeout=0), name='schema-redoc'),
                  path('hrm/', include(('apps.hrm.urls', 'hrm'))),
                  path('user/', include(('apps.user.urls', 'user'))),
                  path('accounting/', include(('apps.accounting.urls', 'accounting'))),
                  path('sales/', include(('apps.sales.urls', 'sales'))),
		  path('finances/', include(('apps.finances.urls', 'finances'))),
                  path('', login_required(Home.as_view()), name='home'),
                  path('accounts/login/', Login.as_view(), name='login'),
                  path('logout/', login_required(logout_user), name='logout'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                           document_root=settings.MEDIA_ROOT)
