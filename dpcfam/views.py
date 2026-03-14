# dpcfam/views.py
from django.views.generic import DetailView
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from django.core.paginator import Paginator
from django.templatetags.static import static
from .models import DpcfamMcsProperty
from .tables import DpcfamMcsPropertyTable
from .filters import DpcfamMcsPropertyFilter


class DpcfamMcsPropertyListView(SingleTableMixin, FilterView):
    """
    List view for DPCFam Metacluster Properties
    Displays all metaclusters with filtering and pagination
    """
    model = DpcfamMcsProperty
    table_class = DpcfamMcsPropertyTable
    filterset_class = DpcfamMcsPropertyFilter
    paginate_by = 10
    template_name = 'dpcfam/metacluster_list.html'

    def get_queryset(self):
        # Naturally sort MCIDs by converting numeric part to integer
        # This handles MC1, MC2, ..., MC10, ... instead of lexicographical order
        return DpcfamMcsProperty.objects.extra(
            select={'mc_num': "CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER)"},
            order_by=['mc_num']
        )


class DpcfamMcsDetailView(DetailView):
    """
    Detail view for a single DPCFam Metacluster
    Shows sequences, AlphaFold data, and downloadable files
    """
    model = DpcfamMcsProperty
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
        
        # Split Pfam labels if valid (standardized with -)
        if self.object.pfam_da and self.object.pfam_da != 'UNKNOWN':
            context['pfam_architectures'] = self.object.pfam_da.split('-')
        else:
            context['pfam_architectures'] = []

        return context


# Legacy aliases for backward compatibility
MCSPropertyListView = DpcfamMcsPropertyListView
MCSDetailView = DpcfamMcsDetailView