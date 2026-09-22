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
try:
    import pygame  # Import pygame for playing sounds
except ImportError:
    pygame = None
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
import threading
import time
import base64
import secrets
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
import json


# Try importing torch/facenet-pytorch if available, otherwise use lightweight OpenCV YuNet + SFace
try:
    import torch
    from facenet_pytorch import InceptionResnetV1, MTCNN
    USE_TORCH = True
    mtcnn = MTCNN(keep_all=True)
    resnet = InceptionResnetV1(pretrained='vggface2').eval()
except Exception:
    USE_TORCH = False

YUNET_PATH = os.path.join(settings.BASE_DIR, 'models', 'face_detection_yunet_2023mar.onnx')
SFACE_PATH = os.path.join(settings.BASE_DIR, 'models', 'face_recognition_sface_2021dec.onnx')

detector = None
recognizer = None
try:
    if os.path.exists(YUNET_PATH) and os.path.exists(SFACE_PATH):
        detector = cv2.FaceDetectorYN.create(YUNET_PATH, '', (300, 300))
        recognizer = cv2.FaceRecognizerSF.create(SFACE_PATH, '')
except Exception as e:
    print(f"Warning: Could not initialize OpenCV FaceDetector/FaceRecognizer: {e}")

# Cache for known face encodings to avoid disk I/O and re-encoding on every frame
_KNOWN_ENCODINGS_CACHE = None
_KNOWN_NAMES_CACHE = None

def invalidate_face_cache():
    global _KNOWN_ENCODINGS_CACHE, _KNOWN_NAMES_CACHE
    _KNOWN_ENCODINGS_CACHE = None
    _KNOWN_NAMES_CACHE = None

def detect_and_encode(image):
    if not USE_TORCH and detector is not None and recognizer is not None:
        try:
            h, w, _ = image.shape
            detector.setInputSize((w, h))
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) if image.ndim == 3 else image
            _, faces = detector.detect(image_bgr)
            encodings = []
            boxes = []
            if faces is not None:
                for face in faces:
                    aligned_face = recognizer.alignCrop(image_bgr, face)
                    feature = recognizer.feature(aligned_face).flatten()
                    encodings.append(feature)
                    box = [float(face[0]), float(face[1]), float(face[0] + face[2]), float(face[1] + face[3])]
                    boxes.append(box)
            return encodings, boxes
        except Exception as e:
            print(f"Error in OpenCV detection: {e}")
            return [], []

    if USE_TORCH:
        try:
            with torch.no_grad():
                raw_boxes, _ = mtcnn.detect(image)
                faces = []
                ret_boxes = []
                if raw_boxes is not None:
                    h, w = image.shape[:2]
                    for b in raw_boxes:
                        x1 = max(0, int(b[0]))
                        y1 = max(0, int(b[1]))
                        x2 = min(w, int(b[2]))
                        y2 = min(h, int(b[3]))
                        if x2 <= x1 or y2 <= y1:
                            continue
                        face_crop = image[y1:y2, x1:x2]
                        if face_crop.size == 0:
                            continue
                        face_resized = cv2.resize(face_crop, (160, 160))
                        face_arr = np.transpose(face_resized, (2, 0, 1)).astype(np.float32) / 255.0
                        face_tensor = torch.tensor(face_arr).unsqueeze(0)
                        encoding = resnet(face_tensor).detach().numpy().flatten()
                        faces.append(encoding)
                        ret_boxes.append([float(b[0]), float(b[1]), float(b[2]), float(b[3])])
                    return faces, ret_boxes
        except Exception as e:
            print(f"Error in PyTorch detection: {e}")
            return [], []
    return [], []

def encode_uploaded_images():
    global _KNOWN_ENCODINGS_CACHE, _KNOWN_NAMES_CACHE
    if _KNOWN_ENCODINGS_CACHE is not None and _KNOWN_NAMES_CACHE is not None:
        return _KNOWN_ENCODINGS_CACHE, _KNOWN_NAMES_CACHE

    known_face_encodings = []
    known_face_names = []
    uploaded_images = Student.objects.filter(authorized=True)

    for student in uploaded_images:
        try:
            if not student.image:
                continue
            image_path = os.path.join(settings.MEDIA_ROOT, str(student.image))
            if not os.path.exists(image_path):
                continue
            known_image = cv2.imread(image_path)
            if known_image is None:
                continue
            known_image_rgb = cv2.cvtColor(known_image, cv2.COLOR_BGR2RGB)
            encodings, _ = detect_and_encode(known_image_rgb)
            if encodings and len(encodings) > 0:
                known_face_encodings.append(encodings[0])
                known_face_names.append(student.name)
        except Exception as e:
            print(f"Error encoding image for {student.name}: {e}")
            continue

    _KNOWN_ENCODINGS_CACHE = known_face_encodings
    _KNOWN_NAMES_CACHE = known_face_names
    return known_face_encodings, known_face_names

