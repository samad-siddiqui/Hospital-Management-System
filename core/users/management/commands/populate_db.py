import random
from datetime import timedelta
from faker import Faker
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from users.models import (
    CustomUser, Patients, Doctors, Department, Appointments, Prescriptions,
    Surgeries, Patient_Doctor, Insurance
)

fake = Faker()


class Command(BaseCommand):
    help = "Populate database with fake data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Populating database with fake data...")

        # Create Departments
        departments = []
        for _ in range(5):
            dept = Department.objects.create(
                name=fake.unique.company()
            )
            departments.append(dept)

        self.stdout.write("✔ Created Departments")

        # Create Users, Patients, and Doctors
        doctors = []
        patients = []
        users = []

        for _ in range(10):  # 10 Doctors
            user = CustomUser.objects.create_user(
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_staff=True
            )
            doctor = Doctors.objects.create(
                user=user,
                specialization=fake.job(),
                department=random.choice(departments)
            )
            doctors.append(doctor)
            users.append(user)

        for _ in range(20):  # 20 Patients
            user = CustomUser.objects.create_user(
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            patient = Patients.objects.create(
                user=user,
                dob=fake.date_of_birth(minimum_age=18, maximum_age=90),
                gender=random.choice(["Male", "Female", "Other"]),
                address=fake.address()
            )
            patients.append(patient)
            users.append(user)

        self.stdout.write("✔ Created Users, Doctors, and Patients")

        # Assign Patients to Doctors
        for patient in patients:
            # 1 to 3 doctors per patient
            assigned_doctors = random.sample(doctors, k=random.randint(1, 3))
            for doctor in assigned_doctors:
                Patient_Doctor.objects.create(
                    patient=patient,
                    doctor=doctor,
                    relationship_type=random.choice(
                        ["Primary_Care", "Consultation", "Specialist"])
                )

        self.stdout.write("✔ Assigned Patients to Doctors")

        # Create Appointments
        appointments = []
        for _ in range(30):
            appointment = Appointments.objects.create(
                patient=random.choice(patients),
                doctor=random.choice(doctors),
                appointment_date=now() + timedelta(days=random.randint(1, 30)),
                status=random.choice(["Scheduled", "Completed", "Cancelled"]),
                notes=fake.text(max_nb_chars=200)
            )
            appointments.append(appointment)

        self.stdout.write("✔ Created Appointments")

        # Create Prescriptions
        # Half of the appointments get prescriptions
        for appointment in appointments[:15]:
            Prescriptions.objects.create(
                appointment=appointment,
                doctor=appointment.doctor,
                patient=appointment.patient,
                medicine_detail=fake.sentence(),
                instructions=fake.sentence()
            )

        self.stdout.write("✔ Created Prescriptions")

        # Create Surgeries
        for _ in range(10):  # 10 Surgeries
            Surgeries.objects.create(
                patient=random.choice(patients),
                doctor=random.choice(doctors),
                surgery_date=now() + timedelta(days=random.randint(10, 60)),
                surgery_type=fake.bs(),
                notes=fake.text()
            )

        self.stdout.write("✔ Created Surgeries")

        # Create Insurance for some Patients
        # 10 Patients get insurance
        for patient in random.sample(patients, k=10):
            Insurance.objects.create(
                patient=patient,
                provider=fake.company(),
                policy_number=fake.uuid4(),
                coverage_details=fake.text()
            )

        self.stdout.write("✔ Created Insurance Data")

        self.stdout.write(self.style.SUCCESS(
            "🎉 Database population complete!"))
