import django_tables2 as tables
from django.utils.html import format_html
from .models import DpcStructMcsProperty, DpcStructCath, DpcStructScop


class DpcStructMcsPropertyTable(tables.Table):
    mc_id = tables.LinkColumn("dpcstruct_detail", args=[tables.A("mc_id")], verbose_name="MCID")
    mc_size = tables.Column(verbose_name="Size")
    len_aa = tables.Column(verbose_name="Avg. Len.")
    len_std = tables.Column(verbose_name="Len. Std")
    len_ratio = tables.Column(verbose_name="Len. Ratio")
    plddt = tables.Column(verbose_name="Plddt")
    disorder = tables.Column(verbose_name="Disorder")
    tmscore = tables.Column(verbose_name="TM-Score")
    lddt = tables.Column(verbose_name="Lddt")
    pident = tables.Column(verbose_name="Pident")
    pfam_score = tables.Column(verbose_name="Score Pfam", empty_values=())
    pfam_da = tables.Column(verbose_name="Pfam DA")

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
        model = DpcStructMcsProperty
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-striped table-hover table-bordered"}
        fields = (
            'mc_id',
            'mc_size',
            'len_aa',
            'len_std',
            'len_ratio',
            'plddt',
            'disorder',
            'tmscore',
            'lddt',
            'pident',
            'pfam_score',
            'pfam_da',
        )


class DpcStructCathTable(tables.Table):
    """
    Table for displaying CATH fold annotations
    """
    cath_query = tables.Column(verbose_name="CATH Fold")
    mc = tables.Column(verbose_name="MCID", accessor='mc.mc_id',
                       order_by='-mc__mc_id')
    dpc_target = tables.Column(verbose_name="DPC Target")
    q_range = tables.Column(verbose_name="Q.Range")
    t_range = tables.Column(verbose_name="T.Range")
    qcov = tables.Column(verbose_name="Q.Cov.", empty_values=())
    tcov = tables.Column(verbose_name="T.Cov.", empty_values=())
    qtmscore = tables.Column(verbose_name="Q.TM-Score", empty_values=())
    ttmscore = tables.Column(verbose_name="T.TM-Score", empty_values=())
    alntmscore = tables.Column(verbose_name="A.TM-Score", empty_values=())
    lddt = tables.Column(verbose_name="LDDT")
    pident = tables.Column(verbose_name="% Ident.")

    def render_cath_query(self, value):
        return format_html(
            '<a href="?view=cath&search_fold={}" style="color: #0b4f8a; font-weight: bold; text-decoration: none;">{}</a>',
            value, value
        )

    def render_mc(self, value, record):
        mc = record.mc
        return format_html(
            '<a href="/dpcstruct/mcs/{}/" style="color: #0b4f8a; font-weight: bold; text-decoration: none;">{}</a>',
            mc.mc_id, mc.mc_id
        )

    class Meta:
        model = DpcStructCath
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-striped table-hover table-bordered"}
        fields = (
            'cath_query',
            'mc',
            'dpc_target',
            'q_range',
            't_range',
            'qcov',
            'tcov',
            'qtmscore',
            'ttmscore',
            'alntmscore',
            'lddt',
            'pident',
        )


class DpcStructScopTable(tables.Table):
    """
    Table for displaying SCOP fold annotations
    """
    scop_query = tables.Column(verbose_name="SCOP Fold")
    mc = tables.Column(verbose_name="MCID", accessor='mc.mc_id',
                       order_by='-mc__mc_id')
    dpc_target = tables.Column(verbose_name="DPC Target")
    q_range = tables.Column(verbose_name="Q.Range")
    t_range = tables.Column(verbose_name="T.Range")
    qcov = tables.Column(verbose_name="Q.Cov.", empty_values=())
    tcov = tables.Column(verbose_name="T.Cov.", empty_values=())
    qtmscore = tables.Column(verbose_name="Q.TM-Score", empty_values=())
    ttmscore = tables.Column(verbose_name="T.TM-Score", empty_values=())
    alntmscore = tables.Column(verbose_name="A.TM-Score", empty_values=())
    lddt = tables.Column(verbose_name="LDDT")
    pident = tables.Column(verbose_name="% Ident.")

    def render_scop_query(self, value):
        return format_html(
            '<a href="?view=scop&search_fold={}" style="color: #0b4f8a; font-weight: bold; text-decoration: none;">{}</a>',
            value, value
        )

    def render_mc(self, value, record):
        mc = record.mc
        return format_html(
            '<a href="/dpcstruct/mcs/{}/" style="color: #0b4f8a; font-weight: bold; text-decoration: none;">{}</a>',
            mc.mc_id, mc.mc_id
        )

    class Meta:
        model = DpcStructScop
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-striped table-hover table-bordered"}
        fields = (
            'scop_query',
            'mc',
            'dpc_target',
            'q_range',
            't_range',
            'qcov',
            'tcov',
            'qtmscore',
            'ttmscore',
            'alntmscore',
            'lddt',
            'pident',
        )