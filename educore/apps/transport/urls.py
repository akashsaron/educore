from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, DriverViewSet, RouteViewSet, RouteStopViewSet, StudentRouteViewSet

router = DefaultRouter()
router.register('vehicles',       VehicleViewSet)
router.register('drivers',        DriverViewSet)
router.register('stops',          RouteStopViewSet)
router.register('student-routes', StudentRouteViewSet)
router.register('',               RouteViewSet, basename='route')

urlpatterns = [path('', include(router.urls))]
