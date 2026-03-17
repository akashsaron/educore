"""
apps/attendance/tasks.py  —  Attendance background tasks
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def send_weekly_attendance_summary(self):
    """
    Runs every Monday at 7 AM.
    Emails parents of students whose attendance dropped below 75% last week.
    """
    try:
        from .models import AttendanceRecord
        from apps.students.models import Student

        today      = timezone.localdate()
        week_start = today - timedelta(days=7)
        week_end   = today - timedelta(days=1)

        low_attendance = []
        for student in Student.objects.filter(is_active=True).select_related('section'):
            records = AttendanceRecord.objects.filter(
                student=student,
                date__range=[week_start, week_end]
            )
            total   = records.count()
            present = records.filter(status__in=['present', 'late']).count()
            if total == 0:
                continue
            pct = present / total * 100
            if pct < 75:
                low_attendance.append((student, round(pct, 1), total, present))

        sent = 0
        for student, pct, total, present in low_attendance:
            parent_email = student.parent_email
            if not parent_email:
                continue
            subject = f'Attendance Alert — {student.full_name}'
            body    = (
                f'Dear Parent,\n\n'
                f'{student.full_name} ({student.current_class}) attended '
                f'{present} out of {total} school days last week ({pct}%).\n\n'
                f'Regular attendance is important for academic progress. '
                f'Please ensure your child attends school regularly.\n\n'
                f'For queries, contact the class teacher.\n\n'
                f'Regards,\nEduCore School ERP'
            )
            try:
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [parent_email])
                sent += 1
            except Exception as e:
                logger.warning('Attendance alert failed for %s: %s', parent_email, e)

        logger.info('[ATTENDANCE] Sent %s low-attendance alerts (week %s–%s)', sent, week_start, week_end)
        return {'sent': sent, 'low_attendance_count': len(low_attendance)}
    except Exception as exc:
        logger.error('send_weekly_attendance_summary failed: %s', exc)
        raise self.retry(exc=exc, countdown=300)


@shared_task
def auto_mark_holiday(date_str, section_ids=None):
    """
    Bulk-mark all students as 'holiday' for a given date.
    Used when a holiday is added after the fact.
    """
    from .models import AttendanceRecord
    from apps.students.models import Student
    from datetime import date

    target_date = date.fromisoformat(date_str)
    qs = Student.objects.filter(is_active=True)
    if section_ids:
        qs = qs.filter(section_id__in=section_ids)

    created = 0
    for student in qs:
        _, made = AttendanceRecord.objects.get_or_create(
            student=student,
            date=target_date,
            defaults={'status': 'holiday', 'marked_by': None}
        )
        if made:
            created += 1

    logger.info('[ATTENDANCE] Holiday marked for %s students on %s', created, date_str)
    return {'created': created, 'date': date_str}
