from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

User = get_user_model()

# Utility methods
def profile_pic_path(instance, filename):
    return f'profile_pics/user_{instance.user.id}/{filename}'

def post_media_path(instance, filename):
    post_count = instance.user.posts.count() + 1
    return f'posts/user_{instance.user.id}/post_{post_count}/{filename}'


# Adding manager for custom queries
class PostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(created_at__lte=timezone.now())

    def recent_posts(self):
        return self.get_queryset().order_by('-created_at')[:10]

class ProfileManager(models.Manager):
    def active_profiles(self):
        return self.get_queryset().filter(user__is_active=True)

class CommentManager(models.Manager):
    def recent_comments(self):
        return self.get_queryset().order_by('-created_at')[:10]
    
# Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    profile_pic = models.ImageField(blank=True, null=True, upload_to=profile_pic_path)
    bio = models.TextField(max_length=500,blank=True)
    location = models.CharField(max_length=100, blank=True)
    followers=models.ManyToManyField('self',symmetrical=False,related_name='followed_by',blank=True)
    following=models.ManyToManyField('self',symmetrical=False,related_name='follows_to',blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ProfileManager()
    
    def get_followers(self):
        return Follow.objects.filter(followed=self.user).select_related('follower')

    def get_following(self):
        return Follow.objects.filter(follower=self.user).select_related('followed')
    
    def get_followers_count(self):
        return self.followers.count()

    def get_following_count(self):
        return self.following.count()
    
    def __str__(self):
        return f'{self.user.username}'
    

# Post model
class Post(models.Model):
    user = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to=post_media_path)
    video = models.FileField(blank=True, null=True, upload_to=post_media_path)
    caption = models.TextField(max_length=300,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PostManager() 
    
    def __str__(self):
        return f'{self.user.username} - {self.caption[:20]}'

    def total_likes(self):
        return self.likes.count()

    def extract_hashtags(self):
        import re
        return re.findall(r"#\w+", self.caption)
    
# LikePost model
class LikePost(models.Model):
    post = models.ForeignKey(Post, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('post', 'user')
    
    def __str__(self):
        return f'{self.user.username} likes {self.post.id}'

# Comment model
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=300)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = CommentManager()

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.id}'

# Follow model
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'followed')
    
    def __str__(self):
        return f'{self.follower.username} follows {self.followed.username}'
    
class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between {', '.join([user.username for user in self.participants.all()])}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"

# Signal receivers to create and save user profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
