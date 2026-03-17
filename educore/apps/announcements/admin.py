from django.contrib import admin
from .models import Announcement, NoticeBoard, Event

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display  = ['title', 'priority', 'audience', 'is_published', 'publish_date']
    list_filter   = ['priority', 'audience', 'is_published']
    search_fields = ['title', 'content']

@admin.register(NoticeBoard)
class NoticeBoardAdmin(admin.ModelAdmin):
    list_display = ['title', 'posted_by', 'is_pinned', 'created_at']
    list_filter  = ['is_pinned']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'end_date', 'venue', 'is_holiday']
    list_filter  = ['event_type', 'is_holiday']
    search_fields = ['title']
