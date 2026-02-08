# dpcfam/models.py
from django.db import models

class MCSProperty(models.Model):
    # A. MC Cluster properties
    mcid = models.CharField(max_length=100, primary_key=True)
    size_uniref50 = models.IntegerField(null=True, blank=True)
    avg_len = models.FloatField(null=True, blank=True)
    std_avg_len = models.FloatField(null=True, blank=True) # Added std_avg_len
    lc_percent = models.FloatField(null=True, blank=True)
    cc_percent = models.FloatField(null=True, blank=True)
    dis_percent = models.FloatField(null=True, blank=True)
    tm = models.FloatField(null=True, blank=True)
    # B. PFAM-related fields
    pfam_da = models.CharField(max_length=200, null=True, blank=True)
    da_percent = models.FloatField(null=True, blank=True)
    size_pfam = models.IntegerField(null=True, blank=True)
    avg_ov_percent = models.FloatField(null=True, blank=True) # Added avg_ov_percent
    overlap_label = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        db_table = 'mcs_properties'
        managed = False

    def __str__(self):
        return self.mcid


class MCSSequence(models.Model):
    id = models.BigAutoField(primary_key=True)
    mcid = models.CharField(max_length=100)
    protein_id = models.CharField(max_length=255)
    seq_range = models.CharField(max_length=100)
    seq_length = models.IntegerField()
    aa_seq = models.TextField()

    class Meta:
        db_table = 'mcs_sequences'
        managed = False

    def __str__(self):
        return f"{self.mcid} - {self.protein_id}"


class AlphaFold(models.Model):
    id = models.BigAutoField(primary_key=True)
    mcid = models.CharField(max_length=100)
    alphafold_prot = models.CharField(max_length=255)
    seq_range = models.CharField(max_length=100)
    hmm_coverage = models.FloatField(null=True, blank=True)
    avg_plddt = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'alphafold_reps'
        managed = False

    def __str__(self):
        return f"{self.mcid} - {self.alphafold_prot}"
