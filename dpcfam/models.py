# dpcfam/models.py
from django.db import models


class MCSProperty(models.Model):
    mcid = models.CharField(max_length=100, primary_key=True)
    size_uniref50 = models.IntegerField(null=True, blank=True)
    avg_len = models.FloatField(null=True, blank=True)
    lc_percent = models.FloatField(null=True, blank=True)
    cc_percent = models.FloatField(null=True, blank=True)
    dis_percent = models.FloatField(null=True, blank=True)
    tm = models.FloatField(null=True, blank=True)
    size_pfam = models.IntegerField(null=True, blank=True)
    pfam_da = models.CharField(max_length=200, null=True, blank=True)
    da_percent = models.FloatField(null=True, blank=True)
    overlap_label = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'mcs_properties'
        managed = False

    def __str__(self):
        return self.mcid
