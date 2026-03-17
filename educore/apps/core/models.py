from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Extended user with role-based access."""

    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        ADMIN       = 'admin',       'Admin'
        PRINCIPAL   = 'principal',   'Principal'
        TEACHER     = 'teacher',     'Teacher'
        ACCOUNTANT  = 'accountant',  'Accountant'
        LIBRARIAN   = 'librarian',   'Librarian'
        PARENT      = 'parent',      'Parent'
        STUDENT     = 'student',     'Student'

    role        = models.CharField(max_length=20, choices=Role.choices, default=Role.ADMIN)
    phone       = models.CharField(max_length=15, blank=True)
    avatar      = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_full_name()} ({self.role})'

    @property
    def is_staff_member(self):
        return self.role in [self.Role.ADMIN, self.Role.PRINCIPAL,
                              self.Role.TEACHER, self.Role.ACCOUNTANT,
                              self.Role.LIBRARIAN, self.Role.SUPER_ADMIN]


class AcademicYear(models.Model):
    name       = models.CharField(max_length=20, unique=True)  # e.g. "2025-26"
    start_date = models.DateField()
    end_date   = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class SchoolProfile(models.Model):
    name          = models.CharField(max_length=200)
    logo          = models.ImageField(upload_to='school/', blank=True, null=True)
    address       = models.TextField()
    city          = models.CharField(max_length=100)
    state         = models.CharField(max_length=100)
    pincode       = models.CharField(max_length=10)
    phone         = models.CharField(max_length=15)
    email         = models.EmailField()
    website       = models.URLField(blank=True)
    board         = models.CharField(max_length=20, choices=[
        ('CBSE','CBSE'),('ICSE','ICSE'),('STATE','State Board'),('IB','IB'),
    ])
    affiliation_no = models.CharField(max_length=50, blank=True)
    founded_year   = models.PositiveIntegerField()
    principal_name = models.CharField(max_length=200)
    morning_start  = models.TimeField(default='08:00')
    afternoon_end  = models.TimeField(default='15:30')
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'School Profile'

    def __str__(self):
        return self.name


class Grade(models.Model):
    """e.g. Grade 10"""
    name          = models.CharField(max_length=20, unique=True)
    numeric_grade = models.PositiveSmallIntegerField()
    order         = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Section(models.Model):
    """e.g. Grade 10-A"""
    grade        = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='sections')
    name         = models.CharField(max_length=5)       # A, B, C
    class_teacher = models.ForeignKey(
        'teachers.Teacher', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='class_teacher_of'
    )
    capacity     = models.PositiveSmallIntegerField(default=45)
    room_number  = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('grade', 'name')
        ordering = ['grade__order', 'name']

    def __str__(self):
        return f'{self.grade.name}-{self.name}'

    @property
    def display_name(self):
        return f'{self.grade.name}-{self.name}'
