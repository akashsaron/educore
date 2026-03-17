from django.db import models
from apps.core.models import AcademicYear, Grade, Section
from apps.students.models import Student
from apps.teachers.models import Subject, Teacher
from apps.core.models import User


class Exam(models.Model):
    class ExamType(models.TextChoices):
        UNIT_TEST    = 'unit_test',    'Unit Test'
        MID_TERM     = 'mid_term',     'Mid Term'
        FINAL        = 'final',        'Final Exam'
        PRACTICAL    = 'practical',    'Practical'
        ASSIGNMENT   = 'assignment',   'Assignment'

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        ONGOING   = 'ongoing',   'Ongoing'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    name          = models.CharField(max_length=200)
    exam_type     = models.CharField(max_length=20, choices=ExamType.choices)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    grades        = models.ManyToManyField(Grade, related_name='exams')
    start_date    = models.DateField()
    end_date      = models.DateField()
    status        = models.CharField(max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    max_marks     = models.PositiveSmallIntegerField(default=100)
    pass_marks    = models.PositiveSmallIntegerField(default=35)
    created_by    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.name} ({self.academic_year})'


class ExamSchedule(models.Model):
    """Per-subject schedule within an exam."""
    exam       = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='schedules')
    subject    = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade      = models.ForeignKey(Grade, on_delete=models.CASCADE)
    date       = models.DateField()
    start_time = models.TimeField()
    end_time   = models.TimeField()
    venue      = models.CharField(max_length=100, blank=True)
    max_marks  = models.PositiveSmallIntegerField()
    pass_marks = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.exam} — {self.subject} — {self.date}'


class ExamResult(models.Model):
    class Grade(models.TextChoices):
        A_PLUS = 'A+', 'A+'
        A      = 'A',  'A'
        B_PLUS = 'B+', 'B+'
        B      = 'B',  'B'
        C      = 'C',  'C'
        D      = 'D',  'D'
        F      = 'F',  'F (Fail)'

    schedule      = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name='results')
    student       = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    marks_obtained= models.DecimalField(max_digits=5, decimal_places=2)
    grade         = models.CharField(max_length=2, choices=Grade.choices, blank=True)
    is_absent     = models.BooleanField(default=False)
    remarks       = models.CharField(max_length=200, blank=True)
    entered_by    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    entered_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('schedule', 'student')
        ordering        = ['-marks_obtained']

    def __str__(self):
        return f'{self.student.full_name} — {self.schedule.subject} — {self.marks_obtained}'

    def save(self, *args, **kwargs):
        # Auto-compute grade
        pct = (self.marks_obtained / self.schedule.max_marks) * 100
        if pct >= 90:   self.grade = 'A+'
        elif pct >= 80: self.grade = 'A'
        elif pct >= 70: self.grade = 'B+'
        elif pct >= 60: self.grade = 'B'
        elif pct >= 50: self.grade = 'C'
        elif pct >= 35: self.grade = 'D'
        else:           self.grade = 'F'
        super().save(*args, **kwargs)


class TimetableSlot(models.Model):
    class DayOfWeek(models.IntegerChoices):
        MONDAY    = 1, 'Monday'
        TUESDAY   = 2, 'Tuesday'
        WEDNESDAY = 3, 'Wednesday'
        THURSDAY  = 4, 'Thursday'
        FRIDAY    = 5, 'Friday'
        SATURDAY  = 6, 'Saturday'

    section       = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='timetable')
    subject       = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher       = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day_of_week   = models.IntegerField(choices=DayOfWeek.choices)
    period_number = models.PositiveSmallIntegerField()
    start_time    = models.TimeField()
    end_time      = models.TimeField()
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    room          = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('section', 'day_of_week', 'period_number', 'academic_year')
        ordering        = ['day_of_week', 'period_number']

    def __str__(self):
        return f'{self.section} — {self.get_day_of_week_display()} P{self.period_number} — {self.subject}'
