"""
apps/core/reports.py

PDF generation using ReportLab.
Generates:
  - Fee payment receipt
  - Student result card / marksheet
  - Student ID card
  - Attendance report
"""
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                  TableStyle, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# ── colour palette ────────────────────────────────────────────────────────────
PRIMARY   = colors.HexColor('#1a2744')
ACCENT    = colors.HexColor('#4f8ef7')
SUCCESS   = colors.HexColor('#22c55e')
DANGER    = colors.HexColor('#ef4444')
LIGHT     = colors.HexColor('#f4f6fb')
MUTED     = colors.HexColor('#6b7a99')
WHITE     = colors.white
BLACK     = colors.black


def _base_doc(buffer, title='EduCore', pagesize=A4):
    return SimpleDocTemplate(
        buffer, pagesize=pagesize,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        title=title,
    )


def _school_header(school_name='Greenfield Public School',
                   subtitle='School Management System'):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', fontSize=16, textColor=PRIMARY,
                                  fontName='Helvetica-Bold', alignment=TA_CENTER)
    sub_style   = ParagraphStyle('sub', fontSize=9, textColor=MUTED,
                                  fontName='Helvetica', alignment=TA_CENTER)
    return [
        Paragraph(school_name, title_style),
        Paragraph(subtitle, sub_style),
        HRFlowable(width='100%', thickness=2, color=ACCENT, spaceAfter=8),
    ]


# ── Fee Receipt ───────────────────────────────────────────────────────────────

def generate_fee_receipt(payment) -> HttpResponse:
    """
    Returns an HttpResponse with a PDF fee receipt attached.
    Usage in view:
        from apps.core.reports import generate_fee_receipt
        return generate_fee_receipt(payment_instance)
    """
    buffer   = BytesIO()
    doc      = _base_doc(buffer, title=f'Receipt {payment.receipt_no}')
    story    = []
    styles   = getSampleStyleSheet()

    story += _school_header()

    # Receipt title
    h2 = ParagraphStyle('h2', fontSize=13, textColor=PRIMARY,
                         fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=6)
    story.append(Paragraph('FEE PAYMENT RECEIPT', h2))
    story.append(Spacer(1, 6))

    # Meta row
    meta_data = [
        ['Receipt No.', payment.receipt_no,   'Date', str(payment.paid_date)],
        ['Invoice No.', payment.invoice.invoice_no, 'Method', payment.get_payment_method_display()],
    ]
    meta_table = Table(meta_data, colWidths=[3*cm, 6*cm, 3*cm, 6*cm])
    meta_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 9),
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (2,0), (2,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,-1), MUTED),
        ('TEXTCOLOR', (2,0), (2,-1), MUTED),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e2e8f0')))
    story.append(Spacer(1, 10))

    # Student details
    student = payment.invoice.student
    student_data = [
        ['Student Name',   student.full_name],
        ['Admission No.',  student.admission_no],
        ['Class / Section',student.current_class],
        ['Father\'s Name', student.father_name],
    ]
    s_table = Table(student_data, colWidths=[4.5*cm, 13*cm])
    s_table.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',     (0,0), (-1,-1), 10),
        ('FONTNAME',     (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR',    (0,0), (0,-1), MUTED),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    ]))
    story.append(s_table)
    story.append(Spacer(1, 10))

    # Fee breakdown table
    fee_header = [['Description', 'Amount (₹)']]
    invoice    = payment.invoice
    fee_rows   = [
        [invoice.fee_structure.category.name, f'{invoice.amount_due:,.2f}'],
    ]
    if invoice.late_fee:
        fee_rows.append(['Late Fee', f'{invoice.late_fee:,.2f}'])
    if invoice.discount:
        fee_rows.append(['Discount', f'- {invoice.discount:,.2f}'])
    fee_rows.append(['', ''])
    fee_rows.append([Paragraph('<b>Amount Paid</b>', styles['Normal']),
                     Paragraph(f'<b>₹ {payment.amount:,.2f}</b>', styles['Normal'])])

    fee_table = Table(fee_header + fee_rows, colWidths=[13*cm, 4.5*cm])
    fee_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND',   (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR',    (0,0), (-1,0), WHITE),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,-1), 10),
        ('ALIGN',        (1,0), (1,-1), 'RIGHT'),
        ('ROWBACKGROUNDS',(0,1),(-1,-3), [WHITE, LIGHT]),
        # Totals row
        ('LINEABOVE',    (0,-1), (-1,-1), 1, PRIMARY),
        ('FONTNAME',     (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,-1), (-1,-1), 11),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('GRID',         (0,0), (-1,-2), 0.25, colors.HexColor('#e2e8f0')),
    ]))
    story.append(fee_table)
    story.append(Spacer(1, 20))

    # Status stamp
    status_color = SUCCESS if payment.status == 'paid' else DANGER
    status_style = ParagraphStyle('stamp', fontSize=18, textColor=status_color,
                                   fontName='Helvetica-Bold', alignment=TA_CENTER)
    story.append(Paragraph(f'[ {payment.status.upper()} ]', status_style))
    story.append(Spacer(1, 20))

    # Footer
    footer_style = ParagraphStyle('footer', fontSize=8, textColor=MUTED, alignment=TA_CENTER)
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e2e8f0')))
    story.append(Paragraph('This is a computer-generated receipt. No signature required.', footer_style))

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receipt_{payment.receipt_no}.pdf"'
    return response


