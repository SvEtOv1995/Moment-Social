from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
import random

from django.contrib.auth.models import User
from .models import Post, Profile, ProfileRating
from .forms import PostForm, ProfileForm, UserRegistrationForm

def home(request):
    if request.user.is_authenticated:
        return redirect('feed')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.content = post.content or ''
            post.author = None
            post.save()
            return redirect('home')
    else:
        form = PostForm()

    cutoff = timezone.now() - timedelta(hours=1)
    posts = Post.objects.filter(created_at__gte=cutoff, author=None).order_by('-created_at')
    return render(request, 'home.html', {'form': form, 'posts': posts})

@login_required
def feed(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    
    posts = Post.objects.filter(author__isnull=False).order_by('-created_at')
    return render(request, 'feed.html', {'form': form, 'posts': posts})

@login_required
def view_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'view_profile.html', {'profile': profile})

def view_profile_by_username(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'view_profile.html', {
        'profile': profile,
        'viewed_user': user,
        'is_owner': request.user == user
    })

@login_required
def edit_profile(request):
    # Получаем или создаем профиль для текущего пользователя
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('view_profile')  # Перенаправляем на свой профиль
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'edit_profile.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

@login_required
def messages_view(request):
    return render(request, 'messages.html')

@require_POST
@login_required
def rate_profile(request, profile_id):
    profile = get_object_or_404(Profile, pk=profile_id)
    if profile.user == request.user:
        return redirect('view_profile')
    
    value = int(request.POST.get('value', 0))
    ProfileRating.objects.update_or_create(
        rater=request.user,
        target=profile,
        defaults={'value': value}
    )
    
    # Обновляем средний рейтинг
    ratings = ProfileRating.objects.filter(target=profile)
    profile.rating = sum(r.value for r in ratings) / ratings.count() if ratings.exists() else 0
    profile.total_votes = ratings.count()
    profile.save()
    
    return redirect('view_profile_by_username', username=profile.user.username)


def set_name(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        request.session['user_name'] = name if name else 'Аноним'
        return redirect('home')
    return render(request, 'set_name.html')