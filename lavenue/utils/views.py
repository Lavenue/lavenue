from django.core.exceptions import ImproperlyConfigured
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.utils.encoding import force_str
from django.views.generic import TemplateView, View
from django.views.generic.base import ContextMixin, TemplateResponseMixin


class FormSetMixin(ContextMixin):
	"""Provides some functionality for formsets, analogously to FormMixin.
	Only what is actually used in Tabbycat is implemented."""

	success_url = None

	def get_context_data(self, **kwargs):
		if 'formset' not in kwargs:
			kwargs['formset'] = self.get_formset()
		return super().get_context_data(**kwargs)

	def formset_valid(self, formset):
		return HttpResponseRedirect(self.get_success_url())

	def formset_invalid(self, formset):
		return self.render_to_response(self.get_context_data(formset=formset))

	def get_success_url(self):
		if self.success_url:
			# Forcing possible reverse_lazy evaluation
			url = force_str(self.success_url)
		else:
			raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
		return url


class ModelFormSetMixin(FormSetMixin):
	"""Provides some functionality for model formsets, analogously to
	ModelFormMixin."""

	formset_factory_kwargs = {}
	formset_model = None  # not 'model' to avoid conflicts with SingleObjectMixin

	def get_formset_factory_kwargs(self):
		return self.formset_factory_kwargs.copy()

	def get_formset_class(self):
		return modelformset_factory(self.formset_model, **self.get_formset_factory_kwargs())

	def get_formset_kwargs(self):
		return {}

	def get_formset_queryset(self):
		return self.formset_model.objects.all()

	def get_formset(self):
		formset_class = self.get_formset_class()
		if self.request.method in ('POST', 'PUT'):
			return formset_class(data=self.request.POST, files=self.request.FILES,
					**self.get_formset_kwargs())
		elif self.request.method == 'GET':
			return formset_class(queryset=self.get_formset_queryset(), **self.get_formset_kwargs())

	def formset_valid(self, formset):
		self.instances = formset.save()
		return super().formset_valid(formset)


class ProcessFormSetView(View):
	"""Provides some functionality for model formsets, analogously to
	ProcessFormView."""

	def get(self, request, *args, **kwargs):
		return self.render_to_response(self.get_context_data())

	def post(self, request, *args, **kwargs):
		formset = self.get_formset()
		if formset.is_valid():
			return self.formset_valid(formset)
		else:
			return self.formset_invalid(formset)

	def put(self, request, *args, **kwargs):
		return self.post(request, *args, **kwargs)


class ModelFormSetView(ModelFormSetMixin, TemplateResponseMixin, ProcessFormSetView):
	pass
