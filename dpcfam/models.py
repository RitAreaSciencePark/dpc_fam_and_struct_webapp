# dpcfam/models.py
from django.db import models

class MCSProperty(models.Model):
    # A. MC Cluster properties
    mcid = models.CharField(max_length=50, primary_key=True)
    size_uniref50 = models.IntegerField(null=True, blank=True)
    avg_len = models.FloatField(null=True, blank=True)
    std_avg_len = models.FloatField(null=True, blank=True)
    lc_percent = models.FloatField(null=True, blank=True)
    cc_percent = models.FloatField(null=True, blank=True)
    dis_percent = models.FloatField(null=True, blank=True)
    tm = models.FloatField(null=True, blank=True)
    # B. PFAM-related fields
    pfam_da = models.TextField(null=True, blank=True)
    da_percent = models.FloatField(null=True, blank=True)
    size_pfam = models.IntegerField(null=True, blank=True)
    avg_ov_percent = models.FloatField(null=True, blank=True)
    overlap_label = models.CharField(max_length=50, null=True, blank=True)
    class Meta:
        db_table = 'mcs_properties'
        managed = False

    def __str__(self):
        return self.mcid
 
class MCSSequence(models.Model):
    id = models.BigAutoField(primary_key=True)
    mc = models.ForeignKey(
        MCSProperty,
        on_delete=models.CASCADE,
        related_name='sequences',
        db_column='mcid'
    )

    protein = models.ForeignKey(
        'UniRef50Protein',
        on_delete=models.CASCADE,
        related_name='mcs_sequences',
        db_column='protein_id'
    )
    seq_range = models.CharField(max_length=100)
    seq_length = models.IntegerField()
    aa_seq = models.TextField()

    class Meta:
        db_table = 'mcs_sequences'
        indexes = [
            models.Index(fields=['mc', 'id']),
            models.Index(fields=['protein']),
        ]
        managed = False
    def __str__(self):
        return f"{self.mc.mcid} - {self.protein.uniref50_id}"


class AlphaFold(models.Model):
    id = models.BigAutoField(primary_key=True)
    mc = models.ForeignKey(
        MCSProperty,
        on_delete=models.CASCADE,
        related_name='alphafolds',
        db_column='mcid'
    )

    alphafold_prot = models.TextField()
    seq_range = models.CharField(max_length=100)
    hmm_coverage = models.FloatField()
    avg_plddt = models.FloatField()

    class Meta:
        db_table = 'alphafold_reps'
        indexes = [
            models.Index(fields=['mc']),
        ]
        managed = False 

    def __str__(self):
        return f"{self.mc.mcid} - {self.alphafold_prot}"


class UniRef50Protein(models.Model):
    uniref50_id = models.CharField(max_length=50, primary_key=True)
    uniprotkb_id = models.CharField(max_length=100, null=True, blank=True)
    uniprotkb_accession = models.CharField(max_length=50, null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "uniref50_proteins"
        managed = False

    def __str__(self):
        return self.uniref50_id


class UniRef50Pfam(models.Model):
    id = models.BigAutoField(primary_key=True)
    uniref50 = models.ForeignKey(
        UniRef50Protein,
        on_delete=models.CASCADE,
        db_column="uniref50_id",
        related_name="pfam_domains",
    )
    pfam_ids = models.CharField(max_length=50)
    pfam_ranges = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "uniref50_pfam"
        managed = False
