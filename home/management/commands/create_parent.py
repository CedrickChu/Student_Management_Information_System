import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from home.models import ParentGuardian, Student  # Replace 'your_app' with the actual app name

# Expanded list of first and last names (same as before)
first_names = [
    "Juan", "Maria", "Carlos", "Sofia", "Eduardo", "Elena", "Antonio", "Clara", 
    "Roberto", "Isabel", "Francisco", "Lina", "Gabriel", "Paula", "Hector", 
    "Victoria", "Luis", "Rosario", "Carlos", "Angel", "Carmen", "Miguel", "Julia", 
    "Raul", "Amelia", "Antonio", "Sandra", "Felipe", "Sofia", "Manuel", "Beatriz"
]

last_names = [
    "Cruz", "Reyes", "Lopez", "Santos", "Garcia", "Delgado", "Mendoza", "Villanueva", 
    "Aquino", "Gonzales", "Diaz", "Martinez", "Torres", "Castillo", "Fernandez", 
    "Ramirez", "Alvarez", "Perez", "Gomez", "Moreno", "Jimenez", "Rodriguez", 
    "Serrano", "Navarro", "Vasquez", "Ponce", "Rivera", "Gonzalez", "Suarez", "Ramos"
]

# Utility to generate random birthdates within a range
def random_birth_date():
    start_date = date(2010, 1, 1)
    end_date = date(2017, 12, 31)
    delta = end_date - start_date
    return start_date + timedelta(days=random.randint(0, delta.days))

class Command(BaseCommand):
    help = 'Create 100 student entries, each linked to a parent/guardian'

    def handle(self, *args, **kwargs):
        # Fetch existing parents
        parents = ParentGuardian.objects.all()

        if parents.count() == 0:
            self.stdout.write(self.style.ERROR('No parents found in the database. Please create parent records first.'))
            return

        for _ in range(50):
            first_name = random.choice(first_names)
            middle_name = random.choice([None, "De La Cruz", "Perez", "Santos", "Gonzalez"])  # Some may not have middle name
            last_name = random.choice(last_names)
            birth_date = random_birth_date()
            place_of_birth = f"Puerto Princesa City, Palawan"
            gender = random.choice([('M'), ('F')])
            address = f"Brgy. {random.choice(['San Pedro', 'Bancao-Bancao', 'Maligaya', 'San Jose', 'Tagpait'])}, Puerto Princesa City"
            
            # Randomly select a parent for this student
            parent_guardian = random.choice(parents)

            # Generate a random LRN that starts with 2020- or 2024- followed by a random 4-digit number
            lrn_prefix = random.choice(["2020", "2024"])
            lrn = f"{lrn_prefix}-{random.randint(1000, 9999)}"

            student = Student(
                lrn=lrn,
                first_name=first_name,
                middle_name=middle_name if middle_name else "",  # Ensure no None value
                last_name=last_name,
                birth_date=birth_date,
                place_of_birth=place_of_birth,
                gender=gender,
                address=address,
                parent_guardians=parent_guardian
            )
            student.save()

        self.stdout.write(self.style.SUCCESS('Successfully created 100 Student entries with parent/guardian relationships'))
