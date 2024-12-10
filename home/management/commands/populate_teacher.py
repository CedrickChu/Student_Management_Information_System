import random
import uuid
from django.core.management.base import BaseCommand
from home.models import Teacher

class Command(BaseCommand):
    help = 'Populate Teacher details with random data'

    def handle(self, *args, **kwargs):
        # Expanded list of Puerto Princesa, Palawan addresses
        addresses = [
            "Rizal Avenue Extension, Puerto Princesa, Palawan",
            "San Pedro, Puerto Princesa, Palawan",
            "Rizal Street, Puerto Princesa, Palawan",
            "Bancao-Bancao, Puerto Princesa, Palawan",
            "Iwahig, Puerto Princesa, Palawan",
            "Manalo Street, Puerto Princesa, Palawan",
            "Brgy. San Jose, Puerto Princesa, Palawan",
            "Quezon Street, Puerto Princesa, Palawan",
            "Rizal Drive, Puerto Princesa, Palawan",
            "Barangay New Public Market, Puerto Princesa, Palawan",
            "Puerto Village, Puerto Princesa, Palawan",
            "Cul-de-Sac, Puerto Princesa, Palawan",
            "Dampalit, Puerto Princesa, Palawan",
            "Mendoza Street, Puerto Princesa, Palawan",
            "Mangingisda Street, Puerto Princesa, Palawan",
            "Barangay Poblacion, Puerto Princesa, Palawan",
            "Pio Del Pilar Street, Puerto Princesa, Palawan",
            "Brgy. Bagumbayan, Puerto Princesa, Palawan",
            "Brgy. San Manuel, Puerto Princesa, Palawan",
            "Bagumbayan Extension, Puerto Princesa, Palawan",
            "Narra Street, Puerto Princesa, Palawan",
            "Roxas Extension, Puerto Princesa, Palawan",
            "Lingsat, Puerto Princesa, Palawan",
            "Sta. Monica, Puerto Princesa, Palawan",
            "Valencia Street, Puerto Princesa, Palawan",
            "San Vicente, Puerto Princesa, Palawan",
            "Sampaguita Street, Puerto Princesa, Palawan",
            "Tungloy, Puerto Princesa, Palawan",
            "Brgy. Tiniguiban, Puerto Princesa, Palawan"
        ]

        # List of 30 sample first, middle, and last names for teachers
        first_names = [
            "Juan", "Maria", "Carlos", "Anna", "Pedro", "Luisa", "Miguel", "Isabel", "Antonio", "Sofia",
            "Jose", "Elena", "Luis", "Carmen", "Raul", "Beatriz", "Javier", "Laura", "Ricardo", "Marta",
            "Felipe", "Angela", "Eduardo", "Vera", "Santiago", "Lorena", "Raquel", "Francisco", "Victor", "Paula"
        ]
        middle_names = [
            "Gomez", "Lopez", "Perez", "Santos", "Garcia", "Fernandez", "Rodriguez", "Diaz", "Martinez", "Torres",
            "Alvarez", "Castillo", "Ramirez", "Reyes", "Jimenez", "Morales", "Gonzalez", "Serrano", "Hernandez", "Vargas",
            "Fuentes", "Moreno", "Cabrera", "Silva", "Campos", "Cortes", "Paredes", "Sanchez", "Estrada", "Valencia"
        ]
        last_names = [
            "Rivera", "Castro", "Martinez", "Vargas", "Morales", "Ramos", "Alvarez", "Herrera", "Gonzalez", "Jimenez",
            "Paredes", "Santiago", "Fuentes", "Lozano", "Romero", "Guerra", "Fernandez", "Mendoza", "Ponce", "Campos",
            "Torres", "Salazar", "Riviera", "Ortega", "Navarro", "Guerrero", "Arroyo", "Lopez", "Silva", "Trinidad"
        ]

        # Define status choices
        status_choices = ["Active", "Inactive"]

        # Generate 40 teachers
        for _ in range(40):
            # Generate an 8-character UUID (using a random UUID and truncating it)
            teacher_id = str(uuid.uuid4().hex[:8])
            first_name = random.choice(first_names)
            middle_name = random.choice(middle_names)
            last_name = random.choice(last_names)
            address = random.choice(addresses)

            # Ensure the phone number starts with "09" and has 10 digits
            contact_info = f"09{random.randint(100000000, 999999999)}"  # Philippine mobile number starting with 09
            
            status = "Active"  

            # Create and save the teacher instance
            teacher = Teacher(
                teacher_id=teacher_id,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                address=address,
                contact_information=contact_info,
                status=status
            )
            teacher.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated 40 teachers'))
