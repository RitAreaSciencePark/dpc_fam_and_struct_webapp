from django.urls import path
from .views import MCSPropertyListView

urlpatterns = [
    # show the MCS properties table at the app root
    path('', MCSPropertyListView.as_view(), name='index'),
    path('mcs/', MCSPropertyListView.as_view(), name='mcs_list'),
]