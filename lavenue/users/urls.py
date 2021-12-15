from django.urls import include, path
from rest_framework_simplejwt.views import  TokenObtainPairView, TokenRefreshView, TokenVerifyView


urlpatterns = [
    path('token/', include([
        path('', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),
]
