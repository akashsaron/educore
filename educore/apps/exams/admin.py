from django.contrib import admin
from .models import Exam, ExamSchedule, ExamResult, TimetableSlot

class ExamScheduleInline(admin.TabularInline):
    model = ExamSchedule
    extra = 0

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display  = ['name', 'exam_type', 'academic_year', 'start_date', 'end_date', 'status']
    list_filter   = ['exam_type', 'status', 'academic_year']
    inlines       = [ExamScheduleInline]

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display  = ['student', 'schedule', 'marks_obtained', 'grade', 'is_absent']
    list_filter   = ['grade', 'schedule__exam']
    search_fields = ['student__first_name', 'student__admission_no']

@admin.register(TimetableSlot)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['section', 'day_of_week', 'period_number', 'subject', 'teacher', 'start_time']
    list_filter  = ['section__grade', 'day_of_week', 'academic_year']
