from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookCategoryViewSet, BookViewSet, BookIssueViewSet

router = DefaultRouter()
router.register('categories', BookCategoryViewSet)
router.register('issues',     BookIssueViewSet)
router.register('',           BookViewSet, basename='book')

urlpatterns = [path('', include(router.urls))]
