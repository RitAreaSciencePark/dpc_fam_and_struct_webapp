"""
api/views.py

Read-only REST endpoints for DPCfam and DPCstruct metaclusters.

Design choices, and why:

- ReadOnlyModelViewSet: the API only ever reads dpcexplorer_db. This mirrors
  the read-only admin posture (see ADMIN_PANEL.md) and keeps the published
  data safe from accidental writes through a public endpoint.

- ?mcids=MC1,MC3,MC15 on the list endpoint: this is the "list of Metacluster
  IDs" entry point. A comma-separated query parameter is simple for a user
  pasting IDs into a browser or a requests.get() call, and it composes
  naturally with pagination, so a very long list still returns in pages.

- /members/ custom action: a metacluster's seed/representative sequences are
  a one-to-many relation, not a property of the metacluster itself, so they
  get their own endpoint rather than being embedded (embedding could mean
  thousands of sequences inside one JSON object for the largest DPCfam MCs).

- NamedViewSetMixin: by default, DRF derives the titles shown in the
  browsable API purely from the Python class name (e.g. "DpcfamMcsViewSet"
  becomes "Dpcfam Mcs List" / "Dpcfam Mcs Instance"). That is legible but
  not a real naming convention. This mixin overrides get_view_name() so
  every page reads like a sentence about the actual resource, the same
  intent as the custom admin.site.site_header set for the admin panel
  (see dpc_fam_and_struct_webapp/urls.py).  
"""

from django.db.models.expressions import RawSQL
from django.db.models import IntegerField
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from dpcfam.models import DpcfamMcsProperty
from dpcstruct.models import DpcStructMcsProperty

from .serializers import (
    DpcfamMcsPropertySerializer, DpcfamMcsMemberSerializer,
    DpcStructMcsPropertySerializer, DpcStructMcsMemberSerializer,
)


class MembersPagination(PageNumberPagination):
    """Paginates /members/ separately from the metacluster list, since a
    single metacluster can hold well over 100,000 seed sequences."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 500


def _split_mcids(raw):
    """
    Turn '?mcids=MC1, MC3,MC15' into ['MC1', 'MC3', 'MC15']. 
    Returns None if the parameter was not supplied.
    """
    if not raw:
        return None
    return [m.strip() for m in raw.split(',') if m.strip()]


class NamedViewSetMixin:
    """
    Gives a ViewSet a clean, resource-specific title in the browsable API,
    in OPTIONS responses, and in the auto-generated schema.

    Set two class attributes on each subclass:
      resource_name         e.g. "DPCfam Metacluster"   (singular)
      resource_name_plural  e.g. "DPCfam Metaclusters"  (plural)

    The three routes this project uses (list, retrieve, members) then read,
    respectively: "DPCfam Metaclusters", "DPCfam Metacluster MC1", and
    "DPCfam Metacluster MC1 - Members", instead of DRF's mechanical
    "Dpcfam Mcs List" / "Dpcfam Mcs Instance" / "Members".

    """
    resource_name = "Resource"
    resource_name_plural = "Resources"

    def get_view_name(self):
        action_name = getattr(self, 'action', None)
        lookup = getattr(self, 'lookup_field', None)
        kwargs = getattr(self, 'kwargs', None) or {}
        mc_id = kwargs.get(lookup, '') if lookup else ''

        if action_name == 'members':
            return f"{self.resource_name} {mc_id} - Members"
        if action_name == 'retrieve':
            return f"{self.resource_name} {mc_id}"
        return self.resource_name_plural


class DpcfamMcsViewSet(NamedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    GET /api/dpcfam/mcs/                     -> paginated list, all 81,384 MCs
    GET /api/dpcfam/mcs/?mcids=MC1,MC3,MC15  -> only the requested MCs
    GET /api/dpcfam/mcs/{mcid}/               -> one MC's properties
    GET /api/dpcfam/mcs/{mcid}/members/       -> its seed sequences
                                                  (id, protein_id, seq_range)
    """
    resource_name = "DPCfam Metacluster"
    resource_name_plural = "DPCfam Metaclusters"
    serializer_class = DpcfamMcsPropertySerializer
    lookup_field = 'mcid'

    def get_queryset(self):
        qs = DpcfamMcsProperty.objects.annotate(
            mc_num=RawSQL(
                "CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER)",
                [], output_field=IntegerField(),
            )
        ).order_by('mc_num')

        mcids = _split_mcids(self.request.query_params.get('mcids'))
        if mcids:
            qs = qs.filter(mcid__in=mcids)
        return qs

    @action(detail=True, methods=['get'])
    def members(self, request, mcid=None):
        mc = self.get_object()
        members = mc.sequences.select_related('protein').order_by('id')
        paginator = MembersPagination()
        page = paginator.paginate_queryset(members, request)
        serializer = DpcfamMcsMemberSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DpcStructMcsViewSet(NamedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    GET /api/dpcstruct/mcs/                  -> paginated list, all 28,246 MCs
    GET /api/dpcstruct/mcs/?mcids=MC1,MC5    -> only the requested MCs
    GET /api/dpcstruct/mcs/{mc_id}/           -> one MC's properties
    GET /api/dpcstruct/mcs/{mc_id}/members/   -> its representative sequences
                                                  (id, protein_id, prot_range)
    """
    resource_name = "DPCstruct Metacluster"
    resource_name_plural = "DPCstruct Metaclusters"
    serializer_class = DpcStructMcsPropertySerializer
    lookup_field = 'mc_id'

    def get_queryset(self):
        qs = DpcStructMcsProperty.objects.annotate(
            mc_num=RawSQL(
                "CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER)",
                [], output_field=IntegerField(),
            )
        ).order_by('mc_num')

        mcids = _split_mcids(self.request.query_params.get('mcids'))
        if mcids:
            qs = qs.filter(mc_id__in=mcids)
        return qs

    @action(detail=True, methods=['get'])
    def members(self, request, mc_id=None):
        mc = self.get_object()
        members = mc.sequences.select_related('protein').order_by('id')
        paginator = MembersPagination()
        page = paginator.paginate_queryset(members, request)
        serializer = DpcStructMcsMemberSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)