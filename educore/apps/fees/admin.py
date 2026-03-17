from django.contrib import admin
from .models import FeeCategory, FeeStructure, FeeInvoice, FeePayment, Scholarship

@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_mandatory']

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['grade', 'category', 'term', 'amount', 'due_date', 'academic_year']
    list_filter  = ['academic_year', 'grade', 'term']

@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display   = ['invoice_no', 'student', 'amount_due', 'amount_paid', 'status', 'due_date']
    list_filter    = ['status', 'fee_structure__academic_year']
    search_fields  = ['invoice_no', 'student__first_name', 'student__admission_no']
    readonly_fields= ['invoice_no', 'created_at', 'updated_at']

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display  = ['receipt_no', 'invoice', 'amount', 'payment_method', 'paid_date', 'status']
    list_filter   = ['status', 'payment_method']
    search_fields = ['receipt_no', 'invoice__student__first_name']

@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ['student', 'name', 'amount', 'awarded_date']
