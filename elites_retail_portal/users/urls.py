"""Urls for users."""

from django.urls import path

from rest_framework import routers
from elites_retail_portal.users import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path(r'me/', views.MeView.as_view(), name='user-me'),
]

urlpatterns += router.urls
