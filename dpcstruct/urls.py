from django.urls import path
from django.views.generic import TemplateView
from .views import DpcStructMetaclustersListView, DpcStructDetailView

urlpatterns = [
    path('', DpcStructMetaclustersListView.as_view(), name='dpcstruct_index'),
    path('downloads/', TemplateView.as_view(template_name='dpcstruct/dpcstruct_downloads.html'), name='dpcstruct_downloads'),
    path('mcs/', DpcStructMetaclustersListView.as_view(), name='dpcstruct_mcs_list'),
    path('mcs/<str:mc_id>/', DpcStructDetailView.as_view(), name='dpcstruct_detail'),
]