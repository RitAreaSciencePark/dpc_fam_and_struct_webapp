# dpcstruct/admin.py
"""
Admin registration for the DPCstruct models.

All four models inherit the shared bases in dpc.admin (read-only by default,
full CRUD only when DPCEXPLORER_ADMIN_WRITABLE is on; see that file). The small
properties and CATH/SCOP tables get full features; the large sequence table
uses the exact, index-backed search and the estimated-count paginator.
"""

from django.contrib import admin

from dpc.admin import DpcBaseAdmin, LargeTableAdmin, preview
from .models import (
    DpcStructMcsProperty,
    DpcStructMcsSequence,
    DpcStructCath,
    DpcStructScop,
)


@admin.register(DpcStructMcsProperty)
class DpcStructMcsPropertyAdmin(DpcBaseAdmin):
    # ~28k metaclusters: comfortable to browse in full.
    list_display = (
        'mc_id', 'mc_size', 'len_aa', 'len_std', 'len_ratio',
        'plddt', 'disorder', 'tmscore', 'lddt', 'pident',
        'pfam_score', 'pfam_da_preview',
    )
    # mc_id substring is fine at this size; pfam_da substring is backed by the
    # idx_dpcstruct_mcs_per_pfam GIN trigram index.
    search_fields = ('mc_id', 'pfam_da')

    @admin.display(description='pfam_da', ordering='pfam_da')
    def pfam_da_preview(self, obj):
        return preview(obj.pfam_da)


@admin.register(DpcStructMcsSequence)
class DpcStructMcsSequenceAdmin(LargeTableAdmin):
    # ~1.64M rows.
    list_display = ('id', 'mc', 'protein', 'prot_range', 'prot_seq_preview')
    list_select_related = ('mc', 'protein')
    raw_id_fields = ('mc', 'protein')          # no huge FK dropdown in write mode
    search_fields = ('mc__mc_id', 'protein__protein_id')
    exact_search_fields = ('mc__mc_id', 'protein__protein_id')

    # No ordering: prot_seq is unindexed text, sorting it on a large table
    # would force an expensive ORDER BY. Full value is in the detail view.
    @admin.display(description='prot_seq')
    def prot_seq_preview(self, obj):
        return preview(obj.prot_seq)


@admin.register(DpcStructCath)
class DpcStructCathAdmin(DpcBaseAdmin):
    # Small annotation table (~1,274 rows): full features, normal substring search.
    list_display = (
        'cath_query', 'mc', 'dpc_target', 'q_range', 't_range',
        'qlen', 'tlen', 'qcov', 'tcov', 'alnlen',
        'qtmscore', 'ttmscore', 'alntmscore', 'lddt', 'pident',
    )
    list_select_related = ('mc',)
    raw_id_fields = ('mc',)
    search_fields = ('cath_query', 'dpc_target', 'mc__mc_id')


@admin.register(DpcStructScop)
class DpcStructScopAdmin(DpcBaseAdmin):
    # Small annotation table (~1,359 rows): full features, normal substring search.
    list_display = (
        'scop_query', 'mc', 'dpc_target', 'q_range', 't_range',
        'qlen', 'tlen', 'qcov', 'tcov', 'alnlen',
        'qtmscore', 'ttmscore', 'alntmscore', 'lddt', 'pident',
    )
    list_select_related = ('mc',)
    raw_id_fields = ('mc',)
    search_fields = ('scop_query', 'dpc_target', 'mc__mc_id')
