import debug_toolbar
from django.contrib import admin
from django.urls import include, path

from organisations.views import MeetingViewSet


urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),

    path('accounts/', include('users.urls')),

    path('<slug:organisation>/', MeetingViewSet.as_view({'post': 'create'})),
    path('<slug:organisation>/<slug:meeting>/', include('organisations.urls')),
]
