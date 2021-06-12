from django.forms import ModelForm

from .models import Meeting, Organisation


class CreateMeetingForm(ModelForm):
	class Meta:
		model = Meeting
		fields = ('name', 'slug', 'code')

	def __init__(self, *args, organisation=None, **kwargs):
		self.organisation = organisation
		super().__init__(*args, **kwargs)

	def save(self, commit=False):
		meeting = super().save(commit=False)
		meeting.organisation = self.organisation

		if commit:
			meeting.save()
		return meeting


class CreateOrganisationForm(ModelForm):
	class Meta:
		model = Organisation
		fields = ('name', 'slug')

	def __init__(self, *args, user=None, **kwargs):
		self.user = user
		super().__init__(*args, **kwargs)

	def save(self, commit=True):
		organisation = super().save(commit=False)

		if commit:
			organisation.save()
			organisation.managers.add(self.user)

		return organisation
