from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.sign_in, name='sign_in'),
    path('base/', views.base, name='base'),
    path('search/', views.search_posts, name='search_posts'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('sign-out/', views.sign_out, name='sign_out'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('message/', views.message, name='message'),
    path('chat/<str:username>/', views.open_chat, name='open_chat'),
    path('chat/<int:chat_id>/messages/', views.load_messages, name='get_messages'),
    path('send_message/', views.send_message, name='send_message'),
    path('add_post/', views.create_post, name='create_post'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('toggle-follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handling paths
handler404 = views.handle_404
handler500 = views.handle_500