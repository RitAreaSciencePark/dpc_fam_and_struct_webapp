import django_tables2 as tables
from .models import DpcStructMcsProperty

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
    pfam_labels = tables.Column(verbose_name="Pfam Labels")

    def render_pfam_score(self, value):
        if value is None:
            return "N/A"
        # Check for NaN if it's a float
        import math
        if isinstance(value, float) and math.isnan(value):
            return "N/A"
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
            'pfam_labels',
        )
