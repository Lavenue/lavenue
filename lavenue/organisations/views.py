from copy import deepcopy

from django.views.generic import TemplateView

from .models import Meeting, Point, Session


class BreakRecursionException(Exception):
	pass


class AgendaView(TemplateView):
	template_name = 'agenda.html'

	@staticmethod
	def find_break(session, tree, path):
		"""Uses call by sharing with the path parameter to return the "path",
		thus the indices of the parent nodes to the first node for a different
		session. This is a pre-order DFS tree traversal. As we only want the
		first, we call (and catch) an exception to break."""
		for i, c in enumerate(tree.children):
			if c.session_id != session:
				path.append(i)
				raise BreakRecursionException
			path.append(i)
			AgendaView.find_break(session, c, path)
			path.pop()

	def get_sessions(self, meeting):
		"""Associate branches of the tree to specific sessions.

		This is first done by sorting the root points to the session. Then, the
		last point of each session is studied to determine whether some of their
		subpoints are in the next session. If so, that point is split so that
		the latter session keeps the titles of the points leading up to the
		first point to discuss, and removes that point (including children) from
		the former."""
		tree = meeting.create_point_tree()
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

			"""Go through the path given and deep-copy the point in order to lop
			subpoints that are before or after the session without affecting the
			other."""
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
