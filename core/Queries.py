# 1. Retrieve all **appointments** along with their **related patient and doctor** details, but only for appointments scheduled in the **next 7 days**.

>>> today = now()
>>> next_week = today + timedelta(days=7)
>>> appointment = Appointments.objects.filter(appointment_date__range=[today, next_week]).select_related("patient", "doctor")
# 2. Get all **patients** who **do not have insurance** and have had **at least one appointment in the past month**.

>>> last_month = now() - timedelta(days=30)
>>> patients = Patients.objects.filter(insurance__isnull=True).filter(appointments_as_patient__appointment_date__gte=last_month).distinct()

# 3. Find all **doctors** who have handled **more than 10 appointments** in the last **6 months**.

>>> doctors = Doctors.objects.annotate(appointment_count = Count("appointments_as_doctor", filter= Q(appointments_as_doctor__appointment_date__gte = last_6_months))).filter(appointment_count__gt=10).distinct()

# 4. Update the **appointment status** to `"Missed"` where the **appointment date** is in the past and the **status is still "Scheduled"**.

>>> status = Appointments.objects.filter(appointment_date__lt=now(), status='Scheduled').update(status = 'Cancelled')

# 6. Retrieve a list of **distinct insurance providers** that have **at least one active patient**, ordered **alphabetically**.

>>> providers = Insurance.objects.filter(patient__user__is_active=True).values('provider').distinct().order_by('provider')

# 7. Find **departments** that have **at least 3 doctors** but **no head doctor assigned**.

departments = Department.objects.annotate(doctor_count=Count('doctors')).filter(doctor_count__gte=3, head_doctor__isnull=True)

# 9. Retrieve all **patients with their prescriptions**, but only if they had an **appointment in the last 30 days**, and order by the **most recent appointment**.

today = now()
time_limit = today-timedelta(days=30)
>>> patient_pre = Patients.objects.filter(appointments_as_patient__appointment_date__gte=time_limit).prefetch_related(Prefetch('prescription_patient_id', queryset=Prescriptions.objects.all())).order_by("-appointments_as_patient__appointment_date")

# 11. Find the **average age of patients** who have had **at least one surgery** but have **never had an appointment**.

>>> patient_avg = Patients.objects.filter(patient_surgery__isnull=False, appointments_as_patient__isnull=True, dob__isnull=False)
>>> ages = [(today.year - patient.dob.year) for patient in patient_avg]
>>> average_age = sum(ages)/len(ages) 
>>> print(average_age)
68.0


# 12. **Bulk create** new **appointments** for all **patients** who have visited **a specific doctor**, ensuring they are not **already scheduled**.

future_date = now() + timedelta(days=3)
doctor = Doctors.objects.get(pk=1)
visited_patients = Patient.objects.filter(appointments_as_patient__doctor=doctor).distinct()
already_scheduled = Appointments.objects.filter(doctor=doctor, patient__in =visited_patients, status = "Scheduled")
elig_patients = already_scheduled.exclude(pk__in=already_scheduled)
new_appointments = [Appointments(doctor=doctor, patient=patient, appointment_date=future_date, status="Scheduled") for patient in elig_patients]
Appointments.objects.bulk_create(new_appointments)

# 13. Retrieve the **number of prescriptions written** by each doctor, but only include doctors who have **written at least 5 prescriptions**.

pres = Doctors.objects.annotate(prescription_count = Count('prescription_doctor_id')).filter(prescription_count__gte=5)
print(pres)

# 14. Retrieve **appointments** where the **patient’s insurance provider is "XYZ Insurance"**, but exclude appointments scheduled for **Sunday**.

>>> Appointments.objects.filter(patient__insurance_patient__provider='XYZ Insurance').exclude(appointment_date__week_day=1)

# 1. Retrieve a list of **doctor IDs** who have handled **at least 5 surgeries** in the **past year**.

past_year = now() - timedelta(days=365)
Doctor.objects.annotate( surgery_count = Count("doctor_surgery", filter=Q(doctor_surgery__surgery_date__gte=past_year))).filter(surgery_count__gte=5).values__list('doctor_id', flat=True)

# 2. Get a **union** of all **patients who have at least one appointment** and **patients who have at least one surgery**.


