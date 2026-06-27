# dpcfam/models.py
"""
DPCfam models — sequence-based protein domain metaclusters.

Database: managed = False for all models.

Index documentation (indexes live in the database, declared here for reference):
  dpcfam_mcs_properties  : PRIMARY KEY mcid                     (implicit B-Tree)
                           idx_per_mcid_dpcfam                  (functional B-Tree on 
                                        CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER))
                           idx_dpcfam_mcs_per_pfam_da           (GIN trigram on pfam_da)

  dpcfam_mcs_sequences   : idx_dpcfam_mcs_per_protein           (B-Tree on protein_id)
                           idx_dpcfam_seqs_per_mcid             (B-Tree on mcid)

  dpcfam_alphafold_reps  : idx_dpcfam_reps_per_mcid             (B-Tree on mcid)
"""

from django.db import models
from django.contrib.postgres.indexes import GinIndex
from dpc.models import DpcUniprotProtein


class DpcfamMcsProperty(models.Model):
    """
    Biological and Pfam annotation properties of DPCfam metaclusters.

    DB table : dpcfam_mcs_properties
    Columns  : mcid          VARCHAR(50) PRIMARY KEY
               size_uniref50 INTEGER NOT NULL
               avg_len       DOUBLE PRECISION  (nullable)
               std_avg_len   DOUBLE PRECISION  (nullable)
               lc_percent    DOUBLE PRECISION  (nullable)
               cc_percent    DOUBLE PRECISION  (nullable)
               dis_percent   DOUBLE PRECISION  (nullable)
               tm            DOUBLE PRECISION  (nullable)
               pfam_da       TEXT              (nullable) — dash-separated Pfam IDs
               da_percent    DOUBLE PRECISION  (nullable)
               avg_ov_percent DOUBLE PRECISION (nullable)
               overlap_label  VARCHAR(50)      (nullable)

    Indexes  :
      idx_per_mcid_dpcfam         Functional B-Tree — pre-computes the integer extracted
                                  from 'MC{n}' so ORDER BY mc_num uses the index directly
                                  instead of sorting in memory at query time.
      idx_dpcfam_mcs_per_pfam_da  GIN trigram — decomposes pfam_da into 3-character windows
                                  so regex / ILIKE pattern searches locate matching rows via
                                  index intersection instead of a full sequential scan.
    """
    mcid = models.CharField(max_length=50, primary_key=True)
    size_uniref50 = models.IntegerField()     
    avg_len = models.FloatField(null=True, blank=True)
    std_avg_len = models.FloatField(null=True, blank=True)
    lc_percent = models.FloatField(null=True, blank=True)
    cc_percent = models.FloatField(null=True, blank=True)
    dis_percent = models.FloatField(null=True, blank=True)
    tm = models.FloatField(null=True, blank=True)
    pfam_da = models.TextField(null=True, blank=True)
    da_percent = models.FloatField(null=True, blank=True)
    avg_ov_percent = models.FloatField(null=True, blank=True)
    overlap_label = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'dpcfam_mcs_properties'
        managed = False
        verbose_name = 'DPCfam MC Properties and Pfam Annotations'
        verbose_name_plural = 'DPCfam MC Properties and Pfam Annotations'
        # Declared for documentation — indexes already exist in the database.
        # The GinIndex declaration also serves as an accurate in-code reminder of
        # the operator class (gin_trgm_ops) required by the pg_trgm extension.
        indexes = [
            GinIndex(
                fields=['pfam_da'],
                name='idx_dpcfam_mcs_per_pfam_da',
                opclasses=['gin_trgm_ops'],
            ),
        ]

    def __str__(self):
        return self.mcid


class DpcfamMcsSequence(models.Model):
    """
    Maps individual UniRef50 proteins to their DPCfam metacluster with
    positional range information.

    DB table : dpcfam_mcs_sequences
    Columns  : id         BIGSERIAL PRIMARY KEY
               mcid       VARCHAR(50) NOT NULL  FK -> dpcfam_mcs_properties(mcid)
               protein_id VARCHAR(50) NOT NULL  FK -> dpc_uniprot_proteins(protein_id)
               seq_range  VARCHAR(100) NOT NULL
               seq_length INTEGER NOT NULL
               aa_seq     TEXT NOT NULL

    Indexes  :
      idx_dpcfam_mcs_per_protein  B-Tree on protein_id
          — used by protein_detail view to find all DPCfam metaclusters for one protein
      idx_dpcfam_seqs_per_mcid    B-Tree on mcid
          — used by metacluster detail view to paginate sequences for one metacluster
    """
    id = models.BigAutoField(primary_key=True)

    mc = models.ForeignKey(
        DpcfamMcsProperty,
        on_delete=models.CASCADE,
        db_column='mcid',               # schema column name
        related_name='sequences',
    )
    protein = models.ForeignKey(
        DpcUniprotProtein,
        on_delete=models.CASCADE,
        db_column='protein_id',         # schema column name
        related_name='dpcfam_sequences',
    )

    seq_range = models.CharField(max_length=100)
    seq_length = models.IntegerField()
    aa_seq = models.TextField()

    class Meta:
        db_table = 'dpcfam_mcs_sequences'
        managed = False
        verbose_name = 'DPCfam MC Seed Sequence'
        verbose_name_plural = 'DPCfam MC Seed Sequences'
        indexes = [
            models.Index(fields=['mc'],      name='idx_dpcfam_seqs_per_mcid'),
            models.Index(fields=['protein'], name='idx_dpcfam_mcs_per_protein'),
        ]

    def __str__(self):
        return f"{self.mc.mcid} - {self.protein.protein_id}"


class DpcfamAlphaFoldRep(models.Model):
    """
    Representative AlphaFold-predicted structures for some DPCfam metaclusters.
    Used by the metacluster detail view to populate the 3D Viewer tab.

    DB table : dpcfam_alphafold_reps
    Columns  : id              BIGSERIAL PRIMARY KEY
               mcid            VARCHAR(50) NOT NULL  FK -> dpcfam_mcs_properties(mcid)
               alphafold_prot  TEXT NOT NULL
               seq_range       VARCHAR(100) NOT NULL
               hmm_coverage    DOUBLE PRECISION NOT NULL
               avg_plddt       DOUBLE PRECISION NOT NULL

    Indexes  :
      idx_dpcfam_reps_per_mcid  B-Tree on mcid
          — used by metacluster detail view to fetch all AlphaFold reps for one metacluster
    """
    id = models.BigAutoField(primary_key=True)

    mc = models.ForeignKey(
        DpcfamMcsProperty,
        on_delete=models.CASCADE,
        db_column='mcid',               # schema column name
        related_name='alphafolds',
    )

    alphafold_prot = models.TextField()
    seq_range = models.CharField(max_length=100)
    hmm_coverage = models.FloatField()
    avg_plddt = models.FloatField()

    class Meta:
        db_table = 'dpcfam_alphafold_reps'
        managed = False
        verbose_name = 'DPCfam AlphaFold Representative'
        verbose_name_plural = 'DPCfam AlphaFold Representatives'
        indexes = [
            models.Index(fields=['mc'], name='idx_dpcfam_reps_per_mcid'),
        ]

    def __str__(self):
        return f"{self.mc.mcid} - {self.alphafold_prot}"
