from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'ticket-types', views.TicketTypeViewSet)
router.register(r'tickets', views.TicketViewSet)

urlpatterns = router.urls
