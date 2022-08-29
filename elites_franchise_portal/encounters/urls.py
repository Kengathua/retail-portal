"""Encounters urls file."""

from rest_framework import routers
from elites_franchise_portal.encounters import views

router = routers.DefaultRouter()
router.register(r'encounters', views.EncounterViewSet)

urlpatterns = router.urls
