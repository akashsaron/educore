"""
config/celery.py

Celery application for EduCore background tasks.
Broker: Redis (REDIS_URL env var)

Tasks:
  - Daily fee overdue marker       (runs at midnight)
  - Weekly attendance summary email (runs every Monday 7 AM)
  - Monthly fee reminder SMS/email  (runs 1st of every month)
  - Library overdue checker         (runs daily at 9 AM)
  - Student birthday notifier       (runs daily at 8 AM)
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('educore')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ── Periodic task schedule ────────────────────────────────────────────────────
app.conf.beat_schedule = {

    # Mark overdue invoices every midnight
    'mark-overdue-fees-daily': {
        'task':     'apps.fees.tasks.mark_overdue_invoices',
        'schedule': crontab(hour=0, minute=5),
    },

    # Check library overdue every morning
    'check-library-overdue-daily': {
        'task':     'apps.library.tasks.mark_overdue_books',
        'schedule': crontab(hour=9, minute=0),
    },

    # Birthday notifications every morning
    'birthday-notifications-daily': {
        'task':     'apps.students.tasks.send_birthday_notifications',
        'schedule': crontab(hour=8, minute=0),
    },

    # Weekly attendance summary — every Monday at 7 AM
    'weekly-attendance-summary': {
        'task':     'apps.attendance.tasks.send_weekly_attendance_summary',
        'schedule': crontab(hour=7, minute=0, day_of_week=1),
    },

    # Monthly fee reminder — 1st of every month at 9 AM
    'monthly-fee-reminder': {
        'task':     'apps.fees.tasks.send_fee_reminders',
        'schedule': crontab(hour=9, minute=0, day_of_month=1),
    },

    # Daily database health log
    'daily-stats-snapshot': {
        'task':     'apps.core.tasks.take_daily_snapshot',
        'schedule': crontab(hour=23, minute=50),
    },
}

app.conf.timezone = 'Asia/Kolkata'
