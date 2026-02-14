# dpcfam/views.py
from django.views.generic import DetailView
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from django.core.paginator import Paginator
from django.templatetags.static import static
from .models import MCSProperty
from .tables import MCSPropertyTable
from .filters import MCSPropertyFilter

class MCSPropertyListView(SingleTableMixin, FilterView):
    model = MCSProperty
    table_class = MCSPropertyTable
    filterset_class = MCSPropertyFilter
    paginate_by = 10
    template_name = 'dpcfam/metacluster_list.html'

    def get_queryset(self):
        # Naturally sort MCIDs by converting numeric part to integer
        # This handles MC1, MC2, ..., MC10, ... instead of lexicographical order
        return MCSProperty.objects.extra(
            select={'mc_num': "CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER)"},
            order_by=['mc_num']
    )


class MCSDetailView(DetailView):
    model = MCSProperty
    template_name = 'dpcfam/metacluster_detail.html'
    context_object_name = 'mc'
    pk_url_kwarg = 'mcid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mcid = self.object.mcid
        
        # Pagination for sequences
        sequences_list = self.object.sequences.order_by('id')
        paginator = Paginator(sequences_list, 20)  # Show 20 sequences per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['sequences'] = page_obj
        
        # Fetch AlphaFold data
        alphafolds = self.object.alphafolds.order_by('id')
        context['alphafolds'] = alphafolds
        
        # Paths based on the static structure: static/production_files/dpcfam/...
        context['fasta_file'] = static(f"production_files/dpcfam/metaclusters_fasta/{mcid}.fasta")
        context['msa_file'] = static(f"production_files/dpcfam/metaclusters_msas_cdhit/{mcid}.msa")
        context['hmm_file'] = static(f"production_files/dpcfam/metaclusters_hmms/{mcid}.hmm")
        
        # Split Pfam architecture if valid (standardized with -)
        if self.object.pfam_da and self.object.pfam_da != 'UNKNOWN':
            context['pfam_architectures'] = self.object.pfam_da.split('-')
        else:
            context['pfam_architectures'] = []

        return context
