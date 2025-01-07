from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Post, Comment,Message

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Enter your Email'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets={
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Username'}),
        }
    def __init__ (self,*args,**kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'})

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_pic', 'location']
        widgets = {
            'profile_pic': forms.FileInput(attrs={'accept': 'image/*'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic','bio', 'location']
        widgets = {
            'profile_pic': forms.FileInput(attrs={'accept': 'image/*'}),
        }
        
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'image', 'video']
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
            'video': forms.FileInput(attrs={'accept': 'video/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['caption'].required = True
        
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')
        caption = cleaned_data.get('caption')

        if image and video:
            raise forms.ValidationError("You can't upload both an image and a video.")
        
        if not image and not video:
            raise forms.ValidationError("You must upload either an image or a video.")
        
        if not caption:
            raise forms.ValidationError("Caption is required.")
        
        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Type your message...'}),
        }
