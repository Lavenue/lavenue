from rest_framework import serializers

from motions.models import Motion, Vote
from speakers.models import Intervention

from .models import Meeting, Organisation, Point, Session


class OrganisationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Organisation
		exclude = ('active',)


class ReportSerializer(serializers.ModelSerializer):

	class Meta:
		model = Meeting


class VoteSerializer(serializers.ModelSerializer):
	class Meta:
		model = Vote
		fields = '__all__'


class MotionSerializer(serializers.ModelSerializer):

	votes = VoteSerializer(many=True, source='vote_set')
	order = serializers.IntegerField()
	old_text = serializers.CharField()

	class Meta:
		model = Motion
		exclude = ('proposer', 'supplants', 'introduced',)

	def get_fields(self):
		fields = super().get_fields()
		fields['interventions'] = SpeechSerializer(many=True)
		return fields


class SpeechSerializer(serializers.ModelSerializer):
	class Meta:
		model = Intervention
		exclude = ('point', 'motion', 'time_asked', 'time_granted')

	def get_fields(self):
		fields = super().get_fields()
		fields['introduced'] = MotionSerializer(many=True)
		return fields


class BasePointSerializer(serializers.ModelSerializer):

	continued = serializers.BooleanField(required=False)

	class Meta:
		model = Point
		exclude = ('parent', 'session')

	def get_fields(self):
		fields = super().get_fields()
		fields['subpoints'] = type(self)(many=True)
		return fields

	def create(self, validated_data):
		subpoints = validated_data.pop('subpoints')
		point = super().create(validated_data)

		if len(subpoints) > 0:
			subpoint_serializer = type(self)(many=True)
			subpoint_serializer._validated_data = subpoints
			subpoint_serializer.save(parent=point, session=validated_data['session'])

		return point


class MeetingSerializer(serializers.ModelSerializer):

	class SessionSerializer(serializers.ModelSerializer):
		points = BasePointSerializer(many=True)

		class Meta:
			model = Session
			exclude = ('meeting',)

		def create(self, validated_data):
			points = validated_data.pop('points')

			session = super().create(validated_data)

			point_serializer = BasePointSerializer(many=True)
			point_serializer._validated_data = points
			point_serializer.save(session=session)

			return session

	sessions = SessionSerializer(many=True)

	class Meta:
		model = Meeting
		exclude = ('organisation',)

	def create(self, validated_data):
		sessions = validated_data.pop('sessions')
		meeting = super().create(validated_data)

		session_serializer = self.SessionSerializer(many=True)
		session_serializer._validated_data = sessions
		session_serializer.save(meeting=meeting)

		return meeting


class AgendaSerializer(serializers.ModelSerializer):

	class SessionSerializer(serializers.ModelSerializer):

		class Meta:
			model = Session
			fields = '__all__'

		def get_fields(self):
			fields = super().get_fields()
			fields['points'] = BasePointSerializer(many=True)
			return fields

	class Meta:
		model = Meeting
		fields = '__all__'

	def get_fields(self):
		fields = super().get_fields()
		fields['sessions'] = self.SessionSerializer(many=True)
		return fields


class MinutesSerializer(serializers.ModelSerializer):

	start_time = serializers.DateTimeField()

	class PointSerializer(BasePointSerializer):

		def get_fields(self):
			fields = super().get_fields()
			fields['interventions'] = SpeechSerializer(many=True)
			return fields

	class Meta:
		model = Meeting
		fields = '__all__'

	def get_fields(self):
		fields = super().get_fields()
		fields['points'] = self.PointSerializer(many=True)
		return fields
