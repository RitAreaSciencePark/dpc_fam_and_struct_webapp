# dpcfam/tables.py
import django_tables2 as tables
from django.utils.html import format_html
from .models import DpcfamMcsProperty


class DpcfamMcsPropertyTable(tables.Table):
    mcid = tables.LinkColumn("mcs_detail", args=[tables.A("mcid")], verbose_name="MCID")
    size_uniref50 = tables.Column(verbose_name="Size UniRef50")
    avg_len = tables.Column(verbose_name="Avg. Len.")
    lc_percent = tables.Column(verbose_name="% LC")
    cc_percent = tables.Column(verbose_name="% CC")
    dis_percent = tables.Column(verbose_name="% DIS")
    tm = tables.Column(verbose_name="Avg. TM")
    pfam_da = tables.Column(
        verbose_name="Pfam DA",
        attrs={
            "th": {"style": "border-left: 2px dotted #adb5bd;"},
            "td": {"style": "border-left: 2px dotted #adb5bd;"}
        }
    )
    da_percent = tables.Column(verbose_name="% DA")
    avg_ov_percent = tables.Column(verbose_name="% Avg. Ov.")
    overlap_label = tables.Column(verbose_name="Overlap Label")

    def render_pfam_da(self, value):
        if value:
            if value == 'UNKNOWN':
                from django.utils.safestring import mark_safe
                return mark_safe('<span style="background-color: #dc3545; color: #fff; padding: 4px 10px; border-radius: 4px; font-weight: bold; display: inline-block;">UNKNOWN</span>')
            else:
                # Split by - as standardized in DB
                ids = value.split('-')
                links = [
                    format_html('<a href="/search/?database=Pfam&query_id={}" style="color: #0b4f8a; font-weight: bold; text-decoration: none;">{}</a>', id_val, id_val)
                    for id_val in ids
                ]
                from django.utils.safestring import mark_safe
                return mark_safe('-'.join(links))
        return value

    def render_overlap_label(self, value):
        if value:
            label = str(value).lower()
            if label == "equivalent":
                style = "background-color: #ffc107; color: #000; padding: 4px 10px; border-radius: 4px; font-weight: bold; display: inline-block;"
            elif label == "reduced":
                style = "background-color: #0d6efd; color: #fff; padding: 4px 10px; border-radius: 4px; font-weight: bold; display: inline-block;"
            elif label == "extended":
                style = "background-color: #e83e8c; color: #fff; padding: 4px 10px; border-radius: 4px; font-weight: bold; display: inline-block;"
            elif label == "shifted":
                style = "background-color: #198754; color: #fff; padding: 4px 10px; border-radius: 4px; font-weight: bold; display: inline-block;"
            elif label == "none":
                style = "font-weight: 900;"
            else:
                style = ""
            if style:
                return format_html('<span style="{}">{}</span>', style, value)
        return value

    class Meta:
        model = DpcfamMcsProperty
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
            'avg_ov_percent',
            'overlap_label',
        )