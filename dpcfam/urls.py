from django.urls import path
from django.views.generic import TemplateView
from .views import DpcfamMcsPropertyListView, DpcfamMcsDetailView, MCSPropertyListView, MCSDetailView

urlpatterns = [
    # show the Metacluster properties table at the app root
    path('', DpcfamMcsPropertyListView.as_view(), name='index'),
    path('downloads/', TemplateView.as_view(template_name='dpcfam/downloads.html'), name='dpcfam_downloads'),
    path('mcs/', DpcfamMcsPropertyListView.as_view(), name='mcs_list'),
    path('mcs/<str:mcid>/', DpcfamMcsDetailView.as_view(), name='mcs_detail'),
]