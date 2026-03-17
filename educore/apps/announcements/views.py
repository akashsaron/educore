from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Announcement, NoticeBoard, Event


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model  = Announcement
        fields = '__all__'


class NoticeBoardSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)

    class Meta:
        model  = NoticeBoard
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model  = Event
        fields = '__all__'


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset           = Announcement.objects.select_related('created_by').all()
    serializer_class   = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['priority', 'audience', 'is_published']
    search_fields      = ['title', 'content']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class NoticeBoardViewSet(viewsets.ModelViewSet):
    queryset           = NoticeBoard.objects.select_related('posted_by').all()
    serializer_class   = NoticeBoardSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class EventViewSet(viewsets.ModelViewSet):
    queryset           = Event.objects.all()
    serializer_class   = EventSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['event_type', 'is_holiday']
    search_fields      = ['title']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
