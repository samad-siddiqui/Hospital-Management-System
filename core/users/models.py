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
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)

    @property
    def name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def __str__(self):
        return f"Patient: {self.name} <{self.email}>"


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
                                       blank=True,
                                       null=True)

    def __str__(self):
        return self.name


class Doctors(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255,
                                      blank=True, null=True)
    phone = models.CharField(max_length=15, null=True,
                             blank=True
                             )
    email = models.CharField(max_length=255,
                             blank=True,
                             null=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='doctors'
    )

    @property
    def name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def __str__(self):
        return f"Dr. {self.specialization} <{self.department.name}>"


class Status(models.TextChoices):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Appointments(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE,
                                related_name="patient_id")
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE,
                               related_name="doctor_id")
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=15, choices=Status.choices)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient.name} - {self.doctor.name} - {self.appointment_date}"

class Prescriptions(models.Model):
    pass
