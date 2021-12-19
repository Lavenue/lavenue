from rest_framework import serializers, relations

from speakers.models import Participant

from .models import Motion


class MotionSerializer(serializers.ModelSerializer):
	proposer = relations.PrimaryKeyRelatedField(queryset=Participant.objects.all())
	sponsors = relations.PrimaryKeyRelatedField(many=True, queryset=Participant.objects.all())

	class Meta:
		model = Motion
		exclude = ('point', 'supplants',)

	def get_fields(self):
		fields = super().get_fields()
		fields['submotions'] = MotionSerializer(many=True)
		return fields
