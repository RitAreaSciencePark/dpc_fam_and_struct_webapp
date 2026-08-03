# api/serializers.py
"""
Serializers turn our existing managed=False models into JSON, and back.
Nothing here touches the database schema: these classes only describe
which fields to expose and how to rename or resolve foreign keys.
"""

from rest_framework import serializers

from dpcfam.models import DpcfamMcsProperty, DpcfamMcsSequence
from dpcstruct.models import DpcStructMcsProperty, DpcStructMcsSequence


class DpcfamMcsPropertySerializer(serializers.ModelSerializer):
    """One DPCfam metacluster: intrinsic properties and Pfam annotation."""

    class Meta:
        model = DpcfamMcsProperty
        fields = [
            'mcid', 'size_uniref50', 'avg_len', 'std_avg_len',
            'lc_percent', 'cc_percent', 'dis_percent', 'tm',
            'pfam_da', 'da_percent', 'avg_ov_percent', 'overlap_label',
        ]


class DpcfamMcsMemberSerializer(serializers.ModelSerializer):
    """
    One seed sequence ('member') of a DPCfam metacluster.
    protein_id is resolved from the ForeignKey to DpcUniprotProtein so the
    client receives a plain UniProt accession string, not a nested object.
    """

    protein_id = serializers.CharField(source='protein.protein_id', read_only=True)

    class Meta:
        model = DpcfamMcsSequence
        fields = ['id', 'protein_id', 'seq_range']


class DpcStructMcsPropertySerializer(serializers.ModelSerializer):
    """One DPCstruct metacluster: structural properties and Pfam annotation."""

    class Meta:
        model = DpcStructMcsProperty
        fields = [
            'mc_id', 'mc_size', 'len_aa', 'len_std', 'len_ratio',
            'plddt', 'disorder', 'tmscore', 'lddt', 'pident',
            'pfam_score', 'pfam_da',
        ]


class DpcStructMcsMemberSerializer(serializers.ModelSerializer):
    """One representative sequence ('member') of a DPCstruct metacluster."""

    protein_id = serializers.CharField(source='protein.protein_id', read_only=True)

    class Meta:
        model = DpcStructMcsSequence
        fields = ['id', 'protein_id', 'prot_range']
