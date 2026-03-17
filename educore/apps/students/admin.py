from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display   = ['admission_no', 'full_name', 'section', 'gender', 'parent_phone', 'is_active']
    list_filter    = ['section__grade', 'gender', 'is_active', 'academic_year']
    search_fields  = ['first_name', 'last_name', 'admission_no', 'parent_phone', 'parent_email']
    ordering       = ['section', 'roll_number']
    readonly_fields= ['created_at', 'updated_at']
    list_per_page  = 50
