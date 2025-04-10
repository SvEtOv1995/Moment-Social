from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForm
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import Q
import random
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm  # Убедись, что эта форма тоже есть
from .models import Profile
from django.views.decorators.http import require_POST
from .models import ProfileRating
from .forms import UserRegistrationForm
from django.shortcuts import get_object_or_404
from .models import Profile, User

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
    return render(request, 'moments/edit_profile.html', {'form': form})

@login_required
def view_profile(request):
    return render(request, 'moments/view_profile.html', {'profile': request.user.profile})


def home(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        form.instance.name = request.session.get('user_name', 'Аноним')
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PostForm()

    cutoff = timezone.now() - timedelta(hours=1)
    posts = Post.objects.filter(created_at__gte=cutoff).order_by('-created_at')


    return render(request, 'home.html', {'form': form, 'posts': posts})

def set_name(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        request.session['user_name'] = name if name else 'Аноним'
        return redirect('home')

    return render(request, 'set_name.html')

def find_random_user(current_user):
    users = User.objects.exclude(id=current_user.id)
    users = users.exclude(profile__anonymous=True)
    if users.exists():
        return random.choice(users)
    return None

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

@login_required
def view_profile(request):
    return render(request, 'view_profile.html', {'profile': request.user.profile})

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

    # Обновим агрегированный рейтинг:
    all_ratings = ProfileRating.objects.filter(target=profile)
    avg = sum(r.value for r in all_ratings) / all_ratings.count()
    profile.rating = avg
    profile.total_votes = all_ratings.count()
    profile.save()

    return redirect('view_profile')

def feed(request):
    return render(request, 'feed.html')  # создашь этот шаблон позже

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Перенаправляем на страницу логина после регистрации
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'profile.html', {'profile': profile, 'user': user})


