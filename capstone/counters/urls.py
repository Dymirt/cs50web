from django.urls import path, reverse_lazy
from django.views.generic import UpdateView, CreateView, DeleteView
from .models import Counter, Reading
from django.contrib.auth.decorators import login_required

from .views import (
    CounterListView,
    CounterDetailView,
    SummaryView,
    AddCounter,
    CounterUpdateView,
    ReadingUpdateView,
    AddReadings,
    login_view,
    logout_view,
    register,
    index_view,
)

app_name = "counters"

urlpatterns = [
    path("index", index_view, name="index"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("register", register, name="register"),

    path("counters/add-readings", AddReadings.as_view(), name="add-readings"),
    # path("counters/", SummaryView.as_view(), name="dashboard"),
    path("counters/summary", SummaryView.as_view(), name="summary"),
    # Counters urls
    path("counters/list/", CounterListView.as_view(), name="counters-list"),
    path("counter/create/", AddCounter.as_view(), name="counter-create"),
    path("counter/<int:pk>/edit/", CounterUpdateView.as_view(), name="counter-edit"),

    path("counter/<int:pk>/detail/", CounterDetailView.as_view(), name="counter-detail"),
    # Reading urls
    path("reading/<int:pk>/edit/", ReadingUpdateView.as_view(), name="reading-edit"),
    path(
        "reading/<int:pk>/delete/",
        login_required(
            DeleteView.as_view(
                model=Reading,
                success_url=reverse_lazy("counters:summary"),
                template_name="counters/generic_delete.html",
            )
        ),
        name="reading-delete",
    ),
    path(
        "counter/<int:pk>/delete/",
        DeleteView.as_view(
            model=Counter,
            success_url=reverse_lazy("counters:counters-list"),
            template_name="counters/generic_delete.html",
        )
        ,
        name="counter-delete",
    ),
]
