"""URL configuration for Verzel Events backend."""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
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
