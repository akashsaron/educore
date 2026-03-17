# ── serializers.py ────────────────────────────────────────────────────────────
from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    full_name     = serializers.CharField(read_only=True)
    current_class = serializers.CharField(read_only=True)
    section_name  = serializers.CharField(source='section.display_name', read_only=True)
    grade_name    = serializers.CharField(source='section.grade.name', read_only=True)

    class Meta:
        model  = Student
        fields = '__all__'


class StudentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    full_name     = serializers.CharField(read_only=True)
    section_name  = serializers.CharField(source='section.display_name', read_only=True)

    class Meta:
        model  = Student
        fields = ['id','admission_no','first_name','last_name','full_name',
                  'section_name','parent_phone','parent_email','is_active',
                  'photo','admission_date']
