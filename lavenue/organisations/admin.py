from django.contrib import admin
from django.db.models import Prefetch

from .models import *

@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', 'active')
	ordering = ('name',)
	list_editable = ('active',)
	search_fields = ('name',)


class SessionInline(admin.TabularInline):
		model = Session
		fields = ('start', 'end')

		def get_queryset(self, request):
			return super().get_queryset(request).select_related('meeting__organisation')


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
	list_display = ('name', 'organisation', 'code')
	list_filter = ('organisation',)
	inlines = (SessionInline,)

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('organisation')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
	list_display = ('meeting', 'start', 'end')
	list_filter = ('meeting__organisation',)

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('meeting__organisation')


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
	list_display = ('session', 'name', 'seq', 'current')
	list_editable = ('current',)
	list_filter = ('session',)

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('session__meeting__organisation')

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "session":
			kwargs['queryset'] = Session.objects.all().select_related('meeting__organisation')
		elif db_field.name == "parent":
			kwargs['queryset'] = Point.objects.all().select_related('session__meeting__organisation')
		return super().formfield_for_foreignkey(db_field, request, **kwargs)