# ── Student Result Card ───────────────────────────────────────────────────────

def generate_result_card(student, exam) -> HttpResponse:
    """
    Generates a full marksheet PDF for a student for a given exam.
    """
    buffer = BytesIO()
    doc    = _base_doc(buffer, title=f'Result Card — {student.full_name}')
    story  = []
    styles = getSampleStyleSheet()

    story += _school_header()

    h2 = ParagraphStyle('h2', fontSize=13, textColor=PRIMARY,
                         fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4)
    story.append(Paragraph(f'RESULT CARD — {exam.name.upper()}', h2))
    story.append(Paragraph(f'Academic Year: {exam.academic_year.name}', 
                            ParagraphStyle('yr', fontSize=9, textColor=MUTED, alignment=TA_CENTER)))
    story.append(Spacer(1, 10))

    # Student info
    info_data = [
        ['Name',         student.full_name,    'Admission No.', student.admission_no],
        ['Class',        student.current_class, 'Roll No.',      student.roll_number or '—'],
        ['Father\'s Name', student.father_name,  'Date of Birth', str(student.date_of_birth)],
    ]
    info_table = Table(info_data, colWidths=[3.5*cm, 7*cm, 3.5*cm, 4*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE',  (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (0,-1), MUTED),
        ('TEXTCOLOR', (2,0), (2,-1), MUTED),
        ('BACKGROUND',(0,0), (-1,-1), LIGHT),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [LIGHT, WHITE]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 14))

    # Results table
    from apps.exams.models import ExamResult
    results = ExamResult.objects.filter(
        student=student,
        schedule__exam=exam
    ).select_related('schedule__subject')

    marks_header = [['Subject', 'Max Marks', 'Marks Obtained', 'Percentage', 'Grade', 'Result']]
    marks_rows   = []
    total_max, total_obtained = 0, 0

    for r in results:
        max_m    = r.schedule.max_marks
        obtained = float(r.marks_obtained)
        pct      = round(obtained / max_m * 100, 1) if max_m else 0
        passed   = r.grade not in ('F',) and not r.is_absent
        total_max       += max_m
        total_obtained  += obtained if not r.is_absent else 0
        marks_rows.append([
            r.schedule.subject.name,
            str(max_m),
            'ABSENT' if r.is_absent else str(obtained),
            '—' if r.is_absent else f'{pct}%',
            '—' if r.is_absent else r.grade,
            Paragraph(f'<font color="{"#22c55e" if passed else "#ef4444"}">{"PASS" if passed else "FAIL"}</font>',
                       styles['Normal']),
        ])

    overall_pct = round(total_obtained / total_max * 100, 1) if total_max else 0
    marks_rows.append(['', '', '', '', '', ''])
    marks_rows.append([
        Paragraph('<b>TOTAL</b>', styles['Normal']),
        Paragraph(f'<b>{total_max}</b>', styles['Normal']),
        Paragraph(f'<b>{total_obtained}</b>', styles['Normal']),
        Paragraph(f'<b>{overall_pct}%</b>', styles['Normal']),
        '', '',
    ])

    marks_table = Table(
        marks_header + marks_rows,
        colWidths=[5.5*cm, 2.5*cm, 3.5*cm, 3*cm, 2*cm, 2*cm]
    )
    marks_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME',      (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,0), (-1,-1), 9),
        ('ALIGN',         (1,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS',(0,1), (-1,-3), [WHITE, LIGHT]),
        ('LINEABOVE',     (0,-1), (-1,-1), 1, PRIMARY),
        ('FONTNAME',      (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID',          (0,0), (-1,-2), 0.25, colors.HexColor('#e2e8f0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
    ]))
    story.append(marks_table)
    story.append(Spacer(1, 16))

    # Grade summary
    grade_map = [
        ('A+ (90-100%)', SUCCESS), ('A (80-89%)', SUCCESS),
        ('B+ (70-79%)', ACCENT),   ('B (60-69%)', ACCENT),
        ('C (50-59%)', colors.orange), ('D (35-49%)', colors.orange),
        ('F (< 35%)', DANGER),
    ]
    grade_data = [['Grade Scale'] + [g for g, _ in grade_map]]
    grade_table = Table(grade_data, colWidths=[3*cm] + [2.2*cm]*7)
    grade_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 8),
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,-1), MUTED),
        ('ALIGN',     (0,0), (-1,-1), 'CENTER'),
        ('BOX',       (0,0), (-1,-1), 0.3, colors.HexColor('#e2e8f0')),
        ('GRID',      (0,0), (-1,-1), 0.3, colors.HexColor('#e2e8f0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
    ]))
    story.append(grade_table)
    story.append(Spacer(1, 20))

    # Signature row
    sig_data = [['Class Teacher', 'Exam Controller', 'Principal']]
    sig_table = Table(sig_data, colWidths=[6*cm, 6*cm, 6*cm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',  (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,-1), MUTED),
        ('ALIGN',     (0,0), (-1,-1), 'CENTER'),
        ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('TOPPADDING',(0,0), (-1,-1), 8),
    ]))
    story.append(sig_table)

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="result_{student.admission_no}_{exam.id}.pdf"'
    )
    return response


