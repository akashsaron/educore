from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceRecordViewSet, HolidayCalendarViewSet

router = DefaultRouter()
router.register('holidays', HolidayCalendarViewSet)
router.register('',         AttendanceRecordViewSet, basename='attendance')

urlpatterns = [path('', include(router.urls))]
