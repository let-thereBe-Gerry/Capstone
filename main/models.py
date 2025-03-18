 
from pickle import TRUE
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date

# Create your models here.
# hindi ko pa talaga alam kung ano yung dapat ilalagay dito, shiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiit!!!!

class Ophthalmologist(models.Model): # the Opthal should Have the ability to remove or add staffer/
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    # clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True) 
    opthID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=100)
    middleName = models.CharField(max_length=100, null=True)
    lastName = models.CharField(max_length=100)
    bday = models.DateField(auto_now_add=False, null=True)
    sex = models.CharField(max_length=100)
    homeAddress = models.CharField(max_length=250)
    contactNum = models.CharField(max_length=50)
    age = models.CharField(max_length=50, null=True)
    is_status = models.BooleanField(default=False) 
    is_EmailVerified = models.BooleanField(default=False, null=True)
    auth_token = models.CharField(max_length=100, null=True )

    def __str__(self):
        return f'{self.firstName}  {self.lastName}'

 # SA CLINIC SITE LANG PUWEDE MAG REGISTER NANG STAFF, ALSO LIMITED LANG ANG MA GAGAWA NI STAFFER

class ClinicStaff(models.Model):    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    stafferID = models.AutoField(primary_key=True)
    # clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True) 
    firstName = models.CharField(max_length=100)
    middleName = models.CharField(max_length=100, null=True)
    lastName = models.CharField(max_length=100)
    bday = models.DateField(auto_now_add=False, null=True)
    sex = models.CharField(max_length=100)
    homeAddress = models.CharField(max_length=250)
    age = models.CharField(max_length=50, null=True)
    contactNum = models.CharField(max_length=50)
    is_Accepted= models.BooleanField(default=False) # when the staffer apply to the Clinic, the clinic should accept it or not
    is_EmailVerified = models.BooleanField(default=False, null=True)
    auth_token = models.CharField(max_length=100, null=True )

    def __str__(self):
        return f'{self.firstName}  {self.lastName}'

class Clinic(models.Model):
    clinicID = models.AutoField(primary_key=True)   
    opthID = models.ForeignKey(Ophthalmologist, on_delete=models.CASCADE, null=True) 
    stafferID = models.ForeignKey(ClinicStaff, on_delete=models.CASCADE, null=True) 
    clinicName = models.CharField(max_length=100)
    clinicAddress = models.CharField(max_length=100)
    clinicNumber = models.CharField(max_length=50)
    clinicEMailAdd = models.EmailField(max_length=100, null=True) 
    availDate = models.DateField(auto_now=False, null=True)
    availTime = models.TimeField(auto_now=False, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    is_EmailVerified = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.clinicName}'

class Services(models.Model):
    serviceID = models.AutoField(primary_key=True)
    clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True)     
    service_Name = models.CharField(max_length=1000, null=True)    
    service_Information = models.CharField(max_length=1000, null=True)    
    
    def __str__(self):
        return f'{self.service_Name}'

class UserPatient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    userID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=100)
    middleName = models.CharField(max_length=100, null=True)
    lastName = models.CharField(max_length=100)
    bday = models.DateField(auto_now_add=False, null=True)
    sex = models.CharField(max_length=100)
    homeAddress = models.CharField(max_length=250)
    contactNum = models.CharField(max_length=50)
    age = models.CharField(max_length=50, null=True)
    is_EmailVerified = models.BooleanField(default=False, null=True)
    auth_token = models.CharField(max_length=100, null=True )

    def __str__(self):
        return f'{self.firstName}  {self.lastName}'

class WalkInPatient(models.Model):
    walkInID = models.AutoField(primary_key=True)
    # clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True) # para malimit lang yung record sa iisang clinic lamang
    firstName = models.CharField(max_length=100, null=True)
    middleName = models.CharField(max_length=100, null=True)
    lastName = models.CharField(max_length=100, null=True)
    bday = models.DateField(auto_now_add=False, null=True)
    sex = models.CharField(max_length=100, null=True)
    homeAddress = models.CharField(max_length=250, null=True)
    age = models.CharField(max_length=50, null=True)
    contactNum = models.CharField(max_length=50, null=True)
    is_EmailVerified = models.BooleanField(default=False, null=True)
    auth_token = models.CharField(max_length=100, null=True )
    
    def __str__(self):
        return f'{self.firstName}  {self.lastName}'
   
