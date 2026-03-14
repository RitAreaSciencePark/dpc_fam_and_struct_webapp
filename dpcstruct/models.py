from django.db import models


class DpcStructMcsProperty(models.Model):
    """
    DPCStruct Metacluster Properties Model
    Stores biological and structural properties of protein metaclusters
    """
    # Primary identifier
    mc_id = models.CharField(max_length=50, primary_key=True)
    
    # Cluster metrics
    mc_size = models.IntegerField(null=True, blank=True)
    
    # Length metrics
    len_aa = models.FloatField(null=True, blank=True)
    len_std = models.FloatField(null=True, blank=True)
    len_ratio = models.FloatField(null=True, blank=True)
    
    # Quality metrics
    plddt = models.FloatField(null=True, blank=True)
    disorder = models.FloatField(null=True, blank=True)
    tmscore = models.FloatField(null=True, blank=True)
    lddt = models.FloatField(null=True, blank=True)
    pident = models.FloatField(null=True, blank=True)
    
    # Pfam-related fields
    pfam_score = models.FloatField(null=True, blank=True)
    pfam_da = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'dpcstruct_mcs_properties'
        managed = False
        verbose_name = 'DPCStruct MC Property'
        verbose_name_plural = 'DPCStruct MC Properties'

    def __str__(self):
        return self.mc_id


class DpcStructMcsSequence(models.Model):
    """
    DPCStruct Metacluster Sequences Model
    Maps UniRef50 proteins to DPCStruct metaclusters with position ranges
    """
    id = models.BigAutoField(primary_key=True)
    
    mc = models.ForeignKey(
        DpcStructMcsProperty,
        on_delete=models.CASCADE,
        related_name='sequences',
        db_column='mc_id'
    )
    
    protein = models.ForeignKey(
        'dpc.DpcUniprotProtein',
        on_delete=models.CASCADE,
        related_name='dpcstruct_sequences',
        db_column='protein_id'
    )
    
    prot_range = models.CharField(max_length=100)
    prot_seq = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'dpcstruct_mcs_sequences'
        indexes = [
            models.Index(fields=['mc']),
            models.Index(fields=['protein']),
        ]
        managed = False

    def __str__(self):
        return f"{self.mc.mc_id} - {self.protein.protein_id}"


class DpcStructCath(models.Model):
    """
    DPCStruct CATH Annotations Model
    Stores CATH fold annotations for DPCStruct metaclusters
    CATH (Class, Architecture, Topology, Homology) fold classifications
    """
    # CATH fold identifier
    cath_query = models.CharField(max_length=50,primary_key=True)
    
    # FK to metacluster
    mc = models.ForeignKey(
        DpcStructMcsProperty,
        on_delete=models.CASCADE,
        related_name='cath_annotations',
        db_column='dpc_mcid'
    )
    
    # DPC target protein
    dpc_target = models.CharField(max_length=50)
    
    # Range information
    q_range = models.CharField(max_length=100, null=True, blank=True)
    t_range = models.CharField(max_length=100, null=True, blank=True)
    
    # Length information
    qlen = models.IntegerField(null=True, blank=True)
    tlen = models.IntegerField(null=True, blank=True)
    
    # Coverage metrics
    qcov = models.FloatField(null=True, blank=True)
    tcov = models.FloatField(null=True, blank=True)
    alnlen = models.IntegerField(null=True, blank=True)
    
    # Quality scores
    qtmscore = models.FloatField(null=True, blank=True)
    ttmscore = models.FloatField(null=True, blank=True)
    alntmscore = models.FloatField(null=True, blank=True)
    lddt = models.FloatField(null=True, blank=True)
    pident = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'dpcstruct_cath'
        indexes = [
            models.Index(fields=['mc']),
            models.Index(fields=['cath_query']),
            models.Index(fields=['dpc_target']),
        ]
        managed = False
    
    def __str__(self):
        return f"CATH {self.cath_query} -> MC {self.mc.mc_id}"


class DpcStructScop(models.Model):
    """
    DPCStruct SCOP Annotations Model
    Stores SCOP fold annotations for DPCStruct metaclusters
    SCOP (Structural Classification of Proteins) fold classifications
    """
    # SCOP identifier
    scop_query = models.CharField(max_length=50,primary_key=True)
    
    # FK to metacluster
    mc = models.ForeignKey(
        DpcStructMcsProperty,
        on_delete=models.CASCADE,
        related_name='scop_annotations',
        db_column='dpc_mcid'
    )
    
    # DPC target protein
    dpc_target = models.CharField(max_length=50)
    
    # Range information
    q_range = models.CharField(max_length=50, null=True, blank=True)
    t_range = models.CharField(max_length=50, null=True, blank=True)
    
    # Length information
    qlen = models.IntegerField(null=True, blank=True)
    tlen = models.IntegerField(null=True, blank=True)
    
    # Coverage metrics
    qcov = models.FloatField(null=True, blank=True)
    tcov = models.FloatField(null=True, blank=True)
    alnlen = models.IntegerField(null=True, blank=True)
    
    # Quality scores
    qtmscore = models.FloatField(null=True, blank=True)
    ttmscore = models.FloatField(null=True, blank=True)
    alntmscore = models.FloatField(null=True, blank=True)
    lddt = models.FloatField(null=True, blank=True)
    pident = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'dpcstruct_scop'
        indexes = [
            models.Index(fields=['mc']),
            models.Index(fields=['scop_query']),
            models.Index(fields=['dpc_target']),
        ]
        managed = False
    
    def __str__(self):
        return f"SCOP {self.scop_query} -> MC {self.mc.mc_id}"
