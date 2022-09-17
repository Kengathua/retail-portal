"""Franchise urls file."""

from rest_framework import routers
from elites_franchise_portal.enterprises import views

router = routers.DefaultRouter()
router.register(r'enterprises', views.EnterpriseViewSet)
urlpatterns = router.urls
