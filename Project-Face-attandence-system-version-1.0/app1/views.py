import os
import cv2
import numpy as np
import torch
from facenet_pytorch import InceptionResnetV1, MTCNN
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Student, Attendance, CameraConfiguration
from django.core.files.base import ContentFile
from datetime import datetime, timedelta
from django.utils import timezone
import pygame  # Import pygame for playing sounds
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
import threading
import time
import base64
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Student
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import io


# Initialize MTCNN and InceptionResnetV1
mtcnn = MTCNN(keep_all=True)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

# Function to detect and encode faces
def detect_and_encode(image):
    with torch.no_grad():
        boxes, _ = mtcnn.detect(image)
        if boxes is not None:
            faces = []
            for box in boxes:
                face = image[int(box[1]):int(box[3]), int(box[0]):int(box[2])]
                if face.size == 0:
                    continue
                face = cv2.resize(face, (160, 160))
                face = np.transpose(face, (2, 0, 1)).astype(np.float32) / 255.0
                face_tensor = torch.tensor(face).unsqueeze(0)
                encoding = resnet(face_tensor).detach().numpy().flatten()
                faces.append(encoding)
            return faces
    return []

# Function to encode uploaded images
def encode_uploaded_images():
    known_face_encodings = []
    known_face_names = []

    # Fetch only authorized images
    uploaded_images = Student.objects.filter(authorized=True)

    for student in uploaded_images:
        image_path = os.path.join(settings.MEDIA_ROOT, str(student.image))
        known_image = cv2.imread(image_path)
        known_image_rgb = cv2.cvtColor(known_image, cv2.COLOR_BGR2RGB)
        encodings = detect_and_encode(known_image_rgb)
        if encodings:
            known_face_encodings.extend(encodings)
            known_face_names.append(student.name)

    return known_face_encodings, known_face_names

# Function to recognize faces
def recognize_faces(known_encodings, known_names, test_encodings, threshold=0.6):
    recognized_names = []
    for test_encoding in test_encodings:
        distances = np.linalg.norm(known_encodings - test_encoding, axis=1)
        min_distance_idx = np.argmin(distances)
        if distances[min_distance_idx] < threshold:
            recognized_names.append(known_names[min_distance_idx])
        else:
            recognized_names.append('Not Recognized')
    return recognized_names

# View for capturing student information and image
def capture_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        student_class = request.POST.get('student_class')
        image_data = request.POST.get('image_data')

        # Decode the base64 image data
        if image_data:
            header, encoded = image_data.split(',', 1)
            image_file = ContentFile(base64.b64decode(encoded), name=f"{name}.jpg")

            student = Student(
                name=name,
                email=email,
                phone_number=phone_number,
                student_class=student_class,
                image=image_file,
                authorized=False  # Default to False during registration
            )
            student.save()

            return redirect('selfie_success')  # Redirect to a success page

    return render(request, 'capture_student.html')


# Success view after capturing student information and image
def selfie_success(request):
    return render(request, 'selfie_success.html')


