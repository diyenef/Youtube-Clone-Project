from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>/', views.channel_profile, name='channel_profile'),
    path('<str:username>/subscribe/', views.toggle_subscribe, name='toggle_subscribe'),
]
