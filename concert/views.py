from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.decorators.cache import cache_page
from django.db.models import Q
from django.shortcuts import render, redirect
from datetime import datetime, timezone

from .models import Concert, Area

@method_decorator(cache_page(60 * 5), name="dispatch")
class ConcertList(ListView):
    model = Concert
    context_object_name = "concerts"
    template_name = "concert/concerts.html"

    def get_context_data(self, **kwargs):
        context = super(ConcertList, self).get_context_data(**kwargs)
        context['areas'] = Area.objects.all()
        context['concerts'] = Concert.objects.filter(datetime__gt=datetime.now(timezone.utc))
        return context

class ConcertDetail(DetailView):
    model = Concert
    template_name = "concert/concert_detail.html"
    queryset = Concert.objects.all()
    context_object_name = 'concert_detail'
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

class ConcertSearchResultList(ListView):
    model = Concert
    context_object_name = "search"
    template_name = "concert/concert_search_result.html"

    def get_queryset(self):
        filter_query = Q()
        concert = self.request.GET.get("concert")
        if concert:
            filter_query.add(Q(prfnm__icontains=concert), Q.AND)
        performer = self.request.GET.get("performer")
        if performer:
            filter_query.add(Q(prfcast__icontains=performer), Q.AND)
        composer = self.request.GET.get("composer")
        if composer:
            filter_query.add(Q(compositions__composer__icontains=composer), Q.AND)
        composition = self.request.GET.get("composition")
        if composition:
            filter_query.add(Q(compositions__work__icontains=composition), Q.AND)
        include_past_concerts = self.request.GET.get("include_past_concerts")
        if not include_past_concerts:
            current_time = datetime.now(timezone.utc)
            filter_query.add(Q(datetime__gt=current_time), Q.AND)
        area = self.request.GET.get("area")
        if area != '0':
            filter_query.add(Q(area_id=area), Q.AND)
        from_date = self.request.GET.get("from_date")

        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
            filter_query.add(Q(datetime__gt=from_date), Q.AND)
        to_date = self.request.GET.get("to_date")
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
            filter_query.add(Q(datetime__lt=to_date), Q.AND)
        return Concert.objects.filter(filter_query).order_by('datetime').distinct()