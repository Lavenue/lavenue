from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from motions.rulebooks import get_rulebook_choices, Lesperance


class Organisation(models.Model):
	name = models.CharField(max_length=100, unique=True, verbose_name=_("name"))
	slug = models.SlugField(max_length=20, unique=True, verbose_name=_("slug"))
	active = models.BooleanField(default=True, verbose_name=_("active"))

	managers = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("managers"))

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = _("organisation")
		verbose_name_plural = _("organisations")


class Meeting(models.Model):
	organisation = models.ForeignKey(Organisation, models.CASCADE, verbose_name=_("organisation"))
	name = models.CharField(max_length=100, verbose_name=_("name"))
	slug = models.SlugField(max_length=20, unique=True, verbose_name=_("slug"))
	code = models.CharField(max_length=1, choices=get_rulebook_choices(), default=Lesperance.prefix, verbose_name=_("code"))

	def __str__(self):
		return "%s: %s" % (self.organisation, self.name)

	class Meta:
		verbose_name = _("meeting")
		verbose_name_plural = _("meetings")

		unique_together = (('organisation', 'slug'),)

	@property
	def ended(self):
		return not self.session_set.filter(ended_at__isnull=True).exists()


class Session(models.Model):
	meeting = models.ForeignKey(Meeting, models.CASCADE, verbose_name=_("meeting"))

	start = models.DateTimeField(auto_now=False, verbose_name=_("start time"))
	end = models.DateTimeField(auto_now=False, blank=True, null=True, verbose_name=_("end time"))

	started_at = models.DateTimeField(auto_now=False, blank=True, null=True, verbose_name=_("started at"))
	ended_at = models.DateTimeField(auto_now=False, blank=True, null=True, verbose_name=_("ended at"))

	def __str__(self):
		return "%s @ %s" % (self.meeting, self.start.astimezone().strftime("%Y-%m-%d %H:%M %z"))

	class Meta:
		verbose_name = _("session")
		verbose_name_plural = _("sessions")


class Point(models.Model):
	session = models.ForeignKey(Session, models.CASCADE, verbose_name=_("session"))
	parent = models.ForeignKey('self', models.CASCADE, null=True, blank=True, verbose_name=_("parent point"))
	seq = models.PositiveIntegerField(verbose_name=_("sequence number"))

	name = models.CharField(max_length=150, verbose_name=_("name"))

	start_at = models.DateTimeField(auto_now=False, blank=True, null=True, verbose_name=_("start at"),
		help_text=_("When set, the point should not start after this time."))
	reached_at = models.DateTimeField(auto_now=False, blank=True, null=True, verbose_name=("reached at"))
	current = models.BooleanField(default=False, verbose_name=_("current"))

	def __str__(self):
		return "%s: %s" % (self.session.meeting, self.name)

	class Meta:
		verbose_name = _("point")
		verbose_name_plural = _("points")

		unique_together = (('session', 'parent', 'seq'),)

	@property
	def continued(self):
		return getattr(self, '_continued', False)

	@property
	def subpoints(self):
		if not hasattr(self, '_children'):
			self._children = type(self).objects.filter(parent=self).order_by('seq')
		return self._children
