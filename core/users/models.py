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
    patient = models.OneToOneField(Patients, unique=True,
                                   on_delete=models.CASCADE)
    provider = models.CharField(max_length=255,
                                blank=True,
                                null=True)
    policy_number = models.CharField(max_length=255, blank=True, null=True)
    coverage_details = models.TextField(blank=True, null=True)
