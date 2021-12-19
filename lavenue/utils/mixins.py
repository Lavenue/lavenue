from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.base import ContextMixin

from organisations.models import Organisation


class ViewTitlesMixin(ContextMixin):
	page_title = ''
	page_subtitle = ''

	def get_page_title(self):
		return self.page_title

	def get_page_subtitle(self):
		return self.page_subtitle

	def get_context_data(self, **kwargs):
		if "page_title" not in kwargs:
			kwargs["page_title"] = self.get_page_title()
		if "page_subtitle" not in kwargs:
			kwargs["page_subtitle"] = self.get_page_subtitle()

		return super().get_context_data(**kwargs)


class OrganisationMixin(ViewTitlesMixin):
	@property
	def organisation(self):
		if not hasattr(self, "_organisation"):
			self._organisation = Organisation.objects.get(slug=self.kwargs['organisation_slug'])
		return self._organisation

	def get_context_data(self, **kwargs):
		kwargs['organisation'] = self.organisation
		return super().get_context_data(**kwargs)


class OrganisationManagerMixin(UserPassesTestMixin, OrganisationMixin):
	def test_func(self):
		return self.request.user.is_superuser or self.organisation.managers.filter(pk=self.request.user.pk).exists()
