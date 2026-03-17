from django.db import models
from apps.core.models import User


class BookCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name


class Book(models.Model):
    title        = models.CharField(max_length=300)
    author       = models.CharField(max_length=200)
    isbn         = models.CharField(max_length=20, unique=True, blank=True)
    category     = models.ForeignKey(BookCategory, on_delete=models.SET_NULL, null=True)
    publisher    = models.CharField(max_length=200, blank=True)
    edition      = models.CharField(max_length=50, blank=True)
    total_copies = models.PositiveSmallIntegerField(default=1)
    available    = models.PositiveSmallIntegerField(default=1)
    rack_no      = models.CharField(max_length=20, blank=True)
    added_on     = models.DateField(auto_now_add=True)

    def __str__(self): return f'{self.title} — {self.author}'


class BookIssue(models.Model):
    class Status(models.TextChoices):
        ISSUED   = 'issued',   'Issued'
        RETURNED = 'returned', 'Returned'
        OVERDUE  = 'overdue',  'Overdue'
        LOST     = 'lost',     'Lost'

    book        = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    borrower    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowed_books')
    issued_on   = models.DateField(auto_now_add=True)
    due_date    = models.DateField()
    returned_on = models.DateField(null=True, blank=True)
    status      = models.CharField(max_length=10, choices=Status.choices, default=Status.ISSUED)
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    issued_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_books')

    class Meta:
        ordering = ['-issued_on']

    def __str__(self):
        return f'{self.book.title} -> {self.borrower.get_full_name()}'
