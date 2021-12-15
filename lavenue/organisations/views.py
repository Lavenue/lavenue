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
		self.meeting.participant_set.create(name=user.username, user=user, role=Participant.ROLE_PRESIDENT)
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

	def get_sessions(self):
		"""Associate branches of the tree to specific sessions.

		This is first done by sorting the root points to the session. Then, the
		last point of each session is studied to determine whether some of their
		subpoints are in the next session. If so, that point is split so that
		the latter session keeps the titles of the points leading up to the
		first point to discuss, and removes that point (including children) from
		the former."""
		tree = self.create_point_tree()
		sessions = Session.objects.filter(meeting__slug=self.kwargs['meeting'],
			meeting__organisation__slug=self.kwargs['organisation']).order_by('start')
		s_dict = {s.id: s for s in sessions}

		def dfs(point, current_session, path):
			for i, n in enumerate(point.subpoints):
				if n.session_id != current_session:
					n_path = deepcopy(path)
					for p in n_path:
						p._continued = True
					n_point = n_path.pop(0)
					n_path.extend(point.subpoints[i:])
					del point.subpoints[i:]
					n_point._children = n_path
					s_dict[n.session_id].points.append(n_point)
					break
				else:
					n_path = path.copy()
					n_path.append(n)
					dfs(n, current_session, n_path)

		for s in sessions:
			s.points = []
		for n in tree:
			s_dict[n.session_id].points.append(n)
			dfs(n, n.session_id, [n])

		return s_dict.values()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['meeting'] = self.meeting
		context['sessions'] = self.get_sessions()
		return context
