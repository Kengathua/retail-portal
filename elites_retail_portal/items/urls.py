"""Item registry urls file."""

from rest_framework import routers
from elites_retail_portal.items import views

router = routers.DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'item_types', views.ItemTypeViewSet)
router.register(r'brands', views.BrandViewSet)
router.register(r'brand_item_types', views.BrandItemTypeViewSet)
router.register(r'item_models', views.ItemModelViewSet)
router.register(r'items', views.ItemViewSet)
router.register(r'units', views.UnitsViewSet)
router.register(r'units_item_types', views.UnitsItemTypeViewSet)
router.register(r'item_units', views.ItemUnitsViewSet)
router.register(r'item_attributes', views.ItemAttributeViewSet)
router.register(r'item_images', views.ItemImageViewSet)

urlpatterns = router.urls
