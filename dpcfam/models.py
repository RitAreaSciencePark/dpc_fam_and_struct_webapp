# dpcfam/models.py
"""
DPCFam Models - Domain Family Classification System
Defines models for metaclusters and their properties in the DPCFam database
"""

from django.db import models
from dpc.models import DpcUniprotProtein, DpcUniref50Pfam


class DpcfamMcsProperty(models.Model):
    """
    DPCFam Metacluster Properties Model
    Stores biological and structural properties of protein metaclusters in DPCFam
    
    Fields:
    - Cluster metrics: size_uniref50 (number of sequences in cluster)
    - Length metrics: avg_len, std_avg_len (average and std dev of protein lengths)
    - Region composition: lc_percent, cc_percent, dis_percent (region type percentages)
    - Structural: tm (transmembrane score)
    - Pfam metrics: pfam_labels (Pfam domain assignments), da_percent (% with annotations)
    - Overlap metrics: avg_ov_percent, overlap_label
    """
    mcid = models.CharField(max_length=50, primary_key=True)
    size_uniref50 = models.IntegerField(null=True, blank=True)
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
        verbose_name = 'DPCFam MC Property'
        verbose_name_plural = 'DPCFam MC Properties'

    def __str__(self):
        return self.mcid


class DpcfamMcsSequence(models.Model):
    """
    DPCFam Metacluster Sequences Model
    Maps UniRef50 proteins to DPCFam metaclusters with position information
    """
    id = models.BigAutoField(primary_key=True)
    
    mc = models.ForeignKey(
        DpcfamMcsProperty,
        on_delete=models.CASCADE,
        related_name='sequences',
        db_column='mcid'
    )

    protein = models.ForeignKey(
        DpcUniprotProtein,
        on_delete=models.CASCADE,
        related_name='dpcfam_sequences',
        db_column='protein_id'
    )
    
    seq_range = models.CharField(max_length=100)
    seq_length = models.IntegerField()
    aa_seq = models.TextField()

    class Meta:
        db_table = 'dpcfam_mcs_sequences'
        indexes = [
            models.Index(fields=['mc']),
            models.Index(fields=['protein']),
        ]
        managed = False

    def __str__(self):
        return f"{self.mc.mcid} - {self.protein.protein_id}"


class DpcfamAlphaFoldRep(models.Model):
    """
    DPCFam AlphaFold Representative Structures
    Stores representative AlphaFold-predicted structures for each metacluster
    """
    id = models.BigAutoField(primary_key=True)
    
    mc = models.ForeignKey(
        DpcfamMcsProperty,
        on_delete=models.CASCADE,
        related_name='alphafolds',
        db_column='mcid'
    )

    alphafold_prot = models.TextField()
    seq_range = models.CharField(max_length=100)
    hmm_coverage = models.FloatField()
    avg_plddt = models.FloatField()

    class Meta:
        db_table = 'dpcfam_alphafold_reps'
        indexes = [
            models.Index(fields=['mc']),
        ]
        managed = False
        verbose_name = 'DPCFam AlphaFold Representative'
        verbose_name_plural = 'DPCFam AlphaFold Representatives'

    def __str__(self):
        return f"{self.mc.mcid} - {self.alphafold_prot}"


# Legacy model names for backward compatibility (deprecated)
class UniRef50Protein(models.Model):
    """
    Deprecated: Use DpcUniprotProtein instead
    Maintained for backward compatibility with existing code
    """
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
    """
    Deprecated: Use DpcUniref50Pfam instead
    Maintained for backward compatibility with existing code
    """
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


# Legacy model names for backward compatibility (deprecated)
class MCSProperty(DpcfamMcsProperty):
    """Deprecated: Use DpcfamMcsProperty instead"""
    class Meta:
        proxy = True
        
    def save(self, *args, **kwargs):
        raise NotImplementedError("Use DpcfamMcsProperty instead")


class MCSSequence(DpcfamMcsSequence):
    """Deprecated: Use DpcfamMcsSequence instead"""
    class Meta:
        proxy = True
        
    def save(self, *args, **kwargs):
        raise NotImplementedError("Use DpcfamMcsSequence instead")


class AlphaFold(DpcfamAlphaFoldRep):
    """Deprecated: Use DpcfamAlphaFoldRep instead"""
    class Meta:
        proxy = True
        
    def save(self, *args, **kwargs):
        raise NotImplementedError("Use DpcfamAlphaFoldRep instead")
