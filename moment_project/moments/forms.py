from django import forms
from .models import Post
from .models import Profile
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'video', 'hashtags']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
            'hashtags': forms.TextInput(attrs={'placeholder': '#fun #life'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['display_name', 'anonymous', 'age', 'interests', 'photo']

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
