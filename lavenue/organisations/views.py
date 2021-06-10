from copy import copy, deepcopy
from itertools import groupby

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import CreateView, FormView, TemplateView

from speakers.models import Participant
from utils.mixins import OrganisationManagerMixin, OrganisationMixin

from .forms import CreateMeetingForm, CreateOrganisationForm
from .models import Meeting, Point, Session


class BreakRecursionException(Exception):
	pass


class CreateMeetingView(OrganisationManagerMixin, FormView):
	template_name = 'create-meeting.html'
	form_class = CreateMeetingForm

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['organisation'] = self.organisation
		return kwargs

	def form_valid(self, form):
		self.meeting = form.save(commit=True)
		user = self.request.user
		meeting.participant_set.create(name=user.username, user=user, role=Participant.ROLE_PRESIDENT)
		return super().form_valid(form)


class CreateOrganisationView(LoginRequiredMixin, CreateView):
	template_name = 'create-organisation.html'
	form_class = CreateOrganisationForm

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['user'] = self.request.user
		return kwargs

	def get_success_url(self):
		return reverse('organisation-homepage', kwargs={'organisation_slug': self.object.slug})


class OrganisationHomepageView(OrganisationMixin, TemplateView):
	template_name = 'organisation-homepage.html'


class AgendaView(OrganisationMixin, TemplateView):
	template_name = 'agenda.html'

	def get_page_title(self):
		return _("Agenda for %(meeting)s") % {'meeting': self.meeting.name}

	@property
	def meeting(self):
		if not hasattr(self, '_meeting'):
			self._meeting = Meeting.objects.select_related('organisation').get(
				organisation=self.organisation, slug=self.kwargs['meeting_slug'])
		return self._meeting

	def create_point_tree(self):
		"""Get all points for meeting and then treat as a tree with an
		imaginary root. As the objects are shared (call by sharing without
		copies), they can be grouped by their immediate parent to make a list of
		children."""
		points = Point.objects.filter(session__meeting=self.meeting).order_by('parent', 'seq')
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

	def get_sessions(self):
		"""Associate branches of the tree to specific sessions.

		This is first done by sorting the root points to the session. Then, the
		last point of each session is studied to determine whether some of their
		subpoints are in the next session. If so, that point is split so that
		the latter session keeps the titles of the points leading up to the
		first point to discuss, and removes that point (including children) from
		the former."""
		tree = self.create_point_tree()
		sessions = Session.objects.filter(meeting=self.meeting).order_by('start')
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
		context['meeting'] = self.meeting
		context['sessions'] = self.get_sessions()
		return context
