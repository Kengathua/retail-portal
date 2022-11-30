"""Franchise urls file."""

from rest_framework import routers
from elites_retail_portal.enterprises import views

router = routers.DefaultRouter()
router.register(r'enterprises', views.EnterpriseViewSet)
router.register(r'staff', views.StaffViewSet)
urlpatterns = router.urls
