import random
from django.core.management.base import BaseCommand
from home.models import GradeLevel, Subject

class Command(BaseCommand):
    help = 'Create subjects and assign them to grade levels'

    def handle(self, *args, **kwargs):
        # Fetch all existing grade levels
        grade_levels = GradeLevel.objects.all()

        if not grade_levels:
            self.stdout.write(self.style.ERROR('No grade levels found in the database. Please create grade level records first.'))
            return

        # Adding Nursery and Kindergarten with their respective subjects
        subjects_data = {
           
            "Kinder-1": ["Basic Math", "Art & Crafts", "Reading & Writing", "Physical Activities", "Music", "Introduction to Numbers"],
            "Kinder-2": ["Basic Math", "Art & Crafts", "Reading & Writing", "Physical Activities", "Music", "Introduction to Numbers"],
        }

        # Iterate through each grade level and create subjects for it
        for grade_level_name, subject_list in subjects_data.items():
            try:
                grade_level = grade_levels.get(name=grade_level_name)
            except GradeLevel.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Grade level {grade_level_name} does not exist. Skipping..."))
                continue

            for subject_name in subject_list:
                # Create the subject and link it to the grade level
                subject, created = Subject.objects.get_or_create(name=subject_name, grade_level=grade_level)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Successfully created subject '{subject_name}' for {grade_level_name}."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Subject '{subject_name}' already exists for {grade_level_name}."))
        
        self.stdout.write(self.style.SUCCESS('Successfully created subjects for all grade levels, including Nursery and Kindergarten.'))
