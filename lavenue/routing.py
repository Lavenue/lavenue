from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from django.contrib.auth.models import AnonymousUser
from django.core.asgi import get_asgi_application
from django.db import close_old_connections
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from organisations.consumers import SpeakerRequestConsumer


class TokenAuthMiddleware:

	def __init__(self, inner):
		self.inner = inner

	def __call__(self, scope):
		close_old_connections()

		headers = dict(scope['headers'])
		auth = JSONWebTokenAuthentication()
		if b'Authorization' in headers:
			try:
				token = auth.get_token_from_authorization_header(
					headers[b'Authorization'].decode())
				payload = auth.jwt_decode_token(token)
				scope['user'] = self.authenticate_credentials(payload)
			except:  # noqa: E722
				scope['user'] = AnonymousUser()
		return self.inner(scope)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))  # noqa: E731


application = ProtocolTypeRouter({

	"http": get_asgi_application(),

	# WebSocket handlers
	"websocket": TokenAuthMiddlewareStack(
		URLRouter([
			re_path(r'ws/(?P<organisation>[-\w]+)/(?P<meeting>[-\w]+)/order/$', SpeakerRequestConsumer.as_asgi()),
		]),
	),

	# Worker handlers (which don't need a URL/protocol)
	# "channel": ChannelNameRouter({}),
})
