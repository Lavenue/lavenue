from django.forms import ModelForm

from .models import Intervention


class InterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = [
            'participant',
            'point',
            'motion',
            'time_asked',
            'time_granted',
            'seq',
            'summary'
        ]