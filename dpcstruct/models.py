from django.db import models
class DpcStructMcsProperty(models.Model):
    # A. MC properties
    mc_id = models.CharField(max_length=50, primary_key=True)
    mc_size = models.IntegerField(null=True, blank=True)
    len_aa = models.FloatField(null=True, blank=True)
    len_std = models.FloatField(null=True, blank=True)
    len_ratio = models.FloatField(null=True, blank=True)
    plddt = models.FloatField(null=True, blank=True)
    disorder = models.FloatField(null=True, blank=True)
    tmscore = models.FloatField(null=True, blank=True)
    lddt = models.FloatField(null=True, blank=True)
    pident = models.FloatField(null=True, blank=True)
    # B. PFAM-related fields
    pfam_score = models.FloatField(null=True, blank=True)
    pfam_labels = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'dpcstruct_mcs_properties'
        managed = False
        verbose_name = 'DPCStruct MC Property'
        verbose_name_plural = 'DPCStruct MC Properties'

    def __str__(self):
        return self.mc_id
