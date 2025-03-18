from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClinicViewSet, update_booking_status
from . import views 

router = DefaultRouter()
router.register(r'clinics', ClinicViewSet)

urlpatterns = [
    path ("", views.index, name = "index"),
    path ('api/', include(router.urls)),
    # path ("home/", views.index, name = "index"), #why ito gumagana pero hindi yung nasa itaas? - SOLVED
    path ("login/", views.login_page, name = "login"),

    path ("signUp/", views.signUp, name = "signUp"), #gumagana yung pag lipat lipat or directing ng pages pero lagi s'ya kasama - solved
    path ("register", views.signUp),
    # path('token' , token_send , name="token_send"), # it jus a test page
    path('verify/<auth_token>' , views.verify , name="verify"),

    path('generate_pdf/<int:patient>/report', views.generate_pdf, name='generate_pdf'),
    path('requested_Report/<int:userID>/report', views.requested_Report, name='requested_Report'),
    path('clinic_Report/ID/<int:clinicID>/', views.clinic_Report, name='clinic_Report'),

    path ("logout/", views.logout, name="logout" ),    
    path ("test_Map/", views.test_Map, name="test_Map" ), # just for experimental
    path ("booking_Page/", views.booking_Page, name="booking_Page" ),
    path ("update_page/", views.update_page, name="update_page" ),
    path ("user_profile/", views.user_profile, name="user_profile" ),
    path ("test_Calendar/", views.DashCalendar, name="test_Calendar" ),
    path ("locate/", views.locate, name="locate" ),
    path ("clinics/", views.clinics, name="clinics" ),
     path("index_ClinicsProfile/<int:clinicID>/", views.index_ClinicsProfile, name="index_ClinicsProfile"),

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ OPTHALMOLOGIST SIDE // CLINIC
    path ("dashboard/", views.dashboard, name = "dashboard"),
    path ("dashboard/Current_Session", views.clinic_dash_curS, name = "clinic_dash_curS"),
    path ("dashboard/Notes", views.clinic_dashboard_notes, name = "clinic_dashboard_notes"),
    path ("dashboard/Statistics", views.clinic_dashboard_Stats, name = "clinic_dashboard_Stats"),
    path ("dashboard/Add_Appointment", views.clinic_dashboard_walkIn, name = "clinic_dashboard_AddApt"),

    path ("dashboard/Form", views.clinic_dashboard_walkInForm, name = "clinic_dashboard_walkInForm"),
    path ("dashboard/CheckUserAccount", views.checkPatientInformation, name = "checkPatientInformation"),

    path('viewTest/', views.viewTest, name='viewTest'),


    path ("profile", views.clinic_dashboard_profile, name = "clinic_dashboard_profile"),
    path ("profile/Staff", views.clinic_dashboard_profile_Staff, name = "clinic_dashboard_profile_Staff"),
    path ("profile/Opthalmologist", views.clinic_dashboard_profile_Opthal, name = "clinic_dashboard_profile_Opthal"),    
    path ("clinic_services/", views.clinic_services, name = "clinic_services"),
    path ("clinic_messages/", views.clinic_messages, name = "clinic_messages"),
    path ("clinic_patintTables/", views.clinic_patintTables, name = "clinic_patintTables"),
    path ('update_booking_status/', views.update_booking_status, name='update_booking_status'),
    path ("clinic_regServices/", views.clinic_regServices, name="clinic_regServices"),
    path ("clinic_editServices/", views.clinic_editServices, name="clinic_editServices"),
    path ("delete_service/<int:serviceID>/", views.delete_service, name="delete_service"),
    path ("signUp_Opthal/", views.signUp_Opthal, name = "signUp_Opthal"), #gumagana yung pag lipat lipat or directing ng pages pero lagi s'ya kasama - solved
    path ("register", views.signUp_Opthal),
    
    path('move_appointment/<int:booking_id>/', views.move_appointment, name='move_appointment'),
    #path ("registerService", views.clinic_regServices), 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ ADMIN SIDE
    path ("admin_Cregistration/", views.admin_Cregistration, name="admin_Cregistration" ),
    path ('location/', views.location, name='location'),
    path ("admin_registerC", views.admin_Cregistration), 
    path ("admin_Tables/", views.admin_Tables, name="admin_Tables" ),
    path ('delete_users/', views.delete_users, name='delete_users'),
    path ('admin_UpdateUser/', views.admin_UpdateUser, name='admin_UpdateUser'),
    path ("admin_RegisterUser/", views.admin_RegisterUser, name="admin_RegisterUser" ),
    path ("admin_RegisterOptha/", views.admin_RegisterOptha, name="admin_RegisterOptha" ),
    path ('admin_UpdateOptha/<int:userID>/', views.admin_UpdateOptha, name='admin_UpdateOptha'),
    path ("admin_OpthalInfo/", views.admin_OpthalInfo, name="admin_OpthalInfo" ),
    path ("admin_Dashboard/", views.admin_Dashboard, name="admin_Dashboard" ),
    path ("Inbox/", views.patient_Inbox, name="patient_Inbox" ),
    path ("admin_Clinics_Table/", views.admin_Clinics_Table, name="admin_Clinics_Table" ),
    path ("admin_Clinics_Information/<int:clinicID>/Clnc", views.admin_Clinics_Information, name="admin_Clinics_Information" ),
    path ("admin_Opthal/", views.admin_Opthal, name="admin_Opthal" ),
    path ("admin_Users/", views.admin_Users, name="admin_Users" ),

    path('view_Profile/<int:bookingID>/', views.patientProfile, name='view_booking'),
    path('dataSheet/<int:bookingID>/', views.dataSheet, name='dataSheet'),
    path('savedData/', views.savedData, name='savedData'),
    # path('savedDataForWalkIn/', views.savedDataForWalkIn, name='savedDataForWalkIn'),

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ END ADMIN SIDE

    path ('saveReview/', views.saveReview, name='saveReview'),
    path ('make_Review/<int:clinic_id>/', views.patientReview, name='patientReview'),
    path ('save_event/', views.save_event, name='save_event'),
    path('get_events/<int:clinic_id>/', views.get_events, name='get_events'),
    path('get_location/', views.get_events, name='get_events'),
    path('update_session_status/', views.update_session_status, name='update_session_status'),
    
    path('check_availability/', views.check_availability, name='check_availability'),
    path ('clinic/<int:clinic_id>/booking_Page/', views.pop_up_redirect, name='clinic-booking-page'),
    path ('check_authentication/', views.check_authentication, name='check_authentication'),

    # Patient Messaging
    path('createmessage', views.createmessage, name='createmessage'),
    path('<str:room>/', views.room, name='room'), # room
    path('send', views.send, name='send'),
    path('getMessages/<str:room>/', views.getMessages, name='getMessages'),

    # path('mark_messages_as_read/', views.mark_messages_as_read, name='mark_messages_as_read'),
    path('<str:cRoom>/mark_messages_as_read_Clini/', views.mark_messages_as_read_Clini, name='mark_messages_as_read_Clini'),
    path('<str:room>/mark_messages_as_read/', views.mark_messages_as_read, name='mark_messages_as_read'),
    path('messageNotification/NewMessage/', views.messageNotification, name='messageNotification'),

    # Clinic Messaging
    path ('clinic/<str:cRoom>/', views.cRoom, name='cRoom'), # ito yung room
    path('viewRoom', views.viewRoom, name='viewRoom'),
    path('send_Clinic', views.send_Clinic, name='send_Clinic'),
    path('getMessages_Clinic/<str:cRoom>/', views.getMessages_Clinic, name='getMessages_Clinic'),


    path('test/Form/', views.signupOption, name='signupOption'),

]