class UserContacts (models.Model): # hiniwalay ko ito kasi may possible na hindi lang yung iisa ang emergency contact nang isang patient
    pConID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(UserPatient, on_delete=models.CASCADE, null=True) 
    walkInID = models.ForeignKey(WalkInPatient, on_delete=models.CASCADE, null=True)
    firstName = models.CharField(max_length=100)
    middleName = models.CharField(max_length=100, null=True)
    lastName = models.CharField(max_length=100)
    relationship = models.CharField(max_length=100)
    # sex = models.CharField(max_length=100)
    # homeAddress = models.CharField(max_length=250)
    contactNum = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.firstName}  {self.lastName}'

class Message(models.Model): 
    textID = models.AutoField(primary_key=True)

    userID = models.ForeignKey(UserPatient, on_delete=models.CASCADE, blank=True, null=True) # the one who will send the message
    opthID = models.ForeignKey(Ophthalmologist, on_delete=models.CASCADE, blank=True, null=True) # the one who will send the message
    stafferID = models.ForeignKey(ClinicStaff, on_delete=models.CASCADE, blank=True, null=True) # the one who will send the message    
    #walkInID = models.ForeignKey(WalkInPatient, on_delete=models.CASCADE, null=True)
    clinicID = models.CharField(max_length=10000) # this will serve as the room # kung ito ang gagawin kong room, so makikita nang iba yung message ng iba rin?
    is_Archieve = models.BooleanField(default=False, null=True)
    sender = models.CharField(max_length=10000, blank=True, null=True)
    reciever = models.CharField(max_length=10000, blank=True, null=True)
    is_read = models.BooleanField(default=False)

    messageContent = models.CharField(max_length=10000)
    date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        # pass
        return f'{self.sender} ==> {self.reciever}'

class ChatRoom(models.Model):
    chatRoomID = models.AutoField(primary_key=True)
    chatRoomName = models.CharField(max_length=10000, null=True)
    patientID = models.ForeignKey(UserPatient, on_delete=models.CASCADE, blank=True, null=True) # para ma filter lang yung message na ilalabas

    def __str__(self):
        # pass
        return f'{self.chatRoomName}'

# ito ay for booking/appointment lang, so ang kailangan lang na data ay yung nandito lang sa baba
class Booking(models.Model):  
    bookingID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(UserPatient, on_delete=models.CASCADE, null=True, blank=True) 
    clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True) 
    serviceID = models.ForeignKey(Services, on_delete=models.CASCADE, null=True, blank=True)
    walkInID = models.ForeignKey(WalkInPatient, on_delete=models.CASCADE, null=True, blank=True)
    
    appoint_Date = models.DateField(null=True)
    appt_Start_Time = models.TimeField(auto_now=False, null=True)
    appt_End_Time = models.TimeField(auto_now=False, null=True)
    
    notes = models.CharField(max_length=1000, null=True) 
    declinedNotes = models.CharField(max_length=1000, null=True) 
    cancelationReason = models.CharField(max_length=1000, null=True) 

    is_Accepted = models.BooleanField(default=False) 
    is_Denied = models.BooleanField(default=False) 
    is_hidden = models.BooleanField(default=False)
    is_cancel = models.BooleanField(default=False)
    is_Status = models.BooleanField(default=False) 
    is_Success = models.BooleanField(default=False) 
    
    prev_appoint_Date = models.DateField(null=True, blank=True)
    prev_appt_Start_Time = models.TimeField(auto_now=False, null=True, blank=True)
    prev_appt_End_Time = models.TimeField(auto_now=False, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.pk:  
            prev_booking = Booking.objects.get(pk=self.pk)
            self.prev_appoint_Date = prev_booking.appoint_Date
            self.prev_appt_Start_Time = prev_booking.appt_Start_Time
            self.prev_appt_End_Time = prev_booking.appt_End_Time

        super(Booking, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Booking {self.bookingID}"
    
class Session(models.Model): # this table should be included in the patient data sheet
    sessionID = models.AutoField(primary_key=True)
    walkInPatientID = models.ForeignKey(WalkInPatient, on_delete=models.CASCADE, null=True, blank=True) # for whom is this record
    patientID = models.ForeignKey(UserPatient, on_delete=models.CASCADE, null=True, blank=True) # for whom is this record
    clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True) # from what clinic

    dateRecorded = models.DateField(auto_now_add=False, null=True) # when did the patient made the session

    sessionNotes = models.CharField(max_length=3000, null=True) # 

# ~~~ Services
class ocularHealthExamination(models.Model):
    oheID = models.AutoField(primary_key=True)
    patientID = models.ForeignKey(UserPatient, on_delete=models.CASCADE, null=True, blank=True) # for whom is this record
    clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True)  # where it was stored
    walkInID = models.ForeignKey(WalkInPatient, on_delete=models.CASCADE, null=True, blank=True)
    
    dateRecorded = models.DateField(null=True)

    def save(self, *args, **kwargs):
        if not self.dateRecorded:
            self.dateRecorded = date.today()
        super().save(*args, **kwargs)

    # OD
    od_Lids_Lashes = models.CharField(max_length=1000, blank=True, null=True) 
    od_Bulbar = models.CharField(max_length=1000, blank=True, null=True) 
    od_Palpebral = models.CharField(max_length=1000, blank=True, null=True) 
    od_Cornea = models.CharField(max_length=1000, blank=True, null=True) 
    od_ChamgerAngle = models.CharField(max_length=1000, blank=True, null=True) 
    od_Iris = models.CharField(max_length=1000, blank=True, null=True) 
    od_Lens = models.CharField(max_length=1000, blank=True, null=True) 
    od_Tonometry = models.CharField(max_length=1000, blank=True, null=True) 

    # OS
    os_Lids_Lashes = models.CharField(max_length=1000, blank=True, null=True) 
    os_Bulbar = models.CharField(max_length=1000, blank=True, null=True) 
    os_Palpebral = models.CharField(max_length=1000, blank=True, null=True) 
    os_Cornea = models.CharField(max_length=1000, blank=True, null=True) 
    os_ChamgerAngle = models.CharField(max_length=1000, blank=True, null=True) 
    os_Iris = models.CharField(max_length=1000, blank=True, null=True) 
    os_Lens = models.CharField(max_length=1000, blank=True, null=True) 
    os_Tonometry = models.CharField(max_length=1000, blank=True, null=True) 

