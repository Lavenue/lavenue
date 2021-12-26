import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from organisations.views import MeetingViewSet, OrganisationViewSet


urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),

    path('accounts/', include('users.urls')),

    path('organisations/', include([
        path('', OrganisationViewSet.as_view({'get': 'list', 'post': 'create'})),
        path('<slug:organisation>/', include([
            path('', OrganisationViewSet.as_view({'get': 'retrieve'})),
            path('meetings/', include([
                path('', MeetingViewSet.as_view({'get': 'list', 'post': 'create'})),
                path('<slug:meeting>/', include('organisations.urls')),
            ])),
        ])),
    ])),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
