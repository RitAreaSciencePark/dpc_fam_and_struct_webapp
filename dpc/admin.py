# dpc/admin.py
"""
Admin registration for the shared DPC reference models, plus the small toolkit
that dpcfam/admin.py and dpcstruct/admin.py reuse.

Admin write mode
----------------
Every DPC* model is mapped onto a production PostgreSQL table with
``managed = False``. The data is produced by the reproducible pipeline
(setup_dpcexplorer_data.sh and the SQL loaders), which is the single source of
truth.

By default the admin is READ-ONLY: add / change / delete are disabled for
everyone, superusers included, so the panel can never write to the scientific
tables. This is the default posture (v1.0.3).

An operator can grant full CRUD by setting ``DPCEXPLORER_ADMIN_WRITABLE=True``
(read in settings.py). It is a deliberate, per-deployment opt-in; the data is
never writable by accident. When it is on, the admin falls back to Django's
normal per-user permissions, so superusers can write and other staff write
according to the permissions they hold. The flag is read at request time, so
one build serves both postures and tests can override it.

Performance
-----------
Some tables hold tens of millions of rows. EstimatedCountPaginator avoids the
full COUNT(*) on every changelist, and LargeTableAdmin replaces the default
substring search with an exact, index-backed lookup. The large-table admins
also set raw_id_fields, so that in write mode a foreign-key field never tries
to load millions of related rows into a dropdown.
"""

import logging

from django.conf import settings
from django.contrib import admin
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.text import Truncator

from .models import DpcUniprotProtein, DpcPfamDomain, DpcUniref50Pfam

logger = logging.getLogger(__name__)


def admin_writable():
    """Return True only when the operator has explicitly enabled write mode."""
    return getattr(settings, 'DPCEXPLORER_ADMIN_WRITABLE', False)


# Logged once at startup (admin modules are imported during admin autodiscover).
logger.info(
    "DPCexplorer admin mode: %s",
    "READ/WRITE (CRUD enabled)" if admin_writable() else "READ-ONLY",
)


# --------------------------------------------------------------------------- #
# Reusable toolkit (imported by dpcfam/admin.py and dpcstruct/admin.py)
# --------------------------------------------------------------------------- #
class EstimatedCountPaginator(Paginator):
    """
    Paginator that avoids a full COUNT(*) on large, unfiltered tables.

    On a table of tens of millions of rows an exact count forces a sequential
    scan that can take several seconds and makes the changelist feel broken.
    When the queryset is unfiltered we return PostgreSQL's planner estimate
    (pg_class.reltuples), read instantly from catalog statistics. As soon as a
    filter or search adds a WHERE clause, the result set is small, so we fall
    back to the exact count and the number stays correct.
    """

    @cached_property
    def count(self):
        queryset = self.object_list
        if connection.vendor != 'postgresql':
            return super().count
        try:
            if queryset.query.where:
                return super().count
            db_table = queryset.model._meta.db_table
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT reltuples::bigint FROM pg_class WHERE relname = %s",
                    [db_table],
                )
                row = cursor.fetchone()
            # reltuples is -1 on a table that was never analyzed; guard for it.
            if row and row[0] and row[0] > 0:
                return int(row[0])
        except Exception:
            pass
        return super().count


def preview(value, length=48):
    """Shorten a long text value so it never bloats a changelist column."""
    if not value:
        return value
    return Truncator(str(value)).chars(length)


class DpcBaseAdmin(admin.ModelAdmin):
    """
    Shared base for the DPC data models.

    Writes (add / change / delete) are denied unless DPCEXPLORER_ADMIN_WRITABLE
    is on. When it is off (the default), the denial is absolute, even for
    superusers, so nothing can modify the production tables through the admin.
    When it is on, permissions defer to Django's normal per-user checks.
    Viewing is always allowed, so in read mode the detail page renders as a
    read-only form.
    """

    show_full_count = False
    paginator = EstimatedCountPaginator
    list_per_page = 50

    def has_add_permission(self, request):
        return admin_writable() and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return admin_writable() and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return admin_writable() and super().has_delete_permission(request, obj)

    def has_view_permission(self, request, obj=None):
        return True


class LargeTableAdmin(DpcBaseAdmin):
    """
    Base tuned for the very large tables.

    The admin's default search builds a substring ``ILIKE '%term%'`` filter,
    which cannot use a B-tree index and would scan tens of millions of rows.
    Here, search is an exact, case-sensitive match on the fields listed in
    ``exact_search_fields``, so it uses the primary-key / foreign-key indexes
    and returns instantly. Substring search on these tables is not offered on
    purpose; the public application views provide the proper indexed search.
    """

    exact_search_fields = ()

    def get_search_results(self, request, queryset, search_term):
        term = search_term.strip()
        if not term or not self.exact_search_fields:
            return queryset, False
        condition = Q()
        for field in self.exact_search_fields:
            condition |= Q(**{field: term})
        return queryset.filter(condition), False


# --------------------------------------------------------------------------- #
# dpc reference models
# --------------------------------------------------------------------------- #
@admin.register(DpcUniprotProtein)
class DpcUniprotProteinAdmin(LargeTableAdmin):
    # ~14.1M rows: browse the first pages, look up a protein by exact accession.
    list_display = ('protein_id', 'protein_length')
    search_fields = ('protein_id',)            # shows the search box
    exact_search_fields = ('protein_id',)      # exact, index-backed lookup


@admin.register(DpcPfamDomain)
class DpcPfamDomainAdmin(DpcBaseAdmin):
    # Small lookup table (~19k rows): full features are comfortable here.
    list_display = ('pfam_id', 'pfam_type')
    search_fields = ('pfam_id', 'pfam_type')


@admin.register(DpcUniref50Pfam)
class DpcUniref50PfamAdmin(LargeTableAdmin):
    # ~14.55M rows.
    list_display = ('id', 'uniref50', 'pfam_id', 'pfam_ranges')
    list_select_related = ('uniref50', 'pfam_id')   # flat changelist, no N+1
    raw_id_fields = ('uniref50', 'pfam_id')         # no huge FK dropdown in write mode
    search_fields = ('uniref50__protein_id', 'pfam_id__pfam_id')
    exact_search_fields = ('uniref50__protein_id', 'pfam_id__pfam_id')
