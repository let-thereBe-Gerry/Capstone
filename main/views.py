import logging
import json
import time
import calendar
import numpy as np

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.models import User, auth
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import RequestRecord, PatientReview, Session, WalkInPatient, UserPatient, Clinic, Message, PatientPersonalInformation, Booking, DoctorAvailability, DashCalendar, Ophthalmologist, Services, ClinicStaff, UserContacts, ChatRoom, PatientMedicalHistory, ocularHealthExamination, dryEyeTest, Refraction
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import user_passes_test
from rest_framework import viewsets
from .serializers import ClinicSerializer
from django.views.decorators.http import require_http_methods
from datetime import date
from django.utils import timezone
from django.urls import reverse
from django.db.models import TimeField, ExpressionWrapper, F
from django.db.models import Q, Min, Max
from django.db.models import Count, Avg
from django.db.models.functions import ExtractMonth, TruncTime, Cast
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from statistics import mode
from collections import Counter, defaultdict
from io import BytesIO
import base64
from django.core.files.images import ImageFile
import matplotlib
matplotlib.use('TkAgg')
matplotlib.use('agg')
import matplotlib.pyplot as plt
import io
import os

from django.template.loader import get_template
from xhtml2pdf import pisa 
import uuid
from django import template
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login

logger = logging.getLogger(__name__)

def index(request):
    user_client = None
    clinics = Clinic.objects.all() 
    user = request.user
    userType = None

    if user.is_authenticated:
        try:            
            user_client = UserPatient.objects.get(user=user)
            
        except UserPatient.DoesNotExist:
            try:
                user_client = Ophthalmologist.objects.get(user=user)
                userType = "Clinic"
            except Ophthalmologist.DoesNotExist:
                try:
                    user_client = ClinicStaff.objects.get(user=user)
                    userType = "Clinic"
                except ClinicStaff.DoesNotExist:
                    user_client = None
    context = {
            'user_client': user_client,
            'clinics': clinics,
            'user': user,
        } 
    
    if userType == "Clinic":    
        print(user_client.is_status)
        if user_client.is_status == False:
            return render(request, 'logout.html', context)
        return redirect('dashboard')
        return render(request, 'clinic-dashboard.html')
    
    if request.user.is_superuser:    
        return redirect('admin_Dashboard')
    
    print ("user", user)
    print ("user_client", user_client)
    print ("Here are the clinics == ",clinics)
    return render(request, 'index.html', context)
    
def index_ClinicsProfile(request, clinicID):
    getAllReviews = PatientReview.objects.filter(clinicID=clinicID)
    getClinic = Clinic.objects.get(clinicID=clinicID)

    rate = None 

    for review in getAllReviews:
        review.rate = int(review.rate)
        rate = review.rate  

    context = {
        'getAllReviews': getAllReviews,
        'clinicID': getClinic,
        'rate': rate,
    }

    return render(request, 'index-ClinicsProfile.html', context)

def login_page(request):         
    if request.method == 'POST':
        username = request.POST.get('logUName', '')
        password = request.POST.get('logPass','')
        user_obj = User.objects.filter(username = username).first()

        user = authenticate(username = username , password = password)
        if user_obj is None: 
            messages.success(request, 'Account not found.')
            return redirect('login')
        
        try:
            profile_obj = UserPatient.objects.filter(user = user_obj ).first()
            print("Here inside of first Try")

            try:
                if not profile_obj.is_EmailVerified:
                    messages.success(request, 'Account is not verified check your mail.')
                    return redirect('login')
                user = authenticate(username = username , password = password)
                login(request, user)
                print("User authenticated ", user)
                return redirect('/')
            except:
                pass
        except UserPatient.DoesNotExist:
            pass

        try:
            profile_obj = Ophthalmologist.objects.filter(user = user_obj ).first()        
            print("Here inside of secod Try")

            try:
                if not profile_obj.is_EmailVerified :
                    messages.success(request, 'Account is not verified check your mail.')
                    return redirect('login')
                user = authenticate(username = username , password = password)
                login(request, user)
                try:
                    clinicExist = Clinic.objects.get(opthID = profile_obj)
                    if clinicExist:
                        
                        return redirect('dashboard')

                except:
                    pass
                return redirect('/')
            except:
                pass
        except Ophthalmologist.DoesNotExist:
            pass

        try:
            profile_obj = ClinicStaff.objects.filter(user = user_obj ).first()
            print("Here inside of 3rd Try")

            try:
                if not profile_obj.is_EmailVerified:
                    messages.success(request, 'Account is not verified check your mail.')
                    return redirect('login')
                user = authenticate(username = username , password = password)
                login(request, user)
                return redirect('dashboard')
            except:
                pass
        except ClinicStaff.DoesNotExist:
            pass

        if user is None:
            messages.success(request, 'Wrong password or Username.')
            return redirect('login')
        
        login(request , user)
        print("User Log In: ", user)
        return redirect('/')
    
    return render(request, 'login.html')

def signUp(request):      
    if request.method=="POST": 
        
        fName = request.POST.get('FName','') 
        mName = request.POST.get('MName','')
        lName = request.POST.get('LName','')
        bDay = request.POST.get('bday','')
        sex = request.POST.get('sex','')
        homeAdd = request.POST.get('HomeAdd','')
        contactNum = request.POST.get('ContactNum','')

        # Emergency Person
        efName = request.POST.get('EFName','')
        emName = request.POST.get('EMName','')
        elName = request.POST.get('ELName','')
        rShip = request.POST.get('ERelatioship','')
        eContactNum = request.POST.get('contactEmNum','')      

        # this will be imported in User
        email = request.POST.get('Email','')
        username = request.POST.get('Username','')
        password = request.POST.get('Pass','')
        password2 = request.POST.get('Pass2','')   
      

        if password == password2: 
            if User.objects.filter(email=email).exists():  
                messages.info(request, 'Email already used')
                return redirect ('signUp')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already used')  
                return redirect ('signUp')
            else:
                user = User (username = username, email = email)
                user.set_password(password)
                user.save()
                
                auth_token = str(uuid.uuid4())

                birthdate = datetime.strptime(bDay, '%Y-%m-%d')
                # Calculate the age based on the current date
                current_date = datetime.now()
                age = current_date.year - birthdate.year - ((current_date.month, current_date.day) < (birthdate.month, birthdate.day))

                print("Print Age: ", age)

                userInfo = UserPatient.objects.create(user=user,firstName=fName, middleName=mName, lastName=lName, bday=bDay, sex=sex, homeAddress=homeAdd, 
                                       contactNum=contactNum, age = age, auth_token = auth_token)
                userInfo.save()
                send_mail_after_registration(email , auth_token)

                try:
                    pContact = UserContacts (
                        userID = userInfo, firstName=efName, middleName=emName, lastName=elName, relationship=rShip, 
                                        contactNum=eContactNum
                    )
                    pContact.save()
                    return redirect('login')
                except:
                    print("Contact not saved")
        else:
            messages.info(request, 'Password Not Match!')
            return redirect('signUp.html')
    else:
        return render(request, 'signUp.html')
   
def signUp_Opthal(request):       
    if request.method=="POST": 
        # this will be imported in DB - UserPatient
        fName = request.POST.get('FName','') 
        mName = request.POST.get('MName','')
        lName = request.POST.get('LName','')
        bDay = request.POST.get('bday','')
        sex = request.POST.get('sex','')
        homeAdd = request.POST.get('HomeAdd','')
        contactNum = request.POST.get('ContactNum','')

        # Emergency Person
        efName = request.POST.get('EFName','')
        emName = request.POST.get('EMName','')
        elName = request.POST.get('ELName','')
        rShip = request.POST.get('ERelatioship','')
        eContactNum = request.POST.get('contactEmNum','')      

        # this will be imported in User
        email = request.POST.get('Email','')
        username = request.POST.get('Username','')
        password = request.POST.get('Pass','')
        password2 = request.POST.get('Pass2','')   

        if password == password2: 
            if User.objects.filter(email=email).exists(): 
                messages.info(request, 'Email already used')
                return redirect ('signUp')
            elif User.objects.filter(username=username).exists(): 
                messages.info(request, 'Username already used') 
                return redirect ('signUp')
            else:
                user = User.objects.create_user (username = username, email = email, password = password)
                userInfo = UserPatient(user=user,firstName=fName, middleName=mName, lastName=lName, bday=bDay, sex=sex, homeAddress=homeAdd, contactNum=contactNum)
                opContact = UserContacts (
                    userID = userInfo.userID, firstName=efName, middleName=emName, lastName=elName, relationship=rShip, 
                                       contactNum=eContactNum
                )
                               
                user.save()
                userInfo.save()
                opContact.save()
                return redirect('login')
            
        else:
            messages.info(request, 'Password Not Match!')
            return redirect('signUp.html')
    else:
        return render(request, 'signUp_for_Opthal.html')
    
def logout(request):
    auth.logout(request)
    return redirect('login')

def generate_pdf(request, patient):
    if request.method=="POST":     
        getCategory = request.POST.get('category') 
        getClinic = request.POST.get('getClinic') 

        get_Clinic = int(getClinic)

        clinicID = Clinic.objects.get(clinicID = get_Clinic)

        userID = None

        if getCategory == "True":
            try:
                findWalkIn = WalkInPatient.objects.get(walkInID = patient)
                userID = findWalkIn
            except WalkInPatient.DoesNotExist:
                pass

        elif getCategory == "False":
            try: 
                findWalkIn = UserPatient.objects.get(userID = patient)
                userID = findWalkIn
            except WalkInPatient.DoesNotExist:
                pass

        get_AllMedHis = None
        get_AllOHE = None
        get_AllDET = None
        get_AllRefra = None
        get_CivilStat = None
        get_Occup = None
        addInfo = None

        if getCategory == "True":    

            try: 
                addInfo = PatientPersonalInformation.objects.get(walkInID = userID.walkInID, clinicID = clinicID)
            except PatientMedicalHistory.DoesNotExist:
                pass

            try:
                getAllMedHis = PatientMedicalHistory.objects.filter(walkInID=userID.walkInID, clinicID=clinicID.clinicID)
                get_AllMedHis = getAllMedHis
            except PatientMedicalHistory.DoesNotExist:
                pass

            try:
                getAllOHE = ocularHealthExamination.objects.filter(walkInID=userID.walkInID, clinicID=clinicID.clinicID)
                get_AllOHE = getAllOHE
            except ocularHealthExamination.DoesNotExist:
                pass

            try:
                getAllDET = dryEyeTest.objects.filter(walkInID=userID.walkInID, clinicID=clinicID.clinicID)
                get_AllDET = getAllDET
            except dryEyeTest.DoesNotExist:
                pass

            try:
                getAllRefra = Refraction.objects.filter(walkInID=userID.walkInID, clinicID=clinicID.clinicID)
                get_AllRefra = getAllRefra
            except Refraction.DoesNotExist:
                pass

            try:
                getCivilStat = PatientPersonalInformation.objects.filter(walkInID=userID.walkInID, clinicID=clinicID.clinicID)
                get_CivilStat = getCivilStat
            except PatientPersonalInformation.DoesNotExist:
                pass

        if getCategory == "False":

            try: 
                addInfo = PatientPersonalInformation.objects.get(patientID = userID.userID, clinicID = clinicID)
            except PatientPersonalInformation.DoesNotExist:
                pass


            try:
                getAllMedHis = PatientMedicalHistory.objects.filter(patientID=userID.userID, clinicID=clinicID.clinicID)
                get_AllMedHis = getAllMedHis
            except PatientMedicalHistory.DoesNotExist:
                pass

            try:
                getAllOHE = ocularHealthExamination.objects.filter(patientID=userID.userID, clinicID=clinicID.clinicID)
                get_AllOHE = getAllOHE
            except ocularHealthExamination.DoesNotExist:
                pass

            try:
                getAllDET = dryEyeTest.objects.filter(patientID=userID.userID, clinicID=clinicID.clinicID)
                get_AllDET = getAllDET
            except dryEyeTest.DoesNotExist:
                pass

            try:
                getAllRefra = Refraction.objects.filter(patientID=userID.userID, clinicID=clinicID.clinicID)
                get_AllRefra = getAllRefra
            except Refraction.DoesNotExist:
                pass

            try:
                getCivilStat = PatientPersonalInformation.objects.filter(patientID=userID.userID, clinicID=clinicID.clinicID)
                get_CivilStat = getCivilStat
            except PatientPersonalInformation.DoesNotExist:
                pass

        if get_AllMedHis is not None:
            for record in get_AllMedHis:
                print("Record Date (PatientMedicalHistory):", record.dateRecorded)

        if get_AllOHE is not None:
            for record in get_AllOHE:
                print("Record Date (OcularHealthExamination):", record.dateRecorded)

        if get_AllDET is not None:
            for record in get_AllDET:
                print("Record Date (DryEyeTest):", record.dateRecorded)

        if get_AllRefra is not None:
            for record in get_AllRefra:
                print("Record Date (Refraction):", record.dateRecorded)
        
        if get_CivilStat is not None:
            for record in get_CivilStat:
                print("Record Date (Refraction):", record.dateRecorded)

        context = {
            "userID" : userID,
            "clinicID" : clinicID,
            "addInfo" : addInfo,

            "get_AllMedHis" : get_AllMedHis,
            "get_AllOHE" : get_AllOHE,
            "get_AllDET" : get_AllDET,
            "get_AllRefra" : get_AllRefra,
        }

        # Render HTML template with table data
        template = get_template('zz-test-for-visual.html')
        html = template.render(context)

        # Create PDF using xhtml2pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename="report.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')

        return response
    else:
        return render(request, 'clinic-patientProfile.html')

def requested_Report(request, userID):
    if request.method=="POST":     
        getClinic = request.POST.get('getClinic') 
        get_Clinic = int(getClinic)
        getAppointmentID = request.POST.get('getAppointmentID') 
        get_AppointmentID = int(getAppointmentID)
        clinicID = Clinic.objects.get(clinicID = get_Clinic)
        bookingID = Booking.objects.get(bookingID = get_AppointmentID)
        userID = UserPatient.objects.get(userID = userID)
        addInfo = PatientPersonalInformation.objects.get(patientID = userID, clinicID = clinicID)
        get_AllMedHis = PatientMedicalHistory.objects.filter(patientID = userID, clinicID = clinicID)
        
        getRecordedDate = bookingID.appoint_Date

        get_AllMedHis = None
        get_AllOHE = None
        get_AllDET = None
        get_AllRefra = None
        get_CivilStat = None
        get_Occup = None

        try:
            get_AllMedHis = PatientMedicalHistory.objects.filter(patientID=userID, clinicID=clinicID.clinicID)
        except PatientMedicalHistory.DoesNotExist:
            pass
        
        try:
            get_AllOHE = ocularHealthExamination.objects.filter(patientID=userID, clinicID=clinicID.clinicID, dateRecorded = getRecordedDate)
        except ocularHealthExamination.DoesNotExist:
            pass

        try:
            get_AllDET = dryEyeTest.objects.filter(patientID=userID, clinicID=clinicID.clinicID, dateRecorded = getRecordedDate)
        except dryEyeTest.DoesNotExist:
            pass

        try:
            get_AllRefra = Refraction.objects.filter(patientID=userID, clinicID=clinicID.clinicID, dateRecorded = getRecordedDate)
        except Refraction.DoesNotExist:
            pass

        try:
            get_CivilStat = PatientPersonalInformation.objects.filter(patientID=userID, clinicID=clinicID.clinicID, dateRecorded = getRecordedDate)
        except PatientPersonalInformation.DoesNotExist:
            pass

        if get_AllMedHis is not None:
            for record in get_AllMedHis:
                print("Record Date (PatientMedicalHistory):", record.dateRecorded)

        if get_AllOHE is not None:
            for record in get_AllOHE:
                print("Record Date (OcularHealthExamination):", record.dateRecorded)

        if get_AllDET is not None:
            for record in get_AllDET:
                print("Record Date (DryEyeTest):", record.dateRecorded)

        if get_AllRefra is not None:
            for record in get_AllRefra:
                print("Record Date (Refraction):", record.dateRecorded)
        
        if get_CivilStat is not None:
            for record in get_CivilStat:
                print("Record Date (Refraction):", record.dateRecorded)
        context = {
            "userID" : userID,
            "clinicID" : clinicID,
            "addInfo" : addInfo,

            "get_AllMedHis" : get_AllMedHis,
            "get_AllOHE" : get_AllOHE,
            "get_AllDET" : get_AllDET,
            "get_AllRefra" : get_AllRefra,

        }

        template = get_template('zz-test-for-visual.html')
        html = template.render(context)

        # Create PDF using xhtml2pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachement;filename="report.pdf"' 

        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')

        return response
    else:
        return render(request, 'clinic-patientProfile.html')

