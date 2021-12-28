from django.urls import re_path

from organisations.consumers import SpeakerRequestConsumer


websocket_urlpatterns = [
	re_path(r'ws/(?P<organisation>\w+)/(?P<meeting>\w+)/order/$', SpeakerRequestConsumer.as_asgi()),
]
