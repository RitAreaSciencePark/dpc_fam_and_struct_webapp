from django.views.generic import DetailView
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from django.core.paginator import Paginator
from django.templatetags.static import static
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


class DpcStructDetailView(DetailView):
    model = DpcStructMcsProperty
    template_name = 'dpcstruct/dpcstruct_detail.html'
    context_object_name = 'mc'
    pk_url_kwarg = 'mc_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mc_id = self.object.mc_id

        # Pagination for sequences
        sequences_list = self.object.sequences.order_by('id')
        paginator = Paginator(sequences_list, 20)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['sequences'] = page_obj

        # Per-MC downloadable files
        context['seqs_file'] = static(f"production_files/dpcstruct/dpcstruct_reps_seqs/{mc_id}.fasta")
        context['pdbs_dir'] = static(f"production_files/dpcstruct/dpcstruct_reps_pdbs_zipped/{mc_id}_pdb.zip")

        # Split Pfam labels if valid
        if self.object.pfam_labels and self.object.pfam_labels != 'NONE':
            context['pfam_label_list'] = [l.strip() for l in self.object.pfam_labels.split('-')]
        else:
            context['pfam_label_list'] = []

        return context
