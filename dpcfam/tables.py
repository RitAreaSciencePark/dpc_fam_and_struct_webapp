# dpcfam/tables.py
import django_tables2 as tables
from django.utils.html import format_html
from .models import MCSProperty


class MCSPropertyTable(tables.Table):
    mcid = tables.LinkColumn("mcs_detail", args=[tables.A("mcid")], verbose_name="MCID")
    size_uniref50 = tables.Column(verbose_name="Size UniRef50")
    avg_len = tables.Column(verbose_name="Avg. Len.")
    lc_percent = tables.Column(verbose_name="% LC")
    cc_percent = tables.Column(verbose_name="% CC")
    dis_percent = tables.Column(verbose_name="% DIS")
    tm = tables.Column(verbose_name="Avg. TM")
    pfam_da = tables.Column(verbose_name="Pfam DA")
    da_percent = tables.Column(verbose_name="% DA")
    size_pfam = tables.Column(verbose_name="Size Pfam")
    avg_ov_percent = tables.Column(verbose_name="% Avg. Ov.")
    overlap_label = tables.Column(verbose_name="Overlap Label")

    def render_pfam_da(self, value):
        if value and value != 'UNKNOWN':
            # Split by - as standardized in DB
            ids = value.split('-')
            links = [
                format_html('<a href="/search/?database=PFam&query_id={}" style="color: #0b4f8a; font-weight: bold; text-decoration: none;">{}</a>', id_val, id_val)
                for id_val in ids
            ]
            from django.utils.safestring import mark_safe
            return mark_safe('-'.join(links))
        return value

    class Meta:
        model = MCSProperty
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-striped table-hover table-bordered"}
        fields = (
            'mcid',
            'size_uniref50',
            'avg_len',
            'std_avg_len',
            'lc_percent',
            'cc_percent',
            'dis_percent',
            'tm',
            'pfam_da',
            'da_percent',
            'size_pfam',
            'avg_ov_percent',
            'overlap_label',
        )
