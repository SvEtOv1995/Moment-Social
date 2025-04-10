from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
import random

from django.contrib.auth.models import User
from .models import Post, Profile, ProfileRating
from .forms import PostForm, ProfileForm, UserRegistrationForm

# --- Главная страница (анонимная публикация) ---
def home(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.content = post.content or ''
            post.author = request.user if request.user.is_authenticated else None
            post.save()
            return redirect('home')
    else:
        form = PostForm()

    cutoff = timezone.now() - timedelta(hours=1)
    posts = Post.objects.filter(created_at__gte=cutoff).order_by('-created_at')

    return render(request, 'home.html', {'form': form, 'posts': posts})


# --- Лента для авторизованных пользователей ---
@login_required
def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'feed.html', {'form': form, 'posts': posts})


# --- Установка имени (если используешь сессии и анонимность) ---
def set_name(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        request.session['user_name'] = name if name else 'Аноним'
        return redirect('home')
    return render(request, 'set_name.html')


# --- Страница редактирования профиля ---
@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})


# --- Просмотр своего профиля ---
@login_required
def view_profile(request):
    return render(request, 'view_profile.html', {'profile': request.user.profile})


# --- Просмотр профиля по username ---
def view_profile_by_username(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'view_profile.html', {'profile': profile, 'user': user})


# --- Регистрация ---
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


# --- Случайный юзер для "встречи" ---
def find_random_user(current_user):
    users = User.objects.exclude(id=current_user.id).exclude(profile__anonymous=True)
    if users.exists():
        return random.choice(users)
    return None


# --- Оценка профиля ---
@require_POST
@login_required
def rate_profile(request, profile_id):
    profile = Profile.objects.get(pk=profile_id)
    value = int(request.POST.get('value'))

    rating_obj, created = ProfileRating.objects.update_or_create(
        rater=request.user,
        target=profile,
        defaults={'value': value}
    )

    all_ratings = ProfileRating.objects.filter(target=profile)
    avg = sum(r.value for r in all_ratings) / all_ratings.count()
    profile.rating = avg
    profile.total_votes = all_ratings.count()
    profile.save()

    return redirect('view_profile_by_username', username=profile.user.username)

def profile_view(request, username):
    # Получаем пользователя по имени (username)
    user = get_object_or_404(User, username=username)
    
    # Возвращаем шаблон с данными пользователя
    return render(request, 'edit_profile.html', {'user': user})