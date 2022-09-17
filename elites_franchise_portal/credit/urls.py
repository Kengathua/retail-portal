"""Credit side urls file."""

from rest_framework import routers
from elites_franchise_portal.credit import views

router = routers.DefaultRouter()
router.register(r'purchases', views.PurchaseViewSet)

urlpatterns = router.urls
