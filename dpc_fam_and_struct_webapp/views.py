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
            
    # Placeholder for other databases
    return render(request, 'index.html', {'error': f'Search for {database} not implemented yet.'})
