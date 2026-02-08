# dpcfam/views.py
from django.views.generic import DetailView
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from .models import MCSProperty, MCSSequence, AlphaFold
from .tables import MCSPropertyTable
from .filters import MCSPropertyFilter
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator # Import Paginator

class MCSPropertyListView(SingleTableMixin, FilterView):
    model = MCSProperty
    table_class = MCSPropertyTable
    filterset_class = MCSPropertyFilter
    paginate_by = 20
    template_name = 'dpcfam/metacluster_list.html'


from django.templatetags.static import static

class MCSDetailView(DetailView):
    model = MCSProperty
    template_name = 'dpcfam/metacluster_detail.html'
    context_object_name = 'mc'
    pk_url_kwarg = 'mcid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mcid = self.object.mcid
        
        # Pagination for sequences
        sequences_list = MCSSequence.objects.filter(mcid=mcid).order_by('id')
        paginator = Paginator(sequences_list, 10)  # Show 10 sequences per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['sequences'] = page_obj
        
        # Fetch AlphaFold data
        alphafolds = AlphaFold.objects.filter(mcid=mcid).order_by('id')
        context['alphafolds'] = alphafolds
        
        # Paths based on the static structure: static/production_files/dpcfam/...
        context['fasta_file'] = static(f"production_files/dpcfam/metaclusters_fasta/{mcid}.fasta")
        context['msa_file'] = static(f"production_files/dpcfam/metaclusters_msas_cdhit/{mcid}.msa")
        context['hmm_file'] = static(f"production_files/dpcfam/metaclusters_hmms/{mcid}.hmm")
        
        return context
