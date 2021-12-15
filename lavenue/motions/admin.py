from django.contrib import admin

from organisations.models import Point

from .models import *


@admin.register(Motion)
class MotionAdmin(admin.ModelAdmin):
	list_display = ('proposition', 'point', 'proposer')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('proposer', 'point')

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "point":
			kwargs['queryset'] = Point.objects.all().select_related('session__meeting__organisation')
		return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
	list_display = ('motion', 'requester', 'favour', 'oppose', 'abstain', 'passed')
	list_editable = ('favour', 'oppose', 'abstain', 'passed')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('motion__proposer', 'requester')


@admin.register(Ballot)
class BallotAdmin(admin.ModelAdmin):
	list_display = ('participant', 'vote', 'cast', 'worth')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('participant', 'vote__motion')