# API view for real-time face recognition from browser webcam
@csrf_exempt
def recognize_face_api(request):
    """API endpoint that accepts image data from browser and returns recognition results."""
    if request.method == 'POST':
        try:
            # Get image data from request
            image_data = request.POST.get('image_data', '')
            if not image_data:
                return JsonResponse({'error': 'No image data provided'}, status=400)
            
            # Decode base64 image
            header, encoded = image_data.split(',', 1)
            image_bytes = base64.b64decode(encoded)
            
            # Convert to PIL Image then to numpy array
            pil_image = Image.open(io.BytesIO(image_bytes))
            frame_rgb = np.array(pil_image)
            
            # Get camera configuration (use first one or default threshold)
            cam_configs = CameraConfiguration.objects.all()
            threshold = 0.6  # Default threshold
            if cam_configs.exists():
                threshold = cam_configs.first().threshold
            
            # Detect and encode faces in the frame
            test_face_encodings = detect_and_encode(frame_rgb)
            
            if not test_face_encodings:
                return JsonResponse({
                    'recognized': False,
                    'message': 'No face detected',
                    'faces': []
                })
            
            # Get known face encodings
            known_face_encodings, known_face_names = encode_uploaded_images()
            
            if not known_face_encodings:
                return JsonResponse({
                    'recognized': False,
                    'message': 'No authorized students found',
                    'faces': []
                })
            
            # Recognize faces
            names = recognize_faces(np.array(known_face_encodings), known_face_names, test_face_encodings, threshold)
            
            # Get face boxes for drawing
            boxes, _ = mtcnn.detect(frame_rgb)
            faces_data = []
            recognized_any = False
            attendance_messages = []
            
            for name, box in zip(names, boxes if boxes is not None else []):
                face_info = {
                    'name': name,
                    'box': box.tolist() if box is not None else None,
                    'recognized': name != 'Not Recognized'
                }
                faces_data.append(face_info)
                
                if name != 'Not Recognized':
                    recognized_any = True
                    # Handle attendance
                    students = Student.objects.filter(name=name)
                    if students.exists():
                        student = students.first()
                        attendance, created = Attendance.objects.get_or_create(
                            student=student, 
                            date=datetime.now().date()
                        )
                        
                        if created:
                            attendance.mark_checked_in()
                            attendance_messages.append(f"{name} checked in")
                        else:
                            if attendance.check_in_time and not attendance.check_out_time:
                                if timezone.now() >= attendance.check_in_time + timedelta(seconds=60):
                                    attendance.mark_checked_out()
                                    attendance_messages.append(f"{name} checked out")
                                else:
                                    attendance_messages.append(f"{name} already checked in")
                            elif attendance.check_in_time and attendance.check_out_time:
                                attendance_messages.append(f"{name} already checked out")
            
            return JsonResponse({
                'recognized': recognized_any,
                'faces': faces_data,
                'messages': attendance_messages
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# This views for capturing studen faces and recognize (Browser-based webcam)
def capture_and_recognize(request):
    """Render the webcam interface for face recognition."""
    # Get camera configurations for display
    cam_configs = CameraConfiguration.objects.all()
    threshold = 0.6
    if cam_configs.exists():
        threshold = cam_configs.first().threshold
    
    context = {
        'threshold': threshold,
        'has_cameras': cam_configs.exists()
    }
    return render(request, 'capture_and_recognize.html', context)

#this is for showing Attendance list
def student_attendance_list(request):
    # Get the search query and date filter from the request
    search_query = request.GET.get('search', '')
    date_filter = request.GET.get('attendance_date', '')

    # Get all students
    students = Student.objects.all()

    # Filter students based on the search query
    if search_query:
        students = students.filter(name__icontains=search_query)

    # Prepare the attendance data
    student_attendance_data = []

    for student in students:
        # Get the attendance records for each student, filtering by attendance date if provided
        attendance_records = Attendance.objects.filter(student=student)

        if date_filter:
            # Assuming date_filter is in the format YYYY-MM-DD
            attendance_records = attendance_records.filter(date=date_filter)

        attendance_records = attendance_records.order_by('date')
        
        student_attendance_data.append({
            'student': student,
            'attendance_records': attendance_records
        })

    context = {
        'student_attendance_data': student_attendance_data,
        'search_query': search_query,  # Pass the search query to the template
        'date_filter': date_filter       # Pass the date filter to the template
    }
    return render(request, 'student_attendance_list.html', context)


def home(request):
    total_students = Student.objects.count()
    total_attendance = Attendance.objects.count()
    total_check_ins = Attendance.objects.filter(check_in_time__isnull=False).count()
    total_check_outs = Attendance.objects.filter(check_out_time__isnull=False).count()
    total_cameras = CameraConfiguration.objects.count()

    context = {
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_check_ins': total_check_ins,
        'total_check_outs': total_check_outs,
        'total_cameras': total_cameras,
    }
    return render(request, 'home.html', context)


# Custom user pass test for admin access
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def student_list(request):
    students = Student.objects.all()
    return render(request, 'student_list.html', {'students': students})

@login_required
@user_passes_test(is_admin)
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'student_detail.html', {'student': student})

@login_required
@user_passes_test(is_admin)
def student_authorize(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        authorized = request.POST.get('authorized', False)
        student.authorized = bool(authorized)
        student.save()
        return redirect('student-detail', pk=pk)
    
    return render(request, 'student_authorize.html', {'student': student})

# This views is for Deleting student
@login_required
@user_passes_test(is_admin)
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully.')
        return redirect('student-list')  # Redirect to the student list after deletion
    
    return render(request, 'student_delete_confirm.html', {'student': student})


# View function for user login
def user_login(request):
    # Check if the request method is POST, indicating a form submission
    if request.method == 'POST':
        # Retrieve username and password from the submitted form data
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user using the provided credentials
        user = authenticate(request, username=username, password=password)

        # Check if the user was successfully authenticated
        if user is not None:
            # Log the user in by creating a session
            login(request, user)
            # Redirect the user to the student list page after successful login
            return redirect('home')  # Replace 'student-list' with your desired redirect URL after login
        else:
            # If authentication fails, display an error message
            messages.error(request, 'Invalid username or password.')

    # Render the login template for GET requests or if authentication fails
    return render(request, 'login.html')


# This is for user logout
def user_logout(request):
    logout(request)
    return redirect('login')  # Replace 'login' with your desired redirect URL after logout

# Function to handle the creation of a new camera configuration
@login_required
@user_passes_test(is_admin)
def camera_config_create(request):
    # Check if the request method is POST, indicating form submission
    if request.method == "POST":
        # Retrieve form data from the request
        name = request.POST.get('name')
        camera_source = request.POST.get('camera_source')
        threshold = request.POST.get('threshold')

        try:
            # Save the data to the database using the CameraConfiguration model
            CameraConfiguration.objects.create(
                name=name,
                camera_source=camera_source,
                threshold=threshold,
            )
            # Redirect to the list of camera configurations after successful creation
            return redirect('camera_config_list')

        except IntegrityError:
            # Handle the case where a configuration with the same name already exists
            messages.error(request, "A configuration with this name already exists.")
            # Render the form again to allow user to correct the error
            return render(request, 'camera_config_form.html')

    # Render the camera configuration form for GET requests
    return render(request, 'camera_config_form.html')


# READ: Function to list all camera configurations
@login_required
@user_passes_test(is_admin)
def camera_config_list(request):
    # Retrieve all CameraConfiguration objects from the database
    configs = CameraConfiguration.objects.all()
    # Render the list template with the retrieved configurations
    return render(request, 'camera_config_list.html', {'configs': configs})


# UPDATE: Function to edit an existing camera configuration
@login_required
@user_passes_test(is_admin)
def camera_config_update(request, pk):
    # Retrieve the specific configuration by primary key or return a 404 error if not found
    config = get_object_or_404(CameraConfiguration, pk=pk)

    # Check if the request method is POST, indicating form submission
    if request.method == "POST":
        # Update the configuration fields with data from the form
        config.name = request.POST.get('name')
        config.camera_source = request.POST.get('camera_source')
        config.threshold = request.POST.get('threshold')

        # Save the changes to the database
        config.save()  

        # Redirect to the list page after successful update
        return redirect('camera_config_list')  
    
    # Render the configuration form with the current configuration data for GET requests
    return render(request, 'camera_config_form.html', {'config': config})


# DELETE: Function to delete a camera configuration
@login_required
@user_passes_test(is_admin)
def camera_config_delete(request, pk):
    # Retrieve the specific configuration by primary key or return a 404 error if not found
    config = get_object_or_404(CameraConfiguration, pk=pk)

    # Check if the request method is POST, indicating confirmation of deletion
    if request.method == "POST":
        # Delete the record from the database
        config.delete()  
        # Redirect to the list of camera configurations after deletion
        return redirect('camera_config_list')

    # Render the delete confirmation template with the configuration data
    return render(request, 'camera_config_delete.html', {'config': config})
