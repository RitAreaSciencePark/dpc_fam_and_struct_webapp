import django_filters
from django import forms
from .models import DpcStructMcsProperty, DpcStructCath, DpcStructScop


class DpcStructMcsPropertyFilter(django_filters.FilterSet):
    mc_id = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter MCID',
            'class': 'form-control'
        })
    )

    class Meta:
        model = DpcStructMcsProperty
        fields = ["mc_id"]


class DpcStructCathFilter(django_filters.FilterSet):
    """Filter CATH annotations by metacluster ID or CATH fold"""
    mc_id = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter MCID',
            'class': 'form-control'
        }),
        field_name='mc__mc_id'
    )

    cath_query = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter CATH ID',
            'class': 'form-control'
        })
    )

    class Meta:
        model = DpcStructCath
        fields = ["mc_id", "cath_query"]


class DpcStructScopFilter(django_filters.FilterSet):
    """Filter SCOP annotations by metacluster ID or SCOP fold"""
    mc_id = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter MCID',
            'class': 'form-control'
        }),
        field_name='mc__mc_id'
    )

    scop_query = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter SCOP ID',
            'class': 'form-control'
        })
    )

    class Meta:
        model = DpcStructScop
        fields = ["mc_id", "scop_query"]
