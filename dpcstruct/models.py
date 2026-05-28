# dpcstruct/models.py
"""
DPCstruct models — structure-based protein domain metaclusters.

Database: managed = False for all models.

Index documentation (indexes live in the database, declared here for reference):
  dpcstruct_mcs_properties : PRIMARY KEY mc_id                    (implicit B-Tree)
                             idx_per_mcid_dpcstruct               (functional B-Tree on
                                 CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER))
                             idx_dpcstruct_mcs_per_pfam        (GIN trigram on pfam_da)

  dpcstruct_mcs_sequences  : idx_dpcstruct_mcs_per_prot        (B-Tree on protein_id)
                             idx_dpcstruct_seqs_per_mc          (B-Tree on mc_id)

  dpcstruct_cath           : idx_dpcstruct_cath_per_mc          (B-Tree on dpc_mcid)

  dpcstruct_scop           : idx_dpcstruct_scop_per_mc          (B-Tree on dpc_mcid)
"""

from django.db import models
from django.contrib.postgres.indexes import GinIndex
from dpc.models import DpcUniprotProtein


class DpcStructMcsProperty(models.Model):
    """
    Structural and Pfam annotation properties of DPCstruct metaclusters.

    DB table : dpcstruct_mcs_properties
    Columns  : mc_id       VARCHAR(50) PRIMARY KEY
               mc_size     INTEGER NOT NULL
               len_aa      DOUBLE PRECISION  (nullable)
               len_std     DOUBLE PRECISION  (nullable)
               len_ratio   DOUBLE PRECISION  (nullable)
               plddt       DOUBLE PRECISION  (nullable)
               disorder    DOUBLE PRECISION  (nullable)
               tmscore     DOUBLE PRECISION  (nullable)
               lddt        DOUBLE PRECISION  (nullable)
               pident      DOUBLE PRECISION  (nullable)
               pfam_score  DOUBLE PRECISION  (nullable)
               pfam_da     TEXT              (nullable) — dash-separated Pfam IDs

    Indexes  :
      idx_per_mcid_dpcstruct          Functional B-Tree — same natural-sort strategy
                                      as DPCfam, pre-computing the integer from 'MC{n}'.
      idx_dpcstruct_mcs_per_pfam   GIN trigram — same approach as DPCfam, enabling
                                      fast regex/ILIKE searches on the pfam_da text field.
    """
    mc_id = models.CharField(max_length=50, primary_key=True)
    mc_size = models.IntegerField()               
    len_aa = models.FloatField(null=True, blank=True)
    len_std = models.FloatField(null=True, blank=True)
    len_ratio = models.FloatField(null=True, blank=True)
    plddt = models.FloatField(null=True, blank=True)
    disorder = models.FloatField(null=True, blank=True)
    tmscore = models.FloatField(null=True, blank=True)
    lddt = models.FloatField(null=True, blank=True)
    pident = models.FloatField(null=True, blank=True)
    pfam_score = models.FloatField(null=True, blank=True)
    pfam_da = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'dpcstruct_mcs_properties'
        managed = False
        verbose_name = 'DPCstruct MC Property'
        verbose_name_plural = 'DPCstruct MC Properties'
        # Declared for documentation — indexes already exist in the database.
        indexes = [
            GinIndex(
                fields=['pfam_da'],
                name='idx_dpcstruct_mcs_per_pfam',
                opclasses=['gin_trgm_ops'],
            ),
        ]

    def __str__(self):
        return self.mc_id


class DpcStructMcsSequence(models.Model):
    """
    Maps individual proteins to their DPCstruct metacluster with positional
    range information.

    DB table : dpcstruct_mcs_sequences
    Columns  : id         BIGSERIAL PRIMARY KEY
               mc_id      VARCHAR(50) NOT NULL  FK -> dpcstruct_mcs_properties(mc_id)
               protein_id VARCHAR(50) NOT NULL  FK -> dpc_uniprot_proteins(protein_id)
               prot_range VARCHAR(100) NOT NULL
               prot_seq   TEXT  (nullable)

    Indexes  :
      idx_dpcstruct_mcs_per_prot  B-Tree on protein_id
          — used by protein_detail view to find all DPCstruct metaclusters for one protein
      idx_dpcstruct_seqs_per_mc    B-Tree on mc_id
          — used by metacluster detail view to paginate sequences for one metacluster
    """
    id = models.BigAutoField(primary_key=True)

    mc = models.ForeignKey(
        DpcStructMcsProperty,
        on_delete=models.CASCADE,
        db_column='mc_id',              # schema column name
        related_name='sequences',
    )
    protein = models.ForeignKey(
        DpcUniprotProtein,
        on_delete=models.CASCADE,
        db_column='protein_id',         # schema column name
        related_name='dpcstruct_sequences',
    )

    prot_range = models.CharField(max_length=100)
    prot_seq = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'dpcstruct_mcs_sequences'
        managed = False
        indexes = [
            models.Index(fields=['mc'], name='idx_dpcstruct_seqs_per_mc'),
            models.Index(fields=['protein'], name='idx_dpcstruct_mcs_per_prot'),
        ]

    def __str__(self):
        return f"{self.mc.mc_id} - {self.protein.protein_id}"


