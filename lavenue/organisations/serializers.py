from django.contrib.auth import get_user_model
from rest_framework import serializers

from motions.models import Motion, Vote
from speakers.models import Intervention, Participant
from speakers.serializers import InterventionWebsocketSerializer

from .models import Meeting, Membership, MembershipInvitation, Organisation, Point, Session


class OrganisationSerializer(serializers.ModelSerializer):
	managers = serializers.EmailField(write_only=True, required=False)
	members = serializers.EmailField(write_only=True, required=False)

	class Meta:
		model = Organisation
		exclude = ('active',)

	def create(self, validated_data):
		User = get_user_model()
		managers = validated_data.pop('managers', [])
		members = validated_data.pop('members', [])

		org = super().create(validated_data)

		Membership.objects.create(organisation=org, user=self.context['request'].user, role=Membership.ROLE_MANAGER)

		for role, emails in ((Membership.ROLE_MANAGER, managers), (Membership.ROLE_MEMBER, members)):
			users = User.objects.filter(email__in=emails)
			Membership.objects.bulk_create([
				Membership(organisation=org, user=user, role=role)
				for user in users
			])
			MembershipInvitation.objects.bulk_create([
				MembershipInvitation(organisation=org, email=email, role=role)
				for email in set(emails) - set([u.email for u in users])
			])

		return org


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

		p = Participant.objects.create(meeting=meeting, name=self.context['request'].user.username,
			role=Participant.ROLE_PRESIDENT, voting=0, speaking=True)
		p.users.set([self.context['request'].user])

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

		def save(self, **kwargs):
			points = kwargs.pop('points')
			session = super().save(**kwargs)

			session.point_set.update(seq=None)
			point_serializer = BasePointSerializer(many=True, context=self.context)
			point_serializer._validated_data = points
			point_serializer.save(session=session)

			session.point_set.filter(seq=None).delete()

			return session

	class Meta:
		model = Meeting
		fields = '__all__'

	def get_fields(self):
		fields = super().get_fields()
		fields['sessions'] = self.SessionSerializer(many=True)
		return fields

	def update(self, instance, validated_data):
		sessions = validated_data.pop('sessions')
		if sessions is not None and self.partial:
			instance.point_set.update(seq=None)
			session_serializer = self.SessionSerializer(many=True, context=self.context)
			session_serializer._validated_data = sessions
			session_serializer.save(meeting=instance)

		return super().update(instance, validated_data)

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


class TreeMotionSerializer(serializers.ModelSerializer):
	votes = VoteSerializer(many=True, source='vote_set')
	order = serializers.IntegerField()
	old_text = serializers.CharField()

	class Meta:
		model = Motion
		exclude = ('proposer', 'supplants', 'introduced', 'preamble')

	def get_fields(self):
		fields = super().get_fields()
		fields['interventions'] = TreeSpeechSerializer(many=True)
		return fields


class TreeSpeechSerializer(serializers.ModelSerializer):
	class Meta:
		model = Intervention
		exclude = ('point', 'motion', 'time_asked', 'time_granted', 'summary')

	def get_fields(self):
		fields = super().get_fields()
		fields['introduced'] = TreeMotionSerializer(many=True)
		return fields


class InterventionTreeSerializer(MinutesSerializer):

	class PointSerializer(BasePointSerializer):
		def get_fields(self):
			fields = super().get_fields()
			fields['interventions'] = TreeSpeechSerializer(many=True)
			return fields


class PointSpeechOrderSerializer(serializers.ModelSerializer):

	class Meta:
		model = Point
		fields = '__all__'

	def get_fields(self):
		fields = super().get_fields()
		fields['interventions'] = InterventionWebsocketSerializer(many=True)
		return fields
