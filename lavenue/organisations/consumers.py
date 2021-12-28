from channels.generic.websocket import JsonWebsocketConsumer


class SpeakerRequestConsumer(JsonWebsocketConsumer):
	def connect(self):
		route_kwargs = self.scope['url_route']['kwargs']
		self.organisation = Organisation.objects.get(slug=route_kwargs['organisation'])
		self.meeting = self.organisation.meeting_set.get(slug=route_kwargs['meeting'])

		self.group_name = 'speakerlist_%s_%s' % (self.organisation.slug, self.meeting.slug)

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
			{
				'type': 'chat_message',
				'message': content
			}
		)

	# Receive message from room group
	def chat_message(self, event):
		message = event['message']

		# Send message to WebSocket
		self.send_json(content={
			'message': message,
		})
