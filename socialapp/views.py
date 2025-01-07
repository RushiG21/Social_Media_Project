from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .forms import PostForm, CommentForm, UserRegisterForm, ProfileUpdateForm
from .models import Profile, Post, LikePost, Comment, Follow, Chat, Message
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden, JsonResponse,HttpResponseNotAllowed
import base64
from django.core.files.base import ContentFile
from django.contrib import messages
from django.db.models import Q
from django.core.cache import cache
from time import sleep
from django.utils.dateformat import format

# Base view
def base(request):
    posts = Post.objects.all()
    follow_statuses = {}

    if request.user.is_authenticated:
        follows = Follow.objects.filter(follower=request.user).values_list('followed__username', flat=True)
        follow_statuses = {username: True for username in follows}
        
    return render(request, 'base.html', {'posts': posts, 'follow_statuses': follow_statuses})

# Sign-up view
@csrf_exempt
def sign_up(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. Please log in.')
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user:
                return redirect('sign_in')
        else:
            messages.error(request, 'Error during registration. Please check your input.')
    else:
        form = UserRegisterForm()
    return render(request, 'sign_up.html', {'form': form})

# Sign-in view
def sign_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'sign_in.html')
        
        login_attempts = cache.get(username, 0)

        if login_attempts >= 5:
            messages.error(request, 'Too many failed attempts. Please try again later.')
            return redirect('sign_in')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('base')
            else:
                messages.error(request, 'Your account has been blocked by an admin.')
                return redirect('sign_in')
        else:
            cache.set(username, login_attempts + 1, timeout=300)
            messages.error(request, 'Invalid username or password.')
            sleep(0.5)  # Delay response slightly
    return render(request, 'sign_in.html')

# Sign-out view
@login_required
def sign_out(request):
    logout(request)
    return redirect('sign_in')

# Search view
@login_required
def search_posts(request):
    query = request.GET.get("q")
    posts = None
    profiles = None
    if query:
        posts = Post.objects.filter(Q(caption__icontains=query) | Q(caption__regex=fr"#\b{query}\b")).distinct()
        # Search for user profiles (like usernames or full names)
        profiles = User.objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query)).distinct()
    else:
        # Handle the case when no query is provided (optional)
        posts = Post.objects.none()
        profiles = User.objects.none()
    
    return render(request, "search_results.html", {"posts": posts, "profiles": profiles, "query": query})

# Profile view
@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    following_list = user.following.all()
    followers_list = user.followers.all()
    # chat, created = Chat.objects.get_or_create(participants=request.user)
    posts = Post.objects.filter(user=user)
    is_following = Follow.objects.filter(follower=request.user, followed=user).exists()if request.user.is_authenticated else False
    follow_back = Follow.objects.filter(follower=profile.user, followed=request.user).exists() if request.user.is_authenticated else False
    return render(request, 'profile.html', {'profile': profile, 'posts': posts, 'is_following': is_following, 'following': following_list, 'followers': followers_list, 'follow_back': follow_back,'user': request.user,})

# Message view
@login_required
def message(request):
    chats = Chat.objects.filter(participants=request.user).distinct()
    profiles = []
    for chat in chats:
        other_users = chat.participants.exclude(id=request.user.id)
        if other_users.exists():
            profiles.append(other_users.first())
    context = {'profiles': profiles}
    return render(request,'messages.html',context)

@login_required
def open_chat(request, username):
    recipient = get_object_or_404(User, username=username)
    chat = Chat.objects.filter(participants=request.user).filter(participants=recipient).distinct().first()
    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(request.user, recipient)
    return JsonResponse({'chat_id': chat.id})

@login_required
def load_messages(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    messages = chat.messages.all().order_by('timestamp')
    messages_data = [{'sender__username': msg.sender.username, 'content': msg.content, 'timestamp': msg.timestamp} for msg in messages]
    return JsonResponse({'messages': messages_data})

@login_required
def send_message(request):
    if request.method == 'POST':
        chat_id = request.POST.get('chat_id')
        content = request.POST.get('content')
        if not chat_id or not content:
            return JsonResponse({'error': 'Chat ID and content are required'}, status=400)
        
        chat = get_object_or_404(Chat, id=chat_id)
        message = Message.objects.create(chat=chat, sender=request.user, content=content)
        return JsonResponse({'sender': message.sender.username, 'content': message.content, 'timestamp': message.timestamp.isoformat()})
    
# Profile settings view
@login_required
def profile_settings(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'profile_settings.html', {'form': form})

  
# Create post view
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            cropped_image_data = request.POST.get('cropped_image')
            # If cropped image data is available, decode and save it
            if cropped_image_data:
                format, imgstr = cropped_image_data.split(';base64,')
                ext = format.split('/')[-1]
                cropped_image = ContentFile(base64.b64decode(imgstr), name=f'cropped_image.{ext}')
                post.image = cropped_image  # Set the cropped image in place of the original image
            post.save()
            return redirect('base')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

# Edit post view
@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.user != request.user:
        return HttpResponseForbidden("You are not allowed to edit this post.")
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            cropped_image_data = request.POST.get('cropped_image')
            if cropped_image_data:
                format, imgstr = cropped_image_data.split(';base64,')
                ext = format.split('/')[-1]
                cropped_image = ContentFile(base64.b64decode(imgstr), name=f'cropped_image.{ext}')
                post.image = cropped_image
            form.save()
            return redirect('profile', username=post.user.username)
    else:
        form = PostForm(instance=post)
        
    return render(request, 'edit_post.html', {'form': form,'username': post.user.username,'current_image_url': post.image.url if post.image else None,
        'current_video_url': post.video.url if post.video else None,})

# Delete post view
@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")
    
    if request.method == 'POST':
        post.delete()
        return redirect('profile', request.user)

# AJAX-enabled Like post view
@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    liked = False
    like, created = LikePost.objects.get_or_create(post=post, user=request.user)
    
    if not created:
        like.delete()
    else:
        liked = True
    
    data = {
        'liked': liked,
        'like_count': post.likes.count()
    }
    
    return JsonResponse(data)

# AJAX-enabled Follow/Unfollow user view
@login_required
@require_POST
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)

    # Prevent users from following themselves
    if request.user == target_user:
        return JsonResponse({'error': 'You cannot follow yourself.'}, status=400)

    following_status = False
    follow_instance, created = Follow.objects.get_or_create(follower=request.user, followed=target_user)

    if not created:
        # User is already following, so unfollow
        follow_instance.delete()
    else:
        # Now following
        following_status = True

    followers_count = target_user.followers.count()
    following_count = target_user.following.count()

    return JsonResponse({
        'following_status': following_status,
        'followers_count': followers_count,
        'following_count': following_count,
    })


# AJAX-enabled Add comment view
@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            
            response_data = {
                'username': comment.user.username,
                'text': comment.text,
                'created_at': format(comment.created_at, 'N j, Y, P'),
                'comment_count': post.comments.count()
            }
            return JsonResponse(response_data)
        
    return JsonResponse({'error': 'Invalid request'}, status=400)

# Handle 404 error
def handle_404(request, exception):
    return render(request, '404.html', status=404)

# Handle 500 error
def handle_500(request):
    return render(request, '500.html', status=500)
