from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('subscriptions/', views.subscriptions_feed, name='subscriptions_feed'),
    path('upload/', views.upload, name='upload'),
    path('watch_later/', views.watch_later, name='watch_later'),
    path('playlist/create/', views.create_playlist, name='create_playlist'),
    path('playlist/<int:pk>/', views.playlist_detail, name='playlist_detail'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
    path('video/<int:pk>/like/', views.toggle_like, name='video_like'),
    path('video/<int:pk>/like_ajax/', views.like_ajax, name='video_like_ajax'),
    path('signup/', views.signup, name='signup'),
    path('video/<int:pk>/comment_ajax/', views.comment_ajax, name='video_comment_ajax'),
    path('video/<int:pk>/comment_flag_ajax/', views.flag_comment_ajax, name='video_comment_flag_ajax'),
    path('search/', views.search, name='search'),
]
