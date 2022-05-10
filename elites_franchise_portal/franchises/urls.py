"""Franchise urls file."""

from rest_framework import routers
from elites_franchise_portal.franchises import views

router = routers.DefaultRouter()
router.register(r'franchises', views.FranchiseViewSet)
urlpatterns = router.urls
