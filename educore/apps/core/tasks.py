"""
apps/core/tasks.py  —  System-level background tasks
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def take_daily_snapshot(self):
    """
    Records a nightly snapshot of key metrics to a log.
    Extend this to write to a DailySnapshot model for trend charts.
    """
    try:
        from apps.students.models import Student
        from apps.teachers.models import Teacher
        from apps.attendance.models import AttendanceRecord
        from apps.fees.models import FeePayment

        today         = timezone.localdate()
        total_students = Student.objects.filter(is_active=True).count()
        total_teachers = Teacher.objects.filter(is_active=True).count()
        att_records    = AttendanceRecord.objects.filter(date=today)
        att_present    = att_records.filter(status='present').count()
        att_total      = att_records.count()
        att_pct        = round(att_present / att_total * 100, 1) if att_total else 0

        from django.db.models import Sum
        month_start  = today.replace(day=1)
        fee_today    = FeePayment.objects.filter(
            paid_date=today, status='paid'
        ).aggregate(t=Sum('amount'))['t'] or 0

        logger.info(
            '[SNAPSHOT %s] students=%s teachers=%s attendance=%s%% fee_collected_today=%.2f',
            today, total_students, total_teachers, att_pct, fee_today
        )
        return {'date': str(today), 'students': total_students, 'attendance_pct': att_pct}
    except Exception as exc:
        logger.error('Snapshot task failed: %s', exc)
        raise self.retry(exc=exc, countdown=300)


@shared_task
def send_generic_email(subject, body, recipient_list):
    """Utility task — send any email asynchronously."""
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
        logger.info('Email sent to %s', recipient_list)
        return True
    except Exception as exc:
        logger.error('Email failed to %s: %s', recipient_list, exc)
        return False
