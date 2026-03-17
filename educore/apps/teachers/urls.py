from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, SubjectViewSet, TeacherViewSet, LeaveApplicationViewSet

router = DefaultRouter()
router.register('departments', DepartmentViewSet)
router.register('subjects',    SubjectViewSet)
router.register('leaves',      LeaveApplicationViewSet)
router.register('',            TeacherViewSet, basename='teacher')

urlpatterns = [path('', include(router.urls))]
