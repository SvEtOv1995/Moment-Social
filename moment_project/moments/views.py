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



