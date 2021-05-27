from django.contrib import admin

from .models import *


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
	list_display = ('name', 'user', 'meeting', 'role', 'voting', 'speaking')
	list_editable = ('role', 'voting', 'speaking')
	ordering = ('meeting', 'name')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('meeting__organisation', 'user')


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
	list_display = ('participant', 'point_id', 'motion_id', 'seq')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('participant')
