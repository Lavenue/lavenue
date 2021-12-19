from django.contrib.auth import get_user_model
from rest_framework import serializers, relations

from motions.models import Motion
from organisations.models import Point

from .models import Intervention, Participant


class ParticipantSerializer(serializers.ModelSerializer):
	users = relations.SlugRelatedField(many=True, slug_field='email', queryset=get_user_model().objects.all())

	class Meta:
		model = Participant
		fields = '__all__'


class InterventionSerializer(serializers.ModelSerializer):
	participant = relations.PrimaryKeyRelatedField(queryset=Participant.objects.all())
	point = relations.PrimaryKeyRelatedField(queryset=Point.objects.all())
	motion = relations.PrimaryKeyRelatedField(queryset=Motion.objects.all())
	motions = relations.PrimaryKeyRelatedField(many=True, source='motion_set', queryset=Motion.objects.all())

	class Meta:
		model = Intervention
		fields = '__all__'
