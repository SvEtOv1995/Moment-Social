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

from django.db.models import Q
from .models import Chat, Message

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
    
    # Получаем все посты, как с авторами, так и без, и сортируем по дате создания
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'feed.html', {'form': form, 'posts': posts})

@login_required
def view_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'view_profile.html', {'profile': profile})

@login_required
def view_profile_by_username(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'view_profile.html', {
        'profile': profile,
        'viewed_user': user,  # Make sure this is included
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

@login_required
def messages_view(request):
    chats = Chat.objects.filter(participants=request.user).order_by('-updated_at')
    return render(request, 'messages.html', {'chats': chats})

@login_required
def chat_view(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    
    # Помечаем сообщения как прочитанные
    Message.objects.filter(chat=chat).exclude(sender=request.user).update(is_read=True)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                chat=chat,
                sender=request.user,
                content=content
            )
            chat.save()  # Обновляем updated_at
            return redirect('chat_view', chat_id=chat.id)
    
    messages = chat.messages.all().order_by('timestamp')
    return render(request, 'chat.html', {
        'chat': chat,
        'messages': messages,
        'other_user': chat.participants.exclude(id=request.user.id).first()
    })

@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return redirect('messages_view')
    
    # Ищем существующий чат или создаем новый
    chat = Chat.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(request.user, other_user)
    
    return redirect('chat_view', chat_id=chat.id)