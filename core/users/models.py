from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager


class Gender(models.TextChoices):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=20, blank=True, null=True)
    last_name = models.CharField(max_length=20, blank=True, null=True)
    last_login = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=11, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.email}'

    def has_prem(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class Patients(models.Model):
    patient_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=10,
                              choices=Gender.choices,
                              blank=True, null=True)
    address = models.TextField(max_length=600, blank=True, null=True)

    @property
    def name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def __str__(self):
        return f"Patient: {self.name} <{self.user.email}>"


class Insurance(models.Model):
    insurance_id = models.AutoField(primary_key=True)
    patient = models.OneToOneField(Patients,
                                   on_delete=models.CASCADE)
    provider = models.CharField(max_length=255,
                                blank=True,
                                null=True)
    policy_number = models.CharField(max_length=255, blank=True, null=True)
    coverage_details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Insurance for {self.patient.name}"


class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, blank=True, null=True)
    head_doctor = models.OneToOneField("Doctors", on_delete=models.SET_NULL,
                                       related_name="head_doctor",
                                       blank=True,
                                       null=True)

    def __str__(self):
        return self.name


class Doctors(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255,
                                      blank=True, null=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='doctors'
    )
    patient = models.ManyToManyField(Patients,
                                     related_name="patient_doc")

    @property
    def name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def __str__(self):
        dept_name = self.department.name if self.department else "No Department"
        return f"Dr. {self.specialization} <{dept_name}>"


class Status(models.TextChoices):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Appointments(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE,
                                related_name="appointments_as_patient")
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE,
                               related_name="appointments_as_doctor")
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=15, choices=Status.choices)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient.name} - {self.appointment_date}"


class Prescriptions(models.Model):
    prescription_id = models.AutoField(primary_key=True)
    appointment = models.OneToOneField(Appointments,
                                       unique=True,
                                       on_delete=models.CASCADE,
                                       related_name="prescription_appointments"
                                       )
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE,
                               related_name="prescription_doctor_id")
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE,
                                related_name="prescription_patient_id")
    medicine_detail = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Prescription for {self.patient.name}"


class Surgeries(models.Model):
    surgery_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE,
                                related_name="patient_surgery")
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE,
                               related_name="doctor_surgery")
    surgery_date = models.DateTimeField()
    surgery_type = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient.name} - {self.surgery_date}"


class RelationshipType(models.TextChoices):
    PRIMARY_CARE = 'Primary_Care'
    CONSULTATION = 'Consultation'
    SPECIALIST = 'Specialist'


class Patient_Doctor(models.Model):
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE,
                                related_name="doctor_relationships")
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE,
                               related_name="patient_relationships")
    relationship_type = models.CharField(max_length=15,
                                         choices=RelationshipType.choices,
                                         default=RelationshipType.PRIMARY_CARE)

    def __str__(self):
        return f"{self.patient.user.first_name}-{self.doctor.user.first_name}"
