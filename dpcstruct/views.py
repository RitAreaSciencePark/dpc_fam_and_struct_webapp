from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from .models import DpcStructMcsProperty
from .tables import DpcStructMcsPropertyTable
from .filters import DpcStructMcsPropertyFilter

class DpcStructPropertyListView(SingleTableMixin, FilterView):
    model = DpcStructMcsProperty
    table_class = DpcStructMcsPropertyTable
    filterset_class = DpcStructMcsPropertyFilter
    paginate_by = 10
    template_name = 'dpcstruct/dpcstruct_list_metaclusters.html'

    def get_queryset(self):
        # We sort by numeric part of MCID
        return DpcStructMcsProperty.objects.extra(
            select={'mc_num': "CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER)"}
        ).order_by('mc_num')
