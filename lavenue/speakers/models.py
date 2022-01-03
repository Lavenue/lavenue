from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


class Participant(models.Model):
	ROLE_PRESIDENT = "p"
	ROLE_SECRETARY = "s"
	ROLE_MEMBER = "m"
	ROLE_OBSERVER = "o"
	ROLE_CHOICES = (
		(ROLE_PRESIDENT, _("president")),
		(ROLE_SECRETARY, _("secretary")),
		(ROLE_MEMBER, _("member")),
		(ROLE_OBSERVER, _("observer")),
	)

	meeting = models.ForeignKey('organisations.Meeting', models.CASCADE, verbose_name=_("meeting"))
	name = models.CharField(max_length=100, verbose_name=_("name"))

	role = models.CharField(max_length=1, choices=ROLE_CHOICES, default=ROLE_MEMBER, verbose_name=_("role"))

	voting = models.IntegerField(default=0, verbose_name=_("voting power"))
	speaking = models.BooleanField(default=False, verbose_name=_("speaking"))

	users = models.ManyToManyField(get_user_model(), verbose_name=_("users"))

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = _("participant")
		verbose_name_plural = _("participants")


class Intervention(models.Model):
	PRIORITY_ORDER = 'O'
	PRIORITY_PRIV = 'P'
	PRIORITY_REGULAR = 'R'
	PRIORITY_INFO = 'I'
	PRIORITY_CHOICES = (
		(PRIORITY_REGULAR, _("Ordinary")),
		(PRIORITY_PRIV, _("Privileged")),
		(PRIORITY_ORDER, _("Order")),
		(PRIORITY_INFO, _("Information")),
	)
	participant = models.ForeignKey(Participant, models.PROTECT, verbose_name=_("participant"))
	point = models.ForeignKey('organisations.Point', models.CASCADE, verbose_name=_("point"))
	motion = models.ForeignKey('motions.Motion', models.CASCADE, blank=True, null=True, verbose_name=_("motion"))

	priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default=PRIORITY_REGULAR, blank=True,
		verbose_name=_("priority"))
	time_asked = models.DateTimeField(auto_now=False, blank=True, null=True, verbose_name=_("time asked"))
	time_granted = models.DateTimeField(auto_now=False, blank=True, null=True, verbose_name=_("time granted"))
	seq = models.PositiveIntegerField(blank=True, null=True, verbose_name=("sequence number"))

	summary = models.TextField(blank=True, verbose_name=_("summary"))

	def __str__(self):
		return "%s: %s (%d)" % (self.participant, self.point, self.seq)

	class Meta:
		verbose_name = _("intervention")
		verbose_name_plural = _("interventions")

		unique_together = (('point', 'motion', 'seq'),)
