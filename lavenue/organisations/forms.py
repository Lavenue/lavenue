from django import forms
from django.utils.translation import gettext as _

from .models import Point


class SessionChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, obj):
		return obj.start.astimezone()


class PointForm(forms.ModelForm):
	number = forms.CharField(label=_("Point number"),
		help_text=_("Insert periods between numbers for subpoints, ie. 1.2.3"))

	class Meta:
		model = Point
		fields = ('session', 'number', 'name', 'start_at')
		field_classes = {
			'session': SessionChoiceField,
		}

	def __init__(self, *args, **kwargs):
		session_choices = kwargs.pop('session_choices')
		super().__init__(*args, **kwargs)

		self.fields['session'].queryset = session_choices
		if 'instance' in kwargs:
			self.fields['number'].initial = getattr(kwargs['instance'], 'number', '')

	def save(self, commit=True):
		point = super().save(commit=commit)
		point.number = self.cleaned_data['number']
		return point
