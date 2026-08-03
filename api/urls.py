"""
api/urls.py

Routing and root-view branding for the DPCexplorer REST API.

Design choices, and why:

- DPCexplorerAPIRootView / DPCexplorerRouter: by default, DRF's
  DefaultRouter serves its root view (GET /api/) through
  rest_framework.routers.APIRootView. DRF derives that view's browsable-API
  title from the class name itself ("APIRootView" -> "Api Root") and its
  description from the class docstring ("The default basic root view for
  DefaultRouter"). DRF supports replacing this: subclassing APIRootView,
  overriding get_view_name() and get_view_description(), and pointing
  DefaultRouter.APIRootView at that subclass. This mirrors the
  admin.site.site_header override already used in
  dpc_fam_and_struct_webapp/urls.py, applied here to the DRF root view
  instead of the admin site.
"""
from django.urls import path, include
from rest_framework.routers import APIRootView, DefaultRouter

from .views import DpcfamMcsViewSet, DpcStructMcsViewSet


class DPCexplorerAPIRootView(APIRootView):
    """Same behaviour as DRF's default root view, with DPCexplorer branding
    instead of the generic title and description DRF derives from the
    APIRootView class name and docstring."""

    def get_view_name(self):
        return "DPCexplorer REST API - Django REST Framework"
    def get_view_description(self, html=False):
        return "Root of the DPCexplorer REST API, built with Django REST Framework."


class DPCexplorerRouter(DefaultRouter):
    APIRootView = DPCexplorerAPIRootView


router = DPCexplorerRouter()
router.register(r'dpcfam/mcs', DpcfamMcsViewSet, basename='api-dpcfam-mcs')
router.register(r'dpcstruct/mcs', DpcStructMcsViewSet, basename='api-dpcstruct-mcs')

urlpatterns = [
    path('', include(router.urls)),
]