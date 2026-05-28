# dpc/models.py
"""
Shared data models for DPC, DPCfam, and DPCstruct applications.

Database: managed = False for all models.

Index documentation (indexes live in the database, declared here for reference):
  dpc_uniprot_proteins  : PRIMARY KEY protein_id  (implicit B-Tree)
  dpc_pfam_domains      : PRIMARY KEY pfam_id      (implicit B-Tree)
  dpc_uniref50_pfam     : idx_dpc_pfams_per_protein  (B-Tree on uniref50_id)
                          idx_dpc_ranges_per_pfamid    (B-Tree on pfam_ids)
"""

from django.db import models
from django.contrib.postgres.indexes import GinIndex


class DpcUniprotProtein(models.Model):
    """
    Master Central Registry for all protein sequences.
    Acts as the single source of truth referenced by every mapping table in
    both DPCfam (DPCfam_mcs_sequences) and DPCstruct (DPCstruct_mcs_sequences),
    as well as the cross-application Pfam annotation table (dpc_uniref50_pfam).

    DB table : dpc_uniprot_proteins
    Columns  : protein_id VARCHAR(50) PRIMARY KEY
               protein_length INTEGER NOT NULL
    """
    protein_id = models.CharField(max_length=50, primary_key=True)
    protein_length = models.IntegerField()       

    class Meta:
        db_table = 'dpc_uniprot_proteins'
        managed = False
        verbose_name = 'DPC UniProt Protein'
        verbose_name_plural = 'DPC UniProt Proteins'

    def __str__(self):
        return self.protein_id


class DpcPfamDomain(models.Model):
    """
    Master Central Registry for unique Pfam domain identifiers.
    Used for exact-match validation in the search router and as the FK target for dpc_uniref50_pfam.

    DB table : dpc_pfam_domains
    Columns  : pfam_id   VARCHAR(50) PRIMARY KEY
               pfam_type VARCHAR(50)  (nullable)
    """
    pfam_id = models.CharField(max_length=50, primary_key=True)
    pfam_type = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'dpc_pfam_domains'
        managed = False
        verbose_name = 'DPC Pfam Domain'
        verbose_name_plural = 'DPC Pfam Domains'

    def __str__(self):
        return self.pfam_id


class DpcUniref50Pfam(models.Model):
    """
    Relational mapping joining UniProt proteins to their Pfam domain annotations.
    Stores coordinate ranges so the protein detail view can reconstruct the graphical domain architecture diagram.

    DB table : dpc_uniref50_pfam
    Columns  : id          BIGSERIAL PRIMARY KEY
               uniref50_id VARCHAR(50) NOT NULL  FK -> dpc_uniprot_proteins(protein_id)
               pfam_ids    VARCHAR(50) NOT NULL  FK -> dpc_pfam_domains(pfam_id)
               pfam_ranges VARCHAR(100)          (nullable)

    Indexes  :
      idx_dpc_pfams_per_protein  B-Tree on uniref50_id
          — used when the protein detail view fetches all Pfam entries for one protein
      idx_dpc_ranges_per_pfamid   B-Tree on pfam_ids
          — available for reverse lookups by Pfam domain
    """
    id = models.BigAutoField(primary_key=True)

    # db_column='uniref50_id' mirrors the schema column name exactly.
    # related_name='pfam_domains' is used in protein_detail view:
    #   DpcUniref50Pfam.objects.filter(uniref50=protein)
    uniref50 = models.ForeignKey(
        DpcUniprotProtein,
        on_delete=models.CASCADE,
        db_column='uniref50_id',
        related_name='pfam_domains',
    )

    # db_column='pfam_ids' mirrors the schema column name exactly.
    # Field is named pfam_id so the template can access p.pfam_id.pfam_id
    # (the outer pfam_id is the Django field; the inner .pfam_id is the PK of DpcPfamDomain).
    pfam_id = models.ForeignKey(
        DpcPfamDomain,
        on_delete=models.CASCADE,
        db_column='pfam_ids',
    )

    pfam_ranges = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'dpc_uniref50_pfam'
        managed = False
        # Declared for documentation — indexes already exist in the database.
        indexes = [
            models.Index(fields=['uniref50'], name='idx_dpc_pfams_per_protein'),
            models.Index(fields=['pfam_id'],  name='idx_dpc_ranges_per_pfamid'),
        ]

    def __str__(self):
        return f"{self.uniref50.protein_id} - {self.pfam_id.pfam_id}"
