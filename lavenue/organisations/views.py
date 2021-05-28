from copy import copy, deepcopy
from itertools import groupby

from django.views.generic import TemplateView

from .models import Meeting, Point, Session


class BreakRecursionException(Exception):
	pass


class AgendaView(TemplateView):
	template_name = 'agenda.html'

	def create_point_tree(self):
		points = Point.objects.all().order_by('parent', 'seq')
		p_dict = {p.id: p for p in points}
		for p in points:
			p._children = []

		root = []
		for parent, children in groupby(points, key=lambda i: i.parent_id):
			if parent is None:
				root = list(children)
				continue
			p_dict[parent]._children = list(children)

		return root

	@staticmethod
	def find_break(session, tree, path):
		for i, c in enumerate(tree.children):
			if c.session_id != session:
				path.append(i)
				raise BreakRecursionException
			path.append(i)
			AgendaView.find_break(session, c, path)
			path.pop()

	def get_sessions(self, meeting):
		tree = self.create_point_tree()
		sessions = Session.objects.filter(meeting=meeting).order_by('start')
		s_dict = {s.id: s for s in sessions}
		for s in sessions:
			s.points = []
		for n in tree:
			s_dict[n.session_id].points.append(n)

		session_order = [s.id for s in sessions]
		for i, (pk, session) in enumerate(s_dict.items()):
			path = []
			if len(session.points) > 0:
				try:
					AgendaView.find_break(pk, session.points[-1], path)
				except BreakRecursionException:
					pass

			path_len = len(path)
			if len(path) > 0 and not (len(path) == 1 and path[0] == 0):
				pass_point = deepcopy(session.points[-1])
				s_dict[session_order[i+1]].points.append(pass_point)
				new_point = pass_point
				old_point = session.points[-1]
				for j, p in enumerate(path):
					del new_point._children[0:p]
					if j == path_len-1:
						del old_point._children[p:]
					else:
						del old_point._children[p+1:]
					if j < path_len-1:
						new_point = new_point._children[0]
						old_point = old_point._children[-1]

		return s_dict.values()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['meeting'] = Meeting.objects.select_related(
			'organisation').get(organisation__slug=self.kwargs['organisation_slug'], slug=self.kwargs['slug'])
		context['sessions'] = self.get_sessions(context['meeting'])
		return context