# ── Attendance Report ─────────────────────────────────────────────────────────

def generate_attendance_report(section, from_date, to_date) -> HttpResponse:
    """Section-wise attendance report for a date range."""
    from apps.attendance.models import AttendanceRecord
    from apps.students.models import Student

    buffer = BytesIO()
    doc    = _base_doc(buffer, title='Attendance Report', pagesize=landscape(A4))
    story  = []

    story += _school_header()

    h2 = ParagraphStyle('h2', fontSize=12, textColor=PRIMARY,
                         fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4)
    story.append(Paragraph(
        f'ATTENDANCE REPORT — {section} | {from_date} to {to_date}', h2
    ))
    story.append(Spacer(1, 10))

    students = Student.objects.filter(section=section, is_active=True).order_by('roll_number')
    header   = [['#', 'Admission No', 'Student Name', 'Present', 'Absent', 'Late', 'Total Days', '%']]
    rows     = []

    for i, s in enumerate(students, 1):
        records = AttendanceRecord.objects.filter(student=s, date__range=[from_date, to_date])
        total   = records.count()
        present = records.filter(status='present').count()
        absent  = records.filter(status='absent').count()
        late    = records.filter(status='late').count()
        pct     = round((present + late) / total * 100, 1) if total else 0
        rows.append([
            str(i), s.admission_no, s.full_name,
            str(present), str(absent), str(late), str(total),
            f'{pct}%'
        ])

    table = Table(header + rows, colWidths=[1*cm, 3*cm, 6*cm, 2*cm, 2*cm, 2*cm, 3*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('ALIGN',         (3,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, LIGHT]),
        ('GRID',          (0,0), (-1,-1), 0.25, colors.HexColor('#e2e8f0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
    ]))
    story.append(table)

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="attendance_{section}_{from_date}.pdf"'
    return response
