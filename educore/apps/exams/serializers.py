from rest_framework import serializers
from .models import Exam, ExamSchedule, ExamResult, TimetableSlot


class ExamScheduleSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    grade_name   = serializers.CharField(source='grade.name',   read_only=True)

    class Meta:
        model  = ExamSchedule
        fields = '__all__'


class ExamSerializer(serializers.ModelSerializer):
    schedules = ExamScheduleSerializer(many=True, read_only=True)

    class Meta:
        model  = Exam
        fields = '__all__'


class ExamResultSerializer(serializers.ModelSerializer):
    student_name   = serializers.CharField(source='student.full_name',   read_only=True)
    subject_name   = serializers.CharField(source='schedule.subject.name', read_only=True)
    admission_no   = serializers.CharField(source='student.admission_no', read_only=True)
    max_marks      = serializers.IntegerField(source='schedule.max_marks', read_only=True)
    percentage     = serializers.SerializerMethodField()

    class Meta:
        model  = ExamResult
        fields = '__all__'

    def get_percentage(self, obj):
        if obj.schedule.max_marks:
            return round(float(obj.marks_obtained) / obj.schedule.max_marks * 100, 1)
        return 0


class TimetableSlotSerializer(serializers.ModelSerializer):
    subject_name  = serializers.CharField(source='subject.name',            read_only=True)
    teacher_name  = serializers.CharField(source='teacher.full_name',       read_only=True)
    section_name  = serializers.CharField(source='section.display_name',    read_only=True)
    day_name      = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model  = TimetableSlot
        fields = '__all__'
