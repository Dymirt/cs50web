
from django.urls import path

from . import views

urlpatterns = [
    path("", views.PostsListView.as_view(), name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post/<int:post_id>/put_like", views.put_like),
    path('following', views.FollowingPostsListView.as_view(), name='following'),
    path('profile/<str:user_name>', views.UserPostsListView.as_view(), name='profile'),
]
