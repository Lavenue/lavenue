from django.contrib import admin

from .models import Meeting, Membership, MembershipInvitation, Organisation, Point, Session


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

	def get_form(self, request, obj, **kwargs):
		form = super().get_form(request, obj, **kwargs)
		form.base_fields['meeting'].queryset = form.base_fields['meeting'].queryset.select_related('organisation')
		return form


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
	list_display = ('session', 'name', 'seq', 'current')
	list_editable = ('current',)
	list_filter = ('session',)

	def get_form(self, request, obj, **kwargs):
		form = super().get_form(request, obj, **kwargs)
		form.base_fields['session'].queryset = form.base_fields['session'].queryset.select_related('meeting__organisation')
		form.base_fields['parent'].queryset = form.base_fields['parent'].queryset.select_related('session__meeting__organisation')
		return form

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('session__meeting__organisation')

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "session":
			kwargs['queryset'] = Session.objects.all().select_related('meeting__organisation')
		elif db_field.name == "parent":
			kwargs['queryset'] = Point.objects.all().select_related('session__meeting__organisation')
		return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
	list_display = ('user', 'organisation', 'role')
	list_editable = ('role',)
	list_filter = ('organisation',)

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('user', 'organisation')


@admin.register(MembershipInvitation)
class MembershipInvitationAdmin(admin.ModelAdmin):
	list_display = ('email', 'organisation', 'role')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('organisation')
