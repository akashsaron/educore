from django.db import models
from apps.core.models import User, Grade, Section


class Department(models.Model):
    name  = models.CharField(max_length=100, unique=True)
    head  = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='heads_department')

    def __str__(self):
        return self.name


class Subject(models.Model):
    name        = models.CharField(max_length=100)
    code        = models.CharField(max_length=20, unique=True)
    department  = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    grades      = models.ManyToManyField(Grade, related_name='subjects', blank=True)
    is_elective = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.code})'


class Teacher(models.Model):
    class Qualification(models.TextChoices):
        BTECH  = 'B.Tech',  'B.Tech'
        MTECH  = 'M.Tech',  'M.Tech'
        BSC    = 'B.Sc',    'B.Sc'
        MSC    = 'M.Sc',    'M.Sc'
        BED    = 'B.Ed',    'B.Ed'
        MED    = 'M.Ed',    'M.Ed'
        PHD    = 'Ph.D',    'Ph.D'
        OTHER  = 'Other',   'Other'

    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id     = models.CharField(max_length=20, unique=True)
    department      = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='teachers')
    subjects        = models.ManyToManyField(Subject, related_name='teachers', blank=True)
    sections        = models.ManyToManyField(Section, related_name='teachers', blank=True)
    qualification   = models.CharField(max_length=20, choices=Qualification.choices, blank=True)
    experience_years= models.PositiveSmallIntegerField(default=0)
    joining_date    = models.DateField()
    salary          = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phone           = models.CharField(max_length=15, blank=True)
    address         = models.TextField(blank=True)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user__first_name']

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.employee_id})'

    @property
    def full_name(self):
        return self.user.get_full_name()


class LeaveApplication(models.Model):
    class LeaveType(models.TextChoices):
        SICK      = 'sick',      'Sick Leave'
        CASUAL    = 'casual',    'Casual Leave'
        EARNED    = 'earned',    'Earned Leave'
        MATERNITY = 'maternity', 'Maternity Leave'
        OTHER     = 'other',     'Other'

    class Status(models.TextChoices):
        PENDING  = 'pending',  'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    teacher     = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='leaves')
    leave_type  = models.CharField(max_length=20, choices=LeaveType.choices)
    from_date   = models.DateField()
    to_date     = models.DateField()
    reason      = models.TextField()
    status      = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    applied_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.teacher} — {self.leave_type} ({self.from_date} to {self.to_date})'
