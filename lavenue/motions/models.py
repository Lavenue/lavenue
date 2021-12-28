from django.db import models
from django.db.models import Q, Sum
from django.utils.translation import gettext_lazy as _

from .rulebooks import get_all_prop_choices


class Motion(models.Model):
	proposer = models.ForeignKey('speakers.Participant', models.PROTECT, related_name='proposed_set',
		verbose_name=_("proposer"))
	sponsors = models.ManyToManyField('speakers.Participant', blank=True,
		verbose_name=_("sponsors"))

	introduced = models.ForeignKey('speakers.Intervention', models.CASCADE, null=True, blank=True,
		verbose_name=_("introduced in"), related_name='introduced_set')
	point = models.ForeignKey('organisations.Point', models.CASCADE, verbose_name=_("point"))
	supplants = models.ForeignKey('self', models.CASCADE, blank=True, null=True, verbose_name=_("supplants"))
	seq = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("sequence"))

	proposition = models.CharField(max_length=3, choices=get_all_prop_choices(), verbose_name=_("proposition"))
	preamble = models.TextField(blank=True, verbose_name=_("preamble"))
	operative = models.TextField(verbose_name=_("operative clauses"))

	def __str__(self):
		return "%s: %s" % (self.proposer, self.get_proposition_display())

	class Meta:
		verbose_name = _("motion")
		verbose_name_plural = _("motions")

	@property
	def old_text(self):
		return getattr(self, "_old_text", "")


class Vote(models.Model):
	motion = models.ForeignKey(Motion, models.CASCADE, verbose_name=_("motion"))
	requester = models.ForeignKey('speakers.Participant', models.PROTECT, blank=True, null=True, verbose_name=_("requester"))
	secret = models.BooleanField(default=False, verbose_name=_("secret"))

	favour = models.PositiveIntegerField(default=0, verbose_name=_("in favour"))
	oppose = models.PositiveIntegerField(default=0, verbose_name=_("oppose"))
	abstain = models.PositiveIntegerField(default=0, verbose_name=_("abstain"))

	passed = models.BooleanField(verbose_name=_("passed"))

	def __str__(self):
		return "%s (%d-%d-%d)" % (self.motion.get_proposition_display(), self.favour, self.oppose, self.abstain)

	class Meta:
		verbose_name = _("vote")
		verbose_name_plural = _("votes")

	def calculate_totals(self):
		totals = self.ballot_set.aggregate(
			favour=Sum('worth', filter=Q(cast=Ballot.VOTE_FAVOUR)),
			oppose=Sum('worth', filter=Q(cast=Ballot.VOTE_OPPOSE)),
			abstain=Sum('worth', filter=Q(cast=Ballot.VOTE_ABSTAIN)))
		for cast in ['favour', 'oppose', 'abstain']:
			setattr(self, cast, totals[cast])


class Ballot(models.Model):
	VOTE_FAVOUR = 's'
	VOTE_OPPOSE = 'o'
	VOTE_ABSTAIN = 'a'
	VOTE_OPTIONS = (
		(VOTE_FAVOUR, _("in favour")),
		(VOTE_OPPOSE, _("oppose")),
		(VOTE_ABSTAIN, _("abstain"))
	)
	participant = models.ForeignKey('speakers.Participant', models.PROTECT, verbose_name=_("proposer"))
	vote = models.ForeignKey(Vote, models.CASCADE, verbose_name=_("vote"))
	cast = models.CharField(max_length=1, choices=VOTE_OPTIONS, default=VOTE_ABSTAIN, verbose_name=_("cast"))
	worth = models.PositiveIntegerField(default=1, verbose_name=_("worth"))

	def __str__(self):
		return "%s for %s: %s" % (self.participant, self.vote.motion.get_proposition_display(), self.get_cast_display())

	class Meta:
		verbose_name = _("ballot")
		verbose_name_plural = _("ballots")

		unique_together = (('participant', 'vote'),)
