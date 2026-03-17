from django.contrib import admin
from .models import AttendanceRecord, AttendanceSession, HolidayCalendar

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display  = ['student', 'date', 'status', 'marked_by']
    list_filter   = ['status', 'date', 'student__section__grade']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_no']
    date_hierarchy = 'date'

@admin.register(HolidayCalendar)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['date', 'name', 'holiday_type', 'academic_year']
    list_filter  = ['holiday_type', 'academic_year']
