"""Restrictions management urls file."""

from rest_framework import routers
from elites_franchise_portal.enterprise_mgt import views

router = routers.DefaultRouter()
router.register(r'enterprise_setup', views.EnterpriseSetupViewSet)
router.register(r'enterprise_setup_rules', views.EnterpriseSetupRuleViewSet)
urlpatterns = router.urls