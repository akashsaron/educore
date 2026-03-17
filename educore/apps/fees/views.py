import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone

from .models import FeeCategory, FeeStructure, FeeInvoice, FeePayment, Scholarship
from .serializers import (FeeCategorySerializer, FeeStructureSerializer,
                           FeeInvoiceSerializer, FeePaymentSerializer,
                           ScholarshipSerializer)


class FeeCategoryViewSet(viewsets.ModelViewSet):
    queryset           = FeeCategory.objects.all()
    serializer_class   = FeeCategorySerializer
    permission_classes = [IsAuthenticated]


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.select_related(
        'academic_year', 'grade', 'category'
    ).all()
    serializer_class   = FeeStructureSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['academic_year', 'grade', 'category', 'term']


class FeeInvoiceViewSet(viewsets.ModelViewSet):
    queryset = FeeInvoice.objects.select_related(
        'student', 'student__section', 'fee_structure__category'
    ).prefetch_related('payments').all()
    serializer_class   = FeeInvoiceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['student', 'status', 'fee_structure__academic_year']
    search_fields      = ['invoice_no', 'student__first_name', 'student__last_name', 'student__admission_no']

    def perform_create(self, serializer):
        # Auto-generate invoice number
        prefix = 'INV'
        year   = timezone.localdate().year
        count  = FeeInvoice.objects.count() + 1
        invoice_no = f'{prefix}-{year}-{count:05d}'
        serializer.save(invoice_no=invoice_no)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        today       = timezone.localdate()
        month_start = today.replace(day=1)

        total_due   = FeeInvoice.objects.aggregate(t=Sum('amount_due'))['t'] or 0
        total_paid  = FeePayment.objects.filter(status='paid').aggregate(t=Sum('amount'))['t'] or 0
        this_month  = FeePayment.objects.filter(
            status='paid', paid_date__gte=month_start
        ).aggregate(t=Sum('amount'))['t'] or 0
        pending     = FeeInvoice.objects.filter(
            status__in=['pending','overdue','partial']
        ).aggregate(t=Sum('amount_due'))['t'] or 0
        overdue_count = FeeInvoice.objects.filter(
            status='overdue'
        ).count()

        return Response({
            'total_due':     float(total_due),
            'total_paid':    float(total_paid),
            'this_month':    float(this_month),
            'pending':       float(pending),
            'overdue_count': overdue_count,
        })

    @action(detail=False, methods=['post'])
    def mark_overdue(self, request):
        """Bulk-mark past-due invoices as overdue."""
        today   = timezone.localdate()
        updated = FeeInvoice.objects.filter(
            due_date__lt=today,
            status__in=['pending', 'partial']
        ).update(status=FeeInvoice.Status.OVERDUE)
        return Response({'updated': updated})


class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.select_related(
        'invoice__student', 'collected_by'
    ).all()
    serializer_class   = FeePaymentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['status', 'payment_method', 'paid_date']
    search_fields      = ['receipt_no', 'invoice__student__first_name']

    def perform_create(self, serializer):
        year      = timezone.localdate().year
        count     = FeePayment.objects.count() + 1
        receipt_no = f'RCP-{year}-{count:06d}'
        serializer.save(receipt_no=receipt_no, collected_by=self.request.user)


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset           = Scholarship.objects.select_related('student', 'academic_year').all()
    serializer_class   = ScholarshipSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['academic_year', 'student']
