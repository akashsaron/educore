from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Student
from .serializers import StudentSerializer, StudentListSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related(
        'section', 'section__grade', 'academic_year'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['section', 'section__grade', 'is_active', 'gender', 'academic_year']
    search_fields      = ['first_name', 'last_name', 'admission_no', 'parent_phone', 'parent_email']
    ordering_fields    = ['admission_date', 'last_name', 'roll_number']

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentListSerializer
        return StudentSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total    = Student.objects.filter(is_active=True).count()
        by_grade = Student.objects.filter(is_active=True).values(
            'section__grade__name'
        ).annotate(count=models.Count('id'))
        return Response({'total': total, 'by_grade': list(by_grade)})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        student = self.get_object()
        student.is_active = False
        student.save()
        return Response({'status': 'deactivated'})
