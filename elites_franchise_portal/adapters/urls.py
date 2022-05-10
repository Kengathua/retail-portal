"""Adapters urls file."""
from django.urls import path, include
from elites_franchise_portal.adapters.mobile_money.mpesa import views as mpesa_views


mpesa_c2b_patterns = [
    path("checkout/", mpesa_views.MpesaCheckout.as_view(), name="checkout"),
    path("callback/", mpesa_views.MpesaCallBack.as_view(), name="callback"),
    path('confirmation/', mpesa_views.MpesaConfirmation.as_view(), name="confirmation"),
    path('validation/', mpesa_views.MpesaValidation.as_view(), name="validation"),
    path('register/', mpesa_views.MpesaRegister.as_view(), name="register"),
]

mpesa_patterns = [
    path('c2b/', include((mpesa_c2b_patterns, 'c2b'), namespace='c2b')),
]

airtel_patterns = []

mobile_money_patterns = [
    path('safaricom/', include((mpesa_patterns, 'safaricom'), namespace='safaricom')),
    path('airtel/', include((airtel_patterns, 'airtel'), namespace='airtel')),
]

baking_patterns = []

urlpatterns = [
    path('mobile_money/', include(
        (mobile_money_patterns, 'mobile_money'), namespace='mobile_money')),
    path('baking/', include((baking_patterns, 'baking'), namespace='baking')),
]
