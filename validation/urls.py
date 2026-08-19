from django.urls import path

from . import views

urlpatterns = [
    path('validate/', views.validate_ticket, name='validate-ticket'),
]
