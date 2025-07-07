from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.decorators.cache import cache_page
from django.db.models import Q
from django.shortcuts import render, redirect
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode
from django.http import JsonResponse, Http404, HttpResponse
from django.conf import settings
import boto3
from botocore.exceptions import ClientError

from .models import Concert, Area
from catalog.models import Composer
from django.core.paginator import EmptyPage, PageNotAnInteger

class ConcertList(ListView):
    model = Concert
    context_object_name = "concerts"
    template_name = "concert/concert_list.html"

    def get_context_data(self, **kwargs):
        import random
        context = super(ConcertList, self).get_context_data(**kwargs)
        context['areas'] = Area.objects.all()
        context['concerts'] = Concert.objects.filter(datetime__gt=datetime.now(timezone.utc)).order_by('?')[:12]
        context['composers'] = Composer.objects.all().order_by('name')
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
    paginate_by = 12  # Show 12 concerts per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        if 'page' in params:
            params.pop('page')
        context['querystring'] = '&' + urlencode(params) if params else ''
        return context

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the queryset, but if the page is invalid, return the first page.
        """
        paginator = self.get_paginator(queryset, page_size, allow_empty_first_page=True)
        page = self.request.GET.get('page')
        try:
            page_number = paginator.validate_number(page)
        except (PageNotAnInteger, TypeError):
            page_number = 1
        except EmptyPage:
            page_number = 1
        page_obj = paginator.page(page_number)
        return (paginator, page_obj, page_obj.object_list, page_obj.has_other_pages())

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
            filter_query.add(Q(programs__composer__icontains=composer), Q.AND)
        program = self.request.GET.get("program")
        if program:
            filter_query.add(Q(programs__work__icontains=program), Q.AND)
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
            days_to_add = timedelta(days=1)
            to_date = to_date + days_to_add
            filter_query.add(Q(datetime__lt=to_date), Q.AND)
        return Concert.objects.filter(filter_query).order_by('datetime').distinct()

def get_presigned_url(request):
    key = request.GET.get('key')
    if not key:
        return JsonResponse({'error': 'Missing key'}, status=400)
    s3 = boto3.client('s3')
    try:
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': key},
            ExpiresIn=3600  # 1 hour
        )
        return JsonResponse({'url': url})
    except Exception:
        raise Http404("File not found")

def display_poster_proxy(request, filename):
    s3 = boto3.client('s3')
    key = f'display_poster/{filename}'
    try:
        s3_response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        content_type = s3_response.get('ContentType', 'image/jpeg')
        return HttpResponse(s3_response['Body'].read(), content_type=content_type)
    except ClientError:
        raise Http404("Image not found")

def full_poster_proxy(request, filename):
    s3 = boto3.client('s3')
    key = f'full_poster/{filename}'
    try:
        s3_response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        content_type = s3_response.get('ContentType', 'image/jpeg')
        return HttpResponse(s3_response['Body'].read(), content_type=content_type)
    except ClientError:
        raise Http404("Image not found")