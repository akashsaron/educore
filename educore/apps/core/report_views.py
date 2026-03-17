"""
apps/core/report_views.py

API endpoints that return PDF downloads.

Endpoints (add to config/urls.py):
  GET /api/reports/fee-receipt/<payment_id>/
  GET /api/reports/result-card/<student_id>/<exam_id>/
  GET /api/reports/attendance/<section_id>/?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .reports import generate_fee_receipt, generate_result_card, generate_attendance_report


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fee_receipt_pdf(request, payment_id):
    from apps.fees.models import FeePayment
    payment = get_object_or_404(
        FeePayment.objects.select_related(
            'invoice__student__section__grade',
            'invoice__fee_structure__category',
        ),
        pk=payment_id
    )
    return generate_fee_receipt(payment)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def result_card_pdf(request, student_id, exam_id):
    from apps.students.models import Student
    from apps.exams.models import Exam
    student = get_object_or_404(Student, pk=student_id)
    exam    = get_object_or_404(Exam, pk=exam_id)
    return generate_result_card(student, exam)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_report_pdf(request, section_id):
    from apps.core.models import Section
    from django.utils import timezone
    section   = get_object_or_404(Section, pk=section_id)
    from_date = request.query_params.get('from_date', str(timezone.localdate().replace(day=1)))
    to_date   = request.query_params.get('to_date',   str(timezone.localdate()))
    return generate_attendance_report(section, from_date, to_date)
