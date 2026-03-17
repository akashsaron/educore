"""
apps/students/tasks.py  —  Student-related background tasks
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def send_birthday_notifications():
    """
    Runs daily at 8 AM.
    Sends birthday greetings to students + notifies their class teacher.
    """
    from .models import Student
    today = timezone.localdate()

    birthdays = Student.objects.filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day,
        is_active=True
    ).select_related('section__class_teacher__user')

    notified = 0
    for student in birthdays:
        # Email to parent
        if student.parent_email:
            subject = f'🎂 Happy Birthday, {student.first_name}!'
            body    = (
                f'Dear {student.father_name},\n\n'
                f'Wishing {student.first_name} a very Happy Birthday! '
                f'May this new year of life bring joy, success, and great learning.\n\n'
                f'With warm regards,\n'
                f'Greenfield Public School'
            )
            try:
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [student.parent_email])
                notified += 1
            except Exception as e:
                logger.warning('Birthday email failed for %s: %s', student.full_name, e)

        # Notify class teacher
        teacher = getattr(student.section, 'class_teacher', None)
        if teacher and teacher.user.email:
            try:
                send_mail(
                    f'Birthday Today: {student.full_name}',
                    f'{student.full_name} ({student.section}) celebrates their birthday today!',
                    settings.DEFAULT_FROM_EMAIL,
                    [teacher.user.email]
                )
            except Exception:
                pass

    logger.info('[STUDENTS] Sent %s birthday notifications on %s', notified, today)
    return {'notified': notified, 'date': str(today)}


@shared_task
def bulk_promote_students(from_section_id, to_section_id, academic_year_id):
    """
    End-of-year: bulk-move all active students from one section to another.
    Triggered manually via admin or API at year-end.
    """
    from .models import Student
    from apps.core.models import Section, AcademicYear

    to_section   = Section.objects.get(pk=to_section_id)
    new_year     = AcademicYear.objects.get(pk=academic_year_id)

    students = Student.objects.filter(section_id=from_section_id, is_active=True)
    count    = students.count()
    students.update(section=to_section, academic_year=new_year)

    logger.info('[STUDENTS] Promoted %s students to %s for year %s', count, to_section, new_year)
    return {'promoted': count, 'to_section': str(to_section)}
