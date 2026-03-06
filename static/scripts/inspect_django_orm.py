from django.db import connection,reset_queries
from dpcstruct.models import DpcStructMcsProperty
reset_queries()
mc = DpcStructMcsProperty.objects.get(mc_id='MC7')
seqs = list(mc.sequences.all())
for q in connection.queries:
    print(f"Time: {q['time']}s")
    print(f"SQL: {q['sql']}")
    print()