from enum import Enum, unique
from itertools import groupby

from django.utils.translation import gettext_lazy as _


def get_rulebook_choices():
	for c in Rulebook.__subclasses__():
		yield c.prefix, c.name


def get_all_prop_choices():
	for c in Rulebook.__subclasses__():
		for prop in c.PROP:
			yield c.prefix + "." + prop.prefix, prop.local


class Rulebook:
	class PROP(Enum):
		@property
		def prefix(self):
			return self.value[0]

		@property
		def local(self):
			return self.value[1]

		@property
		def prop_type(self):
			return self.value[2]

	@classmethod
	def get_prop_list(cls):
		return [
			[prop_type.value[1], [(cls.prefix + "." + i.prefix, i.local) for i in items]]
			for prop_type, items in groupby(cls.PROP, key=lambda p: p.prop_type)]


@unique
class PROP_TYPE(Enum):
	PRIVILEGED = 'p', _("Privileged")
	INCIDENTAL = 'i', _("Incidental")
	DILATORY = 'd', _("Dilatory")
	ORDINARY = 'o', _("Ordinary")


class Lesperance(Rulebook):
	prefix = 'l'
	name = _("Code Lespérance")

	@unique
	class PROP(Rulebook.PROP):
		PROP_CLOSE = 'c', _("Close the session"), PROP_TYPE.PRIVILEGED
		PROP_TIME_RESTART = 't', _("Fix a time to resume the session"), PROP_TYPE.PRIVILEGED
		PROP_ADJOURNMENT = 'a', _("Adjourn"), PROP_TYPE.PRIVILEGED
		PROP_SESSION_SUSPENSION = 's', _("Recess"), PROP_TYPE.PRIVILEGED
		PROP_PRIVILEGE = 'P', _("Point of privilege"), PROP_TYPE.PRIVILEGED
		PROP_APPEAL = 'A', _("Appeal the chair's decision"), PROP_TYPE.PRIVILEGED
		PROP_EDIT_AGENDA = 'e', _("Amend the approved agenda"), PROP_TYPE.PRIVILEGED
		PROP_WITHDRAW = 'W', _("Withdraw motion"), PROP_TYPE.INCIDENTAL
		PROP_CAMERA = 'c', _("Enter in camera"), PROP_TYPE.INCIDENTAL
		PROP_TIME_LIMIT = 'T', _("Impose a time limit"), PROP_TYPE.INCIDENTAL
		PROP_READ = 'r', _("Read document"), PROP_TYPE.INCIDENTAL
		PROP_WRITE = 'w', _("Write motion"), PROP_TYPE.INCIDENTAL
		PROP_DIVISION = 'd', _("Divide motion"), PROP_TYPE.INCIDENTAL
		PROP_RULE_SUSPENSION = 'S', _("Suspend the rules"), PROP_TYPE.INCIDENTAL
		PROP_SECRET = 'v', _("Conduct a secret vote"), PROP_TYPE.INCIDENTAL
		PROP_TABLE = 'b', _("Table discussion"), PROP_TYPE.DILATORY
		PROP_VOTE = 'V', _("Immediately vote"), PROP_TYPE.DILATORY
		PROP_PERM_POSTPONE = 'P', _("Postpone discussion definitely"), PROP_TYPE.DILATORY
		PROP_SEND_COMMITTEE = 'C', _("Refer to a committee"), PROP_TYPE.DILATORY
		PROP_TEMP_POSTPONE = 'p', _("Postpone discussion indefinitely"), PROP_TYPE.DILATORY
		PROP_SUB_AMEND = 'm', _("Sub-amendment"), PROP_TYPE.ORDINARY
		PROP_AMEND = 'M', _("Amendment"), PROP_TYPE.ORDINARY
		PROP_PRINCPIAL = 'R', _("Main motion"), PROP_TYPE.ORDINARY
		PROP_RECONSIDER = 'E', _("Reconsideration of a question"), PROP_TYPE.ORDINARY
		PROP_CANDIDATE = 'n', _("Nominate a member for a committee"), PROP_TYPE.ORDINARY
