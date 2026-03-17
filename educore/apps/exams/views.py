from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Max, Min, Count

from .models import Exam, ExamSchedule, ExamResult, TimetableSlot
from .serializers import (ExamSerializer, ExamScheduleSerializer,
                           ExamResultSerializer, TimetableSlotSerializer)


class ExamViewSet(viewsets.ModelViewSet):
    queryset           = Exam.objects.prefetch_related('schedules', 'grades').all()
    serializer_class   = ExamSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['academic_year', 'exam_type', 'status']
    search_fields      = ['name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ExamScheduleViewSet(viewsets.ModelViewSet):
    queryset           = ExamSchedule.objects.select_related('exam', 'subject', 'grade').all()
    serializer_class   = ExamScheduleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['exam', 'subject', 'grade', 'date']


class ExamResultViewSet(viewsets.ModelViewSet):
    queryset = ExamResult.objects.select_related(
        'student', 'schedule__subject', 'schedule__exam'
    ).all()
    serializer_class   = ExamResultSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['student', 'schedule', 'grade', 'schedule__exam']
    search_fields      = ['student__first_name', 'student__admission_no']

    def perform_create(self, serializer):
        serializer.save(entered_by=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_enter(self, request):
        """Enter results for multiple students at once."""
        results_data = request.data.get('results', [])
        created_count = 0
        for rd in results_data:
            obj, created = ExamResult.objects.update_or_create(
                schedule_id=rd['schedule_id'],
                student_id=rd['student_id'],
                defaults={
                    'marks_obtained': rd['marks_obtained'],
                    'is_absent':      rd.get('is_absent', False),
                    'remarks':        rd.get('remarks', ''),
                    'entered_by':     request.user,
                }
            )
            if created: created_count += 1
        return Response({'saved': len(results_data), 'created': created_count})

    @action(detail=False, methods=['get'])
    def section_report(self, request):
        schedule_id = request.query_params.get('schedule')
        results = ExamResult.objects.filter(
            schedule_id=schedule_id
        ).select_related('student')
        stats = results.aggregate(
            avg=Avg('marks_obtained'),
            highest=Max('marks_obtained'),
            lowest=Min('marks_obtained'),
            passed=Count('id', filter=models.Q(grade__in=['A+','A','B+','B','C','D'])),
            total=Count('id'),
        )
        return Response({
            'stats':   stats,
            'results': ExamResultSerializer(results, many=True).data,
        })


class TimetableSlotViewSet(viewsets.ModelViewSet):
    queryset = TimetableSlot.objects.select_related(
        'section', 'subject', 'teacher', 'academic_year'
    ).all()
    serializer_class   = TimetableSlotSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['section', 'teacher', 'day_of_week', 'academic_year']
