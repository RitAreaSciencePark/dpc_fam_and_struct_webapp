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


class DpcStructMcsSequence(models.Model):
    id = models.BigAutoField(primary_key=True)
    mc = models.ForeignKey(
        DpcStructMcsProperty,
        on_delete=models.CASCADE,
        related_name='sequences',
        db_column='mc_id'
    )
    protein_id = models.CharField(max_length=50)
    prot_range = models.CharField(max_length=100)
    prot_seq = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'dpcstruct_mcs_sequences'
        indexes = [
            models.Index(fields=['mc', 'id']),
            models.Index(fields=['protein_id']),
        ]
        managed = False

    def __str__(self):
        return f"{self.mc.mc_id} - {self.protein_id}"
