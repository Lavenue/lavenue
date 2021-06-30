from django.forms import ModelForm

from .models import Intervention, Participant
from motions.models import Motion, Vote

class InterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = [
            'proposer',
            'seconder',
            'point',
            'supplants',
            'proposition',
            'preamble',
            'operative'
        ]

class MotionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = [
            'participant',
            'point',
            'motion',
            'time_asked',
            'time_granted',
            'sequence_number',
            'summary'
        ]

class VoteForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = [
            'motion',
            'requester',
            'secret',
            'favour',
            'oppose',
            'abstain',
            'passed'
        ]