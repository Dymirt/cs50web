from django.urls import path, reverse_lazy
from django.views.generic import DeleteView
from .models import Counter, Reading
from django.contrib.auth.decorators import login_required

from .views import (
    CounterDetailView,
    SummaryView,
    AddCounter,
    CounterUpdateView,
    login_view,
    logout_view,
    register,
    index_view,
    add_readings,
)

app_name = "counters"

urlpatterns = [
    # User
    path("", index_view, name="index"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("register", register, name="register"),
    path("dashboard/", SummaryView.as_view(), name="dashboard"),
    # Counters urls
    path("counter/<int:pk>", CounterDetailView.as_view(), name="counter-detail"),
    path("counter/add", AddCounter.as_view(), name="counter-add"),
    path("counter/<int:pk>/edit", CounterUpdateView.as_view(), name="counter-edit"),
    path(
        "counter/<int:pk>/delete/",
        DeleteView.as_view(
            model=Counter,
            success_url=reverse_lazy("counters:dashboard"),
            template_name="counters/generic_delete.html",
        ),
        name="counter-delete",
    ),
    # Reading urls
    path("readings/add", add_readings, name="readings-add"),
    path(
        "reading/<int:pk>/delete/",
        login_required(
            DeleteView.as_view(
                model=Reading,
                success_url=reverse_lazy("counters:dashboard"),
                template_name="counters/generic_delete.html",
            )
        ),
        name="reading-delete",
    ),
]
