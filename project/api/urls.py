from django.urls import path

from interactivemap import settings

from . import views

urlpatterns = [
    path('nations/', views.nation_list),
    path('nations/<int:pk>/', views.nation_detail),
]
