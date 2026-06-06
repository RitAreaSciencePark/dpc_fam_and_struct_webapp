from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from dpcfam.models import DpcfamMcsProperty, DpcfamMcsSequence
from dpc.models import DpcUniprotProtein, DpcPfamDomain, DpcUniref50Pfam
from dpcstruct.models import DpcStructMcsProperty, DpcStructMcsSequence
from django.db.models.expressions import RawSQL
from django.db.models import IntegerField


def search(request):
    database = request.GET.get('database')
    query_id = request.GET.get('query_id')

    if not database or not query_id:
        return redirect('home')

    query_id = query_id.strip()

    if database == 'DPCfam':
        if DpcfamMcsProperty.objects.filter(mcid=query_id).exists():
            return redirect(f'/dpcfam/mcs/{query_id}/')
        else:
            messages.error(request, 'The MCID doesn\'t exist, please try another')
            return render(request, 'index.html')

    elif database == 'DPCstruct':
        if DpcStructMcsProperty.objects.filter(mc_id=query_id).exists():
            return redirect(f'/dpcstruct/mcs/{query_id}/')
        else:
            messages.error(request, 'The MCID doesn\'t exist, please try another')
            return render(request, 'index.html')

    elif database == 'Pfam':
        query_id = query_id.upper()
        if query_id != 'UNKNOWN' and DpcPfamDomain.objects.filter(pfam_id=query_id).exists():
            return redirect(f'/pfam/{query_id}/')
        else:
            messages.error(request, f'Pfam ID "{query_id}" doesn\'t exist (exact match required), please try another')
            return render(request, 'index.html')

    elif database == 'UniProt':
        query_id = query_id.upper()
        if DpcUniprotProtein.objects.filter(protein_id=query_id).exists():
            return redirect(f'/protein/{query_id}/')
        else:
            messages.error(request, f'UniProt ID "{query_id}" doesn\'t exist, please try another')
            return render(request, 'index.html')

    return render(request, 'index.html', {'error': f'Search for {database} not implemented yet.'})


def pfam_detail(request, pfam_id):
    """
    Display metaclusters containing a specific Pfam domain (exact match).
    Uses a PostgreSQL regex on pfam_da to find only exact token matches
    (e.g. PF00001 must appear as a full token, not as a substring of PF000010).
    The GIN trigram index on pfam_da accelerates the ILIKE pre-filter before the regex refines the result set.
    """
    pfam_id = pfam_id.strip().upper()

    if pfam_id != 'UNKNOWN' and not DpcPfamDomain.objects.filter(pfam_id=pfam_id).exists():
        messages.error(request, f'Pfam ID "{pfam_id}" not found.')
        return redirect('home')

    # Regex enforces exact token boundary matching: PF00001 must be at the
    # start/end of pfam_da or surrounded by dashes — never a substring.
    dpcfam_metaclusters = DpcfamMcsProperty.objects.filter(
        pfam_da__regex=rf'(^|-){pfam_id}(-|$)'
    ).exclude(pfam_da='UNKNOWN').annotate(
        mc_num=RawSQL(
            "CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER)",
            [],
            output_field=IntegerField()
        )
    ).order_by('mc_num')

    dpcstruct_metaclusters = DpcStructMcsProperty.objects.filter(
        pfam_da__regex=rf'(^|-){pfam_id}(-|$)'
    ).exclude(pfam_da='UNKNOWN').annotate(
        mc_num=RawSQL(
            "CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER)",
            [],
            output_field=IntegerField()
        )
    ).order_by('mc_num')

    if not dpcfam_metaclusters.exists() and not dpcstruct_metaclusters.exists():
        messages.error(request, f'Pfam ID "{pfam_id}" exists in our reference database but is not covered by any DPCfam or DPCstruct metacluster.')
        return redirect('home')

    # Build pfam_score_percent and pfam_links for DPCstruct rows
    for mc in dpcstruct_metaclusters:
        if mc.pfam_score is not None:
            mc.pfam_score_percent = min(100, max(0, int(mc.pfam_score)))
        else:
            mc.pfam_score_percent = 0

        if mc.pfam_da and mc.pfam_da != 'UNKNOWN':
            mc.pfam_links = []
            for pfam in mc.pfam_da.split('-'):
                if pfam.strip():
                    mc.pfam_links.append({
                        'id': pfam.strip(),
                        'url': f'/search/?database=Pfam&query_id={pfam.strip()}'
                    })
        else:
            mc.pfam_links = []

    context = {
        'pfam_id': pfam_id,
        'dpcfam_metaclusters': dpcfam_metaclusters,
        'dpcstruct_metaclusters': dpcstruct_metaclusters,
        'dpcfam_count': dpcfam_metaclusters.count(),
        'dpcstruct_count': dpcstruct_metaclusters.count(),
        'total_count': dpcfam_metaclusters.count() + dpcstruct_metaclusters.count()
    }

    return render(request, 'pfam_detail.html', context)


