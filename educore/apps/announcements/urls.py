from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnnouncementViewSet, NoticeBoardViewSet, EventViewSet

router = DefaultRouter()
router.register('notices', NoticeBoardViewSet)
router.register('events',  EventViewSet)
router.register('',        AnnouncementViewSet, basename='announcement')

urlpatterns = [path('', include(router.urls))]
