"""
python manage.py seed_data

Seeds the database with:
  - 1 school profile
  - 1 academic year (2025-26)
  - 7 grades + 21 sections
  - 5 departments + subjects
  - 10 teachers
  - 50 students
  - Sample fees structures
  - Sample announcements & events
  - Superuser: admin / admin@educore.in / Admin@1234
"""
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed database with demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱  Seeding EduCore database...')
        self._create_superuser()
        self._create_school()
        year = self._create_academic_year()
        grades, sections = self._create_grades_sections()
        depts, subjects = self._create_departments_subjects(grades)
        teachers = self._create_teachers(depts, subjects, sections)
        self._create_students(sections, year)
        self._create_fee_structures(year, grades)
        self._create_announcements()
        self._create_events(year)
        self.stdout.write(self.style.SUCCESS('✅  Seeding complete!'))

    # ── helpers ──────────────────────────────────────────────────────────────

    def _create_superuser(self):
        from apps.core.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin', email='admin@educore.in',
                password='Admin@1234', role='super_admin',
                first_name='Super', last_name='Admin'
            )
            self.stdout.write('  👤  Superuser created  (admin / Admin@1234)')

    def _create_school(self):
        from apps.core.models import SchoolProfile
        SchoolProfile.objects.get_or_create(
            name='Greenfield Public School',
            defaults=dict(
                address='#42, MG Road', city='Bengaluru', state='Karnataka',
                pincode='560001', phone='080-12345678',
                email='info@greenfieldschool.in', board='CBSE',
                founded_year=1994, principal_name='Dr. Ramesh Kumar',
            )
        )

    def _create_academic_year(self):
        from apps.core.models import AcademicYear
        year, _ = AcademicYear.objects.get_or_create(
            name='2025-26',
            defaults=dict(start_date=date(2025, 6, 1), end_date=date(2026, 3, 31), is_current=True)
        )
        return year

    def _create_grades_sections(self):
        from apps.core.models import Grade, Section
        grades = []
        sections = []
        for i in range(6, 13):
            g, _ = Grade.objects.get_or_create(
                name=f'Grade {i}', defaults={'numeric_grade': i, 'order': i - 5}
            )
            grades.append(g)
            for sec_name in ['A', 'B', 'C'] if i <= 8 else ['A', 'B']:
                s, _ = Section.objects.get_or_create(grade=g, name=sec_name)
                sections.append(s)
        self.stdout.write(f'  📚  {len(grades)} grades, {len(sections)} sections')
        return grades, sections

    def _create_departments_subjects(self, grades):
        from apps.teachers.models import Department, Subject
        dept_data = {
            'Mathematics':    [('Algebra', 'MATH01'), ('Calculus', 'MATH02'), ('Statistics', 'MATH03')],
            'Science':        [('Physics', 'SCI01'), ('Chemistry', 'SCI02'), ('Biology', 'SCI03')],
            'English':        [('Literature', 'ENG01'), ('Grammar', 'ENG02')],
            'Social Studies': [('History', 'SS01'), ('Geography', 'SS02'), ('Civics', 'SS03')],
            'Computer Science': [('Programming', 'CS01'), ('Information Tech', 'CS02')],
        }
        depts = []
        subjects = []
        for dept_name, subjs in dept_data.items():
            d, _ = Department.objects.get_or_create(name=dept_name)
            depts.append(d)
            for subj_name, code in subjs:
                s, _ = Subject.objects.get_or_create(
                    code=code, defaults={'name': subj_name, 'department': d}
                )
                s.grades.set(grades)
                subjects.append(s)
        return depts, subjects

    def _create_teachers(self, depts, subjects, sections):
        from apps.core.models import User
        from apps.teachers.models import Teacher
        teacher_data = [
            ('savitha', 'Savitha', 'Iyer',    'savitha@gs.in',  0),
            ('arun',    'Arun',    'Kumar',    'arun@gs.in',     1),
            ('preethi', 'Preethi', 'Nair',     'preethi@gs.in',  2),
            ('ramesh',  'Ramesh',  'Babu',     'ramesh@gs.in',   3),
            ('kavitha', 'Kavitha', 'Devi',     'kavitha@gs.in',  1),
            ('sunil',   'Sunil',   'Verma',    'sunil@gs.in',    4),
            ('deepa',   'Deepa',   'Sharma',   'deepa@gs.in',    0),
            ('venkat',  'Venkat',  'Reddy',    'venkat@gs.in',   3),
            ('meena',   'Meena',   'Pillai',   'meena@gs.in',    2),
            ('rajan',   'Rajan',   'Thomas',   'rajan@gs.in',    4),
        ]
        teachers = []
        for idx, (uname, fname, lname, email, dept_idx) in enumerate(teacher_data):
            u, _ = User.objects.get_or_create(
                username=uname,
                defaults=dict(first_name=fname, last_name=lname, email=email,
                              role='teacher', password='temp')
            )
            if _:
                u.set_password('Teacher@1234')
                u.save()
            t, _ = Teacher.objects.get_or_create(
                user=u,
                defaults=dict(
                    employee_id=f'T{idx+1:03d}',
                    department=depts[dept_idx % len(depts)],
                    joining_date=date(2020, 6, 1) - timedelta(days=idx * 180),
                    experience_years=random.randint(3, 15),
                    qualification=random.choice(['B.Ed', 'M.Ed', 'M.Sc', 'M.Tech']),
                )
            )
            t.subjects.set(subjects[dept_idx:dept_idx + 2])
            t.sections.set(sections[:3])
            teachers.append(t)
        self.stdout.write(f'  👩‍🏫  {len(teachers)} teachers created')
        return teachers

    def _create_students(self, sections, year):
        from apps.core.models import User
        from apps.students.models import Student
        first_names = ['Aarav','Priya','Rohan','Ananya','Karthik','Sneha','Arjun',
                       'Divya','Vijay','Lakshmi','Siddharth','Pooja','Rahul','Nisha',
                       'Aditya','Meera','Rajesh','Sunita','Harish','Kavya']
        last_names  = ['Sharma','Mehta','Singh','Patel','Reddy','Joshi','Nair',
                       'Rao','Kumar','Iyer','Verma','Gupta','Pillai','Chauhan']
        count = 0
        for section in sections:
            for j in range(random.randint(3, 5)):
                fname = random.choice(first_names)
                lname = random.choice(last_names)
                adm   = f'GF{2025}{count + 1:04d}'
                if not Student.objects.filter(admission_no=adm).exists():
                    Student.objects.create(
                        admission_no=adm, first_name=fname, last_name=lname,
                        date_of_birth=date(2008, random.randint(1,12), random.randint(1,28)),
                        gender=random.choice(['M','F']),
                        section=section, academic_year=year,
                        admission_date=date(2025, 6, 1),
                        roll_number=str(j + 1),
                        father_name=f'{random.choice(last_names)} {lname}',
                        parent_phone=f'9{random.randint(100000000,999999999)}',
                        parent_email=f'{fname.lower()}.parent@email.com',
                        address='123 Main Street', city='Bengaluru', pincode='560001',
                    )
                    count += 1
        self.stdout.write(f'  👨‍🎓  {count} students created')

    def _create_fee_structures(self, year, grades):
        from apps.fees.models import FeeCategory, FeeStructure
        cats = [
            ('Tuition Fee', True),
            ('Transport Fee', False),
            ('Library Fee', False),
            ('Exam Fee', True),
            ('Sports Fee', False),
        ]
        amounts = [12500, 3200, 500, 800, 600]
        for grade in grades:
            for (cat_name, mandatory), amt in zip(cats, amounts):
                cat, _ = FeeCategory.objects.get_or_create(
                    name=cat_name, defaults={'is_mandatory': mandatory}
                )
                FeeStructure.objects.get_or_create(
                    academic_year=year, grade=grade, category=cat, term='annual',
                    defaults=dict(
                        amount=amt + (grade.numeric_grade - 6) * 200,
                        due_date=date(2025, 7, 31),
                        late_fee_per_day=10,
                    )
                )
        self.stdout.write('  💳  Fee structures created')

    def _create_announcements(self):
        from apps.core.models import User
        from apps.announcements.models import Announcement
        admin = User.objects.filter(role='super_admin').first()
        anns = [
            ('Annual Sports Day — Registration Open', 'Students wishing to participate must register by March 22.', 'high', 'all'),
            ('Parent-Teacher Meeting — March 20', 'All parents are requested to attend PTM on Friday, March 20th.', 'normal', 'parents'),
            ('Science Exhibition — Project Submissions', 'Final projects to be submitted to the Science Lab by March 23.', 'normal', 'students'),
            ('Library Closure Notice', 'Library will remain closed on March 18 for inventory audit.', 'normal', 'all'),
        ]
        for title, content, priority, audience in anns:
            Announcement.objects.get_or_create(
                title=title,
                defaults=dict(content=content, priority=priority, audience=audience, created_by=admin)
            )
        self.stdout.write('  📣  Announcements created')

    def _create_events(self, year):
        from apps.core.models import User
        from apps.announcements.models import Event
        admin = User.objects.filter(role='super_admin').first()
        events = [
            ('Annual Sports Day',       'sports',   date(2026, 3, 28), date(2026, 3, 28), 'School Ground'),
            ('Science Exhibition',      'cultural', date(2026, 3, 25), date(2026, 3, 25), 'Main Hall'),
            ('Parent-Teacher Meeting',  'meeting',  date(2026, 3, 20), date(2026, 3, 20), 'Classrooms'),
            ('Annual Examination',      'exam',     date(2026, 4,  1), date(2026, 4, 20), 'Exam Hall'),
            ('Summer Vacation',         'holiday',  date(2026, 4, 25), date(2026, 6,  2), '', ),
        ]
        for title, etype, start, end, venue in events:
            Event.objects.get_or_create(
                title=title,
                defaults=dict(event_type=etype, start_date=start, end_date=end,
                              venue=venue, created_by=admin,
                              is_holiday=(etype == 'holiday'))
            )
        self.stdout.write('  📅  Events created')
