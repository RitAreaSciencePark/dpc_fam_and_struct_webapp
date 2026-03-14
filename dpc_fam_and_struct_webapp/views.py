from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from dpcfam.models import DpcfamMcsProperty, DpcfamMcsSequence
from dpc.models import DpcUniprotProtein, DpcPfamDomain, DpcUniref50Pfam
from dpcstruct.models import DpcStructMcsProperty, DpcStructCath, DpcStructScop


def search(request):
    database = request.GET.get('database')
    query_id = request.GET.get('query_id')

    if not database or not query_id:
        return redirect('home')
    
    query_id = query_id.strip()

    if database == 'DPCFam':
        # Check if ID exists
        if DpcfamMcsProperty.objects.filter(mcid=query_id).exists():
            # Redirect to the detail view directly
            return redirect(f'/dpcfam/mcs/{query_id}/')
        else:
            # ID doesn't exist
            messages.error(request, 'The id doesn\'t exist, please try another')
            return render(request, 'index.html')
    
    elif database == 'DPCStruct':
        if DpcStructMcsProperty.objects.filter(mc_id=query_id).exists():
            return redirect(f'/dpcstruct/mcs/{query_id}/')
        else:
            messages.error(request, 'The id doesn\'t exist, please try another')
            return render(request, 'index.html')
    
    elif database == 'PFam':
        query_id = query_id.upper()
        # Check if ID exists
        if query_id != 'UNKNOWN' and DpcPfamDomain.objects.filter(pfam_id=query_id).exists():
            return redirect(f'/pfam/{query_id}/')
        else:
            messages.error(request, f'Pfam ID "{query_id}" doesn\'t exist (exact match required), please try another')
            return render(request, 'index.html')

    elif database == 'UniProt':
        query_id = query_id.upper()
        # Check if ID exists
        if DpcUniprotProtein.objects.filter(protein_id=query_id).exists():
            return redirect(f'/protein/{query_id}/')
        else:
            messages.error(request, f'UniProt ID "{query_id}" doesn\'t exist, please try another')
            return render(request, 'index.html')
            
    # Placeholder for other databases
    return render(request, 'index.html', {'error': f'Search for {database} not implemented yet.'})


def pfam_detail(request, pfam_id):
    """
    Display metaclusters containing a specific Pfam domain (exact match)
    Shows results from both DPCFam and DPCStruct
    """
    pfam_id = pfam_id.strip().upper()
    
    # Get DPCFam metaclusters with this Pfam domain
    dpcfam_metaclusters = DpcfamMcsProperty.objects.filter(
        pfam_da__regex=rf'(^|-){pfam_id}(-|$)'
    ).exclude(pfam_da='UNKNOWN').extra(
        select={'mc_num': "CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER)"}
    ).order_by('mc_num')
    
    # Get DPCStruct metaclusters with this Pfam domain
    dpcstruct_metaclusters = DpcStructMcsProperty.objects.filter(
        pfam_da__regex=rf'(^|-){pfam_id}(-|$)'
    ).exclude(pfam_da='UNKNOWN').extra(
        select={'mc_num': "CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER)"}
    ).order_by('mc_num')
    
    if not dpcfam_metaclusters.exists() and not dpcstruct_metaclusters.exists():
        messages.error(request, f'Pfam ID "{pfam_id}" not found')
        return redirect('home')
    
    # Handle pfam_score to display in template
    for mc in dpcstruct_metaclusters:
        if mc.pfam_score is not None:
            mc.pfam_score_percent = min(100, max(0, int(mc.pfam_score)))
        else:
            mc.pfam_score_percent = 0
    
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
    Display domain architecture for a specific UniProt protein
    Shows:
    - DPCFam metaclusters containing this protein
    - DPCStruct clusters matching this protein
    - Pfam domains annotated for this protein
    """
    protein = get_object_or_404(DpcUniprotProtein, protein_id=protein_id)
    
    # Get DPCFam sequences for this protein
    dpcfam_qs = DpcfamMcsSequence.objects.filter(protein=protein)
    
    # Get DPCStruct sequences for this protein
    dpcstruct_qs = None
    try:
        from dpcstruct.models import DpcStructMcsSequence
        dpcstruct_qs = DpcStructMcsSequence.objects.filter(protein=protein)
    except ImportError:
        pass
    
    # Get Pfam domains for this protein
    pfam_qs = DpcUniref50Pfam.objects.filter(uniref50=protein)
    
    # Helper to parse ranges for the diagram
    def parse_domain(obj, id_attr, range_attr):
        try:
            r_str = getattr(obj, range_attr)
            start, end = map(int, r_str.split('-'))
            label = getattr(obj, id_attr)
            # If it's a model instance, the attribute might be a relation or property
            if hasattr(label, 'mcid'):
                label = label.mcid
            elif hasattr(label, 'mc_id'):
                label = label.mc_id
            elif hasattr(label, 'pfam_id'):
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
        parsed = parse_domain(p, 'pfam_id', 'pfam_ranges')
        if parsed:
            pfam_domains.append(parsed)
    
    # Sort domains by width descending so larger domains are rendered first and smaller ones on top
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