patient_appoint = Patients.objects.filter(appointments_as_patient__isnull = False).distinct()
patient_sur = Patients.objects.filter(patient_surgery__isnull=False).distinct()
combined_patients = patient_appoint.union(patient_sur)

# 3. Retrieve all **patients who have both an appointment and a prescription**.

combined_patients =Patients.objects.filter( Q(appointments_as_patient__isnull = False)&Q(prescription_patient_id__isnull = False)) 

# 4. Find all **patients who have appointments but no prescriptions**.

combined_patients =Patients.objects.filter( Q(appointments_as_patient__isnull = False) & Q(prescription_patient_id__isnull = True)) 

# 5. Retrieve **all patients with their doctors**, but **only include patients who have visited more than one doctor** and **exclude those who have insurance**.

patients = Patients.objects.annotate(doctor_count=Count('appointments_as_patient__doctor',distinct=True)).filter(doctor_count__gt=1).exclude(insurance_patient__isnull=False).prefetch_related('appointments_as_patient__doctor')
patient = Patients.objects.first()
print(patient.appointments_as_patient.all())
for appointment in patient.appointments_as_patient.all():
        print(appointment.doctor)
        

# 6. Get a **list of unique doctor specializations**, ordered **by the number of doctors in each specialization**.

doctors = Doctors.objects.values('specialization').distinct().annotate(number_of_doc = Count("doctor_id")).order_by('-number_of_doc')


# 8. Retrieve all **patients** who have received **at least one prescription** containing the word **"Painkiller"**.

prescrip = Prescriptions.objects.filter(medicine_detail__icontains="Painkiller")
combined_pain = Patients.objects.filter(Q(prescription_patient_id__in=prescrip.values('patient')) & Q(prescription_patient_id__isnull=False))

# 9. Find all **doctors** who have had **more than 5 patients but less than 15** in the last **year**.

one_year_ago = timezone.now() - timedelta(days=365)
doc = Doctors.objects.annotate(patient_count=Count('appointments_as_doctor__patient', distinct=True)).filter(patient_count__gt=5, patient_count__lt=15, appointments_as_doctor__appointment_date__gte=one_year_ago).distinct()

# 10. **Bulk create** test **appointments** and then **bulk update** their **status** to `"Completed"` if the **appointment date has passed**.

appointments_to_create = [Appointments(patient=patient,doctor=doctor,appointment_date=timezone.now() + timedelta(days=5),status="Scheduled") 
for patient in Patients.objects.all()[:10]
for doctor in Doctors.objects.all()[:3]]

current_time = timezone.now()
Appointments.objects.filter(appointment_date__lte=current_time).update(status="Completed")

# 11. Find all **patients who have insurance and at least one surgery** using `select_related`, `filter`, and `Q`.

patient_surg = Patients.objects.filter(Q(insurance_patient__isnull = False) & Q(patient_surgery__isnull=False)).select_related('insurance_patient').prefetch_related('patient_surgery')
for patient in patient_surg:
    print(patient.name)

# 12. Retrieve all **doctors and count their appointments** using `annotate`, `Count`, and `prefetch_related`.

docs = Doctors.objects.annotate(count_appoint = Count('appointments_as_doctor'))

# 13. List all **appointments scheduled in the next 30 days** using `filter` and `order_by`.

current_time = now()
end_time = now() + timedelta(days=30)
appoints = Appointments.objects.filter(appointment_date__range =[current_time, end_time], status = 'Scheduled').order_by('appointment_date')

# 14. Retrieve the **youngest and oldest patient** using `aggregate`, `Min`, and `Max`.

>>> dob_agg = Patients.objects.aggregate(old = Min("dob"), elder = Max('dob'))
>>> oldest = Patients.objects.filter(dob = dob_agg['old']).first()
>>> eldest = Patients.objects.filter(dob=dob_agg['elder']).first()

# 15. Find **departments with the most doctors** using `annotate`, `Count`, and `order_by`.

depart = Department.objects.annotate(count_doc = Count('doctors')).order_by('-count_doc')

# 16. Retrieve all **appointments where the doctor's specialization is "Dermatology"** using `select_related` and `filter`.

appoints = Appointments.objects.filter(doctor__specialization__icontains='Dermatology').select_related('doctor')

# 17. Find **patients who had an appointment but no surgery** using `difference`.