def clinic_Report(request, clinicID):
    clinic = Clinic.objects.get(clinicID=clinicID)
    getAllBooking = Booking.objects.filter(clinicID = clinicID)
    allPatientReview = PatientReview.objects.filter(clinicID = clinicID)

    # Get services requested
    services_requestedDict = {}
    total_bookings = 0  # To calculate total number of bookings

    all_bookings = Booking.objects.filter(clinicID=clinicID)
    for booking in all_bookings:
        if booking.serviceID is not None:
            service_name = booking.serviceID.service_Name
            services_requestedDict[service_name] = services_requestedDict.get(service_name, 0) + 1
            total_bookings += 1

    # Generate the chart
    labels = list(services_requestedDict.keys())
    sizes = list(services_requestedDict.values())
    percentages = [(count / total_bookings) * 100 for count in sizes]

    # Find the highest percentage
    max_percentage_index = percentages.index(max(percentages))
    highest_service = labels[max_percentage_index]
    highest_percentage = max(percentages)

    # Print the highest percentage service
    print(f"The service with the highest percentage is '{highest_service}' with {highest_percentage:.2f}%")

    # Plot the pie chart
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

    # Save the chart as an image file
    chart_filename = f"chart_{clinicID}.png"
    plt.savefig(chart_filename)
    plt.close(fig)

    # Encode the chart image file to base64
    with open(chart_filename, "rb") as img_file:
        chart_image = base64.b64encode(img_file.read()).decode('utf-8')

    os.remove(chart_filename)
    
    # Monthly Clinic Cont 
    monthly_counts = getAllBooking.annotate(month=ExtractMonth('appoint_Date')).values('month').annotate(count=Count('bookingID')).order_by('month')

    months = [count['month'] for count in monthly_counts]
    counts = [count['count'] for count in monthly_counts]

    date_today = datetime.now()
    month_today = date_today.month # 2 - 1 = 1
    year_today = date_today.year

    # Yearly Patient Count
    months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    all_months = [] # this will be displayed at the bottom of the chart (x axis)
    for i in range(0, 12):
        if i >= (month_today - 1):
            all_months.append(f'{months[i]} {year_today - 1}')

    for i in range(0,12):
        if len(all_months) != 13:
            all_months.append(f'{months[i]} {year_today}')
        else:
            break

    all_formatted_dates = [] # the values of this container will be used for filtering
    start_year = year_today - 1
    start_month = month_today
    for i in range(0, 13):
        complete_date_today = f'{start_year}-{start_month}-01'
        starting_date = (datetime.strptime(complete_date_today, '%Y-%m-%d')).strftime('%Y-%m-%d')
        endDate = (datetime.strptime(str(starting_date), '%Y-%m-%d')).strftime('%Y-%m-%d')     # first day of the next month - 1 to get the last date of the month (present)

        if (start_month == 12):
            start_month = 1
            start_year = start_year + 1
        else:
            start_month = start_month + 1
        all_formatted_dates.append(endDate)
    
    y_axis = []
    for date in all_formatted_dates:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        all_count = Booking.objects.filter(appoint_Date__month = date_obj.month, appoint_Date__year = date_obj.year, clinicID = clinicID ).count()
        y_axis.append(all_count)

    # Define the range of y-values to include
    min_count = min(y_axis)  # Minimum count from the data
    max_count = max(y_axis)  # Maximum count from the data

    # Find the month with the highest count of patient visits
    max_count_index = y_axis.index(max(y_axis))
    highest_month = all_months[max_count_index]
    highest_count = max(y_axis)

    # Find the months with the lowest counts of patient visits
    sorted_indices = sorted(range(len(y_axis)), key=lambda i: y_axis[i])
    lowest_indices = sorted_indices[:5]  # Get the indices of the 5 lowest counts

    # Get the corresponding months for the lowest counts
    lowest_months = [all_months[i] for i in lowest_indices]
    lowest_counts = [y_axis[i] for i in lowest_indices]

    lowest = zip(lowest_months, lowest_counts)

    # Print the month with the highest count of patient visits
    print(f"The month with the highest count of patient visits is {highest_month} with {highest_count} appointments.")

    # Plotting the line graph
    plt.figure(figsize=(22, 5))
    plt.plot(all_formatted_dates, y_axis, color='skyblue', linewidth=2.5)

    # Adding a horizontal line for each possible y-value within the range
    for count in range(min_count, max_count + 1):
        plt.axhline(y=count, color='gray', linestyle='--',  alpha=0.5)

    # Adding title and labels
    plt.title('Monthly Clinic Appointments')
    plt.xlabel('Month')
    plt.ylabel('Number of Appointments')

    # Rotating x-axis labels for better readability
    plt.xticks(rotation=25)

    # Save the chart as an image file
    clinic_appointments_bar_chart = "clinic_appointments_bar_chart.png"
    plt.savefig(clinic_appointments_bar_chart)
    plt.close()

    # Encode the chart image file to base64
    with open(clinic_appointments_bar_chart, "rb") as img_file:
        appointments_bar_chart = base64.b64encode(img_file.read()).decode('utf-8')

    # Remove the chart image file
    os.remove(clinic_appointments_bar_chart)

    # Initialize defaultdict to count address occurrences
    address_counts = defaultdict(int)

    for booking in getAllBooking:
        try:
            if booking.userID:
                address_counts[booking.userID.homeAddress] += 1
        except AttributeError:
            pass
        
        try:
            if booking.walkInID:
                address_counts[booking.walkInID.homeAddress] += 1
        except AttributeError:
            pass

    for address, count in address_counts.items():
        print(f"Address: {address}, Count: {count}")

    address_counts_json = json.dumps(dict(address_counts))

    max_address, max_count = max(address_counts.items(), key=lambda x: x[1])

    # Extract keys and values from defaultdict
    addresses = list(address_counts.keys())
    counts = list(address_counts.values())

    # Plotting the horizontal bar graph
    plt.figure(figsize=(22, 5))
    plt.barh(addresses, counts, color='skyblue')

    # Adding title and labels
    plt.title('Patient Demographics')
    plt.xlabel('Number of Appointments')
    plt.ylabel('Number of Patient')

    # Save the chart as an image file
    patientDemographic = "patientDemographic.png"
    plt.savefig(patientDemographic)
    plt.close()

    # Encode the chart image file to base64
    with open(patientDemographic, "rb") as img_file:
        patientDemographic_bar_chart = base64.b64encode(img_file.read()).decode('utf-8')

    # Remove the chart image file
    os.remove(patientDemographic)

    # Get all the rate and review
    listOfRate = []
    listOfReviews = []

    uniqueUserIDs = set()
    walkInIDs = set()

    for reviews in allPatientReview:
        try:
            usersIDRev = reviews.patientID

            if usersIDRev is not None and usersIDRev not in uniqueUserIDs:
                accRate = reviews.rate
                accReview = reviews.review

                listOfRate.append(accRate)
                listOfReviews.append(accReview)

                uniqueUserIDs.add(usersIDRev)
        except AttributeError:
            pass

        try:
            wlkIDRev = reviews.walkInID

            if wlkIDRev is not None and wlkIDRev not in walkInIDs:
                wlkRate = reviews.rate
                wlkReview = reviews.review

                listOfRate.append(wlkRate)
                listOfReviews.append(wlkReview)

                walkInIDs.add(wlkIDRev)
        except AttributeError:
            pass
    # End For Loop 

    # Count the occurrences of each rate
    rate_counts = {}
    for rate in listOfRate:
        rate_counts[rate] = rate_counts.get(rate, 0) + 1

    # Generate the pie chart
    labels = list(rate_counts.keys())
    sizes = list(rate_counts.values())
    
    # labels_with_text = [f'{label}: Rated' for label in labels]
    labels_with_text = [f'{label}: Rated ({size:.1f}%)' for label, size in zip(labels, sizes)]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels_with_text, autopct='%1.1f%%')
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

    # Save the chart as an image file
    pie_chart_Rating = f"pie_chart_Rating.png"
    plt.savefig(pie_chart_Rating)
    plt.close(fig)

    # Encode the chart image file to base64
    with open(pie_chart_Rating, "rb") as img_file:
        pie_ChartRating = base64.b64encode(img_file.read()).decode('utf-8')

    # Remove the chart image file
    os.remove(pie_chart_Rating)

    context = {
        "clinic": clinic,
        # highest service
        "highest_service": highest_service,
        "highest_percentage": highest_percentage,

        "highest_month": highest_month,
        "lowest": lowest,

        "max_address": max_address,

        "chart_image": chart_image,
        "pie_ChartRating": pie_ChartRating,
        "appointments_bar_chart": appointments_bar_chart,
        "patientDemographic_bar_chart": patientDemographic_bar_chart,
    }

    # Render HTML template with table data
    template = get_template('pdf_Report_Clinic.html')
    html = template.render(context)

    # Create PDF using xhtml2pdf
    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'inline;filename="report.pdf"'  
    response['Content-Disposition'] = 'attachement;filename="Clinic Report {{clinic.clinicName}}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response

def get_all_user_ids():
    user_ids = Ophthalmologist.objects.values_list('opthID', flat=True)
    return list(user_ids)

def get_user_id_by_username(username):
    try:
        user_client = Ophthalmologist.objects.get(user__username=username)
        return user_client.opthID
    except Ophthalmologist.DoesNotExist: # ito talaga lumalabas. -- SOLVED?  
        print("BlahBlah Error")      
        return None

# DASHBOARD
def dashboard(request): 
    user = request.user
    try:    
        ophthalmologist = Ophthalmologist.objects.get(user=user)

        clinic = Clinic.objects.get(opthID=ophthalmologist) # this is to get the clinic ID base on the current log in
        clinic_name = clinic.clinicName
        counts = Booking.objects.filter(clinicID=clinic)
        total_appointments = counts.count()
        
        today = datetime.now()
        
        current_month = today.month
        current_year = today.year
        
        # Retrieve bookings for the current clinic
        appointments = Booking.objects.filter(clinicID=clinic, is_hidden=False)  
        current_date = date.today()
        todays_appointment = Booking.objects.filter(clinicID=clinic, appoint_Date=current_date, is_hidden=True, is_cancel = False, is_Status = False )
        
        today_appointments_count = Booking.objects.filter(clinicID=clinic,appoint_Date=current_date, is_Accepted = True).count()
        done_Todays_appointment = Booking.objects.filter(clinicID=clinic,appoint_Date=current_date, is_Accepted = True, is_Status = True).count()
        pending_Todays_appointment = Booking.objects.filter(clinicID=clinic,appoint_Date=current_date, is_Accepted = True, is_Status = False).count()
        
        next_appointment = Booking.objects.filter(
            clinicID=clinic,
            appoint_Date__gte=today.date(),
            appt_Start_Time__gte=today.time(),
            is_Accepted=True,
            is_Status=False
        ).aggregate(Min('appoint_Date'), Min('appt_Start_Time'))

        next_appointment_date = next_appointment['appoint_Date__min']
        next_appointment_time = next_appointment['appt_Start_Time__min']

        month_appointments_count = Booking.objects.filter(
            clinicID=clinic,
            appoint_Date__month=current_month,
            appoint_Date__year=current_year
        ).count()  

        current_datetime = timezone.localtime(timezone.now())  # Convert to local timezone

        # Filter appointments that have already passed
        passed_appointments = Booking.objects.filter(
            Q(appoint_Date__lt=current_datetime.date()) |
            (Q(appoint_Date=current_datetime.date()) & Q(appt_End_Time__lt=current_datetime.time()))
        )

        # Print the filtered queryset
        print("Filtered Appointments: ", passed_appointments)

        # Print details of each appointment in the queryset
        for app in passed_appointments:
            print("Appointment:", app.bookingID, "Date:", app.appoint_Date, "Start time:", app.appt_Start_Time)

        if passed_appointments.exists():
            print("Passed Appointments--------")
            passed_appointments.update(is_Status=True)
            for app in passed_appointments:
                appointment_datetime = timezone.make_aware(
                    datetime.combine(app.appoint_Date, app.appt_End_Time),
                    timezone.get_current_timezone()
                )
    
                if appointment_datetime < current_datetime:
                    # delay_seconds = 3600  
                    # time.sleep(delay_seconds)

                    app.is_Status = True
                    app.save()

                    print("Appointment that has passed:", app.clinicID, "start time of:", app.appt_Start_Time, " is status: ", app.is_Status)
                else:
                    print("PRINTTTT:", app.appt_Start_Time)
        else:
            print("No passed Appointments today")

        print("Current Date Time: ", current_datetime)

        for today in todays_appointment:
            print("Today's Start time: ", today.appt_Start_Time)
                
        context = {
            'clinic': clinic,
            'clinic_name': clinic_name,
            'todays_appointment': todays_appointment,            
            'appointments': appointments,            
            'total_appointments': total_appointments,

            'today_appointments_count': today_appointments_count,
            'month_appointments_count': month_appointments_count,
            'done_Todays_appointment': done_Todays_appointment,
            'pending_Todays_appointment': pending_Todays_appointment,
            'next_appointment_time': next_appointment_time,
        }

        return render(request, 'clinic-dashboard.html', context)
    
    except Ophthalmologist.DoesNotExist:
        # Handle the case where the user is not associated with an Ophthalmologist
        return render(request, 'clinic-dashboard.html', {'clinic_name': 'No Clinic Assigned'})
    
def update_booking_status(request): 
    print ("TEST 0 --------------- ZERO")  
    print("CSRF Token from Headers:", request.headers.get('X-CSRFToken'))
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        print ("TEST 1 --------------- ONE")
        try:
            data = json.loads(request.body.decode('utf-8'))
            booking_id = data.get('bookingId')
            status = data.get('status')
            booking = Booking.objects.get(bookingID=booking_id)
            if status == 'accept': # so this is now ok
                booking.is_Accepted = True
                booking.is_hidden = True
                print ("Booking is Accepted")
                print ("TEST 2 --------------- TWO")
            elif status == 'decline':
                booking.is_Denied = True
                booking.is_hidden = True
                print ("Booking is Denied")
                print ("TEST 3 --------------- THREE")
            booking.save()
            return JsonResponse({'success': True})
        except Booking.DoesNotExist:
            print ("TEST 4 --------------- FOUR")
            return JsonResponse({'success': False, 'error': 'Booking not found'})            
    else:
        print(request.headers)
        print ("TEST 5 --------------- FIVE")
        return JsonResponse({'success': False, 'error': 'Invalid request method or not AJAX'})
    
@login_required
def move_appointment(request, booking_id):
    
    print("Move Appointment View Triggered")
    print("Request method:", request.method)
    print("POST data:", request.POST)
    
    print ("Fuck THis Shit!!!")
    print(request.user)
    try:
        booking = get_object_or_404(Booking, bookingID=booking_id)
        
        if request.method == 'POST':
            new_date = request.POST.get('new_date')
            new_time = request.POST.get('time')
            notes = request.POST.get('notes')
            
            booking = Booking.objects.get(bookingID=booking_id)            
            
            print ("New Date ---------", new_date)
            print ("New Time ---------", new_time)

            # Validate that new_date and new_time are not None            
            if new_date and new_time:        

                new_date_obj = datetime.strptime(new_date, "%Y-%m-%d")
                new_time_obj = datetime.strptime(new_time, "%H:%M").time()

                selected_datetime = datetime.combine(new_date_obj, new_time_obj)

                new_end_datetime = selected_datetime + timedelta(hours=1)

                booking.appoint_Date = new_date
                booking.appt_Start_Time = new_time
                booking.appt_End_Time = new_end_datetime  
                booking.save()

                print("PREV SCHEDULE!----------------- ")
                print("Date: ", booking.prev_appoint_Date)
                print("Start Time: ", booking.prev_appt_Start_Time)
                print("End Time: ", booking.prev_appt_End_Time)

                print("NEW SCHEDULE!----------------- ")
                print("Date: ", booking.appoint_Date)
                print("Start Time: ", selected_datetime)
                print("End Time: ", new_end_datetime)
                print("Note: ", notes)

                # Add any additional logic you need, such as sending notifications or updating the user interface.
                return render(request, 'clinic-dashboard.html')  
            else:
                # Handle the case where new_date or new_time is None
                print("Error: new_date or new_time is None")
                # You may want to redirect or render an error page here
        return JsonResponse({'message': 'Move successful'})
              
    except Booking.DoesNotExist as e:
        # Print the exception for debugging
        print(e)
        return HttpResponseNotFound("Booking not found")
    
    except Exception as e:
        print(e)  # Print the exception for debugging

        # Handle other error cases
        return HttpResponseServerError("Internal Server Error")
    
def clinic_dash_curS(request):
    return render(request, 'clinic-dashboard-currentSesion.html')

def clinic_dashboard_notes(request):
    return render(request, 'clinic-dashboard-notes.html')

