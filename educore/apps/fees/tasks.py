"""
apps/fees/tasks.py  —  Fee-related background tasks
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def mark_overdue_invoices(self):
    """
    Runs daily at midnight.
    Marks all pending/partial invoices past their due_date as 'overdue'
    and applies daily late fee where configured.
    """
    try:
        from .models import FeeInvoice, FeeStructure
        today   = timezone.localdate()
        updated = 0

        overdue_invoices = FeeInvoice.objects.filter(
            due_date__lt=today,
            status__in=['pending', 'partial']
        ).select_related('fee_structure')

        for invoice in overdue_invoices:
            days_overdue = (today - invoice.due_date).days
            daily_rate   = invoice.fee_structure.late_fee_per_day
            invoice.late_fee = days_overdue * daily_rate
            invoice.status   = FeeInvoice.Status.OVERDUE
            invoice.save(update_fields=['status', 'late_fee', 'updated_at'])
            updated += 1

        logger.info('[FEES] Marked %s invoices as overdue on %s', updated, today)
        return {'updated': updated, 'date': str(today)}
    except Exception as exc:
        logger.error('mark_overdue_invoices failed: %s', exc)
        raise self.retry(exc=exc, countdown=600)


@shared_task(bind=True, max_retries=2)
def send_fee_reminders(self):
    """
    Runs 1st of every month.
    Sends email reminders to parents of students with pending/overdue invoices.
    """
    try:
        from .models import FeeInvoice
        invoices = FeeInvoice.objects.filter(
            status__in=['pending', 'overdue', 'partial']
        ).select_related('student')

        sent = 0
        for invoice in invoices:
            parent_email = invoice.student.parent_email
            if not parent_email:
                continue
            subject = f'Fee Reminder — {invoice.student.full_name}'
            body    = (
                f'Dear Parent,\n\n'
                f'This is a reminder that the fee invoice {invoice.invoice_no} '
                f'for {invoice.student.full_name} ({invoice.student.current_class}) '
                f'amounting to ₹{invoice.balance_due:,.2f} is pending.\n\n'
                f'Please visit the school to make the payment at the earliest.\n\n'
                f'Regards,\nEduCore School ERP'
            )
            try:
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [parent_email])
                sent += 1
            except Exception as e:
                logger.warning('Failed to send reminder to %s: %s', parent_email, e)

        logger.info('[FEES] Sent %s fee reminder emails', sent)
        return {'sent': sent}
    except Exception as exc:
        logger.error('send_fee_reminders failed: %s', exc)
        raise self.retry(exc=exc, countdown=300)


@shared_task
def generate_invoice_for_student(student_id, fee_structure_id):
    """
    Creates a FeeInvoice for a student when they are admitted or a new term starts.
    Call this via .delay() from StudentViewSet.create() or term-start management command.
    """
    from .models import FeeInvoice, FeeStructure
    from apps.students.models import Student

    student       = Student.objects.get(pk=student_id)
    fee_structure = FeeStructure.objects.get(pk=fee_structure_id)
    count         = FeeInvoice.objects.count() + 1
    year          = timezone.localdate().year
    invoice_no    = f'INV-{year}-{count:05d}'

    invoice, created = FeeInvoice.objects.get_or_create(
        student=student,
        fee_structure=fee_structure,
        defaults={
            'invoice_no': invoice_no,
            'amount_due': fee_structure.amount,
            'due_date':   fee_structure.due_date,
        }
    )
    logger.info('[FEES] Invoice %s for %s — created=%s', invoice.invoice_no, student.full_name, created)
    return {'invoice_no': invoice.invoice_no, 'created': created}
