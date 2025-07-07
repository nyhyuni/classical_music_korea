from django.urls import path

from .views import ConcertList, ConcertSearchResultList, ConcertDetail, get_presigned_url, display_poster_proxy, full_poster_proxy, robots_txt

urlpatterns = [
    path("", ConcertList.as_view(), name="all_concerts"),
    path("search/", ConcertSearchResultList.as_view(), name="concert_search_result"),
    path("<str:pk>/", ConcertDetail.as_view(), name='concert_detail'),
    path('api/get_presigned_url/', get_presigned_url, name='get_presigned_url'),
    path('media/display_poster/<str:filename>/', display_poster_proxy, name='display_poster_proxy'),
    path('media/full_poster/<str:filename>/', full_poster_proxy, name='full_poster_proxy'),
    path('robots.txt', robots_txt, name='robots_txt'),
]
