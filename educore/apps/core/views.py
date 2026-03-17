from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Count, Sum, Q
from django.utils import timezone

from .models import User, AcademicYear, SchoolProfile, Grade, Section
from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer, UserCreateSerializer,
    AcademicYearSerializer, SchoolProfileSerializer, GradeSerializer, SectionSerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset         = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    search_fields    = ['username', 'first_name', 'last_name', 'email']
    filterset_fields = ['role', 'is_active']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset           = AcademicYear.objects.all()
    serializer_class   = AcademicYearSerializer
    permission_classes = [IsAuthenticated]


class SchoolProfileViewSet(viewsets.ModelViewSet):
    queryset           = SchoolProfile.objects.all()
    serializer_class   = SchoolProfileSerializer
    permission_classes = [IsAuthenticated]


class GradeViewSet(viewsets.ModelViewSet):
    queryset           = Grade.objects.all()
    serializer_class   = GradeSerializer
    permission_classes = [IsAuthenticated]


class SectionViewSet(viewsets.ModelViewSet):
    queryset           = Section.objects.select_related('grade', 'class_teacher').all()
    serializer_class   = SectionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['grade']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Aggregated dashboard KPIs."""
    from apps.students.models import Student
    from apps.teachers.models import Teacher
    from apps.attendance.models import AttendanceRecord
    from apps.fees.models import FeePayment, FeeInvoice

    today = timezone.localdate()

    total_students = Student.objects.filter(is_active=True).count()
    total_teachers = Teacher.objects.filter(is_active=True).count()

    # Today's attendance rate
    today_records = AttendanceRecord.objects.filter(date=today)
    present_today = today_records.filter(status='present').count()
    total_today   = today_records.count()
    attendance_pct = round((present_today / total_today * 100), 1) if total_today else 0

    # Fee collection this month
    month_start = today.replace(day=1)
    fee_collected = FeePayment.objects.filter(
        paid_date__gte=month_start, status='paid'
    ).aggregate(total=Sum('amount'))['total'] or 0

    fee_pending = FeeInvoice.objects.filter(
        status__in=['pending', 'overdue']
    ).aggregate(total=Sum('amount_due'))['total'] or 0

    # Monthly attendance trend (last 6 months)
    from apps.attendance.models import AttendanceRecord
    monthly_trend = []
    for i in range(5, -1, -1):
        from dateutil.relativedelta import relativedelta
        month = today - relativedelta(months=i)
        records = AttendanceRecord.objects.filter(
            date__year=month.year, date__month=month.month
        )
        total   = records.count()
        present = records.filter(status='present').count()
        monthly_trend.append({
            'month': month.strftime('%b %Y'),
            'rate': round(present/total*100, 1) if total else 0,
        })

    return Response({
        'total_students':   total_students,
        'total_teachers':   total_teachers,
        'attendance_today': attendance_pct,
        'present_today':    present_today,
        'absent_today':     total_today - present_today,
        'fee_collected':    float(fee_collected),
        'fee_pending':      float(fee_pending),
        'monthly_trend':    monthly_trend,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)
