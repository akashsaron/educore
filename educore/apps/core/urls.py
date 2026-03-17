from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('users',    views.UserViewSet)
router.register('years',    views.AcademicYearViewSet)
router.register('school',   views.SchoolProfileViewSet)
router.register('grades',   views.GradeViewSet)
router.register('sections', views.SectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.dashboard_stats, name='dashboard-stats'),
    path('me/',        views.me,              name='me'),
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='login'),
]
