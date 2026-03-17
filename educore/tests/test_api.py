"""
tests/test_api.py

Core API tests for EduCore ERP.
Run: pytest tests/test_api.py -v
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    from apps.core.models import User
    user = User.objects.create_superuser(
        username='testadmin', email='testadmin@test.com',
        password='TestPass@123', role='admin',
        first_name='Test', last_name='Admin'
    )
    return user


@pytest.fixture
def auth_client(client, admin_user):
    response = client.post('/api/auth/login/', {
        'username': 'testadmin',
        'password': 'TestPass@123'
    }, format='json')
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


@pytest.fixture
def academic_year(db):
    from apps.core.models import AcademicYear
    from datetime import date
    return AcademicYear.objects.create(
        name='2025-26',
        start_date=date(2025, 6, 1),
        end_date=date(2026, 3, 31),
        is_current=True
    )


@pytest.fixture
def grade(db):
    from apps.core.models import Grade
    return Grade.objects.create(name='Grade 10', numeric_grade=10, order=5)


@pytest.fixture
def section(db, grade):
    from apps.core.models import Section
    return Section.objects.create(grade=grade, name='A', capacity=45)


@pytest.fixture
def student(db, section, academic_year):
    from apps.students.models import Student
    from datetime import date
    return Student.objects.create(
        admission_no='GF2025001',
        first_name='Aarav',
        last_name='Sharma',
        date_of_birth=date(2008, 5, 15),
        gender='M',
        section=section,
        academic_year=academic_year,
        admission_date=date(2025, 6, 1),
        roll_number='1',
        father_name='Rajesh Sharma',
        parent_phone='9876543210',
        address='123 MG Road',
        city='Bengaluru',
        pincode='560001',
    )


# ── Auth Tests ────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAuth:

    def test_login_success(self, client, admin_user):
        resp = client.post('/api/auth/login/', {
            'username': 'testadmin', 'password': 'TestPass@123'
        }, format='json')
        assert resp.status_code == status.HTTP_200_OK
        assert 'access'  in resp.data
        assert 'refresh' in resp.data
        assert resp.data['user']['role'] == 'admin'

    def test_login_wrong_password(self, client, admin_user):
        resp = client.post('/api/auth/login/', {
            'username': 'testadmin', 'password': 'wrongpassword'
        }, format='json')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_access_denied(self, client):
        resp = client.get('/api/students/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, client, admin_user):
        login = client.post('/api/auth/login/', {
            'username': 'testadmin', 'password': 'TestPass@123'
        }, format='json')
        refresh = login.data['refresh']
        resp = client.post('/api/auth/refresh/', {'refresh': refresh}, format='json')
        assert resp.status_code == status.HTTP_200_OK
        assert 'access' in resp.data

    def test_me_endpoint(self, auth_client):
        resp = auth_client.get('/api/core/me/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['username'] == 'testadmin'


# ── Student Tests ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestStudents:

    def test_list_students(self, auth_client, student):
        resp = auth_client.get('/api/students/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] >= 1

    def test_create_student(self, auth_client, section, academic_year):
        from datetime import date
        payload = {
            'admission_no':   'GF2025099',
            'first_name':     'Priya',
            'last_name':      'Mehta',
            'date_of_birth':  '2008-08-20',
            'gender':         'F',
            'section':        section.id,
            'academic_year':  academic_year.id,
            'admission_date': '2025-06-01',
            'roll_number':    '2',
            'father_name':    'Suresh Mehta',
            'parent_phone':   '9123456780',
            'address':        '45 Park Street',
            'city':           'Bengaluru',
            'pincode':        '560002',
        }
        resp = auth_client.post('/api/students/', payload, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['admission_no'] == 'GF2025099'
        assert resp.data['full_name'] == 'Priya Mehta'

    def test_get_student_detail(self, auth_client, student):
        resp = auth_client.get(f'/api/students/{student.id}/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['admission_no'] == 'GF2025001'

    def test_search_student(self, auth_client, student):
        resp = auth_client.get('/api/students/?search=Aarav')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] >= 1

    def test_filter_by_section(self, auth_client, student, section):
        resp = auth_client.get(f'/api/students/?section={section.id}')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] >= 1

    def test_deactivate_student(self, auth_client, student):
        resp = auth_client.post(f'/api/students/{student.id}/deactivate/')
        assert resp.status_code == status.HTTP_200_OK
        student.refresh_from_db()
        assert student.is_active is False

    def test_duplicate_admission_no_rejected(self, auth_client, student, section, academic_year):
        payload = {
            'admission_no': 'GF2025001',  # duplicate
            'first_name': 'Duplicate', 'last_name': 'Student',
            'date_of_birth': '2009-01-01', 'gender': 'M',
            'section': section.id, 'academic_year': academic_year.id,
            'admission_date': '2025-06-01', 'father_name': 'X',
            'parent_phone': '9000000000', 'address': 'X', 'city': 'X', 'pincode': '0',
        }
        resp = auth_client.post('/api/students/', payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ── Attendance Tests ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAttendance:

    def test_bulk_mark_attendance(self, auth_client, student, section):
        from django.utils import timezone
        today = str(timezone.localdate())
        payload = {
            'section_id': section.id,
            'date': today,
            'records': [
                {'student_id': student.id, 'status': 'present'},
            ]
        }
        resp = auth_client.post('/api/attendance/bulk_mark/', payload, format='json')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['created'] == 1

    def test_bulk_mark_idempotent(self, auth_client, student, section):
        from django.utils import timezone
        today = str(timezone.localdate())
        payload = {
            'section_id': section.id,
            'date': today,
            'records': [{'student_id': student.id, 'status': 'present'}]
        }
        auth_client.post('/api/attendance/bulk_mark/', payload, format='json')
        resp = auth_client.post('/api/attendance/bulk_mark/', payload, format='json')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['updated'] == 1

    def test_today_summary(self, auth_client, student, section):
        from django.utils import timezone
        from apps.attendance.models import AttendanceRecord
        AttendanceRecord.objects.create(
            student=student, date=timezone.localdate(),
            status='present', marked_by=None
        )
        resp = auth_client.get('/api/attendance/today_summary/')
        assert resp.status_code == status.HTTP_200_OK
        assert 'present' in resp.data
        assert resp.data['present'] >= 1


# ── Fee Tests ─────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFees:

    def test_fee_summary(self, auth_client):
        resp = auth_client.get('/api/fees/invoices/summary/')
        assert resp.status_code == status.HTTP_200_OK
        assert 'total_due' in resp.data
        assert 'total_paid' in resp.data

    def test_create_fee_category(self, auth_client):
        resp = auth_client.post('/api/fees/categories/', {
            'name': 'Sports Fee', 'is_mandatory': False
        }, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['name'] == 'Sports Fee'


# ── Grade & Section Tests ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGradesAndSections:

    def test_list_grades(self, auth_client, grade):
        resp = auth_client.get('/api/core/grades/')
        assert resp.status_code == status.HTTP_200_OK

    def test_list_sections(self, auth_client, section):
        resp = auth_client.get('/api/core/sections/')
        assert resp.status_code == status.HTTP_200_OK

    def test_section_student_count(self, auth_client, section, student):
        resp = auth_client.get(f'/api/core/sections/{section.id}/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['student_count'] == 1


# ── Error Handling Tests ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestErrorHandling:

    def test_404_returns_json(self, auth_client):
        resp = auth_client.get('/api/students/99999/')
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.data['error'] is True
        assert resp.data['code'] == 'NOT_FOUND'

    def test_validation_error_shape(self, auth_client):
        resp = auth_client.post('/api/students/', {}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data['error'] is True
        assert resp.data['code'] == 'VALIDATION_ERROR'
        assert 'details' in resp.data
