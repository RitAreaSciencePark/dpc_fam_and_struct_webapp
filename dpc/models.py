# dpc/models.py
"""
Shared data models for DPC, DPCFam, and DPCStruct applications.
These models represent core entities that are referenced by multiple applications.
"""

from django.db import models


class DpcUniprotProtein(models.Model):
    """
    Core UniProt Protein registry for both DPCFam and DPCStruct
    Acts as the central reference for all protein sequences used in both applications.
    """
    protein_id = models.CharField(max_length=50, primary_key=True)
    protein_length = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'dpc_uniprot_proteins'
        managed = False
        verbose_name = 'DPC UniProt Protein'
        verbose_name_plural = 'DPC UniProt Proteins'

    def __str__(self):
        return self.protein_id


class DpcPfamDomain(models.Model):
    """
    Pfam Domain registry shared across DPCFam and DPCStruct
    Stores unique Pfam domain identifiers and their types
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
    Pfam domain annotations for UniRef50 proteins
    Maps Pfam domains to specific positions on UniRef50 protein sequences
    Used by both DPCFam and DPCStruct applications
    """
    id = models.BigAutoField(primary_key=True)
    
    uniref50 = models.ForeignKey(
        DpcUniprotProtein,
        on_delete=models.CASCADE,
        db_column='uniref50_id',
        related_name='pfam_domains',
    )
    
    pfam_id = models.ForeignKey(
        DpcPfamDomain,
        on_delete=models.CASCADE,
        db_column='pfam_ids',
    )
    
    pfam_ranges = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'dpc_uniref50_pfam'
        managed = False
        indexes = [
            models.Index(fields=['uniref50']),
            models.Index(fields=['pfam_id']),
        ]

    def __str__(self):
        return f"{self.uniref50.protein_id} - {self.pfam_id.pfam_id}"
