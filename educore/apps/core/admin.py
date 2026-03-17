from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AcademicYear, SchoolProfile, Grade, Section


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'get_full_name', 'email', 'role', 'is_active']
    list_filter   = ['role', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    fieldsets     = UserAdmin.fieldsets + (
        ('EduCore', {'fields': ('role', 'phone', 'avatar')}),
    )

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current']

@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'board', 'principal_name', 'city']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'numeric_grade', 'order']

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display  = ['__str__', 'grade', 'name', 'class_teacher', 'capacity']
    list_filter   = ['grade']
