from django.forms import ModelForm
from django.forms.widgets import DateInput
from counters.models import Reading, Counter


class ReadingForm(ModelForm):
    class Meta:
        model = Reading
        fields = ('counter', 'date', 'value')

        widgets = {
            'date': DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the user from the kwargs
        super().__init__(*args, **kwargs)
        if user:
            self.fields['counter'].queryset = Counter.objects.filter(user=user)


class CounterForm(ModelForm):
    class Meta:
        model = Counter
        fields = ('title', 'consumable', 'unit', 'price_per_unit', 'fixed_price')