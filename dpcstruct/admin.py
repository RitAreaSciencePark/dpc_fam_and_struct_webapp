from django.contrib import admin
from .models import DpcStructMcsProperty


@admin.register(DpcStructMcsProperty)
class DpcStructMcsPropertyAdmin(admin.ModelAdmin):
	list_display = (
		'mc_id',
		'mc_size',
		'plddt',
		'tmscore',
		'pident',
		'pfam_score',
        'pfam_labels',
	)
	search_fields = ('mc_id', 'pfam_labels')