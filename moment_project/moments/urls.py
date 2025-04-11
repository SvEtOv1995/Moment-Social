from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('feed/', views.feed, name='feed'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # Важно: без username
    path('profile/', views.view_profile, name='view_profile'),  # Для своего профиля
    path('profile/<str:username>/', views.view_profile_by_username, name='view_profile_by_username'),
    path('register/', views.register, name='register'),
    path('create-post/', views.create_post, name='create_post'),
    path('messages/', views.messages_view, name='messages'),
    path('rate/<int:profile_id>/', views.rate_profile, name='rate_profile'),
    path('set-name/', views.set_name, name='set_name'),
]