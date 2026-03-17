from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Department, Subject, Teacher, LeaveApplication
from .serializers import (DepartmentSerializer, SubjectSerializer,
                           TeacherSerializer, TeacherListSerializer,
                           LeaveApplicationSerializer)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset           = Department.objects.all()
    serializer_class   = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset           = Subject.objects.select_related('department').all()
    serializer_class   = SubjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['department', 'grades', 'is_elective']
    search_fields      = ['name', 'code']


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related(
        'user', 'department'
    ).prefetch_related('subjects', 'sections').all()
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['department', 'is_active']
    search_fields      = ['user__first_name', 'user__last_name', 'employee_id']

    def get_serializer_class(self):
        if self.action == 'list':
            return TeacherListSerializer
        return TeacherSerializer

    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        teacher = self.get_object()
        from apps.exams.models import TimetableSlot
        slots = TimetableSlot.objects.filter(
            teacher=teacher
        ).select_related('subject', 'section').order_by('day_of_week', 'period_number')
        data = [{'day': s.get_day_of_week_display(), 'period': s.period_number,
                 'subject': s.subject.name, 'section': str(s.section)} for s in slots]
        return Response(data)


class LeaveApplicationViewSet(viewsets.ModelViewSet):
    queryset           = LeaveApplication.objects.select_related('teacher__user').all()
    serializer_class   = LeaveApplicationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['teacher', 'status', 'leave_type']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'approved'
        leave.approved_by = request.user
        leave.save()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'rejected'
        leave.approved_by = request.user
        leave.save()
        return Response({'status': 'rejected'})
