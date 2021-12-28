from django.contrib import admin

from .models import Intervention, Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
	list_display = ('name', 'meeting', 'role', 'voting', 'speaking')
	list_editable = ('role', 'voting', 'speaking')
	ordering = ('meeting', 'name')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('meeting__organisation')

	def get_form(self, request, obj, **kwargs):
		form = super().get_form(request, obj, **kwargs)
		form.base_fields['meeting'].queryset = form.base_fields['meeting'].queryset.select_related('organisation')
		return form


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
	list_display = ('participant', 'point_id', 'motion_id', 'seq')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('participant')

	def get_form(self, request, obj, **kwargs):
		form = super().get_form(request, obj, **kwargs)
		form.base_fields['point'].queryset = form.base_fields['point'].queryset.select_related('session__meeting__organisation')
		form.base_fields['motion'].queryset = form.base_fields['motion'].queryset.select_related('proposer')
		return form
