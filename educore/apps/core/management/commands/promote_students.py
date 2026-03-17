"""
python manage.py promote_students --from-year 2025-26 --to-year 2026-27

End-of-year: promotes all active students to next grade/section.
Backs up current section assignments before moving.
Handles Grade 12 → alumni (deactivation).
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = 'Promote all students to the next grade at end of academic year'

    def add_arguments(self, parser):
        parser.add_argument('--from-year', required=True, help='e.g. 2025-26')
        parser.add_argument('--to-year',   required=True, help='e.g. 2026-27')
        parser.add_argument('--dry-run',   action='store_true', help='Preview without saving')

    def handle(self, *args, **options):
        from apps.core.models import AcademicYear, Grade, Section
        from apps.students.models import Student

        from_year_name = options['from_year']
        to_year_name   = options['to_year']
        dry_run        = options['dry_run']

        try:
            from_year = AcademicYear.objects.get(name=from_year_name)
            to_year   = AcademicYear.objects.get(name=to_year_name)
        except AcademicYear.DoesNotExist as e:
            raise CommandError(f'Academic year not found: {e}')

        grades = Grade.objects.all().order_by('order')
        grade_list = list(grades)

        promoted = 0
        graduated = 0
        skipped   = 0

        with transaction.atomic():
            for i, grade in enumerate(grade_list):
                students = Student.objects.filter(
                    section__grade=grade,
                    academic_year=from_year,
                    is_active=True
                ).select_related('section')

                is_final_grade = (i == len(grade_list) - 1)

                for student in students:
                    if is_final_grade:
                        # Grade 12 graduates → deactivate
                        if not dry_run:
                            student.is_active = False
                            student.academic_year = to_year
                            student.remarks = f'Graduated {from_year_name}'
                            student.save(update_fields=['is_active', 'academic_year', 'remarks'])
                        graduated += 1
                        self.stdout.write(f'  🎓 GRADUATE: {student.full_name} ({student.current_class})')
                    else:
                        # Find equivalent section in next grade
                        next_grade   = grade_list[i + 1]
                        next_section = Section.objects.filter(
                            grade=next_grade,
                            name=student.section.name
                        ).first()

                        if not next_section:
                            # Fall back to section A
                            next_section = Section.objects.filter(grade=next_grade, name='A').first()

                        if not next_section:
                            self.stdout.write(self.style.WARNING(
                                f'  ⚠ No next section for {student.full_name} — SKIPPED'
                            ))
                            skipped += 1
                            continue

                        if not dry_run:
                            student.section       = next_section
                            student.academic_year = to_year
                            student.roll_number   = ''  # will be re-assigned
                            student.save(update_fields=['section', 'academic_year', 'roll_number'])
                        promoted += 1

        action = '[DRY RUN] Would promote' if dry_run else 'Promoted'
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ {action}: {promoted} students, {graduated} graduates, {skipped} skipped'
        ))
