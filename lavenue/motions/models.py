from django.db import models
from django.utils.translation import gettext_lazy as _

from .rulebooks import get_all_prop_choices


class Motion(models.Model):
	proposer = models.ForeignKey('speakers.Participant', models.PROTECT, related_name='proposed_set',
		verbose_name=_("proposer"))
	seconder = models.ForeignKey('speakers.Participant', models.PROTECT, null=True, blank=True, related_name='seconded_set',
		verbose_name=_("seconder"))

	point = models.ForeignKey('organisations.Point', models.CASCADE, verbose_name=_("point"))
	supplants = models.ForeignKey('self', models.CASCADE, verbose_name=_("supplants"))

	proposition = models.CharField(max_length=3, choices=get_all_prop_choices(), verbose_name=_("proposition"))
	preamble = models.TextField(blank=True, verbose_name=_("preamble"))
	operative = models.TextField(verbose_name=_("operative clauses"))

	def __str__(self):
		return "%s (%s): %s" % (self.proposer, self.seconder, self.get_proposition_display())

	class Meta:
		verbose_name = _("motion")
		verbose_name_plural = _("motions")


class Vote(models.Model):
	motion = models.ForeignKey(Motion, models.CASCADE, verbose_name=_("motion"))
	requester = models.ForeignKey('speakers.Participant', models.PROTECT, blank=True, null=True, verbose_name=_("requester"))

	favour = models.PositiveIntegerField(default=0, verbose_name=_("in favour"))
	oppose = models.PositiveIntegerField(default=0, verbose_name=_("oppose"))
	abstain = models.PositiveIntegerField(default=0, verbose_name=_("abstain"))

	passed = models.BooleanField(verbose_name=_("passed"))

	def __str__(self):
		return "%s (%d-%d-%d)" % (self.motion.get_proposition_display(), self.favour, self.oppose, self.abstain)

	class Meta:
		verbose_name = _("vote")
		verbose_name_plural = _("votes")
