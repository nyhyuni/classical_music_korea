from django.urls import path
from . import views

app_name = 'catalog'
urlpatterns = [
    path('', views.index, name='index'),
    path('composer/<int:composer_id>/', views.composer_detail, name='composer_detail'),
    path('search/', views.search, name='search'),
]
