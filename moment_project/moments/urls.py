from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('set-name/', views.set_name, name='set_name'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/', views.view_profile, name='view_profile'),
    path('', views.feed, name='feed'),
    path('register/', views.register, name='register'),  # Убедись, что есть эта строка
    path('home/', views.home, name='home'),

]
