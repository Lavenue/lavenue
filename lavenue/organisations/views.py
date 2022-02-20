from copy import deepcopy
from itertools import groupby

from django.db.models import F, Prefetch
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.viewsets import ModelViewSet

from speakers.models import Intervention, Participant

from .models import Meeting, Membership, Point, Session, Organisation
from .serializers import (AgendaSerializer, InterventionTreeSerializer,
	MinutesSerializer, MeetingSerializer, OrganisationSerializer, PointSpeechOrderSerializer)
from .tree import get_interventions, get_motion_old_text


class OrgManagerOrReadOnlyPermission(BasePermission):
	message = "org.notmanager"

	def has_permission(self, request, view):
		return (
			request.user.is_authenticated and Membership.objects.filter(
				organisation=view.organisation, user=request.user, role=Membership.ROLE_MANAGER).exists()
		) or request.method in SAFE_METHODS


class SecretaryOnlyPermission(BasePermission):
	message = "meeting.notsecretary"

	def has_object_permission(self, request, view, obj):
		return Participant.objects.filter(meeting=obj, user=request.user, role__in=[
			Participant.ROLE_PRESIDENT,
			Participant.ROLE_SECRETARY,
		]).exists()


class OrganisationViewSet(ModelViewSet):
	serializer_class = OrganisationSerializer
	queryset = Organisation.objects.all()
	lookup_field = 'slug'
	lookup_url_kwarg = 'organisation'


class BreakRecursionException(Exception):
	pass


class AgendaViewSet(ModelViewSet):
	serializer_class = AgendaSerializer
	lookup_field = 'slug'
	lookup_url_kwarg = 'meeting'

	@property
	def organisation(self):
		return Organisation.objects.prefetch_related('members').get(slug=self.kwargs['organisation'])

	def get_queryset(self):
		return Meeting.objects.filter(organisation__slug=self.kwargs['organisation']).select_related('organisation')

	def get_object(self):
		m = super().get_object()
		m._sessions = self.get_sessions()
		return m

	def create_point_tree(self):
		"""Get all points for meeting and then treat as a tree with an
		imaginary root. As the objects are shared (call by sharing without
		copies), they can be grouped by their immediate parent to make a list of
		children."""
		points = Point.objects.filter(seq__isnull=False, session__meeting__slug=self.kwargs['meeting'],
			session__meeting__organisation__slug=self.kwargs['organisation']).order_by('parent', 'seq')
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
					s_dict[n.session_id]._points.append(n_point)
					break
				else:
					n_path = path.copy()
					n_path.append(n)
					dfs(n, current_session, n_path)

		for s in sessions:
			s._points = []
		for n in tree:
			s_dict[n.session_id]._points.append(n)
			dfs(n, n.session_id, [n])

		return s_dict.values()


class MinutesViewSet(ModelViewSet):
	serializer_class = MinutesSerializer
	lookup_field = 'slug'
	lookup_url_kwarg = 'meeting'

	def get_queryset(self):
		return Meeting.objects.filter(organisation__slug=self.kwargs['organisation']).select_related('organisation').prefetch_related('session_set')

	def get_object(self):
		m = super().get_object()
		m._points = self.get_points()
		m.start_time = m.session_set.all().order_by('start').first().start
		return m

	def get_points(self):
		"""Get all points for meeting and then treat as a tree with an
		imaginary root. As the objects are shared (call by sharing without
		copies), they can be grouped by their immediate parent to make a list of
		children."""
		points = Point.objects.filter(seq__isnull=False, session__meeting__slug=self.kwargs['meeting'],
			session__meeting__organisation__slug=self.kwargs['organisation']).order_by('parent', 'seq')
		p_dict = {p.id: p for p in points}
		for p in points:
			p._children = []
			p.interventions = []

		root = []
		for parent, children in groupby(points, key=lambda i: i.parent_id):
			if parent is None:
				root = list(children)
				continue
			p_dict[parent]._children = list(children)

		for point, interventions in get_interventions(p_dict.values()).items():
			for intervention in interventions:
				for motion in intervention.introduced:
					get_motion_old_text(motion, "")

			p_dict[point].interventions = interventions

		return root


class InterventionTreeViewSet(MinutesViewSet):
	serializer_class = InterventionTreeSerializer


class MeetingViewSet(AgendaViewSet):
	serializer_class = MeetingSerializer
	permission_classes = (OrgManagerOrReadOnlyPermission,)

	def perform_create(self, serializer):
		org = Organisation.objects.get(slug=self.kwargs['organisation'])
		serializer.save(organisation=org)


class CurrentSpeakingRequestsView(ModelViewSet):
	serializer_class = PointSpeechOrderSerializer

	def get_queryset(self):
		return Point.objects.filter(seq__isnull=False,
			session__meeting__slug=self.kwargs['meeting'],
		).prefetch_related(Prefetch('intervention_set', to_attr="interventions",
			queryset=Intervention.objects.filter(motion=None).order_by(F('seq').asc(nulls_last=True), 'time_asked')))
