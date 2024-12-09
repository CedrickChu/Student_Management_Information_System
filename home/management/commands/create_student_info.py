import random
from django.core.management.base import BaseCommand
from home.models import ParentGuardian, Student, SchoolYear, Section, GradeLevel, StudentInfo

class Command(BaseCommand):
    help = 'Create 100 StudentYearInfo entries'

    def handle(self, *args, **kwargs):
        # Fetch existing students, school years, sections, and grade levels
        students = Student.objects.all()
        school_years = SchoolYear.objects.all()
        sections = Section.objects.all()
        grade_levels = GradeLevel.objects.all()

        if not students:
            self.stdout.write(self.style.ERROR('No students found in the database. Please create student records first.'))
            return

        if not school_years:
            self.stdout.write(self.style.ERROR('No school years found in the database. Please create school year records first.'))
            return

        if not sections:
            self.stdout.write(self.style.ERROR('No sections found in the database. Please create section records first.'))
            return

        if not grade_levels:
            self.stdout.write(self.style.ERROR('No grade levels found in the database. Please create grade level records first.'))
            return

        for _ in range(100):  # Create 100 entries
            student = random.choice(students)
            school_year = random.choice(school_years)
            section = random.choice(sections)
            grade_level = random.choice(grade_levels)
            
            # Check if the combination of student and school_year already exists
            if StudentInfo.objects.filter(student=student, school_year=school_year).exists():
                continue  # Skip this entry and move to the next one
            
            # Randomly assign payment status for the four quarters
            paid_first_quarter = random.choice([True, False])
            paid_second_quarter = random.choice([True, False])
            paid_third_quarter = random.choice([True, False])
            paid_fourth_quarter = random.choice([True, False])
            
            # Randomly assign status: new, old, or transferee
            status = random.choice(['new', 'old', 'transferee'])

            # Create the StudentInfo record
            student_info = StudentInfo(
                student=student,
                school_year=school_year,
                section=section,
                grade_level=grade_level,
                paid_first_quarter=paid_first_quarter,
                paid_second_quarter=paid_second_quarter,
                paid_third_quarter=paid_third_quarter,
                paid_fourth_quarter=paid_fourth_quarter,
                status=status
            )
            student_info.save()

        self.stdout.write(self.style.SUCCESS('Successfully created 100 StudentYearInfo entries'))
