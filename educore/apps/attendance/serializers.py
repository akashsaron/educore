from rest_framework import serializers
from .models import AttendanceRecord, AttendanceSession, HolidayCalendar


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name  = serializers.CharField(source='student.full_name', read_only=True)
    section_name  = serializers.CharField(source='student.section.display_name', read_only=True)

    class Meta:
        model  = AttendanceRecord
        fields = '__all__'


class BulkAttendanceSerializer(serializers.Serializer):
    """POST /api/attendance/bulk/ — mark entire section at once."""
    section_id = serializers.IntegerField()
    date       = serializers.DateField()
    records    = serializers.ListField(child=serializers.DictField())
    # records: [{"student_id": 1, "status": "present", "remarks": ""}]


class AttendanceSessionSerializer(serializers.ModelSerializer):
    section_name = serializers.CharField(source='section.display_name', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.get_full_name', read_only=True)

    class Meta:
        model  = AttendanceSession
        fields = '__all__'


class HolidayCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model  = HolidayCalendar
        fields = '__all__'
