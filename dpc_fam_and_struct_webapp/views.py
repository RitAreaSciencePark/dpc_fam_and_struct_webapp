from django.shortcuts import render, redirect
from django.contrib import messages
from dpcfam.models import MCSProperty

def search(request):
    database = request.GET.get('database')
    query_id = request.GET.get('query_id')

    if not database or not query_id:
        return redirect('home')

    if database == 'DPCFam':
        query_id = query_id.strip() # Remove any leading/trailing whitespace
        # Check if ID exists
        if MCSProperty.objects.filter(mcid=query_id).exists():
            # Redirect to the detail view directly
            return redirect(f'/dpcfam/mcs/{query_id}/')
        else:
            # ID doesn't exist
            messages.error(request, 'The id doesn\'t exist, please try another')
            return render(request, 'index.html')
    
    elif database == 'PFam':
        query_id = query_id.strip().upper()
        # Check if Pfam ID exists in pfam_da column (exclude UNKNOWN)
        if query_id != 'UNKNOWN' and MCSProperty.objects.filter(pfam_da__icontains=query_id).exclude(pfam_da='UNKNOWN').exists():
            # Redirect to Pfam detail page
            return redirect('pfam_detail', pfam_id=query_id)
        else:
            messages.error(request, f'Pfam ID "{query_id}" doesn\'t exist, please try another')
            return render(request, 'index.html')
            
    # Placeholder for other databases
    return render(request, 'index.html', {'error': f'Search for {database} not implemented yet.'})


def pfam_detail(request, pfam_id):
    """Display metaclusters containing a specific Pfam domain"""
    pfam_id = pfam_id.strip().upper()
    
    # Get all metaclusters containing this Pfam ID, sorted by avg_ov_percent descending (exclude UNKNOWN)
    metaclusters = MCSProperty.objects.filter(
        pfam_da__icontains=pfam_id
    ).exclude(pfam_da='UNKNOWN').order_by('-avg_ov_percent')
    
    if not metaclusters.exists():
        messages.error(request, f'Pfam ID "{pfam_id}" not found')
        return redirect('home')
    
    context = {
        'pfam_id': pfam_id,
        'metaclusters': metaclusters,
        'total_count': metaclusters.count()
    }
    
    return render(request, 'pfam_detail.html', context)
