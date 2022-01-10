from django.urls import re_path

from .consumers import SpeakerRequestConsumer


urlpatterns = [
	re_path(r'ws/(?P<organisation>[-\w]+)/(?P<meeting>[-\w]+)/order/$', SpeakerRequestConsumer.as_asgi()),
]
