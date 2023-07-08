from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from django.db.models import Count, F, Prefetch, QuerySet


from .models import User, Post


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


class PostsListView(ListView):
    template_name = "network/post_list.html"
    model = Post
    paginate_by = 10


class FollowingPostsListView(ListView):
    template_name = "network/post_list.html"
    model = Post
    paginate_by = 10

    def get_queryset(self):
        posts = QuerySet()
        influencers = self.request.user.influencers.all()
        for influencer in influencers:
            posts.add(influencer.posts.all())
        print(posts)
        return posts


def put_like(request, post_id):
    if request.method == "PUT":
        if request.user.is_authenticated:
            post = Post.objects.get(pk=post_id)
            if request.user in post.liked.all():
                post.liked.remove(request.user)
            else:
                post.liked.add(request.user)
            post.save()
            return JsonResponse({"likes": len(post.liked.all())})
        return HttpResponseForbidden
    return HttpResponseBadRequest





