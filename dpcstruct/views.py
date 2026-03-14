from django.views.generic import DetailView, TemplateView
from django.shortcuts import render
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from django.core.paginator import Paginator
from django.templatetags.static import static
from .models import DpcStructMcsProperty, DpcStructCath, DpcStructScop
from .tables import DpcStructMcsPropertyTable, DpcStructCathTable, DpcStructScopTable
from .filters import DpcStructMcsPropertyFilter, DpcStructCathFilter, DpcStructScopFilter


class DpcStructMetaclustersListView(TemplateView):
    """
    Main view for DPCStruct metaclusters with tabs to toggle between:
    - Metacluster Properties (default)
    - CATH fold annotations
    - SCOP fold annotations
    """
    template_name = 'dpcstruct/dpcstruct_list_metaclusters.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        view_type = self.request.GET.get('view', 'properties')  # Default to properties
        
        context['view_type'] = view_type
        context['view_options'] = [
            {'name': 'Properties', 'value': 'properties'},
            {'name': 'CATH', 'value': 'cath'},
            {'name': 'SCOP', 'value': 'scop'},
        ]

        # Get filter queries
        search_mcid = self.request.GET.get('search_mcid', '').strip()
        search_fold = self.request.GET.get('search_fold', '').strip()

        if view_type == 'properties':
            # Display metacluster properties
            queryset = DpcStructMcsProperty.objects.extra(
                select={'mc_num': "CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER)"}
            ).order_by('mc_num')
            
            if search_mcid:
                queryset = queryset.filter(mc_id__iexact=search_mcid)
            
            # Create table
            import django_tables2 as tables
            table = DpcStructMcsPropertyTable(queryset)
            table.paginate(page=self.request.GET.get('page', 1), per_page=10)
            context['table'] = table
            context['page_obj'] = table.page

        elif view_type == 'cath':
            # Display CATH annotations
            queryset = DpcStructCath.objects.select_related('mc').order_by('-mc__mc_id')
            
            if search_mcid:
                queryset = queryset.filter(mc__mc_id__iexact=search_mcid)
            if search_fold:
                queryset = queryset.filter(cath_query__iexact=search_fold)
            
            # Create table
            import django_tables2 as tables
            table = DpcStructCathTable(queryset)
            table.paginate(page=self.request.GET.get('page', 1), per_page=10)
            context['table'] = table
            context['page_obj'] = table.page

        elif view_type == 'scop':
            # Display SCOP annotations
            queryset = DpcStructScop.objects.select_related('mc').order_by('-mc__mc_id')
            
            if search_mcid:
                queryset = queryset.filter(mc__mc_id__iexact=search_mcid)
            if search_fold:
                queryset = queryset.filter(scop_query__iexact=search_fold)
            
            # Create table
            import django_tables2 as tables
            table = DpcStructScopTable(queryset)
            table.paginate(page=self.request.GET.get('page', 1), per_page=10)
            context['table'] = table
            context['page_obj'] = table.page

        return context


# Legacy views for backward compatibility
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

        # CATH annotations
        cath_annotations = self.object.cath_annotations.all()
        context['cath_count'] = cath_annotations.count()
        context['cath_sample'] = cath_annotations[:5]  # Show first 5

        # SCOP annotations
        scop_annotations = self.object.scop_annotations.all()
        context['scop_count'] = scop_annotations.count()
        context['scop_sample'] = scop_annotations[:5]  # Show first 5

        # Per-MC downloadable files
        context['seqs_file'] = static(f"production_files/dpcstruct/dpcstruct_reps_seqs/{mc_id}.fasta")
        context['pdbs_dir'] = static(f"production_files/dpcstruct/dpcstruct_reps_pdbs_zipped/{mc_id}_pdb.zip")

        # Split Pfam labels if valid
        if self.object.pfam_da and self.object.pfam_da != 'NONE':
            context['pfam_label_list'] = [l.strip() for l in self.object.pfam_da.split('-')]
        else:
            context['pfam_label_list'] = []

        return context
