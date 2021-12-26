from django.urls import path

from speakers.views import ParticipantViewSet

from .views import AgendaViewSet, MinutesViewSet, MeetingViewSet


urlpatterns = [
	path('', MeetingViewSet.as_view({'get': 'retrieve'})),
	path('agenda/', AgendaViewSet.as_view({'get': 'retrieve'})),
	path('minutes/', MinutesViewSet.as_view({'get': 'retrieve'})),
	path('participants/', ParticipantViewSet.as_view({'get': 'list'})),
]
