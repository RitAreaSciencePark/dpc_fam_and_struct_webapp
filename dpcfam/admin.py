# dpcfam/admin.py
"""
Admin registration for the DPCfam models.

All three models inherit the shared bases in dpc.admin (read-only by default,
full CRUD only when DPCEXPLORER_ADMIN_WRITABLE is on; see that file). The small
properties and AlphaFold tables get full features; the large sequence table
uses the exact, index-backed search and the estimated-count paginator.
"""

from django.contrib import admin

from dpc.admin import DpcBaseAdmin, LargeTableAdmin, preview
from .models import DpcfamMcsProperty, DpcfamMcsSequence, DpcfamAlphaFoldRep


@admin.register(DpcfamMcsProperty)
class DpcfamMcsPropertyAdmin(DpcBaseAdmin):
    # ~81k metaclusters: comfortable to browse in full.
    list_display = (
        'mcid', 'size_uniref50', 'avg_len', 'std_avg_len',
        'lc_percent', 'cc_percent', 'dis_percent', 'tm',
        'pfam_da_preview', 'da_percent', 'avg_ov_percent', 'overlap_label',
    )
    # mcid substring is fine at this size; pfam_da substring is backed by the
    # idx_dpcfam_mcs_per_pfam_da GIN trigram index.
    search_fields = ('mcid', 'pfam_da')

    @admin.display(description='pfam_da', ordering='pfam_da')
    def pfam_da_preview(self, obj):
        return preview(obj.pfam_da)


@admin.register(DpcfamMcsSequence)
class DpcfamMcsSequenceAdmin(LargeTableAdmin):
    # ~16.6M rows: the largest table in the project.
    list_display = ('id', 'mc', 'protein', 'seq_range', 'seq_length', 'aa_seq_preview')
    list_select_related = ('mc', 'protein')
    raw_id_fields = ('mc', 'protein')          # no huge FK dropdown in write mode
    search_fields = ('mc__mcid', 'protein__protein_id')
    exact_search_fields = ('mc__mcid', 'protein__protein_id')

    # No ordering on the preview: aa_seq is unindexed text, so sorting it on a
    # large table would trigger an expensive ORDER BY. Full value shows in the
    # detail view.
    @admin.display(description='aa_seq')
    def aa_seq_preview(self, obj):
        return preview(obj.aa_seq)


@admin.register(DpcfamAlphaFoldRep)
class DpcfamAlphaFoldRepAdmin(DpcBaseAdmin):
    # ~38k representative AlphaFold structures: a modest table.
    list_display = ('id', 'mc', 'alphafold_prot_preview', 'seq_range', 'hmm_coverage', 'avg_plddt')
    list_select_related = ('mc',)
    raw_id_fields = ('mc',)
    search_fields = ('mc__mcid', 'alphafold_prot')

    @admin.display(description='alphafold_prot', ordering='alphafold_prot')
    def alphafold_prot_preview(self, obj):
        return preview(obj.alphafold_prot)
