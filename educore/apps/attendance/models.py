from django.db import models
from apps.core.models import Section, AcademicYear
from apps.students.models import Student
from apps.core.models import User


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT  = 'present',  'Present'
        ABSENT   = 'absent',   'Absent'
        LATE     = 'late',     'Late'
        EXCUSED  = 'excused',  'Excused'
        HOLIDAY  = 'holiday',  'Holiday'

    student      = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance')
    date         = models.DateField()
    status       = models.CharField(max_length=10, choices=Status.choices)
    marked_by    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    remarks      = models.CharField(max_length=200, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering        = ['-date', 'student__roll_number']
        indexes         = [models.Index(fields=['date', 'student'])]

    def __str__(self):
        return f'{self.student.full_name} — {self.date} — {self.status}'


class AttendanceSession(models.Model):
    """Tracks who marked attendance for a section on a day."""
    section    = models.ForeignKey(Section, on_delete=models.CASCADE)
    date       = models.DateField()
    marked_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    marked_at  = models.DateTimeField(auto_now_add=True)
    is_finalized = models.BooleanField(default=False)

    class Meta:
        unique_together = ('section', 'date')

    def __str__(self):
        return f'{self.section} — {self.date}'


class HolidayCalendar(models.Model):
    class HolidayType(models.TextChoices):
        NATIONAL  = 'national',  'National Holiday'
        SCHOOL    = 'school',    'School Holiday'
        EXAM      = 'exam',      'Exam Holiday'
        OTHER     = 'other',     'Other'

    date         = models.DateField(unique=True)
    name         = models.CharField(max_length=200)
    holiday_type = models.CharField(max_length=15, choices=HolidayType.choices, default=HolidayType.NATIONAL)
    academic_year= models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'{self.name} ({self.date})'
