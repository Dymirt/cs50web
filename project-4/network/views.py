from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from django.db.models import Count, F, Prefetch, QuerySet, Q

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
    title = "All posts"

    def get_title(self):
        return self.title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_title()
        return context

    def post(self, request, *args, **kwargs):
        # Handle form submission
        post = Post(author=self.request.user, content=request.POST['post_content'])
        post.save()
        # Return the response
        return self.get(request, *args, **kwargs)


class FollowingPostsListView(PostsListView):
    title = "Following"

    def get_queryset(self):
        influencers = self.request.user.influencers.all()
        queryset = Post.objects.filter(Q(author__in=influencers))
        return queryset


class UserPostsListView(PostsListView):
    title = "Profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = User.objects.get(username=self.kwargs['user_name'])
        return context

    def get_queryset(self):
        queryset = Post.objects.filter(author=User.objects.get(username=self.kwargs['user_name']))
        return queryset


def like(request, post_id):
    if request.method == "PUT":
        if request.user.is_authenticated:
            post = Post.objects.get(pk=post_id)
            if request.user not in post.liked.all():
                post.liked.add(request.user)
            else:
                post.liked.remove(request.user)
            post.save()
            return JsonResponse({"likes": len(post.liked.all())})
        return HttpResponseForbidden
    return HttpResponseBadRequest


def follow(request, user_name):
    if request.method == "PUT":
        if request.user.is_authenticated:
            influencer = User.objects.get(username=user_name)
            if influencer not in request.user.influencers.all():
                request.user.influencers.add(influencer)
            else:
                request.user.influencers.remove(influencer)
            request.user.save()
            return JsonResponse({"followers": len(influencer.subscribers.all())})
        return HttpResponseForbidden
    return HttpResponseBadRequest










