from django.db import models
from apps.core.models import AcademicYear, Grade
from apps.students.models import Student
from apps.core.models import User


class FeeCategory(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_mandatory= models.BooleanField(default=True)

    def __str__(self):
        return self.name


class FeeStructure(models.Model):
    """Fee amount per grade per academic year."""
    class Term(models.TextChoices):
        TERM1    = 'term1',    'Term 1'
        TERM2    = 'term2',    'Term 2'
        TERM3    = 'term3',    'Term 3'
        ANNUAL   = 'annual',   'Annual'
        MONTHLY  = 'monthly',  'Monthly'

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    grade         = models.ForeignKey(Grade, on_delete=models.CASCADE)
    category      = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    term          = models.CharField(max_length=10, choices=Term.choices)
    amount        = models.DecimalField(max_digits=10, decimal_places=2)
    due_date      = models.DateField()
    late_fee_per_day = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        unique_together = ('academic_year', 'grade', 'category', 'term')

    def __str__(self):
        return f'{self.grade} — {self.category} — {self.term} — ₹{self.amount}'


class FeeInvoice(models.Model):
    class Status(models.TextChoices):
        PENDING  = 'pending',  'Pending'
        PARTIAL  = 'partial',  'Partially Paid'
        PAID     = 'paid',     'Paid'
        OVERDUE  = 'overdue',  'Overdue'
        WAIVED   = 'waived',   'Waived'

    student       = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='invoices')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    invoice_no    = models.CharField(max_length=30, unique=True)
    amount_due    = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee      = models.DecimalField(max_digits=8,  decimal_places=2, default=0)
    discount      = models.DecimalField(max_digits=8,  decimal_places=2, default=0)
    status        = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    due_date      = models.DateField()
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.invoice_no} — {self.student.full_name}'

    @property
    def balance_due(self):
        return self.amount_due + self.late_fee - self.discount - self.amount_paid


class FeePayment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH    = 'cash',    'Cash'
        ONLINE  = 'online',  'Online Transfer'
        CHEQUE  = 'cheque',  'Cheque'
        DD      = 'dd',      'Demand Draft'
        UPI     = 'upi',     'UPI'

    class Status(models.TextChoices):
        PAID    = 'paid',    'Paid'
        PENDING = 'pending', 'Pending'
        FAILED  = 'failed',  'Failed'

    invoice        = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE, related_name='payments')
    receipt_no     = models.CharField(max_length=30, unique=True)
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    transaction_id = models.CharField(max_length=100, blank=True)
    paid_date      = models.DateField()
    status         = models.CharField(max_length=10, choices=Status.choices, default=Status.PAID)
    collected_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    remarks        = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.receipt_no} — ₹{self.amount}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update invoice amount_paid and status
        invoice = self.invoice
        total_paid = sum(p.amount for p in invoice.payments.filter(status='paid'))
        invoice.amount_paid = total_paid
        if total_paid >= invoice.amount_due:
            invoice.status = FeeInvoice.Status.PAID
        elif total_paid > 0:
            invoice.status = FeeInvoice.Status.PARTIAL
        invoice.save()


class Scholarship(models.Model):
    student       = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scholarships')
    name          = models.CharField(max_length=200)
    amount        = models.DecimalField(max_digits=10, decimal_places=2)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    awarded_date  = models.DateField()
    remarks       = models.TextField(blank=True)

    def __str__(self):
        return f'{self.student.full_name} — {self.name}'
