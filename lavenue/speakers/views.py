from rest_framework.viewsets import ModelViewSet

from organisations.models import Meeting

from .models import Participant
from .serializers import ParticipantSerializer


class ParticipantViewSet(ModelViewSet):
	serializer_class = ParticipantSerializer

	def get_queryset(self):
		return Participant.objects.filter(
			meeting__slug=self.kwargs['meeting'],
			meeting__organisation__slug=self.kwargs['organisation']).prefetch_related('users')

	def perform_create(self, serializer):
		meeting = Meeting.objects.get(organisation__slug=self.kwargs['organisation'], slug=self.kwargs['meeting'])
		serializer.save(meeting=meeting)
