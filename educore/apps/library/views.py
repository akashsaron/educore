from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BookCategory, Book, BookIssue


class BookCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = BookCategory
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model  = Book
        fields = '__all__'


class BookIssueSerializer(serializers.ModelSerializer):
    book_title    = serializers.CharField(source='book.title',              read_only=True)
    borrower_name = serializers.CharField(source='borrower.get_full_name',  read_only=True)

    class Meta:
        model  = BookIssue
        fields = '__all__'


class BookCategoryViewSet(viewsets.ModelViewSet):
    queryset           = BookCategory.objects.all()
    serializer_class   = BookCategorySerializer
    permission_classes = [IsAuthenticated]


class BookViewSet(viewsets.ModelViewSet):
    queryset           = Book.objects.select_related('category').all()
    serializer_class   = BookSerializer
    permission_classes = [IsAuthenticated]
    search_fields      = ['title', 'author', 'isbn']
    filterset_fields   = ['category']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        from django.db.models import Sum
        total     = Book.objects.aggregate(t=Sum('total_copies'))['t'] or 0
        available = Book.objects.aggregate(a=Sum('available'))['a'] or 0
        overdue   = BookIssue.objects.filter(status='overdue').count()
        return Response({'total': total, 'available': available,
                         'borrowed': total - available, 'overdue': overdue})


class BookIssueViewSet(viewsets.ModelViewSet):
    queryset           = BookIssue.objects.select_related('book', 'borrower').all()
    serializer_class   = BookIssueSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['status', 'borrower']
    search_fields      = ['book__title', 'borrower__first_name']

    def perform_create(self, serializer):
        issue = serializer.save(issued_by=self.request.user)
        issue.book.available = max(0, issue.book.available - 1)
        issue.book.save()

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        from django.utils import timezone
        issue = self.get_object()
        issue.returned_on = timezone.localdate()
        issue.status = 'returned'
        issue.book.available += 1
        issue.book.save()
        issue.save()
        return Response({'status': 'returned'})
