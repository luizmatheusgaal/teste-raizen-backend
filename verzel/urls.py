"""URL configuration for Verzel Events backend."""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('', core_views.api_root, name='api-root'),
        path('health/', include('core.urls')),
        path('users/', include('users.urls')),
        path('', include('events.urls')),
        path('', include('tickets.urls')),
        path('', include('orders.urls')),
        path('', include('validation.urls')),
    ])),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
