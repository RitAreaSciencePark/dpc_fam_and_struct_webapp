from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from dpcfam.models import MCSProperty, UniRef50Protein, UniRef50Pfam, MCSSequence
from dpcstruct.models import DpcStructMcsProperty

def search(request):
    database = request.GET.get('database')
    query_id = request.GET.get('query_id')

    if not database or not query_id:
        return redirect('home')
    
    query_id = query_id.strip()

    if database == 'DPCFam':
        # Check if ID exists
        if MCSProperty.objects.filter(mcid=query_id).exists():
            # Redirect to the detail view directly
            return redirect(f'/dpcfam/mcs/{query_id}/')
        else:
            # ID doesn't exist
            messages.error(request, 'The id doesn\'t exist, please try another')
            return render(request, 'index.html')  
    elif database == 'PFam':
        query_id = query_id.upper()
        # Exact match within dash-separated string using regex
        matches = MCSProperty.objects.filter(
            Q(pfam_da__regex=rf'(^|-){query_id}(-|$)')
        ).exclude(pfam_da='UNKNOWN').exists()

        if query_id != 'UNKNOWN' and matches:
            return redirect('pfam_detail', pfam_id=query_id)
        else:
            messages.error(request, f'Pfam ID "{query_id}" doesn\'t exist (exact match required), please try another')
            return render(request, 'index.html')

    elif database == 'UniProtKB':
        # Exact match only for uniref50_id
        protein = UniRef50Protein.objects.filter(uniref50_id=query_id).first()

        if protein:
            return redirect('protein_detail', uniref50_id=protein.uniref50_id)
        else:
            messages.error(request, f'UniRef50 ID "{query_id}" doesn\'t exist, please try another')
            return render(request, 'index.html')
            
    # Placeholder for other databases
    return render(request, 'index.html', {'error': f'Search for {database} not implemented yet.'})


def pfam_detail(request, pfam_id):
    """Display metaclusters containing a specific Pfam domain (exact match)"""
    pfam_id = pfam_id.strip().upper()
    
    # Use regex for exact match in dash-separated list
    # Naturally sort results by the numeric part of MCID
    metaclusters = MCSProperty.objects.filter(
        pfam_da__regex=rf'(^|-){pfam_id}(-|$)'
    ).exclude(pfam_da='UNKNOWN').extra(
        select={'mc_num': "CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER)"}
    ).order_by('mc_num')
    
    if not metaclusters.exists():
        messages.error(request, f'Pfam ID "{pfam_id}" not found')
        return redirect('home')
    
    context = {
        'pfam_id': pfam_id,
        'metaclusters': metaclusters,
        'total_count': metaclusters.count()
    }
    
    return render(request, 'pfam_detail.html', context)


def protein_detail(request, uniref50_id):
    """Display domain architecture for a specific UniRef50 protein"""
    protein = get_object_or_404(UniRef50Protein, uniref50_id=uniref50_id)
    # Using MCSSequence instead of MCSProperty to get the related sequences for this protein
    dpcfam_qs = MCSSequence.objects.filter(protein=protein)
    pfam_qs = UniRef50Pfam.objects.filter(uniref50=protein)
    
    # Helper to parse ranges for the diagram
    def parse_domain(obj, id_attr, range_attr):
        try:
            r_str = getattr(obj, range_attr)
            start, end = map(int, r_str.split('-'))
            label = getattr(obj, id_attr)
            # If it's a model instance, the attribute might be a relation or MCSProperty
            if hasattr(label, 'mcid'): label = label.mcid
            return {
                'id': label,
                'start': start,
                'end': end,
                'width': ((end - start) / protein.length) * 100,
                'left': (start / protein.length) * 100
            }
        except:
            return None

    dpcfam_domains = []
    for d in dpcfam_qs:
        parsed = parse_domain(d, 'mc', 'seq_range')
        if parsed: dpcfam_domains.append(parsed)

    pfam_domains = []
    for p in pfam_qs:
        parsed = parse_domain(p, 'pfam_ids', 'pfam_ranges')
        if parsed: pfam_domains.append(parsed)
    
    # Sort domains by width descending so larger domains are rendered first and smaller ones on top
    dpcfam_domains.sort(key=lambda x: x['width'], reverse=True)
    pfam_domains.sort(key=lambda x: x['width'], reverse=True)
    
    context = {
        'protein': protein,
        'dpcfam_domains': dpcfam_domains,
        'dpcfam_qs': dpcfam_qs,
        'pfam_domains': pfam_domains,
        'pfam_qs': pfam_qs,
    }
    return render(request, 'protein_detail.html', context)
