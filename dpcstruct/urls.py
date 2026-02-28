from django.urls import path
from .views import DpcStructPropertyListView

urlpatterns = [
    path('', DpcStructPropertyListView.as_view(), name='index'),
    path('mcs/', DpcStructPropertyListView.as_view(), name='dpcstruct_mcs_list'),
    # Placeholder for detail view
    path('dpcstruct/<str:mc_id>/', DpcStructPropertyListView.as_view(), name='dpcstruct_detail'),
]