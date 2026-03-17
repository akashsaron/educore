"""
apps/core/analytics.py

Advanced analytics endpoints returning structured data for charts + Excel exports.

Endpoints registered in config/urls.py under /api/analytics/
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
import calendar


# ── Helpers ───────────────────────────────────────────────────────────────────

def _month_range(n=6):
    """Returns last n months as (year, month) tuples, oldest first."""
    today  = timezone.localdate()
    months = []
    for i in range(n - 1, -1, -1):
        d = today.replace(day=1) - timedelta(days=i * 30)
        months.append((d.year, d.month, d.strftime('%b %Y')))
    return months


# ── Attendance Analytics ──────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_analytics(request):
    """
    Returns:
      - monthly_trend: attendance % per month (last 6 months)
      - grade_summary: per-grade average attendance (current month)
      - daily_heatmap: per-day counts for current month
    """
    from apps.attendance.models import AttendanceRecord

    today = timezone.localdate()

    # Monthly trend
    monthly = []
    for year, month, label in _month_range(6):
        recs    = AttendanceRecord.objects.filter(date__year=year, date__month=month)
        total   = recs.count()
        present = recs.filter(status__in=['present', 'late']).count()
        monthly.append({
            'label':   label,
            'rate':    round(present / total * 100, 1) if total else 0,
            'present': present,
            'total':   total,
        })

    # Per-grade attendance this month
    from apps.core.models import Grade
    grade_summary = []
    for grade in Grade.objects.all().order_by('order'):
        recs    = AttendanceRecord.objects.filter(
            date__year=today.year, date__month=today.month,
            student__section__grade=grade
        )
        total   = recs.count()
        present = recs.filter(status__in=['present', 'late']).count()
        grade_summary.append({
            'grade': grade.name,
            'rate':  round(present / total * 100, 1) if total else 0,
        })

    # Daily heatmap for current month
    _, days_in_month = calendar.monthrange(today.year, today.month)
    daily = []
    for day in range(1, days_in_month + 1):
        d       = today.replace(day=day)
        if d > today:
            break
        recs    = AttendanceRecord.objects.filter(date=d)
        total   = recs.count()
        present = recs.filter(status__in=['present', 'late']).count()
        daily.append({
            'date':    str(d),
            'day':     day,
            'rate':    round(present / total * 100, 1) if total else 0,
            'present': present,
            'absent':  recs.filter(status='absent').count(),
        })

    return Response({
        'monthly_trend': monthly,
        'grade_summary': grade_summary,
        'daily_heatmap': daily,
    })


# ── Fee Analytics ─────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fee_analytics(request):
    """
    Returns:
      - monthly_collection: fees collected per month (last 6 months)
      - by_category:        collection breakdown by fee category
      - status_split:       invoice status distribution
      - pending_by_grade:   pending amount per grade
    """
    from apps.fees.models import FeePayment, FeeInvoice

    # Monthly collection trend
    monthly = []
    for year, month, label in _month_range(6):
        collected = FeePayment.objects.filter(
            paid_date__year=year, paid_date__month=month, status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly.append({'label': label, 'collected': float(collected)})

    # By fee category
    by_category = list(
        FeePayment.objects.filter(status='paid')
        .values(category=F('invoice__fee_structure__category__name'))
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    for row in by_category:
        row['total'] = float(row['total'])

    # Invoice status split
    status_split = list(
        FeeInvoice.objects.values('status')
        .annotate(count=Count('id'), amount=Sum('amount_due'))
        .order_by('status')
    )
    for row in status_split:
        row['amount'] = float(row['amount'] or 0)

    # Pending by grade
    from apps.core.models import Grade
    pending_by_grade = []
    for grade in Grade.objects.all().order_by('order'):
        pending = FeeInvoice.objects.filter(
            status__in=['pending', 'overdue', 'partial'],
            student__section__grade=grade
        ).aggregate(total=Sum('amount_due'))['total'] or 0
        pending_by_grade.append({'grade': grade.name, 'pending': float(pending)})

    return Response({
        'monthly_collection': monthly,
        'by_category':        by_category,
        'status_split':       status_split,
        'pending_by_grade':   pending_by_grade,
    })


# ── Exam / Academic Analytics ─────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exam_analytics(request):
    """
    Query params: ?exam_id=<id>
    Returns:
      - grade_distribution: count per grade (A+, A, B+, …)
      - subject_averages:   avg marks per subject
      - top_students:       top 10 by total marks
      - pass_fail_rate:     overall pass/fail
    """
    from apps.exams.models import ExamResult, Exam

    exam_id = request.query_params.get('exam_id')
    qs      = ExamResult.objects.all()
    if exam_id:
        qs = qs.filter(schedule__exam_id=exam_id)

    # Grade distribution
    grade_dist = list(
        qs.values('grade').annotate(count=Count('id')).order_by('grade')
    )

    # Subject averages
    subj_avg = list(
        qs.values(subject=F('schedule__subject__name'))
        .annotate(avg=Avg('marks_obtained'), max=Sum('schedule__max_marks'))
        .order_by('-avg')
    )
    for row in subj_avg:
        row['avg'] = round(float(row['avg'] or 0), 1)

    # Top 10 students by total marks
    from django.db.models import Sum as DSum
    top = list(
        qs.filter(is_absent=False)
        .values(
            student_id=F('student__id'),
            name=F('student__first_name'),
            last=F('student__last_name'),
            section=F('student__section__name'),
            grade_name=F('student__section__grade__name'),
        )
        .annotate(total=DSum('marks_obtained'))
        .order_by('-total')[:10]
    )
    for i, row in enumerate(top, 1):
        row['rank']       = i
        row['full_name']  = f"{row['name']} {row['last']}"
        row['total']      = float(row['total'] or 0)

    # Pass / fail
    total  = qs.count()
    passed = qs.filter(grade__in=['A+', 'A', 'B+', 'B', 'C', 'D']).count()
    failed = qs.filter(grade='F').count()

    return Response({
        'grade_distribution': grade_dist,
        'subject_averages':   subj_avg,
        'top_students':       top,
        'pass_fail': {
            'total':      total,
            'passed':     passed,
            'failed':     failed,
            'pass_rate':  round(passed / total * 100, 1) if total else 0,
        },
    })


# ── Student Demographics ──────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_demographics(request):
    """Students by grade, gender, admission trends."""
    from apps.students.models import Student
    from apps.core.models import Grade

    # By grade
    by_grade = list(
        Student.objects.filter(is_active=True)
        .values(grade=F('section__grade__name'), grade_order=F('section__grade__order'))
        .annotate(count=Count('id'))
        .order_by('grade_order')
    )

    # By gender
    by_gender = list(
        Student.objects.filter(is_active=True)
        .values('gender')
        .annotate(count=Count('id'))
    )
    gender_map = {'M': 'Male', 'F': 'Female', 'O': 'Other'}
    for row in by_gender:
        row['label'] = gender_map.get(row['gender'], row['gender'])

    # Admission trend (last 6 months)
    admission_trend = []
    for year, month, label in _month_range(6):
        count = Student.objects.filter(
            admission_date__year=year, admission_date__month=month
        ).count()
        admission_trend.append({'label': label, 'admissions': count})

    return Response({
        'by_grade':        by_grade,
        'by_gender':       by_gender,
        'admission_trend': admission_trend,
        'total_active':    Student.objects.filter(is_active=True).count(),
        'total_inactive':  Student.objects.filter(is_active=False).count(),
    })
