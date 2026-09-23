from django.urls import path
from . import views
urlpatterns = [
    path('capture_student/', views.capture_student, name='capture_student'),
    path('student/register/', views.capture_student, name='student_register'),
    path('register/', views.capture_student, name='register_student'),
    path('', views.home, name='home'),
    path('selfie-success/', views.selfie_success, name='selfie_success'),
    path('capture-and-recognize/', views.capture_and_recognize, name='capture_and_recognize'),
    path('capture-and-recognize/', views.capture_and_recognize, name='capture-and-recognize'),
    path('api/recognize-face/', views.recognize_face_api, name='recognize_face_api'),
    path('api/detect-face/', views.detect_face_api, name='detect_face_api'),
    path('api/biometric-login/', views.biometric_login_api, name='biometric_login_api'),
    path('api/fingerprint-login/', views.fingerprint_login_api, name='fingerprint_login_api'),
    path('api/fingerprint-attendance/', views.fingerprint_attendance_api, name='fingerprint_attendance_api'),
    path('api/check-fingerprint-unique/', views.check_fingerprint_unique_api, name='check_fingerprint_unique_api'),
    # Physical Laptop Fingerprint Sensor (WebAuthn / Windows Hello)
    path('api/webauthn/register-challenge/', views.webauthn_register_challenge, name='webauthn_register_challenge'),
    path('api/webauthn/register-verify/', views.webauthn_register_verify, name='webauthn_register_verify'),
    path('api/webauthn/attendance-challenge/', views.webauthn_attendance_challenge, name='webauthn_attendance_challenge'),
    path('api/webauthn/attendance-verify/', views.webauthn_attendance_verify, name='webauthn_attendance_verify'),
    path('api/webauthn/login-verify/', views.webauthn_login_verify, name='webauthn_login_verify'),
    path('students/attendance/', views.student_attendance_list, name='student_attendance_list'),
    path('students/', views.student_list, name='student-list'),
    path('students/<int:pk>/', views.student_detail, name='student-detail'),
    path('students/<int:pk>/authorize/', views.student_authorize, name='student-authorize'),
    path('students/<int:pk>/delete/', views.student_delete, name='student-delete'),
    path('login/', views.user_login, name='login'),
    path('login/student/', views.student_login, name='student_login'),
    path('login/admin/', views.admin_login, name='admin_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('camera-config/', views.camera_config_create, name='camera_config_create'),
    path('camera-config/list/', views.camera_config_list, name='camera_config_list'),
    path('camera-config/update/<int:pk>/', views.camera_config_update, name='camera_config_update'),
    path('camera-config/delete/<int:pk>/', views.camera_config_delete, name='camera_config_delete'),
]
    

