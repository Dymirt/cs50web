import calendar
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
from django.core.serializers import serialize
from django.contrib.auth import get_user_model

from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear

from .forms import (
    ReadingForm,
    AddCounterForm,
    AddCounterPriceForm,
    AddCounterReadingForm,
    UpdateCounterForm,
)
from .models import Counter, Reading, Price, Payment

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
                request,
                "counters/register.html",
                {"message": "Passwords must contain at least 8 characters."},
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
        counter = context["object"]
        readings = (
            Reading.objects.filter(counter=counter, usage__gt=0)
            .annotate(month=ExtractMonth("date"))
            .values("month", "usage")
            .order_by("date")
        )
        readings_month = [
            calendar.month_name[reading.get("month")] for reading in readings
        ]
        readings_usage = [float(reading.get("usage")) for reading in readings]

        context["readings_month"] = readings_month
        context["readings_usage"] = readings_usage
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

            # Validate the AddCounterPriceForm
            price_form = AddCounterPriceForm(self.request.POST)
            if price_form.is_valid():
                Price.objects.create(
                    counter=counter,
                    date=form.cleaned_data["initial_date"],
                    price_per_unit=price_form.cleaned_data["price_per_unit"],
                    price_per_month=price_form.cleaned_data["price_per_month"],
                )

            # Validate the AddCounterReadingForm
            reading_form = AddCounterReadingForm(self.request.POST)
            if reading_form.is_valid():
                Reading.objects.create(
                    counter=counter,
                    date=form.cleaned_data["initial_date"],
                    value=reading_form.cleaned_data["value"],
                )

            return response
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            "price_form"
        ] = AddCounterPriceForm()  # Include the CounterPriceForm in the context
        context["reading_form"] = AddCounterReadingForm()
        return context


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
            context["latest_reading_date"] = latest_reading_date.strftime("%Y-%m-%d")
        context["counter_form"] = AddCounterForm()
        context["payments_per_month"] = (
            Reading.objects.filter(counter__user=self.request.user, usage__gt=0)
            .annotate(month=ExtractMonth("date"), year=ExtractYear("date"))
            .values("month", "year")
            .annotate(total_payment=Sum("payment__amount"))
            .order_by("month")
        )
        return context


def latest_reading_date_for_user_counters(user):
    return Reading.objects.filter(counter__user=user).aggregate(
        latest_date=Max("date")
    )["latest_date"]


def add_readings(request):
    if request.method == "POST":
        readings_date = datetime.strptime(request.POST.get("date"), "%Y-%m-%d")
        for counter in request.user.counters.all():
            # Only one reading per month if this not initial reading
            if counter.readings.exists() and counter.readings.count() > 1:
                latest_reading = counter.readings.latest("pk")

                # Return HttpResponseBadRequest if value of previous reading i greater then new value
                if float(latest_reading.value) > float(request.POST.get(counter.title)):
                    return HttpResponseBadRequest()

                # Delete the latest reading if reading in same month
                if latest_reading.date.month == readings_date.month:
                    latest_reading.delete()

            Reading.objects.create(
                counter=counter,
                date=readings_date,
                value=request.POST.get(counter.title),
            )

            latest_reading = counter.readings.latest("pk")

            # Adding Payment
            Payment.objects.create(
                counter=counter,
                reading=latest_reading,
                price=counter.prices.last(),
                amount=calculate_reading_payment(latest_reading),
            )

        return redirect(reverse_lazy("counters:dashboard"))


def calculate_reading_payment(reading):
    if reading.get_previous_reading():
        if reading.usage_in_units():
            total = reading.usage_in_units() * float(
                reading.counter.prices.last().price_per_unit
            )
            return (
                total + float(reading.counter.prices.last().price_per_month)
                if reading.counter.prices.last().price_per_month
                else total
            )
        return reading.counter.prices.last().price_per_month


class CounterUpdateView(UpdateView):
    form_class = UpdateCounterForm
    template_name = "counters/generic_update.html"

    def get_queryset(self):
        return Counter.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("counters:counter-detail", kwargs={"pk": self.object.pk})
