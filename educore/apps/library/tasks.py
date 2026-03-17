"""
apps/library/tasks.py  —  Library background tasks
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def mark_overdue_books(self):
    """
    Runs daily at 9 AM.
    Marks issued books past their due_date as 'overdue' and
    calculates fines at ₹5/day.
    """
    try:
        from .models import BookIssue
        today   = timezone.localdate()
        FINE_PER_DAY = 5  # ₹ per day

        overdue = BookIssue.objects.filter(
            due_date__lt=today,
            status='issued'
        )
        updated = 0
        for issue in overdue:
            days = (today - issue.due_date).days
            issue.status      = BookIssue.Status.OVERDUE
            issue.fine_amount = days * FINE_PER_DAY
            issue.save(update_fields=['status', 'fine_amount'])
            updated += 1

        logger.info('[LIBRARY] Marked %s books as overdue on %s', updated, today)
        return {'updated': updated}
    except Exception as exc:
        logger.error('mark_overdue_books failed: %s', exc)
        raise self.retry(exc=exc, countdown=300)


@shared_task
def send_overdue_book_reminders():
    """Send email reminders to borrowers with overdue books."""
    from .models import BookIssue
    from django.utils import timezone

    overdue = BookIssue.objects.filter(
        status='overdue'
    ).select_related('book', 'borrower')

    sent = 0
    for issue in overdue:
        email = issue.borrower.email
        if not email:
            continue
        days = (timezone.localdate() - issue.due_date).days
        subject = f'Library Book Overdue — {issue.book.title}'
        body = (
            f'Dear {issue.borrower.get_full_name()},\n\n'
            f'The book "{issue.book.title}" borrowed on {issue.issued_on} '
            f'was due on {issue.due_date} and is {days} days overdue.\n\n'
            f'Current fine: ₹{issue.fine_amount}\n\n'
            f'Please return the book to the library immediately.\n\n'
            f'Regards,\nSchool Library'
        )
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email])
            sent += 1
        except Exception as e:
            logger.warning('Library reminder failed for %s: %s', email, e)

    logger.info('[LIBRARY] Sent %s overdue reminders', sent)
    return {'sent': sent}
