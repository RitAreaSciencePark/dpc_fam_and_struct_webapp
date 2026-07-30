# dpcfam/views.py
from django.conf import settings
from django.shortcuts import render, redirect 
from django.contrib import messages   
from django.views.generic import DetailView
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models.expressions import RawSQL
from django.db.models import IntegerField
from .models import DpcfamMcsProperty
from .tables import DpcfamMcsPropertyTable
from .filters import DpcfamMcsPropertyFilter


class DpcfamMcsPropertyListView(SingleTableMixin, FilterView):
    """
    List view for DPCfam Metacluster Properties
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
        qs = DpcfamMcsProperty.objects.annotate(
            mc_num=RawSQL(
                "CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER)",
                [],
                output_field=IntegerField()
            )
        ).order_by('mc_num')
        
        dataset = self.request.GET.get('dataset', 'all')
        if dataset == 'standard':
            qs = qs.filter(size_uniref50__gte=50) 
        elif dataset == 'b':
            qs = qs.filter(size_uniref50__lt=50)
            
        return qs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dataset'] = self.request.GET.get('dataset', 'all')
        return context


class DpcfamMcsDetailView(DetailView):
    """
    Detail view for a single DPCfam Metacluster
    Shows sequences, AlphaFold data, and downloadable files
    """
    model = DpcfamMcsProperty
    template_name = 'dpcfam/metacluster_detail.html'
    context_object_name = 'mc'  # template uses {{ mc.mcid }}, {{ mc.pfam_da }}, etc.
    pk_url_kwarg = 'mcid'       # URL captures <str:mcid>

    def get_object(self, queryset=None):        
        mcid = self.kwargs.get(self.pk_url_kwarg)
        try:
            return DpcfamMcsProperty.objects.get(mcid=mcid)
        except DpcfamMcsProperty.DoesNotExist:
            messages.error(self.request, f'DPCfam metacluster "{mcid}" not found.')
            return None

    def get(self, request, *args, **kwargs):    
        self.object = self.get_object()
        if self.object is None:
            return redirect('home')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mcid = self.object.mcid
        
        # Pagination for sequences
        sequences_list = self.object.sequences.select_related('protein').order_by('id')
        paginator = Paginator(sequences_list, 10)  # Show 10 sequences per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['sequences'] = page_obj
        
        # Fetch AlphaFold data
        alphafolds = self.object.alphafolds.order_by('id')
        context['alphafolds'] = alphafolds
        
        # Paths based on the static structure: static/production_files/dpcfam/...
        context["fasta_file"] = reverse(
            "data_file",
            kwargs={
                "path": (
                    f"production_files/dpcfam/"
                    f"metaclusters_fasta/{mcid}.fasta"
                )
            },
        )

        context["msa_file"] = reverse(
            "data_file",
            kwargs={
                "path": (
                    f"production_files/dpcfam/"
                    f"metaclusters_cdhit_msas/{mcid}_msa.fasta"
                )
            },
        )

        hmm_path = (
            settings.DPC_DATA_ROOT
            / "production_files"
            / "dpcfam"
            / "metaclusters_hmms"
            / f"{mcid}.hmm"
        )

        if hmm_path.exists():
            context["hmm_file"] = reverse(
                "data_file",
                kwargs={
                    "path": (
                        f"production_files/dpcfam/"
                        f"metaclusters_hmms/{mcid}.hmm"
                    )
                },
            )
        else:
            context["hmm_file"] = None

        # Split Pfam labels if valid (standardized with -)
        if self.object.pfam_da and self.object.pfam_da != 'UNKNOWN':
            context['pfam_architectures'] = self.object.pfam_da.split('-')
        else:
            context['pfam_architectures'] = []

        return context


