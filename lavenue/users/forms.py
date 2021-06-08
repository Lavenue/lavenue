from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class UserCreationForm(BaseUserCreationForm):
	"""A form that creates a user from the given username and password."""

	class Meta(BaseUserCreationForm.Meta):
		fields = ("username", "email")
		labels = {"email": _("Email address")}

	def clean_email(self):
		data = self.cleaned_data['email']
		if get_user_model().objects.filter(email=data).exists():
			raise ValidationError(_("An account already exists with that email address"))
		return data
