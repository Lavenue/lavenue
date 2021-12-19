from rest_framework.viewsets import ModelViewSet

from .models import Participant
from .serializers import ParticipantSerializer


class ParticipantViewSet(ModelViewSet):
	serializer_class = ParticipantSerializer
	lookup_field = 'slug'
	lookup_url_kwarg = 'meeting'

	def get_queryset(self):
		return Participant.objects.filter(meeting__organisation__slug=self.kwargs['organisation']).prefetch_related('users')