def protein_detail(request, protein_id):
    """
    Display domain architecture for a specific UniProt protein.
    Shows DPCfam metaclusters, DPCstruct metaclusters, and Pfam domains all plotted on a single graphical scale.
    """
    protein = get_object_or_404(DpcUniprotProtein, protein_id=protein_id)

    # Get DPCfam sequences for this protein
    dpcfam_qs = DpcfamMcsSequence.objects.filter(protein=protein)

    # Get DPCstruct sequences for this protein
    dpcstruct_qs = None
    try:
        dpcstruct_qs = DpcStructMcsSequence.objects.filter(protein=protein)
    except ImportError:
        pass

    # Get Pfam domains for this protein
    pfam_qs = DpcUniref50Pfam.objects.filter(uniref50=protein)

    def parse_domain(obj, id_attr, range_attr):
        try:
            r_str = getattr(obj, range_attr)
            start, end = map(int, r_str.split('-'))
            label = getattr(obj, id_attr)
            # Resolve FK objects to their string identifier
            if hasattr(label, 'mcid'):
                label = label.mcid
            elif hasattr(label, 'mc_id'):
                label = label.mc_id
            elif hasattr(label, 'pfam_id'):
                # DpcPfamDomain instance — pfam_id is the primary key string
                label = label.pfam_id
            return {
                'id': label,
                'start': start,
                'end': end,
                'width': ((end - start) / protein.protein_length) * 100 if protein.protein_length else 0,
                'left': (start / protein.protein_length) * 100 if protein.protein_length else 0
            }
        except Exception:
            return None

    dpcfam_domains = []
    for d in dpcfam_qs:
        parsed = parse_domain(d, 'mc', 'seq_range')
        if parsed:
            dpcfam_domains.append(parsed)

    dpcstruct_domains = []
    if dpcstruct_qs:
        for d in dpcstruct_qs:
            parsed = parse_domain(d, 'mc', 'prot_range')
            if parsed:
                dpcstruct_domains.append(parsed)

    pfam_domains = []
    for p in pfam_qs:
        # p.pfam_id is a DpcPfamDomain FK — parse_domain resolves it via hasattr
        parsed = parse_domain(p, 'pfam_id', 'pfam_ranges')
        if parsed:
            pfam_domains.append(parsed)

    # Sort by descending width so larger background domains render first
    dpcfam_domains.sort(key=lambda x: x['width'], reverse=True)
    dpcstruct_domains.sort(key=lambda x: x['width'], reverse=True)
    pfam_domains.sort(key=lambda x: x['width'], reverse=True)

    context = {
        'protein': protein,
        'dpcfam_domains': dpcfam_domains,
        'dpcfam_qs': dpcfam_qs,
        'dpcstruct_domains': dpcstruct_domains,
        'dpcstruct_qs': dpcstruct_qs if dpcstruct_qs else [],
        'pfam_domains': pfam_domains,
        'pfam_qs': pfam_qs,
    }
    return render(request, 'protein_detail.html', context)