class dryEyeTest(models.Model):
    dryEyeID = models.AutoField(primary_key=True)
    patientID = models.ForeignKey(UserPatient, on_delete=models.CASCADE, null=True, blank=True) # for whom is this record
    clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True)  # where it was stored
    walkInID = models.ForeignKey(WalkInPatient, on_delete=models.CASCADE, null=True, blank=True)

    dateRecorded = models.DateField(null=True)

    def save(self, *args, **kwargs):
        if not self.dateRecorded:
            self.dateRecorded = date.today()
        super().save(*args, **kwargs)

    od_DryEye = models.CharField(max_length=1000, blank=True, null=True) 
    os_DryEye = models.CharField(max_length=1000, blank=True, null=True) 

class Refraction(models.Model):
    refractionID = models.AutoField(primary_key=True)
    patientID = models.ForeignKey(UserPatient, on_delete=models.CASCADE, null=True, blank=True) # for whom is this record
    clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True)  # where it was stored
    walkInID = models.ForeignKey(WalkInPatient, on_delete=models.CASCADE, null=True, blank=True)

    dateRecorded = models.DateField(null=True)

    def save(self, *args, **kwargs):
        if not self.dateRecorded:
            self.dateRecorded = date.today()
        super().save(*args, **kwargs)

    # Subjective Refraction = subRef_
    subRef_OD = models.CharField(max_length=1000, blank=True, null=True) 
    subRef_OS = models.CharField(max_length=1000, blank=True, null=True) 

    # VA
    va_OD = models.CharField(max_length=1000, blank=True, null=True) 
    va_OS = models.CharField(max_length=1000, blank=True, null=True) 

    # PD
    pd_OD = models.CharField(max_length=1000, blank=True, null=True) 
    pd_OS = models.CharField(max_length=1000, blank=True, null=True) 

    # Automated Refraction = autRef_
    autRef_OD = models.CharField(max_length=1000, blank=True, null=True) 
    autRef_OS = models.CharField(max_length=1000, blank=True, null=True) 

    # Near Add    
    od_Refraction = models.CharField(max_length=1000, blank=True, null=True) 
    os_Refraction = models.CharField(max_length=1000, blank=True, null=True) 

    # Remarks
    remarks_Refraction = models.CharField(max_length=2000, blank=True, null=True) 
# ~~~ End of Services

class RequestRecord(models.Model):
    requestID = models.AutoField(primary_key=True)
    patientID = models.ForeignKey(UserPatient, on_delete=models.CASCADE, null=True, blank=True) # the requester
    clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, blank=True)  # the clinic that will be requested
    oheID = models.ForeignKey(ocularHealthExamination, on_delete=models.CASCADE, null=True, blank=True)  
    dryEyeID = models.ForeignKey(dryEyeTest, on_delete=models.CASCADE, null=True, blank=True)  
    refractionID = models.ForeignKey(Refraction, on_delete=models.CASCADE, null=True, blank=True)  

    is_Request_Granted = models.CharField(max_length=1000, blank=True, null=True)  # response of the clinic. It's either True or False
    requestRecord = models.CharField(max_length=1000, blank=True, null=True) # this is the message that will be sent to the clinic for requesting record
    
    
    dateRequested = models.DateField(null=True)

    def save(self, *args, **kwargs):
        if not self.dateRecorded:
            self.dateRecorded = date.today()
        super().save(*args, **kwargs)

