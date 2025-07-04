from django.urls import path

from .views import ConcertList, ConcertSearchResultList, ConcertDetail

urlpatterns = [
    path("", ConcertList.as_view(), name="all_concerts"),
    path("search/", ConcertSearchResultList.as_view(), name="concert_search_result"),
    path("<str:pk>/", ConcertDetail.as_view(), name='concert_detail'),
]
