from django.forms import ModelForm, DateField
from django.forms.widgets import DateInput
from .models import Reading, Counter, Price


class ReadingForm(ModelForm):
    class Meta:
        model = Reading
        fields = "__all__"

        widgets = {
            "date": DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # Get the user from the kwargs
        super().__init__(*args, **kwargs)
        if user:
            self.fields["counter"].queryset = Counter.objects.filter(user=user)


class UpdateCounterForm(ModelForm):
    class Meta:
        model = Counter
        exclude = ["user"]


class AddCounterPriceForm(ModelForm):
    class Meta:
        model = Price
        exclude = ["counter", "date"]


class AddCounterReadingForm(ModelForm):
    class Meta:
        model = Reading
        exclude = ["counter", "date", "usage"]


class AddCounterForm(UpdateCounterForm):
    class Meta:
        model = Counter
        exclude = ["user"]

    initial_date = DateField(widget=DateInput(attrs={"type": "date"}))
