from django.contrib import admin
from .models import BookCategory, Book, BookIssue

@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display  = ['title', 'author', 'category', 'total_copies', 'available', 'rack_no']
    list_filter   = ['category']
    search_fields = ['title', 'author', 'isbn']

@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display  = ['book', 'borrower', 'issued_on', 'due_date', 'status', 'fine_amount']
    list_filter   = ['status']
    search_fields = ['book__title', 'borrower__first_name']
