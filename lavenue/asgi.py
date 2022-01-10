"""
ASGI config for lavenue project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from jwt import decode as jwt_decode
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from organisations.routing import urlpatterns


@database_sync_to_async
def get_user(pk):
	from django.contrib.auth import get_user_model
	from django.contrib.auth.models import AnonymousUser
	user = None
	try:
		user = get_user_model().objects.get(id=pk)
	except Exception as e:
		pass
	return user or AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):

	async def __call__(self, scope, receive, send):
		from django.conf import settings
		scope = dict(scope)
		scope["query_params"] = parse_qs(scope["query_string"].decode())
		raw_token = scope['query_params'].get('token', [None])[0]

		# Try to authenticate the user
		try:
			UntypedToken(raw_token)
		except (InvalidToken, TokenError) as e:
			scope['user'] = AnonymousUser()
		else:
			#  Then token is valid, decode it
			decoded_data = jwt_decode(raw_token, settings.SECRET_KEY, algorithms=["HS256"])
			print(decoded_data)

			scope['user'] = await get_user(decoded_data['user_id'])

		return await self.inner(scope, receive, send)



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')


application = ProtocolTypeRouter({
	"http": get_asgi_application(),
	"websocket": TokenAuthMiddleware(URLRouter(urlpatterns)),
})
