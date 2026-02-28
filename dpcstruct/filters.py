import django_filters
from django import forms
from .models import DpcStructMcsProperty

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
