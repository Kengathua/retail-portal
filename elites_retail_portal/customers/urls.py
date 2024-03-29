"""Customer urls file."""

from rest_framework import routers
from elites_retail_portal.customers import views

router = routers.DefaultRouter()
router.register(r'customers', views.CustomerViewSet)

urlpatterns = router.urls
