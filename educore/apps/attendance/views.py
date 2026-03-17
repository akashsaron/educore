from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone

from .models import AttendanceRecord, AttendanceSession, HolidayCalendar
from .serializers import (AttendanceRecordSerializer, BulkAttendanceSerializer,
                           AttendanceSessionSerializer, HolidayCalendarSerializer)
from apps.students.models import Student


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.select_related(
        'student', 'student__section', 'marked_by'
    ).all()
    serializer_class   = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['student', 'date', 'status', 'student__section']
    ordering_fields    = ['date']

    @action(detail=False, methods=['post'])
    def bulk_mark(self, request):
        """Mark attendance for an entire section in one API call."""
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        section_id = serializer.validated_data['section_id']
        date       = serializer.validated_data['date']
        records    = serializer.validated_data['records']

        created, updated = 0, 0
        for rec in records:
            obj, is_new = AttendanceRecord.objects.update_or_create(
                student_id=rec['student_id'],
                date=date,
                defaults={
                    'status':    rec.get('status', 'present'),
                    'remarks':   rec.get('remarks', ''),
                    'marked_by': request.user,
                }
            )
            if is_new: created += 1
            else:      updated += 1

        # Mark session as finalized
        AttendanceSession.objects.update_or_create(
            section_id=section_id, date=date,
            defaults={'marked_by': request.user, 'is_finalized': True}
        )

        return Response({'created': created, 'updated': updated, 'date': str(date)})

    @action(detail=False, methods=['get'])
    def section_report(self, request):
        """Attendance summary for a section over a date range."""
        section_id = request.query_params.get('section')
        from_date  = request.query_params.get('from_date', str(timezone.localdate()))
        to_date    = request.query_params.get('to_date',   str(timezone.localdate()))

        students = Student.objects.filter(section_id=section_id, is_active=True)
        data = []
        for s in students:
            records = AttendanceRecord.objects.filter(
                student=s, date__range=[from_date, to_date]
            )
            total   = records.count()
            present = records.filter(status__in=['present','late']).count()
            data.append({
                'student_id':   s.id,
                'student_name': s.full_name,
                'admission_no': s.admission_no,
                'total_days':   total,
                'present':      present,
                'absent':       total - present,
                'percentage':   round(present/total*100, 1) if total else 0,
            })
        return Response(data)

    @action(detail=False, methods=['get'])
    def today_summary(self, request):
        today   = timezone.localdate()
        records = AttendanceRecord.objects.filter(date=today)
        return Response({
            'date':    str(today),
            'present': records.filter(status='present').count(),
            'absent':  records.filter(status='absent').count(),
            'late':    records.filter(status='late').count(),
            'total':   records.count(),
        })


class HolidayCalendarViewSet(viewsets.ModelViewSet):
    queryset           = HolidayCalendar.objects.all()
    serializer_class   = HolidayCalendarSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['academic_year', 'holiday_type']
