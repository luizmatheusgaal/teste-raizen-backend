from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'venues', views.VenueViewSet)
router.register(r'events', views.EventViewSet)

urlpatterns = router.urls
