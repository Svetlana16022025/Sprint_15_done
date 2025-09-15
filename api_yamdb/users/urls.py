from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, AuthViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

auth_viewset = AuthViewSet.as_view({
    'post': 'signup'
})

token_viewset = AuthViewSet.as_view({
    'post': 'token'
})

urlpatterns = [
    path('v1/auth/signup/', auth_viewset, name='signup'),
    path('v1/auth/token/', token_viewset, name='token'),
    path('v1/', include(router.urls)),
]
