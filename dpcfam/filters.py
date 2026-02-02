# dpcfam/filters.py
import django_filters
from django import forms
from .models import MCSProperty


class MCSPropertyFilter(django_filters.FilterSet):
    mcid = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={
            'placeholder': 'MC1',
            'class': 'form-control'
        })
    )

    class Meta:
        model = MCSProperty
        fields = ["mcid"]
