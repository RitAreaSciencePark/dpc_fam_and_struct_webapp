from django.contrib import admin
from .models import DpcfamMcsProperty


@admin.register(DpcfamMcsProperty)
class DpcfamMcsPropertyAdmin(admin.ModelAdmin):
	list_display = (
		'mcid',
		'size_uniref50',
		'pfam_da',
		'overlap_label',
	)
	search_fields = ('mcid', 'pfam_da')