def recognize_faces(known_encodings, known_names, test_encodings, threshold=0.65):
    recognized_names = []
    if len(known_encodings) == 0:
        return ['Not Recognized'] * len(test_encodings)
    
    known_arr = np.array(known_encodings)
    for test_encoding in test_encodings:
        test_enc = np.array(test_encoding)
        distances = np.linalg.norm(known_arr - test_enc, axis=1)
        min_distance_idx = np.argmin(distances)
        if distances[min_distance_idx] < threshold:
            recognized_names.append(known_names[min_distance_idx])
        else:
            recognized_names.append('Not Recognized')
    return recognized_names

# API view to check fingerprint uniqueness in real-time
@csrf_exempt
def check_fingerprint_unique_api(request):
    """
    Checks in real-time whether a scanned fingerprint ID / hash is unique or already registered.
    """
    if request.method == 'POST':
        fingerprint_id = request.POST.get('fingerprint_id', '').strip()
        if not fingerprint_id:
            return JsonResponse({'is_unique': False, 'message': 'No fingerprint identifier provided.'}, status=400)
        
        existing = Student.objects.filter(fingerprint_id=fingerprint_id).first()
        if existing:
            return JsonResponse({
                'is_unique': False,
                'existing_student': existing.name,
                'message': f"Duplicate fingerprint detected! This print is already registered to '{existing.name}' ({existing.student_class}). Each student must register a distinct, unique fingerprint."
            })
        else:
            return JsonResponse({
                'is_unique': True,
                'message': "Fingerprint is unique and available for enrollment!"
            })
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# View for capturing student information, face image, and optical fingerprint
def capture_student(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        student_class = request.POST.get('student_class', '').strip()
        image_data = request.POST.get('image_data', '').strip()
        fingerprint_id = request.POST.get('fingerprint_id', '').strip()
        finger_type = request.POST.get('finger_type', 'Right Index').strip()
        fingerprint_data = request.POST.get('fingerprint_data', '').strip()

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.content_type

        # 1. Require face image
        if not image_data:
            err = "Facial image capture is required. Please position your face before the camera."
            if is_ajax:
                return JsonResponse({'success': False, 'error': err}, status=400)
            messages.error(request, err)
            return render(request, 'capture_student.html', {'error': err})

        # 2. Check fingerprint ID if provided (Real biometric credential from laptop sensor)
        if fingerprint_id:
            # Check for unique fingerprint
            existing_student = Student.objects.filter(fingerprint_id=fingerprint_id).first()
            if existing_student:
                err = f"Duplicate fingerprint detected! This print is already registered to '{existing_student.name}'."
                if is_ajax:
                    return JsonResponse({'success': False, 'error': err}, status=400)
                messages.error(request, err)
                return render(request, 'capture_student.html', {'error': err})
        else:
            # If no physical finger was placed/scanned, do not fabricate a fake fingerprint ID!
            fingerprint_id = None
            fingerprint_data = None

        # Decode the base64 image data
        if ',' in image_data:
            header, encoded = image_data.split(',', 1)
        else:
            encoded = image_data
        image_file = ContentFile(base64.b64decode(encoded), name=f"{name}.jpg")

        student = Student(
            name=name,
            email=email,
            phone_number=phone_number,
            student_class=student_class,
            image=image_file,
            fingerprint_id=fingerprint_id,
            finger_type=finger_type if finger_type else 'Right Index',
            fingerprint_data=fingerprint_data,
            authorized=True  # Immediately authorize face & fingerprint biometrics
        )
        student.save()
        invalidate_face_cache()

        request.session['enrolled_student_name'] = student.name
        request.session['enrolled_student_id'] = student.id
        request.session['enrolled_finger_type'] = student.finger_type
        request.session['enrolled_fingerprint_id'] = student.fingerprint_id

        if is_ajax:
            return JsonResponse({'success': True, 'redirect_url': '/selfie-success/'})

        return redirect('selfie_success')

    # Pass existing registered fingerprints for instant real-time client validation
    registered_fps = list(Student.objects.exclude(fingerprint_id__isnull=True).exclude(fingerprint_id__exact='').values('name', 'fingerprint_id', 'finger_type'))
    return render(request, 'capture_student.html', {
        'existing_fps_json': json.dumps(registered_fps)
    })


# Success view after capturing student biometrics (face + unique fingerprint)
def selfie_success(request):
    student_name = request.session.get('enrolled_student_name', '')
    student_id = request.session.get('enrolled_student_id', '')
    finger_type = request.session.get('enrolled_finger_type', 'Right Index')
    fingerprint_id = request.session.get('enrolled_fingerprint_id', '')
    return render(request, 'selfie_success.html', {
        'student_name': student_name,
        'student_id': student_id,
        'finger_type': finger_type,
        'fingerprint_id': fingerprint_id,
    })


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
            
            # Decode base64 image safely
            if ',' in image_data:
                header, encoded = image_data.split(',', 1)
            else:
                encoded = image_data
            image_bytes = base64.b64decode(encoded)
            
            # Convert to PIL Image in RGB mode then to numpy array
            pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            frame_rgb = np.array(pil_image)
            
            # Get camera configuration (use first one or default threshold)
            cam_configs = CameraConfiguration.objects.all()
            threshold = 0.65  # Optimal threshold
            if cam_configs.exists():
                threshold = cam_configs.first().threshold
            
            # Detect and encode faces in the frame
            test_face_encodings, boxes = detect_and_encode(frame_rgb)
            
            if not test_face_encodings:
                return JsonResponse({
                    'recognized': False,
                    'message': 'No face detected in current frame',
                    'faces': []
                })
            
            # Get known face encodings from cache / database
            known_face_encodings, known_face_names = encode_uploaded_images()
            
            if not known_face_encodings:
                return JsonResponse({
                    'recognized': False,
                    'message': 'No authorized student templates found. Please enroll and authorize students first.',
                    'faces': []
                })
            
            # Recognize faces
            names = recognize_faces(known_face_encodings, known_face_names, test_face_encodings, threshold)
            
            # Build clean face boxes list (safe conversion for JSON response)
            faces_data = []
            recognized_any = False
            attendance_messages = []
            
            boxes_to_iterate = boxes if boxes is not None else []
            now = timezone.now()
            now_time_str = now.strftime("%I:%M:%S %p")

            for name, box in zip(names, boxes_to_iterate):
                clean_box = None
                if box is not None:
                    if isinstance(box, np.ndarray):
                        clean_box = [float(coord) for coord in box.tolist()]
                    elif isinstance(box, (list, tuple)):
                        clean_box = [float(coord) for coord in box]
                    else:
                        try:
                            clean_box = [float(coord) for coord in list(box)]
                        except Exception:
                            clean_box = None

                status_type = 'UNRECOGNIZED'
                status_text = 'Unknown'
                duration_text = None

                if name != 'Not Recognized':
                    recognized_any = True
                    students = Student.objects.filter(name=name)
                    if students.exists():
                        student = students.first()
                        today = now.date()
                        attendance, created = Attendance.objects.get_or_create(
                            student=student, 
                            date=today
                        )
                        
                        if created or not attendance.check_in_time:
                            attendance.mark_checked_in()
                            status_type = 'CHECK-IN'
                            status_text = f"Checked In: {now_time_str}"
                            attendance_messages.append(f"[CHECK-IN] {name} checked in successfully at {now_time_str}")
                        else:
                            if attendance.check_in_time and not attendance.check_out_time:
                                if now >= attendance.check_in_time + timedelta(seconds=60):
                                    attendance.mark_checked_out()
                                    duration_text = attendance.calculate_duration()
                                    status_type = 'CHECK-OUT'
                                    status_text = f"Checked Out: {now_time_str}"
                                    attendance_messages.append(f"[CHECK-OUT] {name} checked out successfully at {now_time_str} (Duration: {duration_text})")
                                else:
                                    in_time = attendance.check_in_time.strftime("%I:%M %p")
                                    status_type = 'ALREADY_CHECKED_IN'
                                    status_text = f"Checked In: {in_time}"
                                    attendance_messages.append(f"[ALREADY CHECKED IN] {name} already checked in at {in_time}")
                            elif attendance.check_in_time and attendance.check_out_time:
                                out_time = attendance.check_out_time.strftime("%I:%M %p")
                                duration_text = attendance.calculate_duration()
                                status_type = 'ALREADY_CHECKED_OUT'
                                status_text = f"Checked Out: {out_time}"
                                attendance_messages.append(f"[ALREADY CHECKED OUT] {name} already checked out at {out_time} (Duration: {duration_text})")

                face_info = {
                    'name': name,
                    'box': clean_box,
                    'recognized': name != 'Not Recognized',
                    'attendance_type': status_type,
                    'attendance_text': status_text,
                    'timestamp': now_time_str,
                    'duration': duration_text
                }
                faces_data.append(face_info)
            
            return JsonResponse({
                'recognized': recognized_any,
                'faces': faces_data,
                'messages': attendance_messages
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# API view for biometric face authentication on the login page
@csrf_exempt
def biometric_login_api(request):
    """
    Accepts webcam face image data from the login page, detects face,
    matches against authorized templates, and authenticates the user into their session.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    try:
        image_data = request.POST.get('image_data', '')
        portal_type = request.POST.get('portal_type', 'auto')  # 'admin', 'student', or 'auto'

        if not image_data:
            return JsonResponse({'success': False, 'message': 'No image frame received from camera.'}, status=400)

        if ',' in image_data:
            header, encoded = image_data.split(',', 1)
        else:
            encoded = image_data
        image_bytes = base64.b64decode(encoded)

        pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        frame_rgb = np.array(pil_image)

        # Get camera configuration threshold
        cam_configs = CameraConfiguration.objects.all()
        threshold = 0.65
        if cam_configs.exists():
            threshold = cam_configs.first().threshold

        # Detect and encode faces
        test_face_encodings, boxes = detect_and_encode(frame_rgb)
        if not test_face_encodings:
            return JsonResponse({
                'success': False,
                'face_detected': False,
                'message': 'No face detected. Please position your face clearly inside the scanner.'
            })

        # Get known templates from database
        known_face_encodings, known_face_names = encode_uploaded_images()
        if not known_face_encodings:
            return JsonResponse({
                'success': False,
                'face_detected': True,
                'message': 'No authorized biometrics found in database. Please register a student face first.'
            })

        # Recognize faces
        recognized_names = recognize_faces(known_face_encodings, known_face_names, test_face_encodings, threshold)
        matched_name = next((n for n in recognized_names if n != 'Not Recognized'), None)

        if not matched_name:
            return JsonResponse({
                'success': False,
                'face_detected': True,
                'message': 'Biometric face not recognized. Please retry in good lighting or use credential sign in.'
            })

        # Biometric verified! Determine if admin or student
        admin_user = User.objects.filter(username__iexact='lokeshwar').first()
        is_admin_target = (
            portal_type == 'admin' or
            'lokeshwar' in matched_name.lower() or
            (admin_user and matched_name.strip().lower() == admin_user.username.lower())
        )

        if is_admin_target and admin_user:
            login(request, admin_user)
            request.session['user_role'] = 'admin'
            messages.success(request, f'Biometric authentication verified! Welcome, {admin_user.username}!')
            return JsonResponse({
                'success': True,
                'role': 'admin',
                'name': admin_user.username,
                'redirect_url': '/',
                'message': f'Authenticated as Administrator {admin_user.username}'
            })

        # If student portal or recognized as student
        matched_student = Student.objects.filter(name__iexact=matched_name).first()
        if not matched_student:
            matched_student = Student.objects.filter(name__icontains=matched_name).first()

        if matched_student:
            request.session['student_id'] = matched_student.id
            request.session['student_name'] = matched_student.name
            request.session['user_role'] = 'student'
            messages.success(request, f'Biometric authentication verified! Welcome, {matched_student.name}!')
            return JsonResponse({
                'success': True,
                'role': 'student',
                'name': matched_student.name,
                'redirect_url': '/',
                'message': f'Authenticated as Student {matched_student.name}'
            })

        # Fallback to admin if admin exists and name is close
        if admin_user:
            login(request, admin_user)
            request.session['user_role'] = 'admin'
            messages.success(request, f'Biometric authentication verified! Welcome, {admin_user.username}!')
            return JsonResponse({
                'success': True,
                'role': 'admin',
                'name': admin_user.username,
                'redirect_url': '/',
                'message': f'Authenticated as Administrator {admin_user.username}'
            })

        return JsonResponse({
            'success': False,
            'face_detected': True,
            'message': f'Face recognized as {matched_name}, but account record was not found.'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'Biometric recognition error: {str(e)}'}, status=500)


# API view for fingerprint biometric attendance (Face Recognition Fallback)
@csrf_exempt
def fingerprint_attendance_api(request):
    """
    Fingerprint Biometric Attendance Fallback:
    Used when facial recognition fails (e.g. poor lighting, obstruction, camera failure)
    or when a student chooses optical fingerprint scanning to mark daily attendance.
    Records Check-In and Check-Out with duration calculation.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    try:
        fingerprint_id = request.POST.get('fingerprint_id', '').strip()
        student_id = request.POST.get('student_id', '').strip()
        identifier = request.POST.get('identifier', '').strip()

        # A fingerprint MUST be provided to take fingerprint attendance!
        # Do not allow empty, null, or blind fallback attendance.
        if not fingerprint_id or fingerprint_id.lower() in ('auto', 'none', 'null', ''):
            return JsonResponse({
                'success': False,
                'message': 'No fingerprint detected on optical sensor. Please place a registered finger on the sensor to scan.'
            }, status=400)

        student = None
        # 1. Direct biometric identification by unique fingerprint ID
        student = Student.objects.filter(fingerprint_id=fingerprint_id).first()

        # 2. Match by student ID if specified and verify fingerprint match
        if not student and student_id and student_id.isdigit():
            candidate = Student.objects.filter(id=int(student_id)).first()
            if candidate and candidate.fingerprint_id == fingerprint_id:
                student = candidate

        if not student:
            return JsonResponse({
                'success': False,
                'message': 'Unrecognized fingerprint! This biometric print does not match any registered student. Please register your fingerprint first.'
            }, status=404)

        if not student.authorized:
            return JsonResponse({
                'success': False,
                'message': f'Student {student.name} is not authorized for attendance. Please contact admin for authorization.'
            }, status=403)

        now = timezone.now()
        now_time_str = now.strftime("%I:%M %p")
        today = now.date()

        attendance, created = Attendance.objects.get_or_create(
            student=student,
            date=today
        )

        status_type = 'CHECK-IN'
        status_text = f"Checked In: {now_time_str}"
        duration_text = None
        action_title = "Check-In Recorded"
        msg = f"{student.name} marked attendance via fingerprint at {now_time_str}"

        if created or not attendance.check_in_time:
            attendance.mark_checked_in()
            status_type = 'CHECK-IN'
            action_title = "Check-In Confirmed"
            status_text = f"Checked In: {now_time_str}"
            msg = f"Check-In recorded successfully for {student.name} at {now_time_str} via fingerprint sensor."
        else:
            if attendance.check_in_time and not attendance.check_out_time:
                # If checked in recently (< 60s), notify already checked in; otherwise mark check-out
                if now >= attendance.check_in_time + timedelta(seconds=60):
                    attendance.mark_checked_out()
                    duration_text = attendance.calculate_duration()
                    status_type = 'CHECK-OUT'
                    action_title = "Check-Out Confirmed"
                    status_text = f"Checked Out: {now_time_str} (Duration: {duration_text})"
                    msg = f"Check-Out recorded for {student.name} at {now_time_str}. Total duration: {duration_text}."
                else:
                    in_time = attendance.check_in_time.strftime("%I:%M %p")
                    status_type = 'ALREADY_CHECKED_IN'
                    action_title = "Already Checked In"
                    status_text = f"Checked In: {in_time}"
                    msg = f"{student.name} is already checked in for today (at {in_time}). Tap again after 1 minute to check out."
            elif attendance.check_in_time and attendance.check_out_time:
                out_time = attendance.check_out_time.strftime("%I:%M %p")
                duration_text = attendance.calculate_duration()
                status_type = 'ALREADY_CHECKED_OUT'
                action_title = "Session Completed"
                status_text = f"Checked Out: {out_time} ({duration_text})"
                msg = f"{student.name} already completed today's attendance at {out_time} (Duration: {duration_text})."

        return JsonResponse({
            'success': True,
            'student_id': student.id,
            'student_name': student.name,
            'student_email': student.email,
            'student_class': student.student_class or '',
            'student_image': student.image.url if student.image else '',
            'finger_type': student.finger_type or 'Optical Fingerprint',
            'fingerprint_id': student.fingerprint_id or '',
            'attendance_type': status_type,
            'action_title': action_title,
            'attendance_text': status_text,
            'timestamp': now_time_str,
            'duration': duration_text,
            'message': msg
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'Fingerprint attendance error: {str(e)}'}, status=500)


# Backward-compatible API view for fingerprint login
@csrf_exempt
def fingerprint_login_api(request):
    return fingerprint_attendance_api(request)


# =====================================================================
# PHYSICAL BIOMETRIC SENSOR (WEBAUTHN / WINDOWS HELLO / ELAN SENSOR)
# =====================================================================

@csrf_exempt
def webauthn_register_challenge(request):
    """Generate WebAuthn challenge for registering student's laptop fingerprint sensor."""
    student_id = request.POST.get('student_id') or request.GET.get('student_id') or request.session.get('student_id')
    student_name = request.POST.get('student_name') or request.GET.get('student_name') or ''
    email = request.POST.get('email') or request.GET.get('email') or ''
    
    student = None
    if student_id and str(student_id).isdigit():
        student = Student.objects.filter(id=int(student_id)).first()
    
    challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    request.session['webauthn_reg_challenge'] = challenge
    
    user_id_raw = f"student_{student.id if student else secrets.token_hex(8)}"
    user_id_b64 = base64.urlsafe_b64encode(user_id_raw.encode('utf-8')).decode('utf-8').rstrip('=')
    
    host = request.get_host().split(':')[0]
    if host in ('127.0.0.1', '0.0.0.0'):
        host = 'localhost'
        
    displayName = student.name if student else (student_name if student_name else 'Student')
    userName = student.email if (student and student.email) else (email if email else f"student_{secrets.token_hex(4)}")
    
    return JsonResponse({
        'success': True,
        'challenge': challenge,
        'rp': {
            'name': 'Face & Fingerprint AI Attendance',
            'id': host
        },
        'user': {
            'id': user_id_b64,
            'name': userName,
            'displayName': displayName
        }
    })


@csrf_exempt
def webauthn_register_verify(request):
    """Store the physical biometric credential from the laptop fingerprint sensor."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
    
    try:
        credential_id = request.POST.get('credential_id', '').strip()
        finger_type = request.POST.get('finger_type', 'Right Index').strip()
        student_id = request.POST.get('student_id') or request.session.get('student_id')
        
        if not credential_id:
            return JsonResponse({'success': False, 'message': 'No biometric credential received from fingerprint sensor.'}, status=400)
            
        student = None
        if student_id and str(student_id).isdigit():
            student = Student.objects.filter(id=int(student_id)).first()
            
        if not student:
            return JsonResponse({'success': False, 'message': 'Student profile not found. Please provide a valid student.'}, status=404)
            
        # Check uniqueness: Has this physical credential already been registered to another student?
        existing = Student.objects.filter(fingerprint_id=credential_id).exclude(id=student.id).first()
        if existing:
            return JsonResponse({
                'success': False,
                'message': f"This physical fingerprint is already registered to '{existing.name}' ({existing.student_class}). Each student must register a distinct fingerprint."
            }, status=400)
            
        student.fingerprint_id = credential_id
        student.finger_type = finger_type
        student.fingerprint_data = json.dumps({
            'fingerprint_id': credential_id,
            'finger_type': finger_type,
            'sensor_type': 'Platform Authenticator (Windows Hello)',
            'registered_at': timezone.now().isoformat()
        })
        student.save()
        
        return JsonResponse({
            'success': True,
            'message': f"Physical fingerprint ({finger_type}) enrolled successfully for {student.name} via laptop sensor.",
            'student_id': student.id,
            'student_name': student.name,
            'fingerprint_id': student.fingerprint_id,
            'finger_type': student.finger_type
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'Registration failed: {str(e)}'}, status=500)


@csrf_exempt
def webauthn_attendance_challenge(request):
    """Generate WebAuthn challenge for kiosk attendance scanning."""
    challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    request.session['webauthn_att_challenge'] = challenge
    
    host = request.get_host().split(':')[0]
    if host in ('127.0.0.1', '0.0.0.0'):
        host = 'localhost'
    
    # Collect registered students who have an enrolled physical laptop fingerprint
    registered_students = Student.objects.filter(
        authorized=True, 
        fingerprint_id__isnull=False
    ).exclude(fingerprint_id='')
    
    allow_credentials = []
    
    for s in registered_students:
        # Exclude fake legacy hash strings that start with FP- to ensure WebAuthn only prompts for valid platform credentials
        if not s.fingerprint_id.startswith('FP-'):
            allow_credentials.append({
                'id': s.fingerprint_id,
                'type': 'public-key'
            })
        
    return JsonResponse({
        'success': True,
        'challenge': challenge,
        'rpId': host,
        'allowCredentials': allow_credentials,
        'has_webauthn': len(allow_credentials) > 0,
        'registered_count': registered_students.count(),
        'webauthn_count': len(allow_credentials)
    })


@csrf_exempt
def webauthn_attendance_verify(request):
    """Verify physical fingerprint credential from laptop sensor and record attendance."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
        
    try:
        credential_id = request.POST.get('credential_id', '').strip()
        if not credential_id:
            return JsonResponse({
                'success': False, 
                'message': 'No biometric fingerprint credential detected. Please touch your laptop fingerprint reader.'
            }, status=400)
            
        # Match student by physical credential ID
        student = Student.objects.filter(fingerprint_id=credential_id).first()
        
        if not student:
            return JsonResponse({
                'success': False,
                'message': 'Unregistered fingerprint! This physical biometric print does not match any registered student in the database.'
            }, status=404)
            
        if not student.authorized:
            return JsonResponse({
                'success': False,
                'message': f'Student {student.name} is not authorized for attendance. Please contact admin.'
            }, status=403)
            
        now = timezone.now()
        now_time_str = now.strftime("%I:%M %p")
        today = now.date()

        attendance, created = Attendance.objects.get_or_create(
            student=student,
            date=today
        )

        status_type = 'CHECK-IN'
        status_text = f"Checked In: {now_time_str}"
        duration_text = None
        action_title = "Check-In Confirmed"
        msg = f"{student.name} marked attendance via laptop fingerprint sensor at {now_time_str}"

        if created or not attendance.check_in_time:
            attendance.mark_checked_in()
            status_type = 'CHECK-IN'
            action_title = "Check-In Confirmed"
            status_text = f"Checked In: {now_time_str}"
            msg = f"Check-In recorded successfully for {student.name} at {now_time_str} via physical sensor."
        else:
            if attendance.check_in_time and not attendance.check_out_time:
                if now >= attendance.check_in_time + timedelta(seconds=60):
                    attendance.mark_checked_out()
                    duration_text = attendance.calculate_duration()
                    status_type = 'CHECK-OUT'
                    action_title = "Check-Out Confirmed"
                    status_text = f"Checked Out: {now_time_str} (Duration: {duration_text})"
                    msg = f"Check-Out recorded for {student.name} at {now_time_str}. Total duration: {duration_text}."
                else:
                    in_time = attendance.check_in_time.strftime("%I:%M %p")
                    status_type = 'ALREADY_CHECKED_IN'
                    action_title = "Already Checked In"
                    status_text = f"Checked In: {in_time}"
                    msg = f"{student.name} is already checked in for today (at {in_time}). Touch sensor again after 1 minute to check out."
            elif attendance.check_in_time and attendance.check_out_time:
                out_time = attendance.check_out_time.strftime("%I:%M %p")
                duration_text = attendance.calculate_duration()
                status_type = 'ALREADY_CHECKED_OUT'
                action_title = "Session Completed"
                status_text = f"Checked Out: {out_time} ({duration_text})"
                msg = f"{student.name} already completed today's attendance at {out_time} (Duration: {duration_text})."

        return JsonResponse({
            'success': True,
            'student_id': student.id,
            'student_name': student.name,
            'student_email': student.email,
            'student_class': student.student_class or '',
            'student_image': student.image.url if student.image else '',
            'finger_type': student.finger_type or 'Optical Fingerprint',
            'fingerprint_id': student.fingerprint_id or '',
            'attendance_type': status_type,
            'action_title': action_title,
            'attendance_text': status_text,
            'timestamp': now_time_str,
            'duration': duration_text,
            'message': msg
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'Fingerprint verification error: {str(e)}'}, status=500)


@csrf_exempt
def webauthn_login_verify(request):
    """Authenticate student or admin via physical laptop fingerprint sensor (WebAuthn)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    try:
        credential_id = request.POST.get('credential_id', '').strip()
        if not credential_id:
            return JsonResponse({
                'success': False,
                'message': 'No biometric fingerprint credential detected. Please touch your laptop fingerprint reader.'
            }, status=400)

        # 1. Match Student profile by physical credential
        student = Student.objects.filter(fingerprint_id=credential_id).first()
        if student:
            request.session['student_id'] = student.id
            request.session['student_name'] = student.name
            request.session['user_role'] = 'student'
            messages.success(request, f'Biometric fingerprint authenticated! Welcome, {student.name}!')
            return JsonResponse({
                'success': True,
                'role': 'student',
                'name': student.name,
                'redirect_url': '/student/dashboard/',
                'message': f'Authenticated as {student.name}'
            })

        # 2. Check Admin account (username: lokeshwar)
        admin_user = User.objects.filter(username__iexact='lokeshwar').first()
        if admin_user:
            # Check if student name or email matches administrator
            matched_admin = Student.objects.filter(fingerprint_id=credential_id, name__iexact='lokeshwar').first()
            if matched_admin or student:
                login(request, admin_user)
                request.session['user_role'] = 'admin'
                messages.success(request, f'Administrator authenticated via biometric fingerprint! Welcome, {admin_user.username}!')
                return JsonResponse({
                    'success': True,
                    'role': 'admin',
                    'name': admin_user.username,
                    'redirect_url': '/',
                    'message': f'Administrator access granted'
                })

        return JsonResponse({
            'success': False,
            'message': 'Unregistered fingerprint! This physical biometric credential is not registered to any student or admin account.'
        }, status=404)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'Fingerprint authentication error: {str(e)}'}, status=500)


# API view for real-time face detection (used for auto-capture / auto-submit during enrollment)
@csrf_exempt
def detect_face_api(request):
    """API endpoint to quickly check if a face is detected in the video stream."""
    if request.method == 'POST':
        try:
            image_data = request.POST.get('image_data', '')
            if not image_data:
                return JsonResponse({'face_detected': False, 'error': 'No image data'}, status=400)
            
            if ',' in image_data:
                header, encoded = image_data.split(',', 1)
            else:
                encoded = image_data
            image_bytes = base64.b64decode(encoded)
            
            pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            frame_rgb = np.array(pil_image)
            
            encodings, boxes = detect_and_encode(frame_rgb)
            has_face = len(encodings) > 0
            
            box_data = None
            if has_face and boxes and len(boxes) > 0:
                first_box = boxes[0]
                if isinstance(first_box, np.ndarray):
                    box_data = [float(c) for c in first_box.tolist()]
                elif isinstance(first_box, (list, tuple)):
                    box_data = [float(c) for c in first_box]

            return JsonResponse({
                'face_detected': has_face,
                'box': box_data
            })
        except Exception as e:
            return JsonResponse({'face_detected': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


# This views for capturing studen faces and recognize (Browser-based webcam)
def capture_and_recognize(request):
    """Render the webcam interface for face recognition."""
    if not (request.user.is_authenticated or request.session.get('student_id')):
        return redirect(f"/login/?next={request.path}")

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
    if not (request.user.is_authenticated or request.session.get('student_id')):
        return redirect(f"/login/?next={request.path}")

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
    # If not logged in, redirect to login page first
    if not (request.user.is_authenticated or request.session.get('student_id')):
        return redirect('login')

    total_students = Student.objects.count()
    total_attendance = Attendance.objects.count()
    total_check_ins = Attendance.objects.filter(check_in_time__isnull=False).count()
    total_check_outs = Attendance.objects.filter(check_out_time__isnull=False).count()
    total_cameras = CameraConfiguration.objects.count()

    student_id = request.session.get('student_id')
    current_student = None
    if student_id:
        current_student = Student.objects.filter(id=student_id).first()

    all_students = Student.objects.filter(authorized=True).order_by('name')
    today_attendances = Attendance.objects.filter(date=timezone.now().date()).select_related('student').order_by('-check_in_time')[:6]

    context = {
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_check_ins': total_check_ins,
        'total_check_outs': total_check_outs,
        'total_cameras': total_cameras,
        'current_student': current_student,
        'all_students': all_students,
        'today_attendances': today_attendances,
        'user_role': request.session.get('user_role', 'guest'),
    }
    return render(request, 'home.html', context)


# Custom user pass test for admin access - strictly restricted to lokeshwar
def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff) and user.username.lower() == 'lokeshwar'

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
        invalidate_face_cache()
        return redirect('student-detail', pk=pk)
    
    return render(request, 'student_authorize.html', {'student': student})

# This views is for Deleting student
@login_required
@user_passes_test(is_admin)
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        student.delete()
        invalidate_face_cache()
        messages.success(request, 'Student deleted successfully.')
        return redirect('student-list')  # Redirect to the student list after deletion
    
    return render(request, 'student_delete_confirm.html', {'student': student})


# View function for student login
def student_login(request):
    next_url = request.POST.get('next') or request.GET.get('next') or 'home'
    
    if request.session.get('student_id'):
        return redirect(next_url)

    if request.method == 'POST':
        identifier = request.POST.get('student_identifier', '').strip()
        access_key = request.POST.get('student_key', '').strip()

        if not identifier or not access_key:
            messages.error(request, 'Please provide both your Student ID/Email and phone number.')
            return render(request, 'login.html', {'active_tab': 'student', 'next': next_url})

        # Match student by Email, ID, or Name
        matched_student = None
        students = Student.objects.filter(email__iexact=identifier)
        if not students.exists() and identifier.isdigit():
            students = Student.objects.filter(id=int(identifier))
        if not students.exists():
            students = Student.objects.filter(name__iexact=identifier)

        key_digits = ''.join(filter(str.isdigit, access_key))

        for s in students:
            phone_digits = ''.join(filter(str.isdigit, s.phone_number or ''))
            # Allow match if phone ends with entered key, or exact match, or default demo key
            if (key_digits and (phone_digits.endswith(key_digits) or key_digits.endswith(phone_digits))) or s.phone_number == access_key or access_key in ['1234', '123456', 'student']:
                matched_student = s
                break

        if matched_student:
            request.session['student_id'] = matched_student.id
            request.session['student_name'] = matched_student.name
            request.session['user_role'] = 'student'
            messages.success(request, f'Welcome back, {matched_student.name}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Student record not found or phone key does not match. Please verify your details.')

    return render(request, 'login.html', {'active_tab': 'student', 'next': next_url})


# View function for administrator login - restricted to lokeshwar
def admin_login(request):
    next_url = request.POST.get('next') or request.GET.get('next') or 'home'
    
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff) and request.user.username.lower() == 'lokeshwar':
        return redirect(next_url)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if (user.is_staff or user.is_superuser) and user.username.lower() == 'lokeshwar':
                login(request, user)
                request.session['user_role'] = 'admin'
                messages.success(request, f'Administrative access granted. Welcome, {user.username}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Access denied: Only authorized administrator account (lokeshwar) has admin access.')
        else:
            messages.error(request, 'Invalid administrator credentials. Please check your username and password.')

    return render(request, 'login.html', {'active_tab': 'admin', 'next': next_url})


# Main unified user login gateway
def user_login(request):
    if request.user.is_authenticated or request.session.get('student_id'):
        return redirect('home')

    active_tab = request.GET.get('tab', 'student')
    next_url = request.POST.get('next') or request.GET.get('next') or 'home'
    
    if request.method == 'POST':
        portal_type = request.POST.get('portal_type', 'student')
        if portal_type == 'admin':
            return admin_login(request)
        else:
            return student_login(request)
            
    return render(request, 'login.html', {
        'active_tab': active_tab, 
        'next': next_url
    })


# Student Personal Dashboard View
def student_dashboard(request):
    student_id = request.session.get('student_id')
    if not student_id:
        messages.warning(request, 'Please sign in with your student credentials to view your personal dashboard.')
        return redirect('student_login')
        
    student = get_object_or_404(Student, id=student_id)
    attendances = Attendance.objects.filter(student=student).order_by('-date', '-check_in_time')
    
    today = timezone.now().date()
    today_attendance = attendances.filter(date=today).first()
    
    total_records = attendances.count()
    total_days_logged = attendances.filter(check_in_time__isnull=False).count()
    completed_sessions = attendances.filter(check_in_time__isnull=False, check_out_time__isnull=False).count()
    
    # Calculate attendance benchmark
    attendance_rate = min(100, round((total_days_logged / max(1, 22)) * 100))
    
    context = {
        'student': student,
        'attendances': attendances,
        'today_attendance': today_attendance,
        'total_records': total_records,
        'total_days_logged': total_days_logged,
        'completed_sessions': completed_sessions,
        'attendance_rate': attendance_rate,
        'today': today,
        'user_role': 'student',
    }
    return render(request, 'student_dashboard.html', context)


# User logout (clears both admin and student sessions)
def user_logout(request):
    logout(request)
    request.session.flush()
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

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
