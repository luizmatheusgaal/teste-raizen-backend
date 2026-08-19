"""URL configuration for Verzel Events backend."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('health/', include('core.urls')),
        path('users/', include('users.urls')),
        path('', include('events.urls')),
        path('', include('tickets.urls')),
    ])),
]
