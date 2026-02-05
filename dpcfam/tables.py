# dpcfam/tables.py
import django_tables2 as tables
from .models import MCSProperty


class MCSPropertyTable(tables.Table):
    mcid = tables.LinkColumn("mcs_detail", args=[tables.A("mcid")])

    class Meta:
        model = MCSProperty
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-striped table-hover table-bordered"}
        fields = (
            'mcid',
            'size_uniref50',
            'avg_len',
            'lc_percent',
            'cc_percent',
            'dis_percent',
            'tm',
            'pfam_da',
            'da_percent',
            'size_pfam',
            'overlap_label',
        )
