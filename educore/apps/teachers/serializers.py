from rest_framework import serializers
from apps.core.serializers import UserSerializer
from .models import Department, Subject, Teacher, LeaveApplication


class DepartmentSerializer(serializers.ModelSerializer):
    teacher_count = serializers.SerializerMethodField()

    class Meta:
        model  = Department
        fields = '__all__'

    def get_teacher_count(self, obj):
        return obj.teachers.filter(is_active=True).count()


class SubjectSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model  = Subject
        fields = '__all__'


class TeacherSerializer(serializers.ModelSerializer):
    full_name       = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    subject_names   = serializers.SerializerMethodField()
    email           = serializers.EmailField(source='user.email', read_only=True)
    user_detail     = UserSerializer(source='user', read_only=True)

    class Meta:
        model  = Teacher
        fields = '__all__'

    def get_subject_names(self, obj):
        return [s.name for s in obj.subjects.all()]


class TeacherListSerializer(serializers.ModelSerializer):
    full_name       = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    subject_names   = serializers.SerializerMethodField()
    email           = serializers.EmailField(source='user.email', read_only=True)
    is_active       = serializers.BooleanField(source='user.is_active', read_only=True)

    class Meta:
        model  = Teacher
        fields = ['id','employee_id','full_name','department_name',
                  'subject_names','qualification','experience_years',
                  'joining_date','phone','email','is_active']

    def get_subject_names(self, obj):
        return [s.name for s in obj.subjects.all()]


class LeaveApplicationSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)

    class Meta:
        model  = LeaveApplication
        fields = '__all__'
