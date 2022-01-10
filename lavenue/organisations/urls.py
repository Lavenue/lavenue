from django.urls import include, path

from speakers.views import ParticipantViewSet

from .views import AgendaViewSet, MinutesViewSet, MeetingViewSet


urlpatterns = [
	path('', MeetingViewSet.as_view({'get': 'retrieve'})),
	path('agenda/', AgendaViewSet.as_view({'get': 'retrieve'})),
	path('minutes/', MinutesViewSet.as_view({'get': 'retrieve'})),
	path('participants/', include([
		path('', ParticipantViewSet.as_view({'get': 'list', 'post': 'create'})),
		path('<int:pk>/', ParticipantViewSet.as_view({'get': 'retrieve'})),
	])),
]