class DpcStructCath(models.Model):
    """
    CATH fold annotations aligned against DPCstruct metaclusters.
    CATH classifies protein structures by Class, Architecture, Topology,
    and Homologous superfamily.

    DB table : dpcstruct_cath
    Columns  : cath_query   VARCHAR(50) PRIMARY KEY
               dpc_mcid     VARCHAR(50) NOT NULL  FK -> dpcstruct_mcs_properties(mc_id)
               dpc_target   VARCHAR(50) NOT NULL
               q_range      VARCHAR(100)  (nullable)
               t_range      VARCHAR(100)  (nullable)
               qlen         INTEGER       (nullable)
               tlen         INTEGER       (nullable)
               qcov         DOUBLE PRECISION  (nullable)
               tcov         DOUBLE PRECISION  (nullable)
               alnlen       INTEGER       (nullable)
               qtmscore     DOUBLE PRECISION  (nullable)
               ttmscore     DOUBLE PRECISION  (nullable)
               alntmscore   DOUBLE PRECISION  (nullable)
               lddt         DOUBLE PRECISION  (nullable)
               pident       DOUBLE PRECISION  (nullable)

    Index  :
      idx_dpcstruct_cath_per_mc    B-Tree on dpc_mcid
          — used by metacluster detail view to count and sample CATH annotations
    """
    cath_query = models.CharField(max_length=50, primary_key=True)

    # db_column='dpc_mcid' mirrors the schema FK column name exactly.
    mc = models.ForeignKey(
        DpcStructMcsProperty,
        on_delete=models.CASCADE,
        db_column='dpc_mcid',
        related_name='cath_annotations',
    )

    dpc_target = models.CharField(max_length=50)
    q_range = models.CharField(max_length=100, null=True, blank=True)
    t_range = models.CharField(max_length=100, null=True, blank=True)
    qlen = models.IntegerField(null=True, blank=True)
    tlen = models.IntegerField(null=True, blank=True)
    qcov = models.FloatField(null=True, blank=True)
    tcov = models.FloatField(null=True, blank=True)
    alnlen = models.IntegerField(null=True, blank=True)
    qtmscore = models.FloatField(null=True, blank=True)
    ttmscore = models.FloatField(null=True, blank=True)
    alntmscore = models.FloatField(null=True, blank=True)
    lddt = models.FloatField(null=True, blank=True)
    pident = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'dpcstruct_cath'
        managed = False
        indexes = [
            models.Index(fields=['mc'], name='idx_dpcstruct_cath_per_mc'),
        ]

    def __str__(self):
        return f"CATH {self.cath_query} -> MC {self.mc.mc_id}"


class DpcStructScop(models.Model):
    """
    SCOP fold annotations aligned against DPCstruct metaclusters.
    SCOP classifies proteins by evolutionary and structural relationships.

    DB table : dpcstruct_scop
    Columns  : scop_query   VARCHAR(50) PRIMARY KEY
               dpc_mcid     VARCHAR(50) NOT NULL  FK -> dpcstruct_mcs_properties(mc_id)
               dpc_target   VARCHAR(50) NOT NULL
               q_range      VARCHAR(50)   (nullable)  
               t_range      VARCHAR(50)   (nullable)
               qlen         INTEGER       (nullable)
               tlen         INTEGER       (nullable)
               qcov         DOUBLE PRECISION  (nullable)
               tcov         DOUBLE PRECISION  (nullable)
               alnlen       INTEGER       (nullable)
               qtmscore     DOUBLE PRECISION  (nullable)
               ttmscore     DOUBLE PRECISION  (nullable)
               alntmscore   DOUBLE PRECISION  (nullable)
               lddt         DOUBLE PRECISION  (nullable)
               pident       DOUBLE PRECISION  (nullable)

    Index  :
      idx_dpcstruct_scop_per_mc    B-Tree on dpc_mcid
          — used by metacluster detail view to count and sample SCOP annotations
    """
    scop_query = models.CharField(max_length=50, primary_key=True)

    # db_column='dpc_mcid' mirrors the schema FK column name exactly.
    mc = models.ForeignKey(
        DpcStructMcsProperty,
        on_delete=models.CASCADE,
        db_column='dpc_mcid',
        related_name='scop_annotations',
    )

    dpc_target = models.CharField(max_length=50)
    q_range = models.CharField(max_length=50, null=True, blank=True)
    t_range = models.CharField(max_length=50, null=True, blank=True)
    qlen = models.IntegerField(null=True, blank=True)
    tlen = models.IntegerField(null=True, blank=True)
    qcov = models.FloatField(null=True, blank=True)
    tcov = models.FloatField(null=True, blank=True)
    alnlen = models.IntegerField(null=True, blank=True)
    qtmscore = models.FloatField(null=True, blank=True)
    ttmscore = models.FloatField(null=True, blank=True)
    alntmscore = models.FloatField(null=True, blank=True)
    lddt = models.FloatField(null=True, blank=True)
    pident = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'dpcstruct_scop'
        managed = False
        indexes = [
            models.Index(fields=['mc'], name='idx_dpcstruct_scop_per_mc'),
        ]

    def __str__(self):
        return f"SCOP {self.scop_query} -> MC {self.mc.mc_id}"
