from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, ExamScheduleViewSet, ExamResultViewSet, TimetableSlotViewSet

router = DefaultRouter()
router.register('schedules',  ExamScheduleViewSet)
router.register('results',    ExamResultViewSet)
router.register('timetable',  TimetableSlotViewSet)
router.register('',           ExamViewSet, basename='exam')

urlpatterns = [path('', include(router.urls))]
