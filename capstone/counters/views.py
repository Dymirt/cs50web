import json
from datetime import datetime
from types import NoneType

from django.db import IntegrityError
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, UpdateView, View, CreateView
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
    HttpResponseForbidden,
    HttpResponseBadRequest,
)
from django.contrib.auth import get_user_model

from .forms import ReadingForm, AddCounterForm, UpdateCounterForm
from .models import Counter, Reading

from django.db.models import OuterRef, Subquery, Max


def index_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("counters:dashboard"))
    else:
        return render(request, "counters/index.html")


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("counters:dashboard"))
        else:
            return render(
                request,
                "counters/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "counters/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("counters:login"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        if not username:
            return render(
                request, "counters/register.html", {"message": "Username is required"}
            )

        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if len(password) < 8:
            return render(
                request, "counters/register.html", {"message": "Passwords must contain at least 8 characters."}
            )

        if password != confirmation:
            return render(
                request, "counters/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = get_user_model().objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "counters/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("counters:dashboard"))
    else:
        return render(request, "counters/register.html")


class CounterDetailView(DetailView):
    model = Counter

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        counter = context['object']
        readings = Reading.objects.filter(counter=counter).order_by('date')
        readings_month = []
        readings_usage = []
        for reading in readings:
            readings_month.append(reading.date.strftime('%b'))
            readings_usage.append(reading.usage_in_units())

        context['readings_month'] = readings_month
        context['readings_usage'] = readings_usage

        return context


class AddCounter(LoginRequiredMixin, CreateView):
    form_class = AddCounterForm
    template_name = "counters/generic_update.html"
    success_url = reverse_lazy("counters:dashboard")

    def form_valid(self, form):
        if form.is_valid():
            form.instance.user = self.request.user
            response = super().form_valid(form)

            # Get the counter by its name
            counter_name = form.cleaned_data["title"]
            try:
                counter = Counter.objects.get(
                    user=self.request.user, title=counter_name
                )
            except Counter.DoesNotExist:
                # Handle the case when the counter with the given name doesn't exist
                # (e.g., show an error message or redirect to an error page)
                raise ValueError("Counter with the given name does not exist.")

            Reading.objects.create(
                counter=counter,
                date=form.cleaned_data["initial_date"],
                value=form.cleaned_data["initial_reading_value"],
            )
            return response
        return self.form_invalid(form)


class SummaryView(ListView):
    model = Counter
    template_name = "counters/summary.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_reading_date = latest_reading_date_for_user_counters(self.request.user)
        if latest_reading_date:
            context['latest_reading_date'] = latest_reading_date.strftime('%Y-%m-%d')
        context["counter_form"] = AddCounterForm()
        return context


def latest_reading_date_for_user_counters(user):
    return Reading.objects.filter(counter__user=user)\
        .aggregate(latest_date=Max('date'))['latest_date']


class AddReadings(View):
    def post(self, request):
        readings_date = datetime.strptime(request.POST.get("date"), "%Y-%m-%d")
        for counter in request.user.counters.all():
            if counter.readings.exists() and counter.readings.count() >= 2:
                latest_reading = counter.readings.latest("pk")
                if float(latest_reading.value) > float(request.POST.get(counter.title)):
                    return HttpResponseBadRequest()
                if latest_reading.date.month == readings_date.month:
                    latest_reading.delete()
            Reading.objects.create(
                counter=counter,
                date=readings_date,
                value=request.POST.get(counter.title),
            )
        return redirect(reverse_lazy("counters:dashboard"))


class CounterUpdateView(UpdateView):
    form_class = UpdateCounterForm
    template_name = "counters/generic_update.html"

    def get_queryset(self):
        return Counter.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("counters:counter-detail", kwargs={'pk': self.object.pk})


class ReadingUpdateView(UpdateView):
    form_class = ReadingForm
    success_url = reverse_lazy("counters:dashboard")
    template_name = "counters/generic_update.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields.pop("counter")  # Remove the 'counter' field from the form
        return form

    def get_queryset(self):
        return Reading.objects.filter(counter__user=self.request.user)
