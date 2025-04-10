from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('feed/', views.feed, name='feed'),
    path('set-name/', views.set_name, name='set_name'),
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/<str:username>/', views.view_profile_by_username, name='view_profile_by_username'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # Используйте эту строку
    path('register/', views.register, name='register'),
    path('rate/<int:profile_id>/', views.rate_profile, name='rate_profile'),
]
