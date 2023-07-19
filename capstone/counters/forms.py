from django.forms import ModelForm, DateField, DecimalField
from django.forms.widgets import DateInput
from .models import Reading, Counter


class ReadingForm(ModelForm):
    class Meta:
        model = Reading
        fields = "__all__"

        widgets = {
            'date': DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the user from the kwargs
        super().__init__(*args, **kwargs)
        if user:
            self.fields['counter'].queryset = Counter.objects.filter(user=user)


class CounterForm(ModelForm):
    initial_date = DateField(widget=DateInput(attrs={"type": "date"}))
    initial_reading_value = DecimalField()

    class Meta:
        model = Counter
        exclude = ["user"]