class PatientReview(models.Model):
    patientRevID = models.AutoField(primary_key=True)
    patientID = models.ForeignKey(UserPatient, on_delete=models.CASCADE, null=True, blank=True) # for whom is this record
    clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True)  # where it was stored
    walkInID = models.ForeignKey(WalkInPatient, on_delete=models.CASCADE, null=True, blank=True)

    dateRecorded = models.DateField(null=True)

    def save(self, *args, **kwargs):
        if not self.dateRecorded:
            self.dateRecorded = date.today()
        super().save(*args, **kwargs)

    rate = models.CharField(max_length=1000, blank=True, null=True) 
    review = models.CharField(max_length=1000, blank=True, null=True) 
    
class PatientPersonalInformation(models.Model):
    perInID = models.AutoField(primary_key=True)
    patientID = models.ForeignKey(UserPatient, on_delete=models.CASCADE, null=True, blank=True) # for whom is this record
    clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, blank=True)  # where it was stored
    walkInID = models.ForeignKey(WalkInPatient, on_delete=models.CASCADE, null=True, blank=True)
    
    dateRecorded = models.DateField(null=True)

    def save(self, *args, **kwargs):
        if not self.dateRecorded:
            self.dateRecorded = datetime.now().strftime("%Y-%m-%d")
        super().save(*args, **kwargs)

    civilStatus = models.CharField(max_length=1000, null=True)
    Occupation = models.CharField(max_length=1000, null=True)

class PatientMedicalHistory(models.Model):
    historyRecordID = models.AutoField(primary_key=True)
    patientID = models.ForeignKey(UserPatient, on_delete=models.CASCADE, null=True, blank=True) # for whom is this record
    walkInID = models.ForeignKey(WalkInPatient, on_delete=models.CASCADE, null=True, blank=True) # for whom is this record
    clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True)  # where it was stored
    
    aggrement = models.BooleanField(default=False, null=True) 

    dateRecorded = models.DateField(null=True)

    def save(self, *args, **kwargs):
        if not self.dateRecorded:
            self.dateRecorded = datetime.now().strftime("%Y-%m-%d")
        super().save(*args, **kwargs)

    # Diagnosed Health Problem
    is_Hypertention = models.BooleanField(default=False, null=True)
    recordDate1 = models.CharField(max_length=1000, null=True, blank=True) # ALL the record date should be drop down only the year are recorded

    is_HeartProblem = models.BooleanField(default=False, null=True)
    recordDate2 = models.CharField(max_length=1000, null=True, blank=True)

    is_Diabetes = models.BooleanField(default=False, null=True)
    recordDate3 = models.CharField(max_length=1000, null=True, blank=True)

    is_Stroke = models.BooleanField(default=False, null=True)
    recordDate4 = models.CharField(max_length=1000, null=True, blank=True)

    is_Asthma = models.BooleanField(default=False, null=True)
    recordDate5 = models.CharField(max_length=1000, null=True, blank=True)

    otherDiagnosedHealth = models.CharField(max_length=1000, null=True, blank=True) 
    recordDate7 = models.CharField(max_length=1000, null=True, blank=True)

    is_DiagnosedNone = models.BooleanField(default=False, null=True)
    # recordDate6 = models.CharField(max_length=1000, null=True)

    # Habits
    is_Smoking = models.BooleanField(default=False, null=True)
    is_SmokingFreq = models.CharField(max_length=1000, null=True, blank=True) # S = Seldom, O = Occasionally, F = Frequently
    is_SmokingYear = models.CharField(max_length=1000, null=True, blank=True)

    is_Alcohol = models.BooleanField(default=False, null=True)
    is_AlcoholFreq = models.CharField(max_length=1000, null=True, blank=True) # S = Seldom, O = Occasionally, F = Frequently
    recordDate8 = models.CharField(max_length=1000, null=True, blank=True)

    is_HabitsNone = models.BooleanField(default=False, null=True)

    # Allergies
    medicinesAller = models.CharField(max_length=1000, null=True, blank=True)
    foodsAller = models.CharField(max_length=1000, null=True, blank=True)
    otherAller = models.CharField(max_length=1000, null=True, blank=True)
    is_AllergiesNone = models.BooleanField(default=False, null=True)

    # Eye History
    is_Cataract = models.BooleanField(default=False, null=True)
    is_Glaucama = models.BooleanField(default=False, null=True)
    is_RetinalDisease = models.BooleanField(default=False, null=True)
    is_Astigmatism = models.CharField(max_length=1000, null=True, blank=True)

    is_MacularDegeneration = models.CharField(max_length=1000, null=True, blank=True)
    is_DiabeticRetinopathy = models.CharField(max_length=1000, null=True, blank=True)
    is_DryEyeSyndrome = models.CharField(max_length=1000, null=True, blank=True)
    is_Strabismus = models.CharField(max_length=1000, null=True, blank=True)

    is_ColorBlindness = models.CharField(max_length=1000, null=True, blank=True)
    is_Keratoconus = models.CharField(max_length=1000, null=True, blank=True)
    is_Uveitis = models.CharField(max_length=1000, null=True, blank=True)
    othersEyeHis = models.CharField(max_length=1000, null=True, blank=True)
    
    is_EHNone = models.BooleanField(default=False, null=True)  # is Eye History is None

    # Prevous Eye Surgeries
    eyeSurgeries = models.CharField(max_length=1000, null=True, blank=True)

    # Family History
    is_GlaucamaF = models.BooleanField(default=False, null=True)
    is_HypertentionF = models.BooleanField(default=False, null=True)
    is_Blindness = models.BooleanField(default=False, null=True)
    is_DiabetesF = models.BooleanField(default=False, null=True)
    is_CataractF = models.BooleanField(default=False, null=True)
    is_FHNone = models.BooleanField(default=False, null=True)  # is Family History is None

