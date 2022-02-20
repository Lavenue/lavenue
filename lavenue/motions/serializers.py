from rest_framework import serializers, relations

from organisations.models import Meeting
from organisations.serializers import BasePointSerializer
from speakers.models import Intervention, Participant

from .models import Motion, Vote


class VoteSerializer(serializers.ModelSerializer):
	class Meta:
		model = Vote
		fields = '__all__'


class MotionSerializer(serializers.ModelSerializer):
	proposer = relations.PrimaryKeyRelatedField(queryset=Participant.objects.all())
	introduced = relations.PrimaryKeyRelatedField(queryset=Intervention.objects.all())
	sponsors = relations.PrimaryKeyRelatedField(many=True, queryset=Participant.objects.all())

	class Meta:
		model = Motion
		exclude = ('point', 'supplants',)

	def get_fields(self):
		fields = super().get_fields()
		fields['submotions'] = MotionSerializer(many=True, read_only=True)
		return fields


class EditMotionSerializer(serializers.ModelSerializer):
	introduced = relations.PrimaryKeyRelatedField(queryset=Intervention.objects.all())
	sponsors = relations.PrimaryKeyRelatedField(many=True, queryset=Participant.objects.all())

	class Meta:
		model = Motion
		exclude = ('point', 'supplants',)

	def create(self, validated_data):
		validated_data['point'] = validated_data['introduced'].point
		validated_data['proposer'] = validated_data['introduced'].participant

		return super().create(validated_data)


class ApprovedMotionsSerializer(serializers.ModelSerializer):

	class PointSerializer(BasePointSerializer):

		class MotionSerializer(serializers.ModelSerializer):
			votes = VoteSerializer(many=True, source='vote_set')
			full_num = serializers.CharField()
			adopted_text = serializers.CharField()

			class Meta:
				model = Motion
				exclude = ('point', 'supplants', 'proposer', 'sponsors', 'introduced')

		def get_fields(self):
			fields = super().get_fields()
			fields['motions'] = self.MotionSerializer(many=True)
			return fields

	class Meta:
		model = Meeting
		fields = '__all__'

	def get_fields(self):
		fields = super().get_fields()
		fields['points'] = self.PointSerializer(many=True)
		return fields
