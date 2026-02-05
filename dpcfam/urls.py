from django.urls import path
from django.views.generic import TemplateView
from .views import MCSPropertyListView, MCSDetailView

urlpatterns = [
    # show the MCS properties table at the app root
    path('', MCSPropertyListView.as_view(), name='index'),
    path('downloads/', TemplateView.as_view(template_name='dpcfam/downloads.html'), name='dpcfam_downloads'),
    path('mcs/', MCSPropertyListView.as_view(), name='mcs_list'),
    path('mcs/<str:mcid>/', MCSDetailView.as_view(), name='mcs_detail'),
]