class PatientClinicalObservation(models.Model):
    pcObservationID =  models.AutoField(primary_key=True)
    userID = models.ForeignKey(UserPatient, on_delete=models.CASCADE)
    clinicID = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True)
    walkInID = models.ForeignKey(WalkInPatient, on_delete=models.CASCADE, null=True)

    refractionTest = models.CharField(max_length=1000, null=True) # so ito yung may phoropter, dito ay mag peprescribe lang si doctor
        # references = https://www.healthline.com/health/refraction-test
        # https://www.mountsinai.org/health-library/tests/refraction-test#:~:text=A%20refraction%20is%20an%20eye,in%20front%20or%20behind%20it.                         cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    diagnosticCodes = models.CharField(max_length=1000, null=True)  # references = https://icdcodelookup.com/icd-10/common-codes/ophthalmology  

    # Procedures and treatments:
    patientPrecribtion = models.CharField(max_length=1000, null=True)  # dito ay kung ooperahan ba or something out of consultation na 

    # Visual acuity measures
    snellenChart = models.CharField(max_length=1000, null=True)  # 20/200, 20/100, 20/70 , 20/50, 20/40, 20/30, 20 /25, 20/20, 20/15, 20/13, 20/10 <= ito ang mga dapat i srtore dito, ito yung mag kakaibang font size
    contrastSensitivityTests = models.CharField(max_length=1000, null=True) 
        # references = https://www.adaptivesensorytech.com/vision/vision-testing.html
            # https://www.jutronvision.com/product/rabin-contrast-sensitivity-test-for-2425-large-cabinet/
    # Imaging modalities
    fundusPhotographs = models.ImageField(upload_to='images/')
    OCT = models.CharField(max_length=1000, null=True) # references = https://www.aao.org/eye-health/treatments/what-is-optical-coherence-tomography
                                                            # https://my.clevelandclinic.org/health/diagnostics/17293-optical-coherence-tomography
    # corneal topography = med'yo advance na ito
    # visual field = med'yo advance na ito

class DoctorAvailability(models.Model):
    clinicID = models.ForeignKey(Ophthalmologist, on_delete=models.CASCADE, null=True)
    # since the doctor are sometime unavailable on a specific time, date and time should be seperated too
    availDate = models.DateField(auto_now=False, null=True)
    availTime = models.TimeField(auto_now=False, null=True)

    def __str__(self):
        pass
        # return f'{self.firstName} {self.lastNamex}'

class DashCalendar(models.Model): # TSAKA NA MUNA ITO, SUBJECT TO CHANGED

    bookingID = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200, null=True)
    apptStart = models.DateTimeField(auto_now=False,null=True)
    apptEnd = models.DateTimeField(auto_now=False,null=True)
    is_allDay = models.BooleanField(default=False) 

    def __str__(self):
        return f'{self.title}'    