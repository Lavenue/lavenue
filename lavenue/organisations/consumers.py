import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer, JsonWebsocketConsumer, WebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from speakers.models import Intervention
from speakers.serializers import InterventionWebsocketSerializer

from .models import Organisation, Point


class SpeakerRequestConsumer(JsonWebsocketConsumer):
	def connect(self):
		route_kwargs = self.scope['url_route']['kwargs']
		self.organisation = Organisation.objects.get(slug=route_kwargs['organisation'])
		self.meeting = self.organisation.meeting_set.get(slug=route_kwargs['meeting'])

		self.group_name = 'speakerlist_%s_%s' % (self.organisation.slug, self.meeting.slug)

		self.is_super = self.meeting.participant_set.filter(users=self.scope['user'], role='p').exists()

		# Join room group
		async_to_sync(self.channel_layer.group_add)(
			self.group_name,
			self.channel_name,
		)

		self.accept()

	def disconnect(self, close_code):
		# Leave room group
		async_to_sync(self.channel_layer.group_discard)(
			self.group_name,
			self.channel_name,
		)

	def receive_json(self, content, **kwargs):
		async_to_sync(self.channel_layer.group_send)(
			self.group_name,
			content,
		)

	def get_participant(self, pk):
		try:
			user_filter = Q()
			if not self.is_super:
				user_filter = Q(users=self.scope['user'])
			return self.meeting.participant_set.all().get(id=pk)
		except ObjectDoesNotExist:
			self.send_json(content={'error': 'Invalid participant'})

	def get_list(self, point_id, motion_id):
		point = None
		try:
			point = Point.objects.get(session__meeting=self.meeting, id=point_id)
		except ObjectDoesNotExist:
			self.send_json(content={'error': 'Invalid point'})

		motion = None
		if not (motion_id is None or point is None):
			try:
				motion = point.motion_set.get(id=motion_id)
			except ObjectDoesNotExist:
				self.send_json(content={'error': 'Invalid motion'})
				point = None

		return point, None

	def add_participant(self, event):
		participant = self.get_participant(event['participant'])
		if participant is None:
			return

		point, motion = self.get_list(event['point'], event['motion'])
		if point is None:
			return

		intervention, new = Intervention.objects.get_or_create(participant=participant, point=point, motion=motion, seq=None,
			defaults={'time_asked': timezone.now()})

		self.send_json(content={
			'action': 'add_to_list',
			'intervention': InterventionWebsocketSerializer(intervention).data
		})

	def remove_participant(self, event):
		participant = self.get_participant(event['participant'])
		if participant is None:
			return

		point, motion = self.get_list(event['point'], event['motion'])
		if point is None:
			return

		Intervention.objects.filter(seq=None, participant=participant, point=point, motion=motion).delete()

		self.send_json(content={
			'action': 'remove_from_list',
			'intervention': {
				'point': point.pk,
				'motion': getattr(motion, 'pk'),
				'participant': participant.pk,
			},
		})

	def reset_list(self, event):
		if not self.is_super:
			return

		point, motion = self.get_list(event['point'], event['motion'])
		if point is None:
			return

		Intervention.objects.filter(seq=None, point=point, motion=motion).delete()

		self.send_json(content={
			'action': 'clear_list',
			'point': point.pk,
			'motion': getattr(motion, 'pk'),
		})

	def give_floor(self, event):
		if not self.is_super:
			return

		participant = self.get_participant(event['participant'])
		if participant is None:
			return

		point, motion = self.get_list(event['point'], event['motion'])
		if point is None:
			return

		try:
			intervention = Intervention.objects.filter(seq=None, point=point, motion=motion, participant=participant).get()
		except Intervention.MultipleObjectsReturned:
			self.send_json(content={'error': 'Multiple same interventions'})
			return

		seq = Intervention.objects.filter(point=point, motion=motion).aggregate(
			s=Coalesce(Max('seq', default=0), 0) + 1)['s']
		Intervention.objects.filter(id=intervention.pk).update(seq=seq, time_granted=timezone.now())

		self.send_json(content={
			'action': 'give_floor',
			'intervention': InterventionWebsocketSerializer(intervention).data
		})

	def start_timer(self, event):
		if not self.is_super:
			return

		self.send_json(content={
			'action': 'start_timer',
			'length': event['length'],
		})

	def stop_timer(self, event):
		if not self.is_super:
			return

		self.send_json(content={
			'action': 'stop_timer',
		})
