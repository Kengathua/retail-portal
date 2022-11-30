"""Catalog urls file."""

from rest_framework import routers
from elites_retail_portal.catalog import views

router = routers.DefaultRouter()
router.register(r'sections', views.SectionViewSet)
router.register(r'catalogs', views.CatalogViewSet)
router.register(r'catalog_items', views.CatalogItemViewSet)
router.register(r'catalog_catalog_items', views.CatalogCatalogItemViewSet)
router.register(r'catalog_item_audit_logs', views.CatalogItemAuditLogViewSet)

urlpatterns = router.urls
