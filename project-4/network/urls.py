
from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path("", views.PostsListView.as_view(), name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('following', login_required(views.FollowingPostsListView.as_view()), name='following'),
    path('profile/<str:user_name>', views.UserPostsListView.as_view(), name='profile'),
    # Fatch calls
    path("post/<int:post_id>/like", login_required(views.like)),
    path("post/<int:post_id>/edit", login_required(views.update_post)),
    path('profile/<str:user_name>/follow', login_required(views.follow)),
]
