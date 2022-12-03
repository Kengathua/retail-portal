"""Elites Enterprise Portal URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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

from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

v1_patterns = [
    path(r'debit/', include(
        ('elites_retail_portal.debit.urls', 'debit'), namespace='debit')),
    path(r'users/', include(
        ('elites_retail_portal.users.urls', 'users'), namespace='users')),
    path(r'items/', include(
        ('elites_retail_portal.items.urls', 'items'), namespace='items')),
    path(r'credit/', include(
        ('elites_retail_portal.credit.urls', 'credit'), namespace='credit')),
    path(r'wallet/', include(
        ('elites_retail_portal.wallet.urls', 'wallet'), namespace='wallet')),
    path(r'orders/', include(
        ('elites_retail_portal.orders.urls', 'orders'), namespace='orders')),
    path(r'catalog/', include(
        ('elites_retail_portal.catalog.urls', 'catalog'), namespace='catalog')),
    path(r'adapters/', include(
        ('elites_retail_portal.adapters.urls', 'adapters'), namespace='adapters')),
    path(r'customers/', include(
        ('elites_retail_portal.customers.urls', 'customers'), namespace='customers')),
    path(r'warehouses/', include(
        ('elites_retail_portal.warehouses.urls', 'warehouses'), namespace='warehouses')),
    path(r'encounters/', include(
        ('elites_retail_portal.encounters.urls', 'encounters'), namespace='encounters')),
    path(r'enterprises/', include(
        ('elites_retail_portal.enterprises.urls', 'enterprises'), namespace='enterprises')),
    path(r'transactions/', include(
        ('elites_retail_portal.transactions.urls', 'transactions'), namespace='transactions')),
    path(r'enterprise_mgt/', include(
        ('elites_retail_portal.enterprise_mgt.urls', 'enterprise_mgt'),
        namespace='enterprise_mgt')),
]

urlpatterns = [
    path('v1/', include((v1_patterns, 'v1'), namespace='v1')),
    path('api/auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
