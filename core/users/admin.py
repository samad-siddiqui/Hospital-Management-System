from django.contrib import admin
from .models import CustomUser, Patients, Department
from .models import Doctors, Insurance, Appointments


admin.site.site_header = "My Hospital Administration System"
admin.site.site_title = "Hospital Admin Portal"
admin.site.index_title = "Welcome to the Hospital Management Dashboard"

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Patients)
admin.site.register(Department)
admin.site.register(Doctors)
admin.site.register(Insurance)
admin.site.register(Appointments)
