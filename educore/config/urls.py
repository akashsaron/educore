from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenBlacklistView
)
from apps.core import report_views, analytics, exports

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/auth/login/',   TokenObtainPairView.as_view(),  name='token_obtain'),
    path('api/auth/refresh/', TokenRefreshView.as_view(),     name='token_refresh'),
    path('api/auth/logout/',  TokenBlacklistView.as_view(),   name='token_blacklist'),

    # App APIs
    path('api/core/',          include('apps.core.urls')),
    path('api/students/',      include('apps.students.urls')),
    path('api/teachers/',      include('apps.teachers.urls')),
    path('api/attendance/',    include('apps.attendance.urls')),
    path('api/fees/',          include('apps.fees.urls')),
    path('api/exams/',         include('apps.exams.urls')),
    path('api/library/',       include('apps.library.urls')),
    path('api/transport/',     include('apps.transport.urls')),
    path('api/announcements/', include('apps.announcements.urls')),

    # Analytics
    path('api/analytics/attendance/',    analytics.attendance_analytics,  name='analytics-attendance'),
    path('api/analytics/fees/',          analytics.fee_analytics,          name='analytics-fees'),
    path('api/analytics/exams/',         analytics.exam_analytics,         name='analytics-exams'),
    path('api/analytics/demographics/',  analytics.student_demographics,   name='analytics-demographics'),

    # Excel exports
    path('api/exports/students/',        exports.export_students,          name='export-students'),
    path('api/exports/attendance/',      exports.export_attendance,        name='export-attendance'),
    path('api/exports/fee-collection/',  exports.export_fee_collection,    name='export-fees'),
    path('api/exports/exam-results/',    exports.export_exam_results,      name='export-exams'),

    # PDF report downloads
    path('api/reports/fee-receipt/<int:payment_id>/',
         report_views.fee_receipt_pdf,       name='fee-receipt-pdf'),
    path('api/reports/result-card/<int:student_id>/<int:exam_id>/',
         report_views.result_card_pdf,       name='result-card-pdf'),
    path('api/reports/attendance/<int:section_id>/',
         report_views.attendance_report_pdf, name='attendance-pdf'),

    # SPA catch-all
    path('', include('apps.core.frontend_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
