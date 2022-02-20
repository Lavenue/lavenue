from django.urls import include, path

from motions.views import AdoptedMotionsViewSet, EditMotionViewSet
from speakers.views import InterventionViewSet, ParticipantViewSet

from .views import AgendaViewSet, CurrentSpeakingRequestsView, InterventionTreeViewSet, MinutesViewSet, MeetingViewSet


list_methods = {'get': 'list', 'post': 'create'}
detail_methods = {'get': 'retrieve', 'post': 'update', 'patch': 'partial_update', 'delete': 'destroy'}


urlpatterns = [
	path('', MeetingViewSet.as_view({'get': 'retrieve'})),
	path('agenda/', AgendaViewSet.as_view(detail_methods)),
	path('minutes/', MinutesViewSet.as_view({'get': 'retrieve'})),
	path('tree/', InterventionTreeViewSet.as_view({'get': 'retrieve'})),
	path('participants/', include([
		path('', ParticipantViewSet.as_view(list_methods)),
		path('<int:pk>/', ParticipantViewSet.as_view(detail_methods)),
	])),
	path('motions/', include([
		path('', AdoptedMotionsViewSet.as_view({'get': 'retrieve'})),
		path('', EditMotionViewSet.as_view({'post': 'create'})),
		path('<int:pk>/', EditMotionViewSet.as_view(detail_methods)),
	])),
	path('interventions/<int:pk>/', InterventionViewSet.as_view(detail_methods)),
	path('points/', include([
		path('', CurrentSpeakingRequestsView.as_view({'get': 'list'})),
		path('<int:pk>/', CurrentSpeakingRequestsView.as_view({'get': 'retrieve'})),
	]))
]
