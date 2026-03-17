from django.contrib import admin
from .models import Department, Subject, Teacher, LeaveApplication

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display  = ['name', 'code', 'department', 'is_elective']
    list_filter   = ['department', 'is_elective']
    search_fields = ['name', 'code']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display  = ['employee_id', 'full_name', 'department', 'qualification', 'joining_date', 'is_active']
    list_filter   = ['department', 'is_active', 'qualification']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']

@admin.register(LeaveApplication)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'leave_type', 'from_date', 'to_date', 'status']
    list_filter  = ['status', 'leave_type']
