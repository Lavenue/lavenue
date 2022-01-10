from django.contrib import admin

from .models import Ballot, Motion, Vote


@admin.register(Motion)
class MotionAdmin(admin.ModelAdmin):
	list_display = ('proposition', 'point', 'proposer')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('proposer', 'point')

	def get_form(self, request, obj, **kwargs):
		form = super().get_form(request, obj, **kwargs)
		form.base_fields['introduced'].queryset = form.base_fields['introduced'].queryset.select_related('participant', 'point__session__meeting__organisation')
		form.base_fields['point'].queryset = form.base_fields['point'].queryset.select_related('session__meeting__organisation')
		form.base_fields['supplants'].queryset = form.base_fields['supplants'].queryset.select_related('proposer')
		return form


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
	list_display = ('motion', 'requester', 'favour', 'oppose', 'abstain', 'passed')
	list_editable = ('favour', 'oppose', 'abstain', 'passed')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('motion__proposer', 'requester')

	def get_form(self, request, obj, **kwargs):
		form = super().get_form(request, obj, **kwargs)
		form.base_fields['motion'].queryset = form.base_fields['motion'].queryset.select_related('proposer')
		return form


@admin.register(Ballot)
class BallotAdmin(admin.ModelAdmin):
	list_display = ('participant', 'vote', 'cast', 'worth')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('participant', 'vote__motion')
