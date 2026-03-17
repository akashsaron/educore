from django.db import models
from apps.core.models import User, Grade


class Announcement(models.Model):
    class Priority(models.TextChoices):
        LOW    = 'low',    'Low'
        NORMAL = 'normal', 'Normal'
        HIGH   = 'high',   'High'
        URGENT = 'urgent', 'Urgent'

    class Audience(models.TextChoices):
        ALL      = 'all',      'Everyone'
        STUDENTS = 'students', 'Students Only'
        TEACHERS = 'teachers', 'Teachers Only'
        PARENTS  = 'parents',  'Parents Only'
        STAFF    = 'staff',    'Staff Only'

    title       = models.CharField(max_length=300)
    content     = models.TextField()
    priority    = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    audience    = models.CharField(max_length=10, choices=Audience.choices, default=Audience.ALL)
    grades      = models.ManyToManyField(Grade, blank=True, help_text='Leave blank for all grades')
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements')
    is_published= models.BooleanField(default=True)
    publish_date= models.DateField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    attachment  = models.FileField(upload_to='announcements/', null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class NoticeBoard(models.Model):
    title      = models.CharField(max_length=300)
    content    = models.TextField()
    posted_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_pinned  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title


class Event(models.Model):
    class EventType(models.TextChoices):
        ACADEMIC   = 'academic',   'Academic'
        SPORTS     = 'sports',     'Sports'
        CULTURAL   = 'cultural',   'Cultural'
        EXAM       = 'exam',       'Exam'
        HOLIDAY    = 'holiday',    'Holiday'
        MEETING    = 'meeting',    'Meeting'
        OTHER      = 'other',      'Other'

    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type  = models.CharField(max_length=15, choices=EventType.choices)
    start_date  = models.DateField()
    end_date    = models.DateField()
    venue       = models.CharField(max_length=200, blank=True)
    is_holiday  = models.BooleanField(default=False)
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f'{self.title} ({self.start_date})'
