from rest_framework.viewsets import ModelViewSet

from organisations.models import Meeting

from .models import Intervention, Participant
from .serializers import InterventionSerializer, ParticipantSerializer


class ParticipantViewSet(ModelViewSet):
	serializer_class = ParticipantSerializer

	def get_queryset(self):
		return Participant.objects.filter(
			meeting__slug=self.kwargs['meeting'],
			meeting__organisation__slug=self.kwargs['organisation']).prefetch_related('users')

	def perform_create(self, serializer):
		meeting = Meeting.objects.get(organisation__slug=self.kwargs['organisation'], slug=self.kwargs['meeting'])
		serializer.save(meeting=meeting)


class InterventionViewSet(ModelViewSet):
	serializer_class = InterventionSerializer

	def get_queryset(self):
		return Intervention.objects.filter(point__session__meeting__slug=self.kwargs['meeting'],
			point__session__meeting__organisation__slug=self.kwargs['organisation'])
