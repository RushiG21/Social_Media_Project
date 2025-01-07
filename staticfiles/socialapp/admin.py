from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Post, LikePost, Comment, Follow, Chat, Message


admin.site.site_header = "𝕾𝖔𝖈𝖎𝖆𝖑𝕬𝖕𝖕 Admin"
admin.site.site_title = "𝕾𝖔𝖈𝖎𝖆𝖑𝕬𝖕𝖕"
admin.site.index_title = "Welcome to 𝕾𝖔𝖈𝖎𝖆𝖑𝕬𝖕𝖕 Administration"

# Profile model admin customization
class ProfileAdmin(admin.ModelAdmin):    
    list_display = ('user', 'profile_pic_display', 'bio', 'location', 'created_at', 'updated_at')
    search_fields = ('user__username', 'bio', 'location')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    def profile_pic_display(self, obj):
        if obj.profile_pic:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50%;" />', obj.profile_pic.url)
        return "No Image"
    profile_pic_display.short_description = 'Profile Picture'

# Inline comments for posts
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ('user', 'text', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

# Post model admin customization
class PostAdmin(admin.ModelAdmin):
    def total_likes(self, obj):
        return obj.likes.count()
    
    def total_comments(self, obj):
        return obj.comments.count()

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "No Image"
    preview_image.short_description = 'Preview'
    
    def preview_video(self, obj):
        if obj.video:
            return format_html('<video src="{}" style="width: 100px; height: auto;" controls muted></video>', obj.video.url)
        return "No Video"
    preview_image.short_description = 'Preview'

    total_likes.short_description = 'Total Likes'
    list_display = ('user', 'preview_image', 'preview_video', 'total_likes', 'total_comments', 'caption', 'created_at', 'updated_at')
    search_fields = ('user__username', 'caption')
    list_filter = ('user', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_select_related = ('user',)
    list_per_page = 20
    inlines = [CommentInline]
    actions = ['mark_as_featured']
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)  # Assuming you have an `is_featured` field
        self.message_user(request, "Selected posts have been marked as featured.")
    mark_as_featured.short_description = "Mark selected posts as featured"

# LikePost model admin customization
class LikePostAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    list_filter = ('post', 'created_at')
    ordering = ('-created_at',)
    list_select_related = ('post', 'user')

# Comment model admin customization
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post','post_id_display', 'user', 'text', 'created_at')
    search_fields = ('user__username', 'text')
    list_filter = ('post', 'created_at')
    ordering = ('-created_at',)

    def post_id_display(self, obj):
        return obj.post.id
    post_id_display.short_description = 'Post ID'


# Follow model admin customization
class FollowAdmin(admin.ModelAdmin):
    list_display = ('followed','follower',  'created_at')
    list_filter = ('followed','follower',  'created_at')
    ordering = ('-created_at',)
    list_select_related = ( 'followed','follower')

# Chat model admin customization
class ChatAdmin(admin.ModelAdmin):
    def participants_display(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    participants_display.short_description = 'Participants'
    
    list_display = ('participants_display', 'created_at')
    list_filter = ('participants', 'created_at')
    ordering = ('-created_at',)

# Message model admin customization
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'content_preview', 'timestamp')
    list_filter = ('chat', 'sender', 'timestamp')
    ordering = ('-timestamp',)
    list_select_related = ('chat', 'sender')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

# Registering models with admin site
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(LikePost, LikePostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)
