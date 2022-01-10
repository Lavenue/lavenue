from itertools import groupby

from rest_framework.viewsets import ModelViewSet

from organisations.models import Meeting, Point
from organisations.tree import get_interventions, get_motion_adopted_text, get_point_full_num, get_point_motions_full_num

from .serializers import ApprovedMotionsSerializer


class AdoptedMotionsViewSet(ModelViewSet):
	serializer_class = ApprovedMotionsSerializer
	lookup_field = 'slug'
	lookup_url_kwarg = 'meeting'

	def get_queryset(self):
		return Meeting.objects.filter(organisation__slug=self.kwargs['organisation']).select_related('organisation').prefetch_related('session_set')

	def get_object(self):
		m = super().get_object()
		m._points = self.get_points()
		return m

	def get_points(self):
		points = Point.objects.filter(session__meeting__slug=self.kwargs['meeting'],
			session__meeting__organisation__slug=self.kwargs['organisation']).order_by('parent', 'seq')
		p_dict = {p.id: p for p in points}
		for p in points:
			p._children = []
			p.motions = []

		root = []
		for parent, children in groupby(points, key=lambda i: i.parent_id):
			if parent is None:
				root = list(children)
				continue
			p_dict[parent]._children = list(children)

		for p in root:
			get_point_full_num(p)

		for point, interventions in get_interventions(p_dict.values()).items():
			p_dict[point].interventions = interventions
			p_dict[point].motions = get_point_motions_full_num(p_dict[point])
			for motion in p_dict[point].motions:
				get_motion_adopted_text(motion)

		return root
