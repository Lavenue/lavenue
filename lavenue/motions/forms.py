from django.forms import ModelForm

from .models import Motion, Vote

class MotionForm(forms.ModelForm):
    class Meta:
        model = Motion
        fields = [
            'proposer',
            'seconder',
            'point',
            'supplants',
            'proposition',
            'preamble',
            'operative'
        ]

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = [
            'motion',
            'requester',
            'secret',
            'favour',
            'oppose',
            'abstain',
            'passed'
        ]