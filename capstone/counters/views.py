from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic import CreateView
from .forms import ReadingForm, AddCounterForm, UpdateCounterForm

from .models import Counter, Reading


class CounterListView(ListView):
    model = Counter

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset


class ReadingListView(ListView):
    model = Reading
    template_name = "counters/reading_list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(counter__user=self.request.user)
        return queryset


class CounterDetailView(DetailView):
    model = Counter

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset


class AddCounterReading(CreateView):
    template_name = "counters/generic_update.html"
    form_class = ReadingForm
    success_url = reverse_lazy("counters:readings-list")

    def form_valid(self, form):
        if form.is_valid():
            form_counter = form.cleaned_data['counter']
            form_reading_date = form.cleaned_data['date']
            if form_counter in self.request.user.counters.all():
                if form_counter.readings.exists() and form_counter.readings.count() >= 2:
                    latest_reading = form_counter.readings.latest('pk')
                    if latest_reading.date.month == form_reading_date.month:
                        latest_reading.delete()
                return super().form_valid(form)

        return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the user object to the form
        return kwargs


class AddCounter(LoginRequiredMixin, CreateView):
    form_class = AddCounterForm
    template_name = "counters/generic_update.html"
    success_url = reverse_lazy("counters:counters-list")

    def form_valid(self, form):
        if form.is_valid():
            form.instance.user = self.request.user
            response = super().form_valid(form)

            # Get the counter by its name
            counter_name = form.cleaned_data['title']
            try:
                counter = Counter.objects.get(user=self.request.user, title=counter_name)
            except Counter.DoesNotExist:
                # Handle the case when the counter with the given name doesn't exist
                # (e.g., show an error message or redirect to an error page)
                raise ValueError("Counter with the given name does not exist.")

            Reading.objects.create(
                counter=counter,
                date=form.cleaned_data['initial_date'],
                value=form.cleaned_data['initial_reading_value'])
            return response
        return self.form_invalid(form)


class SummaryView(ListView):
    model = Counter
    template_name = "counters/summary.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset


class CounterUpdateView(UpdateView):
    form_class = UpdateCounterForm
    success_url = reverse_lazy("counters:readings-list")
    template_name = "counters/generic_update.html"

    def get_queryset(self):
        return Counter.objects.filter(user=self.request.user)


class ReadingUpdateView(UpdateView):
    form_class = ReadingForm
    success_url = reverse_lazy("counters:readings-list")
    template_name = "counters/generic_update.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields.pop('counter')  # Remove the 'counter' field from the form
        return form

    def get_queryset(self):
        return Reading.objects.filter(counter__user=self.request.user)


