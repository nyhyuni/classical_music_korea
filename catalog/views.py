from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Composer, Work

def index(request):
    composers = Composer.objects.all().order_by('name')
    popular_composers = Composer.objects.filter(popular=True).order_by('name')
    return render(request, 'catalog/index.html', {
        'composers': composers,
        'popular_composers': popular_composers
    })

def composer_detail(request, composer_id):
    composer = get_object_or_404(Composer, id=composer_id)
    works = Work.objects.filter(composer=composer).order_by('title')
    popular_works = works.filter(popular=True)
    return render(request, 'catalog/composer_detail.html', {
        'composer': composer,
        'works': works,
        'popular_works': popular_works
    })

def search(request):
    query = request.GET.get('q', '')
    results = {'composers': [], 'works': []}
    
    if query:
        # Search composers
        composers = Composer.objects.filter(
            Q(name__icontains=query) | 
            Q(name_ko__icontains=query) |
            Q(lastname_ko__icontains=query) |
            Q(complete_name__icontains=query)
        )
        
        # Search works
        works = Work.objects.filter(
            Q(title__icontains=query) |
            Q(title_ko__icontains=query) |
            Q(subtitle__icontains=query) |
            Q(subtitle_ko__icontains=query)
        ).select_related('composer')
        
        results = {'composers': composers, 'works': works}
    
    return render(request, 'catalog/search_results.html', {
        'query': query,
        'results': results
    })