def clinic_dashboard_Stats(request):
    user = request.user
    ophthalmologist = Ophthalmologist.objects.get(user=user)
    clinic = Clinic.objects.get(opthID=ophthalmologist)
    allPatientReview = PatientReview.objects.filter(clinicID = clinic)
    appointments = Booking.objects.filter(clinicID=clinic, is_Accepted=True, is_Status = True)

    listOfNames = []
    listOfBday = []

    uniqueWalkIDs = set()
    uniqueUserIDs = set()
    current_year = datetime.now().year

    for a in appointments:  # for APPOINTMENT/BOOKING COUNT 
        try:
            usersID = a.userID
            if usersID not in uniqueUserIDs:
                accFirstBday = a.userID.bday
                accFirstName = a.userID.firstName
                listOfNames.append(accFirstName)
                listOfBday.append(accFirstBday.year)                
                uniqueUserIDs.add(usersID)
        except:
            pass
        try:
            wlkID = a.walkInID
            if wlkID not in uniqueWalkIDs:
                wlkFirstBday = a.walkInID.bday
                wlkFirstName = a.walkInID.firstName
                listOfNames.append(wlkFirstName)
                listOfBday.append(wlkFirstBday.year)
                uniqueWalkIDs.add(wlkID)
        except:
            pass
      
    listOfRate = []
    listOfReviews = []

    uniqueUserIDs = set()
    walkInIDs = set()

    for reviews in allPatientReview:
        try:
            usersIDRev = reviews.patientID

            if usersIDRev is not None and usersIDRev not in uniqueUserIDs:
                accRate = reviews.rate
                accReview = reviews.review

                listOfRate.append(accRate)
                listOfReviews.append(accReview)

                uniqueUserIDs.add(usersIDRev)
        except AttributeError:
            pass

        try:
            wlkIDRev = reviews.walkInID

            if wlkIDRev is not None and wlkIDRev not in walkInIDs:
                wlkRate = reviews.rate
                wlkReview = reviews.review

                listOfRate.append(wlkRate)
                listOfReviews.append(wlkReview)

                walkInIDs.add(wlkIDRev)
        except AttributeError:
            pass
        
    print("List of Rates: ", listOfRate)
    print("List of Reviews: ", listOfReviews)
    print("List of Set for Users: ", uniqueUserIDs)
    print("List of Set for Walk In: ", walkInIDs)

    ages = [current_year - year for year in listOfBday]
    monthly_counts = appointments.annotate(month=ExtractMonth('appoint_Date')).values('month').annotate(count=Count('bookingID')).order_by('month')

    months = [count['month'] for count in monthly_counts]
    counts = [count['count'] for count in monthly_counts]

    date_today = datetime.now()
    month_today = date_today.month # 2 - 1 = 1
    year_today = date_today.year

    # Yearly Patient Count
    months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    all_months = [] # this will be displayed at the bottom of the chart (x axis)
    for i in range(0, 12):
        if i >= (month_today - 1):
            all_months.append(f'{months[i]} {year_today - 1}')

    for i in range(0,12):
        if len(all_months) != 13:
            all_months.append(f'{months[i]} {year_today}')
        else:
            break

    all_formatted_dates = [] # the values of this container will be used for filtering
    start_year = year_today - 1
    start_month = month_today
    for i in range(0, 13):
        complete_date_today = f'{start_year}-{start_month}-01'
        starting_date = (datetime.strptime(complete_date_today, '%Y-%m-%d')).strftime('%Y-%m-%d')
        endDate = (datetime.strptime(str(starting_date), '%Y-%m-%d')).strftime('%Y-%m-%d')     # first day of the next month - 1 to get the last date of the month (present)

        if (start_month == 12):
            start_month = 1
            start_year = start_year + 1
        else:
            start_month = start_month + 1
        all_formatted_dates.append(endDate)
    
    y_axis = []
    for date in all_formatted_dates:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        all_count = Booking.objects.filter(appoint_Date__month = date_obj.month, appoint_Date__year = date_obj.year, clinicID = clinic ).count()
        y_axis.append(all_count)

    # All Services
    services = {}

    # Get all services
    all_services = Services.objects.filter(clinicID = clinic)

    for service in all_services:
        service_count = Services.objects.filter(service_Name=service.service_Name, clinicID = clinic).count()
        services[service.service_Name] = service_count
        
    services_requestedDict = {}

    all_bookings = Booking.objects.all()

    for booking in all_bookings:
        if booking.serviceID is not None:
            service_name = booking.serviceID.service_Name
            service_req_count = Booking.objects.filter(serviceID__service_Name=service_name, clinicID = clinic).count()
            services_requestedDict[service_name] = service_req_count

    services_requested = json.dumps(services_requestedDict)

    context = {
        "appointments": appointments,
        "ages": ages,
        "months": months,
        "counts": counts,
        "listOfRate": listOfRate,
        "listOfReviews": listOfReviews,
        "all_months": all_months,
        "clinic": clinic,
        "y_axis": y_axis,
        "services_requested": services_requested,
    }

    return render(request, 'clinic-dashboard-Stats.html',context)

def clinic_dashboard_profile(request):
    return render(request, 'clinic-dashboard-profile.html')

def clinic_dashboard_profile_Staff(request):
    return render(request, 'clinic-dashboard-profile-Staff.html')

def clinic_dashboard_profile_Opthal(request):
    return render(request, 'clinic-dashboard-profile-Opthal.html')

# WALK IN
def clinic_dashboard_walkIn(request):
    user = request.user
    print(user)
    return render(request, 'clinic-dashboard-WalkIn.html')

def clinic_dashboard_walkInForm(request):
    user = request.user
    getOpthal = Ophthalmologist.objects.get(user = user)
    getClinic = Clinic.objects.get(opthID = getOpthal)

    getAllPatient = Booking.objects.filter(clinicID = getClinic)
    getAllMedicalHis = PatientMedicalHistory.objects.filter(clinicID = getClinic)

    for patient in getAllPatient:
        try:
            if patient.walkInID is None:
                print("User: ",patient.userID)
            else:
                print("Walk In: ",patient.walkInID)
        except:
            pass
        
    context = {
        "getAllPatient": getAllPatient,
        "getAllMedicalHis": getAllMedicalHis,
    }

    return render(request, 'clinic-dashboard-WalkInForm.html', context)

def checkPatientInformation(request):
    user = request.user
    opthID = Ophthalmologist.objects.get(user=user)
    clinicID = Clinic.objects.get(opthID=opthID)

    showAdditionalInfo = True
    showMedicalHistory = True
    perInID = None
    userExisted = False
    userID = None
    contact = None

    NewfirstName = request.POST.get('firstName')
    NewmiddleName = request.POST.get('middleName')
    NewlastName = request.POST.get('lastName')
    bday_str = request.POST.get('bday')
    Newbday = datetime.strptime(bday_str, '%Y-%m-%d').date() if bday_str else None

    Newsex = request.POST.get('sex')
    NewhomeAddress = request.POST.get('homeAddress')
    NewcontactNum = request.POST.get('contactNum')

    selected_patient_id = request.POST.get('selectedPatientID') 
    selectedFirstName = request.POST.get('selectedFirstName') 
    print("Selected Patient First Name: ]]]]] =====================================================0", selectedFirstName)   

    if selected_patient_id is not None:
        toInt = int(selected_patient_id)
    
    if selected_patient_id:

        try:
            seek_patient = WalkInPatient.objects.filter(walkInID=toInt, firstName = selectedFirstName)
            
            if seek_patient.exists():
                user_id = seek_patient.first().walkInID
                getWalkIn = WalkInPatient.objects.get(walkInID=user_id)                  
                try:
                    contact = UserContacts.objects.get(walkInID=getWalkIn)
                except UserContacts.DoesNotExist:
                    contact = None

                walkInID = getWalkIn
                getWalkID = getWalkIn.walkInID
                userExisted = True
                category = "WalkIn"
                                                
                try:
                    check = PatientMedicalHistory.objects.filter(
                        walkInID=getWalkIn,
                        clinicID=clinicID,
                    )
                    if check.exists():
                        showMedicalHistory = False
                    else:
                        pass            
                except:
                        pass   

                try:
                    check = PatientPersonalInformation.objects.filter(walkInID=getWalkIn, clinicID=clinicID)
                    print("check", check)

                    if check.exists():
                        
                        getPatientInfo = check.first()
                        perInID = getPatientInfo
                        showAdditionalInfo = False
                        print("Found additional information for the patient.")
                    else:
                        
                        showAdditionalInfo = None
                        print("No additional information found for the patient.")

                except PatientPersonalInformation.DoesNotExist:
                    showAdditionalInfo = None
                    return HttpResponse("PatientPersonalInformation does not exist.")

                except Exception as e:
                    print("Error:", e)
                
                context = {
                    "contact": contact, 
                    "category": category, 
                    "newPatient": walkInID, 
                    "walkInID": getWalkID, 
                    "userExisted": userExisted, 
                    "clinicID": clinicID, 
                    "showAdditionalInfo": showAdditionalInfo, 
                    "showMedicalHistory": showMedicalHistory, 

                    "NewfirstName": NewfirstName, 
                    "NewmiddleName": NewmiddleName, 
                    "NewlastName": NewlastName, 
                    "Newbday": Newbday, 
                    "Newsex": Newsex, 
                    "NewhomeAddress": NewhomeAddress, 
                    "NewcontactNum": NewcontactNum, 
                    "perInID": perInID,  
                }

                return render(request, "clinic-dashboard-WalkInDataSheet.html", context) 
                    
        except WalkInPatient.DoesNotExist:
            return HttpResponse("WalkInPatient does not exist")
        except UserContacts.DoesNotExist:
            return HttpResponse("UserContacts does not exist")
        except PatientPersonalInformation.DoesNotExist:
            return HttpResponse("PatientPersonalInformation does not exist")
        except Exception as e:
            print("Error:", e)
            return HttpResponse("An error occurred")
        
        try:
            seek_patient = UserPatient.objects.filter(userID=toInt, firstName = selectedFirstName)
            
            if seek_patient.exists():
                user_id = seek_patient.first().userID
                getUser = UserPatient.objects.get(userID=user_id)

                patientID = getUser
                getID = getUser.userID
                userExisted = True
                category = "Account"

                try:
                    checkRecord = PatientMedicalHistory.objects.filter(patientID=getUser, clinicID=clinicID)

                    if checkRecord.exists():
                        showMedicalHistory = False                
                        print("Found!!")                
                    else:
                        print("Not Found!!")                
                except:   
                    pass     
                            
                try:
                    
                    check = PatientPersonalInformation.objects.filter(patientID=getID, clinicID=clinicID)
                    print("check", check)
                    
                    if check.exists():
                        
                        getPatientInfo = check.first()
                        perInID = getPatientInfo
                        showAdditionalInfo = False
                        print("Found additional information for the patient.")
                    else:
                        
                        showAdditionalInfo = None
                        print("No additional information found for the patient.")

                except PatientPersonalInformation.DoesNotExist:
                    showAdditionalInfo = None
                    return HttpResponse("PatientPersonalInformation does not exist.")

                except Exception as e:
                    print("Error:", e)

                context = {
                    "category": category, 
                    "getID": getID, 
                    "patientID": patientID, 
                    "userExisted": userExisted, 
                    "clinicID": clinicID, 
                    "showAdditionalInfo": showAdditionalInfo, 
                    "showMedicalHistory": showMedicalHistory, 
                    "NewfirstName": NewfirstName, 
                    "NewmiddleName": NewmiddleName, 
                    "NewlastName": NewlastName, 
                    "Newbday": Newbday, 
                    "Newsex": Newsex, 
                    "NewhomeAddress": NewhomeAddress, 
                    "NewcontactNum": NewcontactNum,  
                    "perInID": perInID,  
                }
                 
                return render(request, "clinic-dashboard-WalkInDataSheet.html", context)
        except:
            pass

    else:
        birthdate = datetime.strptime(bday_str, '%Y-%m-%d')
        current_date = datetime.now()
        age = current_date.year - birthdate.year - ((current_date.month, current_date.day) < (birthdate.month, birthdate.day))

        createPatients = WalkInPatient.objects.create(
            firstName = NewfirstName,
            middleName = NewmiddleName,
            lastName = NewlastName,
            bday = Newbday,
            age = age,
            sex = Newsex,
            homeAddress = NewhomeAddress,
            contactNum = NewcontactNum,
        )

        createPatients.save()
        getNewPatient = WalkInPatient.objects.get(firstName = NewfirstName, lastName = NewlastName, bday = Newbday)
        walkInID = getNewPatient
        getNewWalkID =  getNewPatient.walkInID
        category = "WalkIn"
        
        context = {
            "category": category, 
            "walkInID": getNewWalkID, 
            "newPatient": walkInID, 
            "userExisted": userExisted, 
            "clinicID": clinicID, 
            "showAdditionalInfo": showAdditionalInfo, 
            "showMedicalHistory": showMedicalHistory, 
            "NewfirstName": NewfirstName, 
            "NewmiddleName": NewmiddleName, 
            "NewlastName": NewlastName, 
            "Newbday": Newbday, 
            "Newsex": Newsex, 
            "NewhomeAddress": NewhomeAddress, 
            "NewcontactNum": NewcontactNum, 
        }
        
        return render(request, "clinic-dashboard-WalkInDataSheet.html", context)
    
    return HttpResponse("Stopeer") 

def dataSheetWalkIn(request):
    return HttpResponse("Data Sheet Walk In")