patient1 = Patients.objects.filter(appointments_as_patient__isnull=False)
patient2 = Patients.objects.filter(patient_surgery__isnull=True)
difference_appointments = patient1.difference(patient2)

# 18. Retrieve **all head doctors of departments** using `select_related`.

head_doc = Department.objects.select_related('head_doctor').all()

# 19. Count the **total number of surgeries** by **each department** using `annotate` and `Count`.

>>> departments_with_surgeries = Department.objects.annotate(total_surgeries=Count('doctors__doctor_surgery')).values('name', 'total_surgeries')

# 20. Find **patients who had an appointment, a prescription, and a surgery** using `intersection`.

patients_with_appointments = Patients.objects.filter(appointments_as_patient__isnull=False)
patients_with_prescriptions = Patients.objects.filter(prescription_patient_id__isnull=False)
patients_with_surgeries = Patients.objects.filter(patient_surgery__isnull=False)
patients_with_all_conditions = patients_with_appointments.intersection(patients_with_prescriptions, patients_with_surgeries)


# 21. Retrieve **prescriptions written in the last 7 days** using `filter` and `Q`.

prescrip = Prescriptions.objects.filter(Q(appointment__appointment_date__gte=now - timedelta(days=7)))

# 22. Get all **insurance providers that cover more than 5 patients** using `values` and `annotate`.

insurances = Insurance.objects.values('provider').annotate(count_provider=Count('patient')).filter(count_provider__gt=5)

# 23. Find all **doctors who have prescribed at least 10 medicines** using `annotate` and `Count`.

doctors = Doctors.objects.annotate(prescription_count=Count('prescription_doctor_id')).filter(prescription_count__gte=10)


# 24. Retrieve **all patients whose last name starts with 'S'** using `filter`.

>>> patients = Patients.objects.filter(user__last_name__startswith='S')

# 25. Count the **number of male and female patients** using `annotate`.

gender_counts = Patients.objects.annotate(male_count=Count(Case(When(gender='Male', then=Value(1)), default=Value(0))), female_count=Count(Case(When(gender='Female', then=Value(1)), default=Value(0))))

# 26. Find **the doctor who has performed the most surgeries** using `annotate` and `order_by`.

top_surgeon = Doctors.objects.annotate(surgery_count=Count('doctor_surgery')).order_by('-surgery_count').first()

# 27. Get **appointments where the patient has visited the same doctor more than once** using `annotate` and `filter`.

repeat_visits = Appointments.objects.values('patient','doctor').annotate(visit_count = Count('id')).filter(visit_count__gt=1)

# 28. List all **departments along with the number of surgeries performed** using `annotate`.
>>> departments = Department.objects.annotate(surgery_count=Count('doctors__doctor_surgery')).values('name', 'surgery_count')

# 29. Retrieve **appointments where the patient and doctor are the same gender** using `F`.

appointments = Appointments.objects.filter(doctor__gender=F('patient__gender')).select_related('doctor', 'patient')

# 30. Count the **number of doctors with more than 3 specializations** using `Count`.

docs = Doctors.objects.annotate(count_doc = Count("specialization"), filter = Q(specialization__gt=3))

# 31. Find all **patients who do not have a phone number** using `exclude`.

>>> patients_without_phone = Patients.objects.exclude(user__phone_number__isnull=False).exclude(user__phone_number__exact='')

# 32. Retrieve the **top 5 doctors with the highest number of patients** using `annotate`.

>>> top_doctors = Doctors.objects.annotate(patient_count=Count('patient')).order_by('-patient_count')[:5]

# 33. Get **departments that have at least 10 doctors** using `annotate` and `filter`.

departments_with_10_doctors = Department.objects.annotate(doctor_count=Count('doctors')).filter(doctor_count__gte=10)

# 34. Find **patients who had a surgery but no prescriptions** using `difference`.

patients_with_surgery = Patients.objects.filter(patient_surgery__isnull=False)
patients_with_prescriptions = Patients.objects.filter(prescription_patient_id__isnull=False)
patients_without_prescriptions = patients_with_surgery.difference(patients_with_prescriptions)

# 35. Retrieve **the most prescribed medicine** using `values`, `annotate`, and `Count`.

most_prescribed_medicine = Prescriptions.objects.values('medicine_detail').annotate(medicine_count=Count('medicine_detail')).order_by('-medicine_count')[:1]




























