from django.contrib import admin
from .models import RequestRecord, PatientReview, Session, WalkInPatient, PatientPersonalInformation, UserPatient, Clinic, DashCalendar, Message, Booking, DoctorAvailability, Ophthalmologist, Services, ClinicStaff, UserContacts, ChatRoom, PatientMedicalHistory, ocularHealthExamination, dryEyeTest, Refraction

# Register your models here.
admin.site.register(UserPatient)
admin.site.register(Clinic)
admin.site.register(DashCalendar)
admin.site.register(Message)
admin.site.register(Booking)
admin.site.register(DoctorAvailability)
admin.site.register(Ophthalmologist)
admin.site.register(Services)
admin.site.register(ClinicStaff)
admin.site.register(UserContacts)
admin.site.register(ChatRoom)
admin.site.register(PatientMedicalHistory)
admin.site.register(ocularHealthExamination)
admin.site.register(dryEyeTest)
admin.site.register(Refraction)
admin.site.register(PatientPersonalInformation)
admin.site.register(WalkInPatient)
admin.site.register(Session)
admin.site.register(PatientReview)
admin.site.register(RequestRecord)
