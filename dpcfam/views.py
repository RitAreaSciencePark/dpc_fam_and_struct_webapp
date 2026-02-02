# dpcfam/views.py
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from .models import MCSProperty
from .tables import MCSPropertyTable
from .filters import MCSPropertyFilter


class MCSPropertyListView(SingleTableMixin, FilterView):
    model = MCSProperty
    table_class = MCSPropertyTable
    filterset_class = MCSPropertyFilter
    paginate_by = 20
    template_name = 'dpcfam/metacluster_list.html'
