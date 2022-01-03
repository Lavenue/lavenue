from itertools import groupby

from django.db.models import Prefetch

from motions.models import Motion
from speakers.models import Intervention


def get_motion_old_text(motion, old=""):
	"""Get previous version of operative text without the proposed changes."""
	motion._old_text = old
	old = motion.operative
	for intervention in motion.interventions:
		for m in intervention.introduced:
			if m.proposition == 'l.M':
				old = get_motion_old_text(m, old)
			else:
				get_motion_old_text(m, "")
	if any(v.passed for v in motion.vote_set.all()):
		return old
	return motion._old_text


def get_motion_adopted_text(motion):
	"""Get version of the motion's operative text with approved amendments.

	We can use the last adopted immediate amendment for this purpose."""
	motion.adopted_text = motion.operative
	submotions = []
	for intervention in motion.interventions:
		for m in intervention.introduced:
			if m.proposition == 'l.M':
				get_motion_adopted_text(m)
				submotions.append(m)
				

	for m in reversed(submotions):
		if any(v.passed for v in m.vote_set.all()):
			motion.adopted_text = m.adopted_text
			return m.adopted_text

	return motion.operative


def get_point_full_num(point, numbering=""):
	if numbering == "":
		point.full_num = str(point.seq)
	else:
		point.full_num = numbering + "." + str(point.seq)
	for p in point.subpoints:
		get_point_full_num(p, point.full_num)


def get_point_motions_full_num(point):
	motion_count = 0
	motions = []

	def get_motion_full_num(motion, numbering):
		sub_count = 0
		motion.full_num = point.full_num + "-" + numbering
		motions.append(motion)
		for intervention in motion.interventions:
			for m in intervention.introduced:
				sub_count += 1
				get_motion_full_num(m, numbering + "." + str(sub_count))

	for intervention in point.interventions:
		for m in intervention.introduced:
			motion_count += 1
			get_motion_full_num(m, str(motion_count))

	return motions


def get_interventions(points):
	interventions = Intervention.objects.filter(point__in=points).order_by('point', 'motion', 'seq').prefetch_related(
		Prefetch('introduced_set', queryset=Motion.objects.all().prefetch_related('sponsors', 'vote_set').order_by('seq')))
	m_dict = {}
	for i in interventions:
		i.introduced = list(i.introduced_set.all())
		for m in i.introduced:
			m.interventions = []
			m_dict[m.id] = m

	root = {}
	for point, children in groupby(interventions, key=lambda i: i.point_id):
		for motion, children_ in groupby(list(children), key=lambda i: i.motion_id):
			ints = list(children_)

			motion_order = 0
			for child in ints:
				for m in child.introduced:
					motion_order += 1
					m.order = motion_order

			if motion is None:
				root[point] = ints
				continue
			m_dict[motion].interventions = ints

	return root