# END WALK IN
@require_POST
def update_session_status(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        print ("TEST 1 --------------- ONE")
        try:
            data = json.loads(request.body.decode('utf-8'))
            booking_id = data.get('bookingId')
            status = data.get('action')
            booking = Booking.objects.get(bookingID=booking_id)
            if status == 'end_session': 
                booking.is_Status = True
                print ("End Session")
                print ("TEST 2 --------------- TWO")
            elif status == 'cancel_session':
                booking.is_cancel = True
                print ("Cancel Session")
                print ("TEST 3 --------------- THREE")
            booking.save()
            
            print ("Status = ", booking.is_Status)
            print ("Cancel = ", booking.is_cancel)

            return JsonResponse({'success': True, 'is_hidden': booking.is_hidden})
        except Booking.DoesNotExist:
            print ("TEST 4 --------------- FOUR") 
            return JsonResponse({'success': False, 'error': 'Booking not found'})
            
    else:
        print(request.headers)
        print ("TEST 5 --------------- FIVE")
        return JsonResponse({'success': False, 'error': 'Invalid request method or not AJAX'})
# END OF DASHBOARD
           
def test_Map(request):    
    return render(request, 'test_Map.html')
    
# BOOKING PAGE!!!
def check_availability(request):
    clinic_id = request.GET.get('clinic_id')
    selected_date = request.GET.get('date')

    print("Print Selected Date: ", selected_date)

    # Query the database to get unavailable times
    unavailable_times = Booking.objects.filter(
        clinicID=clinic_id,
        appoint_Date=selected_date,
        is_Accepted=True,
    ).values_list('appt_Start_Time', flat=True)

    for time in unavailable_times:
        print("Print unavailable time: ", time)

    return JsonResponse(list(unavailable_times), safe=False)

@login_required
def pop_up_redirect(request, clinic_id):
    print("clinicID:", clinic_id)    
    user = request.user
    user_client = None
    clinic = get_object_or_404(Clinic, clinicID=clinic_id) # this is for the clinic itself
    
    try:
        services = Services.objects.filter(clinicID=clinic_id)
    except Services.DoesNotExist:    
        services = []   

    if request.user.is_authenticated:        
        user_client = UserPatient.objects.get(user=user)

        if request.method == 'POST':
            selected_date = request.POST.get('date')    
            selected_time = request.POST.get('time')
            selected_service = request.POST.get('service')  
            
            allBooking = Booking.objects.filter(userID = user_client)
            
            try:
                for bookDate in allBooking:
                    print("Print all the appointment: ", bookDate.appoint_Date, " and type of it ", type(bookDate.appoint_Date))
                    print("Selected Date: ", selected_date, " and type of it ", type(selected_date) )

                    selected_date_object = datetime.strptime(selected_date, "%Y-%m-%d").date()

                    if bookDate.appoint_Date == selected_date_object:
                        print("Appointment at the ", bookDate.clinicID.clinicName)
                        clinic_name = bookDate.clinicID.clinicName if bookDate.clinicID else 'Unknown Clinic'
                        messages.error(request, f'You have an appointment to {clinic_name} on your selected date at {bookDate.appoint_Date} {bookDate.appt_Start_Time}')
                        return redirect(f'/clinic/{clinic.clinicID}/booking_Page/')
            except:
                pass

            if not (selected_date and selected_time and selected_service):
                messages.error(request, 'Please fill in all required fields.')
                return redirect(f'/clinic/{clinic.clinicID}/booking_Page/')
            
            service_instance = Services.objects.get(serviceID=selected_service)  
            notes = request.POST.get('notes')
    
            datetime_str = f"{selected_date} {selected_time.strip()}"
            selected_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

            # Calculate the end time based on the selected time (assuming each appointment is 1 hour)
            end_datetime = selected_datetime + timedelta(hours=1)
            
            bookingInfo = Booking(
                userID=user_client,  
                clinicID=clinic,
                serviceID=service_instance,                
                appoint_Date=selected_date,
                appt_Start_Time=selected_time,
                appt_End_Time=end_datetime,
                notes=notes
            )
            bookingInfo.save()        
            messages.info(request, 'Thank you for chosing ', clinic, ". We will notify you for your appointment approval")
            return redirect('/')
                
    else:        
        return redirect(reverse('login'))

        
    print("Is user authenticated?", request.user.is_authenticated)       
        
    context = {
        'clinic': clinic,
        'user_client': user_client,
        'services': services,
    }
    
    return render(request, 'booking_page.html', context)

def booking_Page(request, clinic_id):    
    return render(request, 'booking_Page.html')
# END OF BOOKING

@login_required
def user_profile(request):     # show user profile
    user = request.user
    user_client = None

    try:
        user_client = UserPatient.objects.get(user=user)
    except UserPatient.DoesNotExist:
        pass

    allPatientContact = UserContacts.objects.filter(userID = user_client)

    allBooking = Booking.objects.filter(userID = user_client, is_Success = True)

    # Filter upcoming appointments
    upcomingBookings = Booking.objects.filter(
        userID=user_client,
        is_Accepted = True,
        is_Success = False,
        appoint_Date__gte=timezone.now().date(),  # Filter appointments with date greater than or equal to the current date
        appt_End_Time__gte=timezone.now().time()   # Filter appointments with end time greater than or equal to the current time
    )

    context = {
        'user': user,
        'user_client': user_client,
        'allPatientContact': allPatientContact,
        'allBooking': allBooking,
        'upcomingBookings': upcomingBookings,
    }

    return render(request, 'user_profile.html', context)

def update_page(request):
    user = request.user
    user_client = UserPatient.objects.get(user=request.user) # this is to get the user's data
    user_contact = UserContacts.objects.get(pConID=UserPatient.userID) # this is to get the user's data
    
    print("User:", request.user)
    print("User Permissions:", request.user.get_all_permissions())

    if request.method=="POST": 
        # updating user information through user input
        user_client.firstName = request.POST.get('FName','')
        user_client.middleName = request.POST.get('MName','')
        user_client.lastName = request.POST.get('LName','')
        user_client.bday = request.POST.get('biday','')
        user_client.sex = request.POST.get('sex','')
        user_client.homeAddress = request.POST.get('HomeAdd','')
        user_client.contactNum = request.POST.get('ContactNum','')

        user_contact.firstName = request.POST.get('EFName','')
        user_contact.middleName = request.POST.get('EMName','')
        user_contact.lastName = request.POST.get('ELName','')
        user_contact.relationship = request.POST.get('ERelatioship','')
        user_contact.contactNum = request.POST.get('contactEmNum','')   

        # this will be imported in User
        new_email = request.POST.get('Email','')
        user.email = new_email
        user.save()
        user_client.save()
        user_contact.save()

        return redirect('user_profile')
    else:
        return render(request, 'update_page.html', {'user_client':user_client})

# CALENDAR
def DashCalendar(request): 
    return render(request, 'selectable.html')

def save_event(request): 
    
    if request.method == 'POST':
        data = request.POST
        title = data.get("appt_title", None)
        start = data.get("appt_start", None)
        end = data.get("appt_end", None)
        all_day = data.get('appt_allDay', False)

        logger.info(f"title: {title}, start: {start}, end: {end}, all_day: {all_day}")
        
        event = DashCalendar(title=title, apptStart=start, apptEnd=end, is_allDay = all_day)
        event.save() 
        data = {}

        response_data = {'message': 'Event saved successfully'}
        return JsonResponse(response_data)
    return render(request, 'clinic-dashboard.html')

@csrf_exempt
def get_events(request, clinic_id): 
    if request.method == 'GET':
        # Retrieve only accepted appointments
        accepted_appointments = Booking.objects.filter(is_Accepted=True, clinicID=clinic_id)

        # Create a list to hold the events
        events = []

        # Iterate over accepted appointments and create events
        for appointment in accepted_appointments:
            # Extract the relevant fields from the Services model
            if appointment.userID:
                # Extract the relevant fields from the Services model
                service_data = serialize('json', [appointment.userID])
                service_dict = json.loads(service_data)[0]['fields']
                service_name = service_dict['firstName']
            elif appointment.walkInID:
                # Extract the relevant fields from the WalkInPatient model 
                service_data = serialize('json', [appointment.walkInID])
                service_dict = json.loads(service_data)[0]['fields']
                service_name = service_dict['firstName']
            else:
                # Set default values when both userID and walkInID are empty
                service_name = 'Unknown User'

            # Combine date and time to create start and end datetime objects
            start_datetime = timezone.make_aware(
                datetime.combine(appointment.appoint_Date, appointment.appt_Start_Time),
                timezone.get_current_timezone()
            )

            end_datetime = timezone.make_aware(
                datetime.combine(appointment.appoint_Date, appointment.appt_End_Time),
                timezone.get_current_timezone()
            )
            
            events.append({

                'bookingID': appointment.bookingID,
                'title': service_name, 
                'start': start_datetime.isoformat(),
                'end': end_datetime.isoformat(),
            })

        # Return events as JSON response
        return JsonResponse(events, safe=False)
    else:
        # Handle other HTTP methods as needed
        return JsonResponse({'error': 'Method not allowed'}, status=405)
# END OF CALENDAR 

# TODAY'S APPOINTMENT
def patientProfile(request, bookingID):
    
    print("PATIENT PROFILEEEEEE --------------- ")
    logger = logging.getLogger(__name__)

    try:
        booking = Booking.objects.get(bookingID=bookingID)
        getClinic = booking.clinicID.clinicID
        get_Clinic =  booking.clinicID

        print("Clinic ID: ", getClinic)

        allSessions = []        
        sessionID = None
        oheID = None
        dryEyeID = None
        refractionID = None
        perInID = None
        historyRecordID = None
        walkIn = "False"
        patient = None

        if booking.walkInID is not None:
            walkInID = booking.walkInID.walkInID
            try:
                walkInPatient = WalkInPatient.objects.get(walkInID=walkInID)
                print("Walk In PROFILEEEEEE --------------- ")
                logger.info("User: %s", walkInPatient)
                patient = walkInPatient
                print("Walk In PROFILEEEEEE --------------- ", patient.walkInID)
                walkIn = "True"

                try:
                    sessions = Session.objects.filter(clinicID = getClinic, walkInPatientID = walkInPatient)                    
                    if sessions.exists():
                        print("Session is not none: ", sessions)                        
                        for session in sessions:
                            sessionID = session.sessionID
                            allSessions.append(sessionID)
                            print("Session's ID: ", sessionID)
                            print("Print all Sessions: ", allSessions)
                    else:
                        print("No Record")
                        sessionID = None
                except Session.DoesNotExist:
                    print("No Record")
                    pass

                try:
                    ocHE = ocularHealthExamination.objects.filter(clinicID = getClinic, walkInID = walkInID)                    
                    if ocHE is not None:
                        print("Session is not none: ", ocHE)
                        for session in ocHE:
                            oheID = session
                            print("Session's ID: ", oheID)
                    else:
                        print("No Record")
                        oheID = None
                except ocularHealthExamination.DoesNotExist:
                    print("oheID No Record")
                    pass

                try:
                    dry = dryEyeTest.objects.filter(clinicID = getClinic, walkInID = walkInID)                    
                    if dry is not None:
                        print("Session is not none: ", sessions)
                        for drys in dry:
                            dryEyeID = drys
                            print("Session's ID: ", dryEyeID)
                    else:
                        print("No Record")
                        dryEyeID = None
                except dryEyeTest.DoesNotExist:
                    print("No Record")
                    pass

                try:
                    refras = Refraction.objects.filter(clinicID = getClinic, walkInID = walkInID)                    
                    if refras is not None:
                        print("Session is not none: ", sessions)
                        for refra in refras:
                            refractionID = refra
                            print("Session's ID: ", refractionID)
                    else:
                        print("No Record")
                        refractionID = None
                except Refraction.DoesNotExist:
                    print("No Record")
                    pass

                try:
                    ppInfo = PatientPersonalInformation.objects.filter(clinicID = getClinic, walkInID = walkInID)                    
                    if ppInfo is not None:
                        print("Session is not none: ", sessions)
                        for ppInfos in ppInfo:
                            perInID = ppInfos
                            print("Session's ID: ", perInID.civilStatus)
                    else:
                        print("No Record a")
                        perInID = None
                except PatientPersonalInformation.DoesNotExist:
                    print("No Record ------------")
                    pass

                try:
                    historys = PatientMedicalHistory.objects.filter(clinicID = getClinic, walkInID = walkInID)                    
                    if historys is not None:
                        print("historys is not none: ", historys)
                        for history in historys:
                            historyRecordID = history
                            print("Session's ID: ", historyRecordID)
                    else:
                        print("No Record")
                        historyRecordID = None
                except PatientMedicalHistory.DoesNotExist:
                    print("No Record")
                    pass


            except WalkInPatient.DoesNotExist:
                logger.error("WalkInPatient with ID %s does not exist", walkInID)
                # Handle the case when the WalkInPatient doesn't exist.
                return HttpResponse("WalkInPatient not found")

        else:
            patientID = booking.userID.userID
            try:
                patient = UserPatient.objects.get(userID=patientID)
                print("PATIENT PROFILEEEEEE --------------- ")
                logger.info("User: %s", patient)
                walkIn = "False"

                try:
                    sessions = Session.objects.filter(clinicID = getClinic, patientID = patient)                    
                    if sessions.exists():
                        print("Session is not none: ", sessions)
                        for session in sessions:
                            sessionID = session.sessionID
                            allSessions.append(sessionID)
                            print("Session's ID: ", sessionID)
                            print("Print all Sessions: ", allSessions)
                    else:
                        print("No Record")
                        sessionID = None
                except Session.DoesNotExist:
                    print("No Record")
                    pass

                try:
                    ocHE = ocularHealthExamination.objects.filter(clinicID = getClinic, patientID = patientID)                    
                    if ocHE is not None:
                        print("Session is not none: ", ocHE)
                        for session in ocHE:
                            oheID = session
                            print("Session's ID: ", oheID)
                    else:
                        print("No Record")
                        oheID = None
                except ocularHealthExamination.DoesNotExist:
                    print("oheID No Record")
                    pass

                try:
                    dry = dryEyeTest.objects.filter(clinicID = getClinic, patientID = patientID)                    
                    if dry is not None:
                        print("Session is not none: ", sessions)
                        for drys in dry:
                            dryEyeID = drys
                            print("Session's ID: ", dryEyeID)
                    else:
                        print("No Record")
                        dryEyeID = None
                except dryEyeTest.DoesNotExist:
                    print("No Record")
                    pass

                try:
                    refras = Refraction.objects.filter(clinicID = getClinic, patientID = patientID)                    
                    if refras is not None:
                        print("Session is not none: ", sessions)
                        for refra in refras:
                            refractionID = refra
                            print("Session's ID: ", refractionID)
                    else:
                        print("No Record")
                        refractionID = None
                except Refraction.DoesNotExist:
                    print("No Record")
                    pass

                try:
                    ppInfo = PatientPersonalInformation.objects.filter(clinicID = getClinic, patientID = patientID)                    
                    if ppInfo is not None:
                        print("Personal Info is not none: ", sessions)
                        for ppInfos in ppInfo:
                            perInID = ppInfos
                            print("Session's ID: ", perInID.civilStatus)
                    else:
                        print("Personal Info No Record")
                        perInID = None
                except PatientPersonalInformation.DoesNotExist:
                    print("No Record")
                    pass
                
                try:
                    historys = PatientMedicalHistory.objects.filter(clinicID = getClinic, patientID = patientID)                    
                    if historys is not None:
                        print("History is not none: ", sessions)
                        for history in historys:
                            historyRecordID = history
                            print("Session's ID: ", historyRecordID)
                    else:
                        print("History No Record")
                        historyRecordID = None
                except PatientMedicalHistory.DoesNotExist:
                    print("No Record")
                    pass

            except UserPatient.DoesNotExist:
                logger.error("UserPatient with ID %s does not exist", patientID)
                # Handle the case when the UserPatient doesn't exist.
                return HttpResponse("UserPatient not found")

        context = {
            'sessions': sessions,
            'sessionID': sessionID,
            'allSessions': allSessions,

            'ocHE': ocHE,
            'oheID': oheID,

            'dry': dry,
            'dryEyeID': dryEyeID,

            'refras': refras,
            'refractionID': refractionID,

            'ppInfo': ppInfo,
            'perInID': perInID,

            'historys': historys,
            'historyRecordID': historyRecordID,

            'getClinic': getClinic,

            'patient': patient,
            'bookingID': booking.bookingID,
            'bookInfo': booking,
            'walkIn': walkIn,
        }
        print("ID for walkIn :", walkIn)

        if booking.serviceID:
            print("Service Name :", booking.serviceID.service_Name)
    except Booking.DoesNotExist:
        logger.error("Booking with ID %s does not exist", bookingID)
        # Handle the case when the booking doesn't exist, e.g., redirect to an error page.

    return render(request, 'clinic-patientProfile.html', context)

def dataSheet(request,bookingID):
    user = request.user
    ophthalmologist = Ophthalmologist.objects.get(user=user)
    clinic = Clinic.objects.get(opthID=ophthalmologist)

    bookID = Booking.objects.get(bookingID = bookingID)
    get_PatientID = bookID.userID.userID
    patient = UserPatient.objects.get(userID = get_PatientID)

    try:
        patientContact = UserContacts.objects.get(userID = patient) 
    except UserContacts.DoesNotExist:
        patientContact = None
    
    bookings = Booking.objects.filter(clinicID=clinic, userID=patient).order_by('appoint_Date')
    total_bookings = bookings.count()

    showMedicalHistoryForm = True
    try:        
        medical_history = PatientMedicalHistory.objects.get(patientID=patient, clinicID=clinic)
        showMedicalHistoryForm = False

        print("Medical History Record Found with ID: ", medical_history)

    except PatientMedicalHistory.DoesNotExist:
        print("No Medical History Record Found for this UserPatient")

    print("Show Medical History Form? ", showMedicalHistoryForm)

    showPatientInfoForm = True
    patientInfo = None
    try:        
        patientAddInfo = PatientPersonalInformation.objects.get(patientID=patient.userID, clinicID=clinic.clinicID)
        patientInfo = patientAddInfo
        showPatientInfoForm = False

        print("Patient Info Found with ID: ", patientInfo)

    except PatientPersonalInformation.DoesNotExist:
        print("No PatientPersonalInformation Record Found for this UserPatient")

    current_booking_index = None
    for i, booking in enumerate(bookings):
        if booking.bookingID == bookID.bookingID:
            current_booking_index = i
            break

    # Calculate previous and next booking indices
    previous_booking_index = current_booking_index - 1 if current_booking_index > 0 else None
    next_booking_index = current_booking_index + 1 if current_booking_index < total_bookings - 1 else None

    # Retrieve previous and next bookings
    previous_booking = bookings[previous_booking_index] if previous_booking_index is not None else None
    next_booking = bookings[next_booking_index] if next_booking_index is not None else None

    if previous_booking is None:
        prevApp = "No recorded appointment"
    else:
        prevApp = previous_booking.appoint_Date

    if next_booking is None:
        nextAppt = "No new appointment are scheduled"
    else:
        nextAppt = next_booking.appoint_Date
    
    print("Book ID: ", bookID)
    print("Patient Name: ", patient)
    print("Total Appointment of the Patients: ", total_bookings)
    print("Previous Appointment: ", prevApp)
    print("Next Appointment: ", nextAppt)

    context = {
            'patientInfo':patientInfo,
            'showPatientInfoForm':showPatientInfoForm,
            'showMedicalHistoryForm':showMedicalHistoryForm,
            'bookingID':bookingID,
            'prevApp':prevApp,
            'nextAppt':nextAppt,
            'patient':patient,
            'total_appointments':total_bookings,
            'patientContact':patientContact,
            'bookID':bookID,
        }

    # return HttpResponse ("Data Sheet")
    return render(request, 'clinic-dashboard-currentSesion.html', context)

def savedData(request):
    if request.method == 'POST':

        user = request.user
        getOpt = Ophthalmologist.objects.get(user=user)
        getClinic = Clinic.objects.get(opthID = getOpt)

        is_WalkIn = None
        is_Account = None
        walkInID = None
        NewpatientID = None
        getPatient = None
        confirm = None

        is_PatientWalkin = request.POST.get('category')

        is_Appointment = request.POST.get('is_Appointment')    

        if is_Appointment == "True": 
            try:
                print("Test if this will be printed!")
                getpatientIDFE = request.POST.get('getID')
                getpatientID = int(getpatientIDFE)
                getNewpatientID = UserPatient.objects.get(userID=getpatientID)
                getPatient = getNewpatientID
                getBookingID = request.POST.get('bookingID')
                getBookID = int(getBookingID)

                try:
                    bookingID = Booking.objects.get(bookingID=getBookID)
                    is_WalkIn = False

                except:
                    pass            
            except Exception as e:
                return HttpResponse("An error occurred: {}".format(e))
        
        getwalkInID = request.POST.get('walkInID')
        getpatientIDFE = request.POST.get('getID')

        print("Is it have a value?  Walk In: ", getwalkInID, " Appointment: ", getpatientIDFE)
        if is_PatientWalkin == "Account" or "WalkIn":
            if is_PatientWalkin == "WalkIn":
                try:
                    if getwalkInID is not None or getwalkInID is not "":            
                        getpatientID = int(getwalkInID)

                        print ("sdffffffffffffffffff", getwalkInID)

                        takewalkInID = WalkInPatient.objects.get(walkInID=getpatientID)
                        walkInID = takewalkInID
                        is_WalkIn = True
                        is_Account = False
                except WalkInPatient.DoesNotExist:
                    return HttpResponse("Can't find  " + str(getwalkInID)) 
                    pass

        
            elif is_PatientWalkin == "Account":
                try:

                    if getpatientIDFE is not None or getpatientIDFE is not "":               

                        getpatientID = int(getpatientIDFE)
                        getNewpatientID = UserPatient.objects.get(userID=getpatientID)
                        NewpatientID = getNewpatientID
                        is_WalkIn = True
                        is_Account = True
                except UserPatient.DoesNotExist:
                    pass
        
        print("is_PatientWalkin: ", is_PatientWalkin)

        confirm_val = request.POST.get('confirm')

        if confirm_val == 'True':
            confirm = True
        else:
            confirm = False

        category = request.POST.get('category')
        showMedicalHistory = request.POST.get('showMedicalHistory') # WalkIn
        showAdditionalInfo = request.POST.get('showAdditionalInfo') # WalkIn

        getMHForm = request.POST.get('showMedicalHistoryForm') # Appointment 
        getPatientInfo = request.POST.get('showPatientInfoForm') # Appointment 

        ocularButton = request.POST.get('send_dataOcular')
        dryEyeButton = request.POST.get('send_dataDryEye')
        refractButton = request.POST.get('send_dataRefraction')      
        status = request.POST.get('status')
        Occupation = request.POST.get('occupationSelect')

        print("category: ", category)
        print("showMedicalHistory: ", showMedicalHistory)
        print("showAdditionalInfo: ", showAdditionalInfo)
        print("getMHForm: ", getMHForm)
        print("getPatientInfo: ", getPatientInfo)
        print("status: ", status)

        # medical history
        is_Hypertention = request.POST.get('is_Hypertention')
        if is_Hypertention == 'True':
            is_Hypertention_value = True
        else:
            is_Hypertention_value = False
        recordDate1 = request.POST.get('recordDate1')

        is_HeartProblem = request.POST.get('is_HeartProblem')
        if is_HeartProblem == 'True':
            is_HeartProblem_value = True
        else:
            is_HeartProblem_value = False
        recordDate2 = request.POST.get('recordDate2')

        is_Diabetes = request.POST.get('is_Diabetes')
        if is_Diabetes == 'True':
            is_Diabetes_value = True
        else:
            is_Diabetes_value = False
        recordDate3 = request.POST.get('recordDate3')

        is_Stroke = request.POST.get('is_Stroke')
        if is_Stroke == 'True':
            is_Stroke_value = True
        else:
            is_Stroke_value = False
        recordDate4 = request.POST.get('recordDate4')

        is_Asthma = request.POST.get('is_Asthma')
        if is_Asthma == 'True':
            is_Asthma_value = True
        else:
            is_Asthma_value = False
        recordDate5 = request.POST.get('recordDate5')

        is_DiagnosedNone = request.POST.get('is_DiagnosedNone')
        if is_DiagnosedNone == 'True':
            is_DiagnosedNone_value = True
        else:
            is_DiagnosedNone_value = False

        otherDiagnosedHealth = request.POST.get('otherDiagnosedHealth')
        if otherDiagnosedHealth == 'True':
            otherDiagnosedHealth_value = True
        else:
            otherDiagnosedHealth_value = False
        recordDate7 = request.POST.get('recordDate7')

        #habits
        is_Smoking = request.POST.get('is_Smoking')
        if is_Smoking == 'True':
            is_Smoking_value = True
        else:
            is_Smoking_value = False
        is_SmokingFreq = request.POST.get('is_SmokingFreq')
        if is_Smoking == 'True':
            is_SmokingFreq_value = is_SmokingFreq
        else:
            is_SmokingFreq_value = "N/A"
        is_SmokingYear = request.POST.get('is_SmokingYear')

        is_Alcohol = request.POST.get('is_Alcohol')
        if is_Alcohol == 'True':
            is_Alcohol_value = True
        else:
            is_Alcohol_value = False

        is_AlcoholFreq = request.POST.get('is_AlcoholFreq')
        if is_Alcohol == 'True':
            is_AlcoholFreq_value = is_AlcoholFreq
        else:
            is_AlcoholFreq_value = "N/A"
        recordDate8 = request.POST.get('recordDate8')

        is_HabitsNone = request.POST.get('is_HabitsNone')
        if is_HabitsNone == 'True':
            is_HabitsNone_value = True
        else:
            is_HabitsNone_value = False

        #allergies
        medicinesAller = request.POST.get('medicinesAller')
        foodsAller = request.POST.get('foodsAller')
        otherAller = request.POST.get('otherAller')
        is_AllergiesNone = request.POST.get('is_AllergiesNone')
        if is_AllergiesNone == 'True':
            is_AllergiesNone_value = True
        else:
            is_AllergiesNone_value = False

        # Eye History
        is_Cataract = request.POST.get('is_Cataract')
        if is_Cataract == 'True':
            is_Cataract_value = True
        else:
            is_Cataract_value = False
        is_Glaucama = request.POST.get('is_Glaucama')
        if is_Glaucama == 'True':
            is_Glaucama_value = True
        else:
            is_Glaucama_value = False

        is_RetinalDisease = request.POST.get('is_RetinalDisease')
        if is_RetinalDisease == 'True':
            is_RetinalDisease_value = True
        else:
            is_RetinalDisease_value = False

        is_Astigmatism = request.POST.get('is_Astigmatism')
        if is_Astigmatism == 'True':
            is_Astigmatism_Val = True
        else:
            is_Astigmatism_Val = False

        is_MacularDegeneration = request.POST.get('is_MacularDegeneration')
        if is_MacularDegeneration == 'True':
            is_MacularDegeneration_Val = True
        else:
            is_MacularDegeneration_Val = False

        is_DiabeticRetinopathy = request.POST.get('is_DiabeticRetinopathy')
        if is_DiabeticRetinopathy == 'True':
            is_DiabeticRetinopathy_Val = True
        else:
            is_DiabeticRetinopathy_Val = False

        is_DryEyeSyndrome = request.POST.get('is_DryEyeSyndrome')
        if is_DryEyeSyndrome == 'True':
            is_DryEyeSyndrome_Val = True
        else:
            is_DryEyeSyndrome_Val = False

        is_Strabismus = request.POST.get('is_Strabismus')
        if is_Strabismus == 'True':
            is_Strabismus_Val = True
        else:
            is_Strabismus_Val = False

        is_ColorBlindness = request.POST.get('is_ColorBlindness')
        if is_ColorBlindness == 'True':
            is_ColorBlindness_Val = True
        else:
            is_ColorBlindness_Val = False

        is_Keratoconus = request.POST.get('is_Keratoconus')
        if is_Keratoconus == 'True':
            is_Keratoconus_Val = True
        else:
            is_Keratoconus_Val = False

        is_Uveitis = request.POST.get('is_Uveitis')
        if is_Uveitis == 'True':
            is_Uveitis_Val = True
        else:
            is_Uveitis_Val = False

        othersEyeHis = request.POST.get('othersEyeHis')
        is_EHNone = request.POST.get('is_EHNone')
        if is_EHNone == 'True':
            is_EHNone_value = True
        else:
            is_EHNone_value = False
        # Prevous Eye Surgeries
        eyeSurgeries = request.POST.get('eyeSurgeries')
        # Family History
        is_GlaucamaF = request.POST.get('is_GlaucamaF')
        if is_GlaucamaF == 'True':
            is_GlaucamaF_value = True
        else:
            is_GlaucamaF_value = False

        is_HypertentionF = request.POST.get('is_HypertentionF')
        if is_HypertentionF == 'True':
            is_HypertentionF_value = True
        else:
            is_HypertentionF_value = False

        is_Blindness = request.POST.get('is_Blindness')
        if is_Blindness == 'True':
            is_Blindness_value = True
        else:
            is_Blindness_value = False

        is_DiabetesF = request.POST.get('is_DiabetesF')
        if is_DiabetesF == 'True':
            is_DiabetesF_value = True
        else:
            is_DiabetesF_value = False

        is_CataractF = request.POST.get('is_CataractF')
        if is_CataractF == 'True':
            is_CataractF_value = True
        else:
            is_CataractF_value = False

        is_FHNone = request.POST.get('is_FHNone')
        if is_FHNone == 'True':
            is_FHNone_value = True
        else:
            is_FHNone_value = False            

        # OD 
        od_Lids_Lashes = request.POST.get('od_Lids_Lashes')
        od_Bulbar = request.POST.get('od_Bulbar')
        od_Palpebral = request.POST.get('od_Palpebral')
        od_Cornea = request.POST.get('od_Cornea')
        od_ChamgerAngle = request.POST.get('od_ChamgerAngle')
        od_Iris = request.POST.get('od_Iris')
        od_Lens = request.POST.get('od_Lens')
        od_Tonometry = request.POST.get('od_Tonometry')
        # OS
        os_Lids_Lashes = request.POST.get('os_Lids_Lashes')
        os_Bulbar = request.POST.get('os_Bulbar')
        os_Palpebral = request.POST.get('os_Palpebral')
        os_Cornea = request.POST.get('os_Cornea')
        os_ChamgerAngle = request.POST.get('os_ChamgerAngle')
        os_Iris = request.POST.get('os_Iris')
        os_Lens = request.POST.get('os_Lens')
        os_Tonometry = request.POST.get('os_Tonometry')
        od_DryEye = request.POST.get('od_DryEye')
        os_DryEye = request.POST.get('os_DryEye')
        subRef_OD = request.POST.get('subRef_OD')
        subRef_OS = request.POST.get('subRef_OS')
        # VA
        va_OD = request.POST.get('va_OD')
        va_OS = request.POST.get('va_OS')
        # PD
        pd_OD = request.POST.get('pd_OD')
        pd_OS = request.POST.get('pd_OS')
        # Automated Refraction = autRef_
        autRef_OD = request.POST.get('autRef_OD')
        autRef_OS = request.POST.get('autRef_OS')
        # Near Add    
        od_Refraction = request.POST.get('od_Refraction')
        os_Refraction = request.POST.get('os_Refraction')
        # Remarks
        remarks_Refraction = request.POST.get('remarks_Refraction')
        sessionNotes = request.POST.get('sessionNotes')
        
        sessionConfirm = None

        sessionConfirm = request.POST.get('sessionConfirm')

        if sessionConfirm == "True":
            print("Hell Yeah 1")

            patientID = None
            savewalkInID = None
            
            if category == "WalkIn":
                savewalkInID = walkInID
            elif category == "Account":
                patientID = NewpatientID
            else:
                patientID = getPatient

            saveSes = Session(
                # save patientID
                patientID = patientID,
                # save clinicID
                walkInPatientID = savewalkInID,
                clinicID = getClinic,
                sessionNotes = sessionNotes,
            )
            saveSes.save()
        else:
            sessionConfirm = False

        if getPatientInfo or showAdditionalInfo == "True":
            if category == "WalkIn":
                savePAInfo = PatientPersonalInformation(
                    # save patientID
                    walkInID = walkInID,
                    # save clinicID
                    clinicID = getClinic,

                    civilStatus = status,
                    Occupation = Occupation,
                ) 
                savePAInfo.save()
            elif category == "Account":
                savePAInfo = PatientPersonalInformation(
                    # save patientID
                    patientID = NewpatientID,
                    # save clinicID
                    clinicID = getClinic,
                    civilStatus = status,
                    Occupation = Occupation,
                ) 
                savePAInfo.save()
            else:
                savePAInfo = PatientPersonalInformation(
                    # save patientID
                    patientID = getPatient,
                    # save clinicID
                    clinicID = getClinic,

                    civilStatus = status,
                    Occupation = Occupation,

                ) 
                savePAInfo.save()

        if getMHForm or showMedicalHistory == "True":
            # declare another variable for conditional
            patientID = None
            savewalkInID = None

            if category == "WalkIn":    # if Walk In
                print("Test if it pass here 0")
                savewalkInID = walkInID
            elif category == "Account": # if Walk In
                print("Test if it pass here 1")
                patientID = NewpatientID
                print("Checked the passed ID: ", NewpatientID)
                print("Is it being passed? ", patientID)
            else:
                print("Test if it pass here 3")
                patientID = getPatient  # if Appointment

            if patientID is None and savewalkInID is None:
                checkIfTrue = patientID and savewalkInID is None
                print("Patient ID: ", patientID)
                return HttpResponse("Patient ID is None. Check patientID: {}, Check savewalkInID {}. Check checkIfTrue {}".format(patientID, savewalkInID, checkIfTrue))
                            
            saveHistory = PatientMedicalHistory(
                # save patientID
                patientID = patientID,
                # save clinicID
                walkInID = walkInID,
                clinicID = getClinic,
                aggrement = confirm,

                # Diagnosed Health Problem
                is_Hypertention = is_Hypertention_value,
                recordDate1 = recordDate1,
                is_HeartProblem = is_HeartProblem_value,
                recordDate2 = recordDate2,
                is_Diabetes = is_Diabetes_value,
                recordDate3 = recordDate3,
                is_Stroke = is_Stroke_value,
                recordDate4 = recordDate4,
                is_Asthma = is_Asthma_value,
                recordDate5 = recordDate5,
                is_DiagnosedNone = is_DiagnosedNone_value,
                # recordDate6 = recordDate6,
                otherDiagnosedHealth = otherDiagnosedHealth_value,
                recordDate7 = recordDate7,

                # Habits
                is_Smoking = is_Smoking_value,
                is_SmokingFreq = is_SmokingFreq_value,
                is_SmokingYear = is_SmokingYear,
                is_Alcohol = is_Alcohol_value,
                is_AlcoholFreq = is_AlcoholFreq_value,
                recordDate8 = recordDate8,
                is_HabitsNone = is_HabitsNone_value,
    
                # Allergies
                medicinesAller = medicinesAller,
                foodsAller = foodsAller,
                otherAller = otherAller,
                is_AllergiesNone = is_AllergiesNone_value,

                # Eye History                
                is_Cataract = is_Cataract_value,
                is_Glaucama = is_Glaucama_value,
                is_RetinalDisease = is_RetinalDisease_value,
                othersEyeHis = othersEyeHis,
                is_EHNone = is_EHNone_value,

                is_Astigmatism = is_Astigmatism_Val,
                is_MacularDegeneration = is_MacularDegeneration_Val,
                is_DiabeticRetinopathy = is_DiabeticRetinopathy_Val,
                is_DryEyeSyndrome = is_DryEyeSyndrome_Val,
                is_Strabismus = is_Strabismus_Val,
                is_ColorBlindness = is_ColorBlindness_Val,
                is_Keratoconus = is_Keratoconus_Val,
                is_Uveitis = is_EHNone_value,

                # Prevous Eye Surgeries
                eyeSurgeries = eyeSurgeries,

                # Prevous Eye Surgeries
                is_GlaucamaF = is_GlaucamaF_value,
                is_HypertentionF = is_HypertentionF_value,
                is_Blindness = is_Blindness_value,
                is_DiabetesF = is_DiabetesF_value,
                is_CataractF = is_CataractF_value,
                is_FHNone = is_FHNone_value,

            )
            saveHistory.save()
            print("Medical History are now being stored.")

        if ocularButton == "True":
            print("Hell Yeah 1")

            patientID = None
            savewalkInID = None
            if category == "WalkIn":
                savewalkInID = walkInID
            elif category == "Account":
                patientID = NewpatientID
            else:
                patientID = getPatient

            saveOcular = ocularHealthExamination(
                # save patientID
                patientID = patientID,
                # save clinicID
                walkInID = savewalkInID,
                clinicID = getClinic,

                # od
                od_Lids_Lashes=od_Lids_Lashes,
                od_Bulbar=od_Bulbar,
                od_Palpebral=od_Palpebral,
                od_Cornea=od_Cornea,
                od_ChamgerAngle=od_ChamgerAngle,
                od_Iris=od_Iris,
                od_Lens=od_Lens,
                od_Tonometry=od_Tonometry,
                #os
                os_Lids_Lashes=os_Lids_Lashes,
                os_Bulbar=os_Bulbar,
                os_Palpebral=os_Palpebral,
                os_Cornea=os_Cornea,
                os_ChamgerAngle=os_ChamgerAngle,
                os_Iris=os_Iris,
                os_Lens=os_Lens,
                os_Tonometry=os_Tonometry,
            )
            saveOcular.save()
            print("Ocular Health Examination Data are now being stored.")
        
        if dryEyeButton == "True":

            patientID = None
            savewalkInID = None
            if category == "WalkIn":
                savewalkInID = walkInID
            elif category == "Account":
                patientID = NewpatientID
            else:
                patientID = getPatient

            saveDryEye = dryEyeTest(
                # save patientID
                patientID = patientID,
                # save clinicID
                walkInID = walkInID,
                clinicID = getClinic,

                od_DryEye = od_DryEye,
                os_DryEye = os_DryEye,
            )
            saveDryEye.save()
            print("Dry Eye Test Data are now being stored.")
                
        if refractButton == "True":

            patientID = None
            savewalkInID = None
            if category == "WalkIn":
                savewalkInID = walkInID
            elif category == "Account":
                patientID = NewpatientID
            else:
                patientID = getPatient
            
            services = None
            
            try: 
                findServiceOffer = Services.objects.get(clinicID = getClinic, service_Name = "Refraction")
                services = findServiceOffer.service_Name
            except:
                pass

            saveRefra = Refraction(
                # save patientID
                patientID = patientID,
                # save clinicID
                walkInID = savewalkInID,
                clinicID = getClinic,

                subRef_OD = subRef_OD,
                subRef_OS = subRef_OS,
                va_OD = va_OD,
                va_OS = va_OS,
                pd_OD = pd_OD,
                pd_OS = pd_OS,
                autRef_OD = autRef_OD,
                autRef_OS = autRef_OS,
                od_Refraction = od_Refraction,
                os_Refraction = os_Refraction,
                remarks_Refraction = remarks_Refraction,
            )


            saveRefra.save()
            print("Refraction Data are now being stored.")
 
        current_datetime = datetime.now()
        appoint_Date = current_datetime.date()
        appt_Start_Time = current_datetime.time()
        appt_End_Time = (current_datetime + timedelta(hours=1)).time()

        if is_WalkIn:
            if is_Account == True:
                print("appoint_Date:", appoint_Date)
                print("appt_Start_Time:", appt_Start_Time)
                print("appt_End_Time:", appt_End_Time)
                        
                newBooking = Booking.objects.create(
                    userID = NewpatientID,
                    clinicID = getClinic,

                    appoint_Date = appoint_Date,
                    appt_Start_Time = appt_Start_Time,
                    appt_End_Time = appt_End_Time,

                    is_Accepted = True,
                    is_hidden = True,
                    is_Status = True,
                    is_Success = True,
                )        

                newBooking.save()
                print("WALK IN PATIENT HAS ADDED A TODAY'S APPOINTMENT")
                
            elif is_Account == False: 
                print("appoint_Date:", appoint_Date)
                print("appt_Start_Time:", appt_Start_Time)
                print("appt_End_Time:", appt_End_Time)

                print(walkInID.walkInID)
                        
                newBooking = Booking.objects.create(
                    walkInID = walkInID,
                    clinicID = getClinic,

                    appoint_Date = appoint_Date,
                    appt_Start_Time = appt_Start_Time,
                    appt_End_Time = appt_End_Time,

                    is_Accepted = True,
                    is_hidden = True,
                    is_Status = True,
                    is_Success = True,
                )        
                newBooking.save()
                print("WALK IN PATIENT WHO HAS AN ACCOUNT HAS ADDED A TODAY'S APPOINTMENT")
                
        elif is_WalkIn == False: 
            # update the current book
            getCurrentBook = Booking.objects.get(bookingID= bookingID.bookingID)
            getCurrentBook.is_Status = True
            getCurrentBook.is_Success = True
            getCurrentBook.save()
            print("BOOKING ARE NOW UPDATED!")
        
        print("Check if the is_WalkIn are True: ", is_WalkIn)
        messages.success(request, "Data are now being stored.")    
        return redirect('dashboard')
    else:
        return HttpResponse("Method not allowed", status=405)
# END TODAY'S APPOINTMENT

class ClinicViewSet(viewsets.ReadOnlyModelViewSet):  # this was use for creating API
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer

def get_location(request):
    clinics = Clinic.objects.all()
    return render(request, 'clinics_list.html', {'clinics': clinics})

def locate(request):   
    user_client = None
    clinics = Clinic.objects.all() 
    user = request.user

    if user.is_authenticated:
        try:            
            user_client = UserPatient.objects.get(user=user)
        except UserPatient.DoesNotExist:
            try:
                user_client = Ophthalmologist.objects.get(user=user)

            except Ophthalmologist.DoesNotExist:
                try:
                    user_client = ClinicStaff.objects.get(user=user)
                except ClinicStaff.DoesNotExist:
                    user_client = None
    context = {
            'user_client': user_client,
            'clinics': clinics
        } 
    
    print ("user_client", user_client)
    print ("Here are the clinics == ",clinics) 
    return render(request, 'locate.html', context)

def admin_Dashboard(request):
    user = request.user
    allOptha = Ophthalmologist.objects.all()
    allClinics = Clinic.objects.all()
    allReview = PatientReview.objects.all()
    allBooking = Booking.objects.all()
    allUser = UserPatient.objects.all()
    allWlkIn = WalkInPatient.objects.all()

    clinic_bookings_dict = {}
    clinic_rate_dict = {}

    monthly_counts = Booking.objects.annotate(month=ExtractMonth('appoint_Date')).values('month').annotate(count=Count('bookingID')).order_by('month')
    counts = []
    current_year = datetime.now().year    
    date_today = datetime.now()
    month_today = date_today.month 
    year_today = date_today.year

    # Yearly Patient Count
    months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    all_months = [] # this will be displayed at the bottom of the chart (x axis)
    for i in range(0, 12):
        if i >= (month_today - 1):
            all_months.append(f'{months[i]} {year_today - 1}')

    for i in range(0,12):
        if len(all_months) != 13:
            all_months.append(f'{months[i]} {year_today}')
        else:
            break

    all_formatted_dates = [] # the values of this container will be used for filtering
    start_year = year_today - 1
    start_month = month_today
    for i in range(0, 13):
        complete_date_today = f'{start_year}-{start_month}-01'
        starting_date = (datetime.strptime(complete_date_today, '%Y-%m-%d')).strftime('%Y-%m-%d')
        endDate = (datetime.strptime(str(starting_date), '%Y-%m-%d')).strftime('%Y-%m-%d')   

        if (start_month == 12):
            start_month = 1
            start_year = start_year + 1
        else:
            start_month = start_month + 1
        all_formatted_dates.append(endDate)

    
    y_axis = []
    for date in all_formatted_dates:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        all_count = Booking.objects.filter(appoint_Date__month = date_obj.month, appoint_Date__year = date_obj.year ).count()
        y_axis.append(all_count)

    # Habits    
    y_axis_Alcohol = []
    y_axis_Smoking = []

    for date in all_formatted_dates:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        alcohol_count = PatientMedicalHistory.objects.filter(
            is_Alcohol=True,
            dateRecorded__month=date_obj.month,
            dateRecorded__year=date_obj.year
        ).count()
        
        y_axis_Alcohol.append(alcohol_count)

    for date in all_formatted_dates:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        smoking_count = PatientMedicalHistory.objects.filter(
            is_Smoking=True,
            dateRecorded__month=date_obj.month,
            dateRecorded__year=date_obj.year
        ).count()
        
        y_axis_Smoking.append(smoking_count)

    # Age
    lstOFbdy = []

    try:
        for user in allUser:
            accFirstBday = user.bday
            lstOFbdy.append(accFirstBday.year)    
    except:
        pass

    try:
        for user in allWlkIn:
            accFirstBday = user.bday
            lstOFbdy.append(accFirstBday.year)    
    except:
        pass

    ages = [current_year - year for year in lstOFbdy]

    # Clinic Booking Count
    for clinic in allClinics:
        clinic_id = clinic.clinicID
        clinic_name = clinic.clinicName  
        try:
            bookings_count = Booking.objects.filter(clinicID=clinic_id).count()
            clinic_bookings_dict[clinic_name] = {
                'clinic_name': clinic_name,
                'bookings_count': bookings_count
            }
        except Booking.DoesNotExist:
            print("No Appointment are recorded to all Clinics")        

    # Clinic Reviews
    for clinic in allClinics:
        clinic_id = clinic.clinicID
        clinic_name = clinic.clinicName

        try:
            patientReview_count = PatientReview.objects.filter(clinicID=clinic_id).count()
            avg_rating = PatientReview.objects.filter(clinicID=clinic_id).aggregate(Avg('rate'))['rate__avg']
            avg_rating = avg_rating if avg_rating is not None else 0
            print("avg_rating: ",avg_rating)
            print(f"Clinic ID: {clinic_id}, Clinic Name: {clinic_name}, Rating Count: {patientReview_count}, Average Rating: {avg_rating}")

            clinic_rate_dict[clinic_name] = {
                'clinic_name': clinic_name,
                'rating_count': patientReview_count,
                'average_rating': avg_rating
            }
            clinic_rate_json = json.dumps(clinic_rate_dict)
        except PatientReview.DoesNotExist:
            print(f"No Ratings recorded for Clinic ID: {clinic_id}, Clinic Name: {clinic_name}")

    # Monthly Patient Count
    for entry in monthly_counts:
        months.append(calendar.month_abbr[entry['month']])
        counts.append(entry['count'])

    js_data = f"var monthlyAppointmentsData = {json.dumps({'months': months, 'counts': counts})};"

    # All the rating of the patient in each clinic  
    listOfRate = []
    listOfReviews = []

    uniqueUserIDs = set()
    walkInIDs = set()

    # reviews
    for reviews in allReview:
        try:
            usersIDRev = reviews.patientID

            if usersIDRev is not None and usersIDRev not in uniqueUserIDs:
                accRate = reviews.rate
                accReview = reviews.review

                listOfRate.append(accRate)
                listOfReviews.append(accReview)

                uniqueUserIDs.add(usersIDRev)
        except AttributeError:
            pass

        try:
            wlkIDRev = reviews.walkInID

            if wlkIDRev is not None and wlkIDRev not in walkInIDs:
                wlkRate = reviews.rate
                wlkReview = reviews.review

                listOfRate.append(wlkRate)
                listOfReviews.append(wlkReview)

                walkInIDs.add(wlkIDRev)
        except AttributeError:
            pass
    

    monthly_counts = allBooking.annotate(month=ExtractMonth('appoint_Date')).values('month').annotate(count=Count('bookingID')).order_by('month')

    months = [count['month'] for count in monthly_counts]
    counts = [count['count'] for count in monthly_counts]

    # Barangay
    address_counts = {}

    for patient in allUser:
        home_address = patient.homeAddress

        if home_address not in address_counts:
            address_counts[home_address] = 1
        else:
            address_counts[home_address] += 1

    for patient in allWlkIn:
        home_address = patient.homeAddress

        if home_address not in address_counts:
            address_counts[home_address] = 1
        else:
            address_counts[home_address] += 1

    for address, count in address_counts.items():
        print(f"Address: {address}, Count: {count}")


    clinic_count = Clinic.objects.all().count()
    patient_count = UserPatient.objects.all().count()
    walk_count = WalkInPatient.objects.all().count()

    # Common Eye Problem
    eyeProbList = {}

    try: 
        heartProb = PatientMedicalHistory.objects.filter(is_HeartProblem = True).count()
        eyeProbList['Heart Problem'] = heartProb
    except:
        pass

    try: 
        hypertension = PatientMedicalHistory.objects.filter(is_Hypertention = True).count()
        eyeProbList['Hyepertention'] = hypertension
    except:
        pass
    
    try: 
        diabetes = PatientMedicalHistory.objects.filter(is_Diabetes = True).count()
        eyeProbList['Diabetes'] = diabetes
    except:
        pass

    try: 
        strokee = PatientMedicalHistory.objects.filter(is_Stroke = True).count()
        eyeProbList['Stroke'] = strokee
    except:
        pass
    
    try: 
        asthmaa = PatientMedicalHistory.objects.filter(is_Asthma = True).count()
        eyeProbList['Heart Problem'] = asthmaa
    except:
        pass
        
    try: 
        otherDiagnosedHealth = PatientMedicalHistory.objects.filter(otherDiagnosedHealth = 'True').count()
        eyeProbList['Other'] = otherDiagnosedHealth
    except:
        pass
            
    eyeProbList_json = json.dumps(eyeProbList)

    # Allergies
    allAllergies = {}

    all_Medical = PatientMedicalHistory.objects.all()

    for allergies in all_Medical:
        allergiesName = allergies.medicinesAller

        if allergiesName:
            if allergiesName not in allAllergies:
                allAllergies[allergiesName] = 1
            else:
                allAllergies[allergiesName] += 1
            
    for allergies in all_Medical:
        allergiesName = allergies.foodsAller

        if allergiesName:
            if allergiesName not in allAllergies:
                allAllergies[allergiesName] = 1
            else:
                allAllergies[allergiesName] += 1
            
    for allergies in all_Medical:
        allergiesName = allergies.otherAller

        if allergiesName:
            if allergiesName not in allAllergies:
                allAllergies[allergiesName] = 1
            else:
                allAllergies[allergiesName] += 1            

    result_string = ""
    for allergyName, count in allAllergies.items():
        if allergyName is not None:  
            result_string += "Allergy: {}, Count: {}\n".format(allergyName, count)
        else:
            pass
    
    # Common Occcupation
    occupationList = {}

    allPatientAddInfo = PatientPersonalInformation.objects.all()

    for occupation in allPatientAddInfo:
        occuCount = PatientPersonalInformation.objects.filter(Occupation = occupation.Occupation).count()
        occupationList[occupation.Occupation] = occuCount    

    occupationList_json = json.dumps(occupationList)

    try: 
        heartProb = PatientMedicalHistory.objects.filter(is_HeartProblem = True).count()
        eyeProbList['Heart Problem'] = heartProb
    except:
        pass



    # Common Eye Problem
    eyeCasesHist = {}

    try: 
        cataract = PatientMedicalHistory.objects.filter(is_Cataract = True).count()
        eyeCasesHist['Cataract'] = cataract
    except:
        pass

    try: 
        glaucam = PatientMedicalHistory.objects.filter(is_Glaucama = True).count()
        eyeCasesHist['Glaucama'] = glaucam
    except:
        pass
    
    try: 
        RetinalDisease = PatientMedicalHistory.objects.filter(is_RetinalDisease = True).count()
        eyeCasesHist['Retinal Disease'] = RetinalDisease
    except:
        pass

    try: 
        Astigmatism = PatientMedicalHistory.objects.filter(is_Astigmatism = True).count()
        eyeCasesHist['Astigmatism'] = Astigmatism
    except:
        pass
    
    try: 
        MacularDegeneration = PatientMedicalHistory.objects.filter(is_MacularDegeneration = True).count()
        eyeCasesHist['Macular Degeneration'] = MacularDegeneration
    except:
        pass
        
    try: 
        DiabeticRetinopathy = PatientMedicalHistory.objects.filter(is_DiabeticRetinopathy = 'True').count()
        eyeCasesHist['Diabetic Retinopathy'] = DiabeticRetinopathy
    except:
        pass

    try: 
        DryEyeSyndrome = PatientMedicalHistory.objects.filter(is_DryEyeSyndrome = 'True').count()
        eyeCasesHist['Dry Eye Syndrome'] = DryEyeSyndrome
    except:
        pass

    try: 
        Strabismus = PatientMedicalHistory.objects.filter(is_Strabismus = 'True').count()
        eyeCasesHist['Strabismus'] = Strabismus
    except:
        pass

    try: 
        ColorBlindness = PatientMedicalHistory.objects.filter(is_ColorBlindness = 'True').count()
        eyeCasesHist['Color Blindness'] = ColorBlindness
    except:
        pass

    try: 
        Keratoconus = PatientMedicalHistory.objects.filter(is_Keratoconus = 'True').count()
        eyeCasesHist['Keratoconus'] = Keratoconus
    except:
        pass

    try: 
        Uveitis = PatientMedicalHistory.objects.filter(is_Uveitis = 'True').count()
        eyeCasesHist['Uveitis'] = Uveitis
    except:
        pass

    try: 
        EyeHis = PatientMedicalHistory.objects.filter(othersEyeHis = 'True').count()
        eyeCasesHist['Other'] = EyeHis
    except:
        pass
            
    eyeCasesHist_json = json.dumps(eyeCasesHist)


    context = {
        "clinic_bookings_dict": clinic_bookings_dict,
        "occupationList_json": occupationList_json,
        "clinic_rate_json": clinic_rate_json,
        "clinic_rate_dict": clinic_rate_dict,
        "address_counts": address_counts,
        "appointments": allBooking,
        "js_data": js_data,
        "ages": ages,
        "months": months,
        "counts": counts,
        "listOfRate": listOfRate,
        "listOfReviews": listOfReviews,
        "y_axis": y_axis,
        "all_months": all_months,
        "clinic_count": clinic_count,
        "patient_count": patient_count,
        "walk_count": walk_count,
        "eyeProbList": eyeProbList_json, # Use the serialized version here
        "y_axis_Alcohol": y_axis_Alcohol,
        "y_axis_Smoking": y_axis_Smoking,
        "allAllergies": allAllergies,
        "eyeCasesHist_json": eyeCasesHist_json,
        "all_formatted_dates ": all_formatted_dates,
    }

    return render(request, 'admin-Dashboard.html', context)

def admin_Users(request):
    return render (request, 'admin-Users.html')

def admin_Opthal(request):
    return render (request, 'admin-Opthal.html')

def admin_Cregistration(request):    
    context = {}
    opthas = Ophthalmologist.objects.filter(is_status = False)  
    if request.method == "POST": 
        users = User.objects.all()
        usernames = [user.username for user in users]

        context = {
            'usernames': usernames,
            'opthas': opthas,
            }
                
    else:
        users = User.objects.all()
        usernames = [user.username for user in users]
        context = {
            'usernames': usernames,
            'opthas': opthas,  # Add the opthas queryset to the context
        }
        return render(request, 'admin-Clinics-Registration.html', context)

@csrf_exempt
def location(request):
    if request.method == 'POST':
        try:
            data = request.POST  # Use request.POST to get form data
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))
            name=data.get('clinicName')
            address=data.get('clinicAdd')
            email=data.get('clinicEmail')
            number=data.get('clinicConNum')
            user_name = data.get('users_name', '')
            print('Received Data:')
            print('Latitude:', latitude)
            print('Longitude:', longitude)
            print('Name:', name)
            print('Address:', address)
            print('Email:', email)
            print('Number:', number)
            print('User Name:', user_name)
            selected_optha = get_object_or_404(Ophthalmologist, user__username=user_name)
            selected_optha.is_status = request.POST.get('userStats', False) == 'True'
            if Clinic.objects.filter(clinicName = name).exists(): 
                messages.info(request, 'Clinic Name Existed' )
                return redirect ('admin_Cregistration')
            else: 

                print('Saving all the Data...')
                clinicInfo = Clinic(
                    opthID = selected_optha,
                    clinicName = name,
                    clinicAddress = address,
                    clinicEMailAdd = email,
                    clinicNumber = number,
                    latitude=latitude,
                    longitude=longitude,
                )
                clinicInfo.save()
                selected_optha.save()            
                messages.info(request, 'Register Successfully')
                return HttpResponse("Clinic Saved!!")
            
        except ValueError as e:
            print('Error converting latitude/longitude:', str(e))
            return JsonResponse({'error': 'Invalid latitude or longitude'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def admin_Clinics_Table(request):
    Clinics = Clinic.objects.all().order_by('clinicID')
    user = request.user
    allOptha = Ophthalmologist.objects.all()
    allClinics = Clinic.objects.all()
    allReview = PatientReview.objects.all()
    allBooking = Booking.objects.all()
    allUser = UserPatient.objects.all()
    allWlkIn = WalkInPatient.objects.all()

    lstOFbdy = []
    clinic_bookings_dict = {}
    clinic_rate_dict = {}

    monthly_counts = Booking.objects.annotate(month=ExtractMonth('appoint_Date')).values('month').annotate(count=Count('bookingID')).order_by('month')
    months = []
    counts = []

    uniqueUserIDs = set()
    current_year = datetime.now().year

    try:
        for user in allUser:
            accFirstBday = user.bday
            lstOFbdy.append(accFirstBday.year)    
    except:
        pass

    try:
        for user in allWlkIn:
            accFirstBday = user.bday
            lstOFbdy.append(accFirstBday.year)    
    except:
        pass

    # Clinic Booking Count
    for clinic in allClinics:
        clinic_id = clinic.clinicID
        clinic_name = clinic.clinicName  
        try:
            bookings_count = Booking.objects.filter(clinicID=clinic_id).count()
            clinic_bookings_dict[clinic_name] = {
                'clinic_name': clinic_name,
                'bookings_count': bookings_count
            }
        except Booking.DoesNotExist:
            print("No Appointment are recorded to all Clinics")        

    # Clinic Reviews
    for clinic in allClinics:
        clinic_id = clinic.clinicID
        clinic_name = clinic.clinicName

        try:
            # Count the number of ratings for the current clinic
            patientReview_count = PatientReview.objects.filter(clinicID=clinic_id).count()

            # Calculate the average rating for the current clinic
            avg_rating = PatientReview.objects.filter(clinicID=clinic_id).aggregate(Avg('rate'))['rate__avg']
            avg_rating = avg_rating if avg_rating is not None else 0
            print("avg_rating: ",avg_rating)
            print(f"Clinic ID: {clinic_id}, Clinic Name: {clinic_name}, Rating Count: {patientReview_count}, Average Rating: {avg_rating}")

            # Store the information in a dictionary
            clinic_rate_dict[clinic_name] = {
                'clinic_name': clinic_name,
                'rating_count': patientReview_count,
                'average_rating': avg_rating
            }

            clinic_rate_json = json.dumps(clinic_rate_dict)
        except PatientReview.DoesNotExist:
            print(f"No Ratings recorded for Clinic ID: {clinic_id}, Clinic Name: {clinic_name}")

       
            
    # Monthly Patient Count
    for entry in monthly_counts:
        months.append(calendar.month_abbr[entry['month']])
        counts.append(entry['count'])

    js_data = f"var monthlyAppointmentsData = {json.dumps({'months': months, 'counts': counts})};"

    # All the rating of the patient in each clinic
    listOfRate = []
    listOfReviews = []

    uniqueUserIDs = set()
    walkInIDs = set()

    for reviews in allReview:
        try:
            usersIDRev = reviews.patientID

            if usersIDRev is not None and usersIDRev not in uniqueUserIDs:
                accRate = reviews.rate
                accReview = reviews.review

                listOfRate.append(accRate)
                listOfReviews.append(accReview)

                uniqueUserIDs.add(usersIDRev)
        except AttributeError:
            pass

        try:
            wlkIDRev = reviews.walkInID

            if wlkIDRev is not None and wlkIDRev not in walkInIDs:
                wlkRate = reviews.rate
                wlkReview = reviews.review

                listOfRate.append(wlkRate)
                listOfReviews.append(wlkReview)

                walkInIDs.add(wlkIDRev)
        except AttributeError:
            pass
        
    ages = [current_year - year for year in lstOFbdy]
    monthly_counts = allBooking.annotate(month=ExtractMonth('appoint_Date')).values('month').annotate(count=Count('bookingID')).order_by('month')

    months = [count['month'] for count in monthly_counts]
    counts = [count['count'] for count in monthly_counts]

    # All Services
    services = {}

    # Get all services
    all_services = Services.objects.all()

    # Iterate over each service
    for service in all_services:
        # Count occurrences of the service in PatientMedicalHistory
        service_count = Services.objects.filter(service_Name=service.service_Name).count()
        # Store the count in the services dictionary
        services[service.service_Name] = service_count        
    services_requestedDict = {}

    # Get all bookings
    all_bookings = Booking.objects.all()
    for booking in all_bookings:
        if booking.serviceID is not None:
            service_name = booking.serviceID.service_Name
            service_req_count = Booking.objects.filter(serviceID__service_Name=service_name).count()
            services_requestedDict[service_name] = service_req_count

    services_requested = json.dumps(services_requestedDict)

    context = {
        "clinic_bookings_dict": clinic_bookings_dict,
        "clinic_rate_json": clinic_rate_json,
        "clinic_rate_dict": clinic_rate_dict,
        "js_data": js_data,
        "appointments": allBooking,
        "ages": ages,
        "months": months,
        "counts": counts,
        "Clinics": Clinics,
        "listOfRate": listOfRate,
        "listOfReviews": listOfReviews,
        "services": services,
        "services_requested": services_requested,
    }

    return  render(request, 'admin-Clinics-Table.html', context)

def admin_Clinics_Information(request, clinicID):

    getClinicID = Clinic.objects.get(clinicID = clinicID)
    allPatientReview = PatientReview.objects.filter(clinicID = getClinicID)

    getAllBooking = Booking.objects.filter(clinicID = getClinicID)

    allUser = None
    allWlkIn = None

    try:
        for getUserID in getAllBooking: # Account
            get_UserID = getUserID.userID.homeAddress
            allUser = get_UserID
    except:
        pass

    try:
        for geWalkInID in getAllBooking: # Account
            get_WalkInID = geWalkInID.walkInID.homeAddress
            allWlkIn = get_WalkInID
    except:
        pass

    # Get all the rate and review
    listOfRate = []
    listOfReviews = []

    uniqueUserIDs = set()
    walkInIDs = set()

    for reviews in allPatientReview:
        try:
            usersIDRev = reviews.patientID

            if usersIDRev is not None and usersIDRev not in uniqueUserIDs:
                accRate = reviews.rate
                accReview = reviews.review

                listOfRate.append(accRate)
                listOfReviews.append(accReview)

                uniqueUserIDs.add(usersIDRev)
        except AttributeError:
            pass

        try:
            wlkIDRev = reviews.walkInID

            if wlkIDRev is not None and wlkIDRev not in walkInIDs:
                wlkRate = reviews.rate
                wlkReview = reviews.review

                listOfRate.append(wlkRate)
                listOfReviews.append(wlkReview)

                walkInIDs.add(wlkIDRev)
        except AttributeError:
            pass
    # End For Loop 
    
    # Monthly Clinic Cont 
    monthly_counts = getAllBooking.annotate(month=ExtractMonth('appoint_Date')).values('month').annotate(count=Count('bookingID')).order_by('month')

    months = [count['month'] for count in monthly_counts]
    counts = [count['count'] for count in monthly_counts]

    date_today = datetime.now()
    month_today = date_today.month # 2 - 1 = 1
    year_today = date_today.year

    # Yearly Patient Count
    months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    all_months = [] # this will be displayed at the bottom of the chart (x axis)
    for i in range(0, 12):
        if i >= (month_today - 1):
            all_months.append(f'{months[i]} {year_today - 1}')

    for i in range(0,12):
        if len(all_months) != 13:
            all_months.append(f'{months[i]} {year_today}')
        else:
            break

    all_formatted_dates = [] 
    start_year = year_today - 1
    start_month = month_today
    for i in range(0, 13):
        complete_date_today = f'{start_year}-{start_month}-01'
        starting_date = (datetime.strptime(complete_date_today, '%Y-%m-%d')).strftime('%Y-%m-%d')
        endDate = (datetime.strptime(str(starting_date), '%Y-%m-%d')).strftime('%Y-%m-%d')     

        if (start_month == 12):
            start_month = 1
            start_year = start_year + 1
        else:
            start_month = start_month + 1
        all_formatted_dates.append(endDate)
    
    y_axis = []
    for date in all_formatted_dates:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        all_count = Booking.objects.filter(appoint_Date__month = date_obj.month, appoint_Date__year = date_obj.year, clinicID = clinicID ).count()
        y_axis.append(all_count)

    services_requestedDict = {}

    all_bookings = Booking.objects.all()

    for booking in all_bookings:
        if booking.serviceID is not None:
            service_name = booking.serviceID.service_Name
            service_req_count = Booking.objects.filter(serviceID__service_Name=service_name, clinicID = clinicID).count()
            services_requestedDict[service_name] = service_req_count

    services_requested = json.dumps(services_requestedDict)
    address_counts = defaultdict(int)

    # Iterate over all bookings for the clinic
    for booking in getAllBooking:
        try:
            if booking.userID:
                address_counts[booking.userID.homeAddress] += 1
        except AttributeError:
            pass
        
        try:
            if booking.walkInID:
                address_counts[booking.walkInID.homeAddress] += 1
        except AttributeError:
            pass

    # Print or process the address counts
    for address, count in address_counts.items():
        print(f"Address: {address}, Count: {count}")

    address_counts_json = json.dumps(dict(address_counts))

    context = {
        "getClinicID": getClinicID,
        "all_months": all_months,
        "y_axis": y_axis,
        "listOfRate": listOfRate,
        "listOfReviews": listOfReviews,
        "services_requested": services_requested,
        "address_counts_json": address_counts_json,
    }
    return  render(request, 'admin-Clinics-Information.html', context)

def admin_Tables(request):
    user_clients = UserPatient.objects.filter(user__is_superuser=False).all().order_by('user__id')

    print(user_clients)

    context = {
        'info': user_clients,
    }
    return render(request, 'admin-Users-UserTables.html', context)

def delete_users(request): # Bawal ang DELETE!!!!
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        user_ids = data.get('user_ids').split(',')
        print(user_ids)
        # Perform the deletion of user accounts using the user_ids list
        # Example:
        for userid in user_ids:
            User.objects.filter(id=userid).delete()
        return JsonResponse({'message': 'Users deleted successfully.'})
   
def admin_RegisterUser(request):  
    if request.method=="POST": 
        # this will be imported in DB - UserPatient
        fName = request.POST.get('FName','') 
        mName = request.POST.get('MName','')
        lName = request.POST.get('LName','')
        bDay = request.POST.get('bday','')
        sex = request.POST.get('sex','')
        homeAdd = request.POST.get('HomeAdd','')
        contactNum = request.POST.get('ContactNum','')

        # Emergency Person
        efName = request.POST.get('EFName','')
        emName = request.POST.get('EMName','')
        elName = request.POST.get('ELName','')
        rShip = request.POST.get('ERelatioship','')
        eContactNum = request.POST.get('contactEmNum','')      

        # this will be imported in User
        email = request.POST.get('Email','')
        username = request.POST.get('Username','')
        password = request.POST.get('Pass','')
        password2 = request.POST.get('Pass2','')   

        if password == password2: 
            if User.objects.filter(email=email).exists(): 
                messages.info(request, 'Email already used')
                return redirect ('admin_RegisterUser')
            elif User.objects.filter(username=username).exists(): 
                messages.info(request, 'Username already used') 
                return redirect ('admin_RegisterUser')
            else:
                user = User.objects.create_user (username = username, email = email, password = password)
                userInfo = UserPatient(user=user,firstName=fName, middleName=mName, lastName=lName, bday=bDay, sex=sex, homeAddress=homeAdd, contactNum=contactNum, emergencyName=efName, emergencyMiddleName=emName, emergencyLastName=elName, relationship=rShip, emergencyContactNum=eContactNum)
                user.save()
                userInfo.save()
                messages.info(request, 'Registered Successufully') 
                return redirect('admin_RegisterUser')
        else:
            messages.info(request, 'Password Not Match!')
            return redirect('admin_RegisterUser')
    else:
        return render(request, 'admin-Users-RegisterPatient.html')

def admin_RegisterOptha(request):   
    if request.method=="POST": 
        fName = request.POST.get('FName','') 
        mName = request.POST.get('MName','')
        lName = request.POST.get('LName','')
        bDay = request.POST.get('bday','')
        sex = request.POST.get('sex','')
        homeAdd = request.POST.get('HomeAdd','')
        contactNum = request.POST.get('ContactNum','')   

        email = request.POST.get('Email','')
        username = request.POST.get('Username','')
        password = request.POST.get('Pass','')
        password2 = request.POST.get('Pass2','')   

        if password == password2: 
            if User.objects.filter(email=email).exists(): 
                messages.info(request, 'Email already used')
                return redirect ('admin_RegisterOptha')
            elif User.objects.filter(username=username).exists(): 
                messages.info(request, 'Username already used') 
                return redirect ('admin_RegisterOptha')
            else:
                user = User (username = username, email = email)
                user.set_password(password)
                user.save()
                
                auth_token = str(uuid.uuid4())
                userInfo = Ophthalmologist.objects.create(user=user,firstName=fName, middleName=mName, lastName=lName, bday=bDay, sex=sex, homeAddress=homeAdd, 
                                       contactNum=contactNum, auth_token = auth_token)
                userInfo.save()
                send_mail_after_registration(email , auth_token)

        else:
            messages.info(request, 'Password Not Match!')
            return redirect('admin_RegisterOptha')
        messages.info(request, 'Opthalmotrist succesfully registered. Please confirm your email first.')
        return redirect('admin_RegisterOptha')        
    else:
        return render(request, 'admin-Opthal-RegisterOptha.html')

def admin_OpthalInfo(request):      
    opthal = Ophthalmologist.objects.filter(user__is_superuser=False).all().order_by('user__id')
    clinics = Clinic.objects.all()
    op = Ophthalmologist.objects.all()
        
    clinic_names_by_opthal_id = {}

    # Populate the dictionary with assigned clinic names
    for clinic in clinics:
        if clinic.opthID not in clinic_names_by_opthal_id:
            clinic_names_by_opthal_id[clinic.opthID] = clinic.clinicName
            
    for a in clinic_names_by_opthal_id:
        print(a,"TEST ONE")

    opthal_info_with_clinic = []
    for ophthalmologist in opthal:
        ophthalmologist_data = {
            'ophthalmologist': ophthalmologist,
            'clinic_name': clinic_names_by_opthal_id.get(ophthalmologist.opthID, ""),  
        }
        opthal_info_with_clinic.append(ophthalmologist_data)
    print(opthal_info_with_clinic, "----------<opthal_info_with_clinic>------------") 
    context = {
        'opthalInfo': opthal,
        'clinics': clinics,
        'clinic_names_by_opthal_id': clinic_names_by_opthal_id,
    }    
    return render (request, 'admin-Opthal-OpthalTable.html', context)

def admin_UpdateUser(request):

    user_id = request.GET.get('userID')
    
    if user_id:
        try:
            user_client = UserPatient.objects.get(user=user_id)  #
            userU = User.objects.get(id=user_id)
        except UserPatient.DoesNotExist:            
            try:
                user_client = Ophthalmologist.objects.get(user=user_id)
                print(user_client, "Ok na?")
                return redirect(f'/admin_UpdateOptha/{user_id}/')                
            except Ophthalmologist.DoesNotExist:
                print("User not found in UserPatient or Ophthalmologist tables.")
                return HttpResponse("User not found. 3", status=404)
            return HttpResponse("User not found. 1", status=404)
    else:
        return HttpResponse("User ID not provided. 2", status=400)
    
    print(userU.email) 
    if request.method=="POST": 
        # updating user information through user input
        user_client.firstName = request.POST.get('FName','')
        user_client.middleName = request.POST.get('MName','')
        user_client.lastName = request.POST.get('LName','')
        user_client.bday = request.POST.get('biday','')
        user_client.sex = request.POST.get('sex','')
        user_client.homeAddress = request.POST.get('HomeAdd','')
        user_client.contactNum = request.POST.get('ContactNum','')
        user_client.emergencyName = request.POST.get('EFName','')
        user_client.emergencyMiddleName = request.POST.get('EMName','')
        user_client.emergencyLastName = request.POST.get('ELName','')
        user_client.relationship = request.POST.get('ERelatioship','')
        user_client.emergencyContactNum = request.POST.get('contactEmNum','')   

        # this will be imported in User
        new_email = request.POST.get('Email','')
        userU.email = new_email
        userU.save()
        user_client.save()

        return redirect('admin_Tables')
    else:
        return render(request, 'admin-Users-UpdateUser.html', {'user_client':user_client})
    
    return render(request, 'admin-UpdateUser.html', {'user_client': user_client, 'user_obj': user})

def admin_UpdateOptha(request, userID):
    if userID:
        try:
            user_client = Ophthalmologist.objects.get(user=userID)
            user = User.objects.get(id=userID)
            print(user_client)
        except Ophthalmologist.DoesNotExist:
            
            return HttpResponse("User not found. 3", status=404)                
    else:
        return HttpResponse("User ID not provided. 2", status=400)    
    if request.method=="POST": 
        # updating user information through user input
        user_client.firstName = request.POST.get('FName','')
        user_client.middleName = request.POST.get('MName','')
        user_client.lastName = request.POST.get('LName','')
        user_client.bday = request.POST.get('biday','')
        user_client.sex = request.POST.get('sex','')
        user_client.homeAddress = request.POST.get('HomeAdd','')
        user_client.contactNum = request.POST.get('ContactNum','') 
        # this will be imported in User
        new_email = request.POST.get('Email','')
        user.email = new_email
        user.save()
        user_client.save()
        messages.info(request, 'User Information Updated!')

        return redirect('admin_OpthalInfo')
    else:
        return render(request, 'admin-Opthal-UpdateOptha.html', {'user_client':user_client})

def check_authentication(request):
    if request.user.is_authenticated:
        return JsonResponse({'authenticated': True})
    else:
        return JsonResponse({'authenticated': False})

def clinics(request):
    clinic = Clinic.objects.all()
    user = request.user

    if request.user.is_authenticated:
        user_client = UserPatient.objects.get(user=user)
        print("On ========= User Log in: ",user_client.firstName)
        
        context = {
            'clinic':clinic, 
            'user_client':user_client,
        } 

        return render(request, 'clinics.html', context)
    else:
        context = {
            'clinic':clinic,
        } 
        return render(request, 'clinics.html', context)

def clinic_services(request):  
    user = request.user 
    clinic_ID = None
    if user.is_authenticated:

        try:
            opthal_ID = Ophthalmologist.objects.get(user=user.id)
            clinic_ID = Clinic.objects.get(opthID=opthal_ID.opthID)
            services = Services.objects.filter(clinicID=clinic_ID)
            print("Potaena bakit dito ka pumupunta?? ",services)
            
        except (Ophthalmologist.DoesNotExist, Clinic.DoesNotExist):
            services = []
            
        context = {
            'services': services,
        }
        return render(request, 'clinic-services.html',context)

def clinic_regServices(request): 
    if request.method=="POST": 
        user = request.user
        if user.is_authenticated:
            opthal_ID = Ophthalmologist.objects.get(user=user.id)
            clinic_ID = Clinic.objects.get(opthID=opthal_ID.opthID)
            serviceName = request.POST.get('serviceName','') 
            serviceInfo = request.POST.get('serviceInfo','')                    
            serv = Services(clinicID=clinic_ID, service_Name=serviceName, service_Information=serviceInfo)
            serv.save()            
            messages.info(request, 'Registered Successfully')       
            return redirect('clinic_services')        
    else:
        return render(request, 'clinic-regServices.html')

def clinic_editServices(request): 
    
    user = request.user
    serv_ID = request.GET.get('serviceID', None)    
    servID = None
    
    if serv_ID is not None:
        try:
            servID = Services.objects.get(serviceID=serv_ID) 
            print(servID)
            print("Here 1")
            
        except UserPatient.DoesNotExist:
            return HttpResponse("User not found. 1", status=404)
            
    if request.method=="POST":   

        if user.is_authenticated:            
            servID.service_Name = request.POST.get('serviceName','') 
            servID.service_Information = request.POST.get('serviceInfo','')
            servID.save()            
            messages.info(request, 'Update Successfully')              
            return redirect('clinic_editServices')
        
    else:
        return render(request, 'clinic-editServices.html', {'servID': servID})

def clinic_patintTables(request):    
    user = request.user
    
    try:    
        ophthalmologist = Ophthalmologist.objects.get(user=user)
        clinic = Clinic.objects.get(opthID=ophthalmologist) 
        clinic_name = clinic.clinicName
        appointments = Booking.objects.filter(clinicID=clinic, is_Accepted=True)
               
        print("CLINIC NAME: ", clinic_name)
        print("OPTHAL NAME: ", user)
        print("OPTHAL NAME: ", user)
        
        context = { 
            'clinic_name': clinic_name,
            'appointments': appointments,
        }

        return render(request, 'clinic-patientTables.html', context)

    except Ophthalmologist.DoesNotExist:
        return render(request, 'clinic-patientTables.html', {'clinic_name': 'No Clinic Assigned'})
    
@require_http_methods(["DELETE"]) 
def delete_service(request, serviceID):
    try:
        service = Services.objects.get(serviceID=serviceID)
        service.delete()
        return JsonResponse({'message': 'Service deleted successfully.'})
    except Services.DoesNotExist:
        return JsonResponse({'error': 'Service not found.'}, status=404)

# CLINIC MESSAGING
def clinic_messages(request): 
    user = request.user
    usersID = Ophthalmologist.objects.get(user=user)
    clinicXOpth = Clinic.objects.get(opthID=usersID)
    to_Str = str(clinicXOpth.clinicID)

    room = str(clinicXOpth.clinicID)

    print("Clinic Room: ", to_Str) 
    print("Clinic: ", clinicXOpth) 
    messages = Message.objects.filter(clinicID=to_Str) 

    user_latest_messages_dict = {}

    if Message.objects.exists():
        for message in messages:
            latest_message = Message.objects.filter(userID=message.userID, clinicID = room).latest('date')
            user_latest_messages_dict[message.userID] = latest_message

    print("Message: ", messages)
    print("Chat Room: ", clinicXOpth)

    context = {
        'user_latest_messages_dict': user_latest_messages_dict,
        'usersID': usersID,
        'clinicXOpth': clinicXOpth,
    }

    return render(request, 'clinic-messages.html', context)

def cRoom(request, cRoom):    
    user = request.user
    if room == 'favicon.ico':
        return HttpResponse(status=204)

    paID = request.session.get('selected_patient_id', None)
    patientName = UserPatient.objects.get(userID=paID)

    if paID is not None:
        print("Selected Patient ID: ", paID)
    else:
        print("paID is  None")
    

    user_client = Ophthalmologist.objects.get(user=user)
    room_to_Int = int(cRoom) 

    if isinstance(cRoom, str): 
        print("The room variable is a string.")
    if isinstance(room_to_Int, int):
        print("room_to_Int is an integer.")

    clinic = Clinic.objects.get(clinicID=room_to_Int) 

    username = user_client.firstName

    room_details = ChatRoom.objects.get(chatRoomName=cRoom) 

    context = {
        'patientName': patientName,
        'paID': paID,
        'cRoom': cRoom,
        'username':username,
        'clinic':clinic,
        'room_details':room_details,
        'user_client':user_client,
    } 

    print("PASSSS ")
    print("user_client == ", username)
    print("user == ", user.id)

    return render (request, 'test-message-Clinic.html', context)

def viewRoom(request): 
    paID = request.POST.get('selectedPatientID') 
    patID = UserPatient.objects.get(userID=paID)

    print("Selected Patient ID: ", patID.firstName)

    if request.user.is_authenticated:
        user = request.user
        usersID = Ophthalmologist.objects.get(user=user)
        roomName = Clinic.objects.get(opthID=usersID)
        roomID = roomName.clinicID
        print("Clinic Room ID: ", roomID)
        print("Clinic Room Name: ", roomName)
        cRoom = str(roomID) 
        opth_str = str(usersID)
        selected_Patient = str(paID)
        print("Clinic ID: ", roomName)
        print("Selected Patient ID === ", selected_Patient)
        print("Clinic Name: ", roomName.clinicName)
        print("Clinic Room: ", cRoom)
        request.session['selected_patient_id'] = paID
        if ChatRoom.objects.filter(chatRoomName=cRoom).exists():
            print("Inside If ============ ")
            return redirect('clinic/'+cRoom+'/?user='+opth_str)    
        else:
            return HttpResponse("Cannot find such a Room")
    
    else:
        return redirect(reverse('login'))

def send_Clinic(request):
    user = request.user

    message = request.POST['message']
    patientID = request.POST['patient_ID']
    pID = UserPatient.objects.get(userID=patientID)
    to_Reciever = pID.firstName

    print("UserPatient ID: ", pID)

    try:
        optha = Ophthalmologist.objects.get(user=user)
        clinic_ID = Clinic.objects.get(opthID=optha)
        to_Sender = clinic_ID.clinicName

        clinicID_str = str(clinic_ID.clinicID)
        print("User Log in: ",optha.firstName)
        print("Ophthalmologist ")
        new_message = Message.objects.create(messageContent=message, userID=pID, clinicID=clinicID_str, opthID = optha, sender = to_Sender, reciever = to_Reciever)
        new_message.save()
        return HttpResponse('Message sent successfully')

    except Ophthalmologist.DoesNotExist:
        print("Ophthalmologist.DoesNotExist")
        pass 
    
    print("Outside::::::::::::::::::::")

def getMessages_Clinic(request, cRoom):
    paID = request.session.get('selected_patient_id', None)
    patientName = UserPatient.objects.get(userID=paID)
    
    user = request.user
    opthal_ID = Ophthalmologist.objects.get(user=user)
    opth = opthal_ID.opthID

    if isinstance(room, str):
        print("The room variable is a string.")
    elif isinstance(room, int):
        print("The room variable is an integer.")

    if not user.is_authenticated:
        print("NOT AUTHENTICATED -------------------")

    room_details = get_object_or_404(ChatRoom, chatRoomName=cRoom)
    print("Room Room: ", room_details)

    messages = Message.objects.filter(clinicID=room_details, userID=patientName, opthID=opth )
    
    print("Messages: ",      )
    messages_data = []

    for message in messages:
        user_id = message.opthID_id
        sender = message.sender    
        theSender = message.sender
        clin = int(message.clinicID)
        clinic = Clinic.objects.get(clinicID=clin)
        patientSender = message.userID.firstName

        user = Ophthalmologist.objects.get(opthID=user_id)

        if sender == clinic.clinicName: 
            label = 'Me'  
        else:
            label = patientSender 
        
        user_data = {
            'user_id': user_id,
            'user_name': user.firstName,
            'user_last_name': user.lastName,
        }

        message_data = {
            'theSender': message.sender,
            'sender': message.userID.firstName,
            'clinicID': message.clinicID,
            'date': message.date,
            'messageContent': message.messageContent,
            'user': user_data,
            'label': label,
        }

        messages_data.append(message_data)

    return JsonResponse({"messages": messages_data})

def patient_Inbox(request):
    user = request.user
    usersID = UserPatient.objects.get(user=user)    
    messages = Message.objects.filter(userID=usersID) 
    
     # Get the latest message date per clinicID
    latest_messages_dates = Message.objects.filter(userID=usersID).values('clinicID').annotate(latest_date=Max('date'))

    # Fetch the latest message per clinicID
    latest_messages = [Message.objects.filter(clinicID=lm['clinicID'], date=lm['latest_date']).first() for lm in latest_messages_dates]

    # Fetch clinic data
    clinics_data = {lm.clinicID: Clinic.objects.get(clinicID=lm.clinicID) for lm in latest_messages}

    # Prepare data for the template
    zipped_data = [(message, clinics_data[message.clinicID]) for message in latest_messages]


    context = {
        'usersID': usersID,
        'zipped_data': zipped_data,
    }
    
    return render(request, 'patient-Inbox.html', context)

def mark_messages_as_read_Clini(request, cRoom):
    
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        user = request.user        
        print("If this is execute then the message are being read")
        messages_to_update = Message.objects.filter(clinicID=cRoom, reciever=user, is_read=False)
        messages_to_update.update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def messageNotificationClinic(request):
    user = request.user

    if user.is_authenticated:
        patient_id = Ophthalmologist.objects.get(user=user)
        # Check for new messages since last check
        last_check_time = timezone.now() - timezone.timedelta(minutes=5)  
        new_messages = Message.objects.filter(opthID=patient_id, is_read=False, date__gt=last_check_time).order_by('-date')        
        latest_messages_by_sender = {}
        for message in new_messages:
            sender = message.sender
            if sender not in latest_messages_by_sender:
                message_data = {
                    'sender': sender,
                    'message_content': message.messageContent,
                    'messageID': message.textID,
                    'clinicID': message.clinicID,
                    'date': message.date.strftime('%Y-%m-%d %H:%M:%S')
                }
                latest_messages_by_sender[sender] = message_data
        latest_messages_data = list(latest_messages_by_sender.values())

        for unread in latest_messages_data:
            print(unread)
        
        return JsonResponse({'messages': latest_messages_data})
    else:
        return JsonResponse({'error': 'User is not authenticated'}, status=401)

# PATIENT MESSAGING
def room(request, room):
    if room == 'favicon.ico':
        return HttpResponse(status=204)        
    user = request.user
    user_client = UserPatient.objects.get(user=user)
    room_to_Int = int(room)
    print("Check Room Type", type(room_to_Int))
    if isinstance(room, str): 
        print("The room variable is a string.")
    if isinstance(room_to_Int, int):
        print("room_to_Int is an integer.")

    clinic = Clinic.objects.get(clinicID=room_to_Int)  
    username = user_client.firstName

    room_details = ChatRoom.objects.get(chatRoomName=room)
    print("room_details: ",room_details)

    context = {
        'room': room,
        'username':username,
        'clinic':clinic,
        'room_details':room_details,
        'user_client':user_client,
    } 

    print("PASSSS ")
    print("user_client == ", username)
    print("user == ", user.id)

    return render (request, 'patient-messaging.html', context)

def createmessage(request): 
    if request.user.is_authenticated:

        user = request.user
        usersID = UserPatient.objects.get(user=user)
        userName = usersID.firstName
        uID = str(usersID.userID)
        print("POST Data:", request.POST)
        print("User Log in: ",usersID.firstName)
        print("User ID: ", uID)
        print("Creating Message Room...")
        clinic_id = request.POST.get('selectedClinicID')
        clinic = Clinic.objects.get(clinicID=clinic_id) 
        printOpthal = clinic.opthID.opthID
        print("Clinic: ", printOpthal) 
        opthaID = Ophthalmologist.objects.get(opthID=printOpthal)

        request.session['selected_clinic_id'] = clinic_id

        clinicID = str(clinic_id)
        room = clinicID 

        print("Clinic ID: ", clinic_id)
        print("Clinic Name: ", clinic.clinicName)
        print("Clinic Room: ", room)

        context = {
            'usersID':usersID,
            'userName':userName,
        } 

        if ChatRoom.objects.filter(chatRoomName=room).exists():
            print("Inside If ============ ")
            return redirect('/'+room+'/?user='+userName, context)    
        else:
            print("Inside e;se ============ ")
            new_room = ChatRoom.objects.create(chatRoomName=room)
            new_room.save()
            return redirect('/'+room+'/?user='+userName, context)
    
    else:
        return redirect(reverse('login'))
    
def send(request):
    user = request.user
    message = request.POST['message']
    try:
        user_ID = UserPatient.objects.get(user=user)
        to_Sender = user_ID.firstName 
        clinic_ID = request.POST['room_id']
        
        clinic = Clinic.objects.get(clinicID=clinic_ID) 
        to_Reciever = clinic.clinicName 

        printOpthal = clinic.opthID.opthID
        print("Clinic: ", printOpthal)
        opthaID = Ophthalmologist.objects.get(opthID=printOpthal)

        print("User Log in: ",user_ID.firstName)
        print("Patient ")
        new_message = Message.objects.create(messageContent=message, userID=user_ID, clinicID=clinic_ID, opthID = opthaID, sender = to_Sender, reciever = to_Reciever)
        new_message.save()

        return HttpResponse('Message sent successfully')
    
    except UserPatient.DoesNotExist:
        return HttpResponse('UserPatient.DoesNotExist')

def getMessages(request, room):
    cliID = request.session.get('selected_clinic_id', None)
    clinic = Clinic.objects.get(clinicID=cliID)  
    printOpthal = clinic.opthID.opthID
    opthaID = Ophthalmologist.objects.get(opthID=printOpthal)

    user = request.user
    patientID = UserPatient.objects.get(user=user)

    if not user.is_authenticated:
        print("NOT AUTHENTICATED -------------------")

    room_details = get_object_or_404(ChatRoom, chatRoomName=room)

    messages = Message.objects.filter(clinicID=room_details, userID=patientID, opthID=opthaID) 
    
    messages_data = []
    for message in messages:
        user_id = message.userID_id
        sender = message.userID.firstName
        clinicSender = message.sender
        theSender = message.sender

        user = UserPatient.objects.get(userID=user_id)
        if sender == theSender: 
            label = 'Me'  
        else:
            label = clinicSender  

        user_data = {
            'user_id': user_id,
            'user_name': user.firstName,
            'user_last_name': user.lastName,
        }

        message_data = {
            'theSender': message.sender,
            'sender': message.userID.firstName,
            'clinicID': message.clinicID,
            'date': message.date,
            'messageContent': message.messageContent,
            'user': user_data,
            'label': label,
            'room': room,
        }

        messages_data.append(message_data)

    return JsonResponse({"messages": messages_data})

def mark_messages_as_read(request, room):
    
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        print("This shall run if the message is marked as read")
        
        user = request.user
        
        messages_to_update = Message.objects.filter(clinicID=room, reciever=user, is_read=False)
        messages_to_update.update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def messageNotification(request):
    user = request.user

    if user.is_authenticated:
        patient_id = UserPatient.objects.get(user=user)
        # Check for new messages since last check
        last_check_time = timezone.now() - timezone.timedelta(minutes=5)  
        
        # Exclude messages where the sender is the user
        new_messages = Message.objects.filter(userID=patient_id, is_read=False, date__gt=last_check_time).exclude(sender=user).order_by('-date')
        
        latest_messages_by_sender = {}
        for message in new_messages:
            sender = message.sender
            if sender not in latest_messages_by_sender:
                message_data = {
                    'sender': sender,
                    'message_content': message.messageContent,
                    'messageID': message.textID,
                    'clinicID': message.clinicID,
                    'date': message.date.strftime('%Y-%m-%d %H:%M:%S')
                }
                latest_messages_by_sender[sender] = message_data
        # Convert the dictionary values to a list as the response expects a list of messages
        latest_messages_data = list(latest_messages_by_sender.values())

        for unread in latest_messages_data:
            print(unread)
        
        return JsonResponse({'messages': latest_messages_data})
    else:
        return JsonResponse({'error': 'User is not authenticated'}, status=401)

# PATIENT REVIEW
def patientReview(request, clinic_id):
    user = request.user
    userID = None
    users = UserPatient.objects.get(user = user)
    userID = users

    getClinic=Clinic.objects.get(clinicID = clinic_id)
    clinicID = getClinic.clinicID
    print("CLinic ID: ", clinicID)
    context = {
        'clinicID' : clinicID,
        'getClinic' : getClinic,
        'userID' : userID,
    }
    return render(request, 'patient-review.html', context)

def saveReview(request):
    user = request.user
    users = UserPatient.objects.get(user=user)
    rev = request.POST.get('review')
    rate = request.POST.get('rate')
    getClinic = request.POST.get('getClinicID')
    clinicID = int(getClinic)
    clinic_instance = Clinic.objects.get(clinicID=clinicID)
    try:
        # Check if a rating already exists for the current patient and clinic
        existing_rating = PatientReview.objects.get(patientID=users, clinicID=clinic_instance)
        # If a rating exists, update the existing record
        existing_rating.rate = rate  # Update the rating value
        existing_rating.review = rev  # Update the review value
        existing_rating.save()
        print(f"Rating updated for Clinic ID: {getClinic}, Clinic Name: {existing_rating.clinicID.clinicName}")
    except PatientReview.DoesNotExist:
        new_rating = PatientReview(patientID=users, clinicID=clinic_instance, rate=rate, review=rev)
        new_rating.save()

    print(type(clinicID))    
    print(clinicID)
    print(rate)
    print(rev)

    messages.info(request, 'Thank you for your feedback!!')
    return redirect(reverse(index))

def viewTest(request):
    user = request.user
    ophthalmologist = Ophthalmologist.objects.get(user=user)
    clinic = Clinic.objects.get(opthID=ophthalmologist)
    appointments = Booking.objects.filter(clinicID=clinic, is_Accepted=True)
    print("List of Appointments: ", appointments)

    for a in appointments:
        print(a.bookingID)
    # Count appointments per month
    monthly_counts = appointments.annotate(month=ExtractMonth('appoint_Date')).values('month').annotate(count=Count('bookingID')).order_by('month')

    # Extract months and counts from the query
    months = [count['month'] for count in monthly_counts]
    counts = [count['count'] for count in monthly_counts]

    context = {
        "appointments": appointments,
        "months": months,
        "counts": counts,
    }

    return render(request, 'zz-test-for-visual.html', context)

def verify(request , auth_token):

    try:
        profile_obj = UserPatient.objects.filter(auth_token = auth_token).first()
        print("Try User Patient")
        if profile_obj:
            if profile_obj.is_EmailVerified:
                messages.success(request, 'Your account is already verified.')
                return redirect('login')
            profile_obj.is_EmailVerified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('login')
        else:
            print("User Patient Not Verified")
    except:
        pass

    try:
        profile_obj = Ophthalmologist.objects.filter(auth_token = auth_token).first()
        print("Verified Opthalmotrist")

        if profile_obj:
            if profile_obj.is_EmailVerified:
                messages.success(request, 'Your account is already verified.')
                return redirect('login')
            profile_obj.is_EmailVerified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')

            try:
                clinicExist = Clinic.objects.get(opthID = profile_obj)
                if clinicExist:
                    return redirect('dashboard')
            except:
                pass
            return redirect('/')
        else:
            print("User Patient Not Verified")
    except:
        pass

    try:
        profile_obj = ClinicStaff.objects.filter(auth_token = auth_token).first()
        print("Verified Clinic Staff")
        if profile_obj:
            if profile_obj.is_EmailVerified:
                messages.success(request, 'Your account is already verified.')
                return redirect('login')
            profile_obj.is_EmailVerified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')            
            try:
                clinicExist = Clinic.objects.get(stafferID = profile_obj)
                if clinicExist:
                    return HttpResponse("if clinic Exist")
                    return redirect('dashboard')
            except:
                pass

            return redirect('/')
        else:
            print("User Patient Not Verified")
    except Exception as e:
        print(e)
        return redirect('/')
    
def send_mail_after_registration(email , token):
    subject = 'Your accounts need to be verified'
    message = f'Hi paste the link to verify your account http://127.0.0.1:8000/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message , email_from ,recipient_list )

def signupOption(request):
    return render(request, 'signupOption.html')