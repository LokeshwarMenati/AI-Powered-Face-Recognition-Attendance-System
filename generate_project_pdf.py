"""
Generate comprehensive project documentation PDF for the
AI-Powered Face Recognition Attendance System.
"""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT_PATH = "Project-Face-attandence-system-version-1.0/docs/AI_Face_Attendance_System_Documentation.pdf"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontSize=26,
            leading=32,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1a237e"),
            spaceAfter=20,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSubtitle",
            parent=styles["Normal"],
            fontSize=14,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#424242"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading1"],
            fontSize=16,
            leading=22,
            textColor=colors.HexColor("#1565c0"),
            spaceBefore=16,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubHeading",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#37474f"),
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyJustified",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletItem",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            leftIndent=18,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeBlock",
            parent=styles["Code"],
            fontSize=8.5,
            leading=11,
            backColor=colors.HexColor("#f5f5f5"),
            leftIndent=10,
            rightIndent=10,
            spaceAfter=8,
        )
    )
    return styles


def add_table(story, headers, rows, col_widths=None):
    data = [headers] + rows
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565c0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 10))


def build_story(styles):
    story = []

    # ---- Cover Page ----
    story.append(Spacer(1, 2.5 * inch))
    story.append(Paragraph("AI-Powered Face Recognition<br/>Attendance System", styles["CoverTitle"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Complete Project Documentation", styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Version 1.0", styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.5 * inch))
    story.append(
        Paragraph(
            "Developed by <b>Lokeshwar Menati</b><br/>"
            "Django + OpenCV + Deep Learning Face Recognition",
            styles["CoverSubtitle"],
        )
    )
    story.append(Spacer(1, 1 * inch))
    story.append(HRFlowable(width="80%", thickness=1, color=colors.HexColor("#1565c0")))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Generated: August 2026", styles["CoverSubtitle"]))
    story.append(PageBreak())

    # ---- Table of Contents ----
    story.append(Paragraph("Table of Contents", styles["SectionHeading"]))
    toc_items = [
        "1. Executive Summary",
        "2. Project Overview",
        "3. Key Features",
        "4. Technology Stack",
        "5. System Architecture",
        "6. Database Design",
        "7. Face Recognition Engine",
        "8. Application Modules &amp; URL Routes",
        "9. User Workflows",
        "10. Installation &amp; Setup",
        "11. Usage Guide",
        "12. Admin &amp; Security",
        "13. Project Directory Structure",
        "14. API Reference",
        "15. Limitations &amp; Future Enhancements",
    ]
    for item in toc_items:
        story.append(Paragraph(item, styles["BulletItem"]))
    story.append(PageBreak())

    # ---- 1. Executive Summary ----
    story.append(Paragraph("1. Executive Summary", styles["SectionHeading"]))
    story.append(
        Paragraph(
            "The <b>AI-Powered Face Recognition Attendance System</b> is a web-based application "
            "designed to automate student attendance tracking using facial recognition technology. "
            "Built with Django (Python) on the backend and OpenCV for computer vision, the system "
            "eliminates manual roll-call processes by identifying registered students through a "
            "webcam or browser camera feed in real time.",
            styles["BodyJustified"],
        )
    )
    story.append(
        Paragraph(
            "Students register by submitting personal details and a facial photograph. After "
            "administrator authorization, their face embeddings are used for recognition during "
            "attendance sessions. The system automatically records check-in and check-out times, "
            "prevents duplicate entries on the same day, and provides searchable attendance reports "
            "with duration calculations.",
            styles["BodyJustified"],
        )
    )

    # ---- 2. Project Overview ----
    story.append(Paragraph("2. Project Overview", styles["SectionHeading"]))
    story.append(
        Paragraph(
            "<b>Project Name:</b> AI-Powered Face Recognition Attendance System<br/>"
            "<b>Version:</b> 1.0<br/>"
            "<b>Framework:</b> Django 5.x<br/>"
            "<b>Primary Use Case:</b> Educational institutions, training centers, and organizations "
            "requiring automated biometric attendance.<br/>"
            "<b>Repository:</b> github.com/LokeshwarMenati/AI-Powered-Face-Recognition-Attendance-System",
            styles["BodyJustified"],
        )
    )
    story.append(Paragraph("Problem Statement", styles["SubHeading"]))
    story.append(
        Paragraph(
            "Traditional attendance methods (paper registers, manual sign-in sheets) are time-consuming, "
            "prone to proxy attendance, and difficult to audit. This project addresses these challenges "
            "by providing a contactless, automated solution that leverages AI-based face recognition.",
            styles["BodyJustified"],
        )
    )
    story.append(Paragraph("Solution", styles["SubHeading"]))
    story.append(
        Paragraph(
            "A Django web application that captures student face data during registration, stores "
            "face encodings derived from ONNX deep learning models (YuNet + SFace) or optionally "
            "FaceNet (PyTorch), and matches live camera frames against the authorized student database "
            "to mark attendance automatically.",
            styles["BodyJustified"],
        )
    )

    # ---- 3. Key Features ----
    story.append(Paragraph("3. Key Features", styles["SectionHeading"]))
    features = [
        ("Student Management", "Register students with name, email, phone, class, and profile photo via webcam capture."),
        ("Authorization Workflow", "Admin must authorize students before they participate in face recognition."),
        ("Real-Time Recognition", "Browser-based webcam feeds frames to the server for face detection and matching."),
        ("Automatic Check-In/Out", "First recognition marks check-in; second recognition (after 60 seconds) marks check-out."),
        ("Duplicate Prevention", "One attendance record per student per day; prevents repeated check-ins."),
        ("Attendance Reports", "Searchable list filtered by student name and date with duration calculation."),
        ("Camera Configuration", "Configurable recognition threshold and camera source settings for admins."),
        ("Dashboard", "Home page displays total students, attendance records, check-ins, check-outs, and cameras."),
        ("Admin Panel", "Django admin interface for managing students, attendance, and camera configs."),
        ("Dual Recognition Backend", "Supports OpenCV YuNet/SFace ONNX models or PyTorch FaceNet as fallback."),
    ]
    add_table(story, ["Feature", "Description"], features, [4.5 * cm, 12 * cm])

    # ---- 4. Technology Stack ----
    story.append(Paragraph("4. Technology Stack", styles["SectionHeading"]))
    stack = [
        ("Backend Framework", "Django 5.0+ (Python web framework)"),
        ("Database", "SQLite (default, file-based)"),
        ("Computer Vision", "OpenCV (opencv-python-headless)"),
        ("Face Detection", "YuNet ONNX model (face_detection_yunet_2023mar.onnx)"),
        ("Face Recognition", "SFace ONNX model (face_recognition_sface_2021dec.onnx)"),
        ("Optional ML Stack", "PyTorch + facenet-pytorch (InceptionResnetV1 + MTCNN)"),
        ("Image Processing", "NumPy, Pillow (PIL)"),
        ("Frontend", "HTML5, CSS3, Bootstrap 5, Font Awesome, JavaScript"),
        ("Authentication", "Django built-in auth (session-based login/logout)"),
        ("Media Storage", "Local filesystem (MEDIA_ROOT/students/)"),
        ("Deployment", "Vercel configuration available (vercel.json)"),
    ]
    add_table(story, ["Component", "Technology"], stack, [4.5 * cm, 12 * cm])

    # ---- 5. System Architecture ----
    story.append(Paragraph("5. System Architecture", styles["SectionHeading"]))
    story.append(
        Paragraph(
            "The application follows a classic Django Model-View-Template (MVT) architecture with "
            "a browser-client capturing webcam frames and a server-side face recognition pipeline.",
            styles["BodyJustified"],
        )
    )
    story.append(Paragraph("Architecture Layers", styles["SubHeading"]))
    layers = [
        ("Presentation Layer", "Django HTML templates with Bootstrap styling; JavaScript captures webcam frames as Base64 and sends them via AJAX to the API."),
        ("Application Layer", "Django views handle HTTP requests, authentication, CRUD operations, and orchestrate the recognition pipeline."),
        ("Business Logic Layer", "Face detection, encoding, distance-based matching, attendance rules (check-in/out timing)."),
        ("Data Layer", "Django ORM models (Student, Attendance, CameraConfiguration) backed by SQLite."),
        ("ML/AI Layer", "OpenCV FaceDetectorYN + FaceRecognizerSF (ONNX) or PyTorch FaceNet pipeline."),
    ]
    add_table(story, ["Layer", "Responsibility"], layers, [4 * cm, 12.5 * cm])

    story.append(Paragraph("Data Flow (Attendance Marking)", styles["SubHeading"]))
    flow_steps = [
        "1. User opens the Mark Attendance page and starts the browser webcam.",
        "2. JavaScript periodically captures video frames and encodes them as Base64 JPEG.",
        "3. Frames are POSTed to /api/recognize-face/ (recognize_face_api view).",
        "4. Server decodes the image and runs face detection (YuNet or MTCNN).",
        "5. Detected faces are aligned and converted to 128/512-dimensional feature vectors (SFace or FaceNet).",
        "6. Feature vectors are compared against all authorized students' stored encodings using L2 distance.",
        "7. If distance is below the configured threshold, the student is recognized.",
        "8. Attendance logic: create record + check-in, or check-out if already checked in (after 60s cooldown).",
        "9. JSON response returns recognized names, bounding boxes, and status messages to the browser.",
    ]
    for step in flow_steps:
        story.append(Paragraph(step, styles["BulletItem"]))

    story.append(PageBreak())

    # ---- 6. Database Design ----
    story.append(Paragraph("6. Database Design", styles["SectionHeading"]))

    story.append(Paragraph("6.1 Student Model", styles["SubHeading"]))
    student_fields = [
        ("name", "CharField(255)", "Full name of the student"),
        ("email", "EmailField(255)", "Contact email address"),
        ("phone_number", "CharField(15)", "Phone number"),
        ("student_class", "CharField(100)", "Class or batch identifier"),
        ("image", "ImageField", "Profile photo stored in media/students/"),
        ("authorized", "BooleanField", "Default False; must be True for recognition"),
    ]
    add_table(story, ["Field", "Type", "Description"], student_fields, [3.5 * cm, 3.5 * cm, 9.5 * cm])

    story.append(Paragraph("6.2 Attendance Model", styles["SubHeading"]))
    attendance_fields = [
        ("student", "ForeignKey(Student)", "Reference to the student"),
        ("date", "DateField", "Auto-set to current date on creation"),
        ("check_in_time", "DateTimeField", "Timestamp when student was first recognized"),
        ("check_out_time", "DateTimeField", "Timestamp when student checked out"),
    ]
    add_table(story, ["Field", "Type", "Description"], attendance_fields, [3.5 * cm, 4 * cm, 9 * cm])
    story.append(
        Paragraph(
            "<b>Methods:</b> mark_checked_in(), mark_checked_out(), calculate_duration() — returns "
            "formatted duration string (e.g., '2h 30m 15s').",
            styles["BodyJustified"],
        )
    )

    story.append(Paragraph("6.3 CameraConfiguration Model", styles["SubHeading"]))
    camera_fields = [
        ("name", "CharField(100, unique)", "Descriptive name for the camera setup"),
        ("camera_source", "CharField(255)", "Camera index (0) or RTSP/HTTP URL for IP cameras"),
        ("threshold", "FloatField", "Recognition confidence threshold (default 0.6)"),
    ]
    add_table(story, ["Field", "Type", "Description"], camera_fields, [3.5 * cm, 4 * cm, 9 * cm])

    # ---- 7. Face Recognition Engine ----
    story.append(Paragraph("7. Face Recognition Engine", styles["SectionHeading"]))
    story.append(
        Paragraph(
            "The system implements a dual-backend approach for maximum compatibility across environments.",
            styles["BodyJustified"],
        )
    )
    story.append(Paragraph("7.1 Primary: OpenCV YuNet + SFace (ONNX)", styles["SubHeading"]))
    story.append(
        Paragraph(
            "When ONNX model files are present in the models/ directory, the system uses:<br/>"
            "• <b>YuNet</b> (face_detection_yunet_2023mar.onnx) — fast, lightweight face detection<br/>"
            "• <b>SFace</b> (face_recognition_sface_2021dec.onnx) — face alignment and 128-D feature extraction<br/><br/>"
            "This approach requires no GPU and works with opencv-python-headless, making it ideal for "
            "lightweight deployments.",
            styles["BodyJustified"],
        )
    )
    story.append(Paragraph("7.2 Fallback: PyTorch FaceNet", styles["SubHeading"]))
    story.append(
        Paragraph(
            "If PyTorch and facenet-pytorch are installed, the system uses MTCNN for face detection "
            "and InceptionResnetV1 (pretrained on VGGFace2) for 512-dimensional embeddings. This provides "
            "higher accuracy but requires more resources.",
            styles["BodyJustified"],
        )
    )
    story.append(Paragraph("7.3 Matching Algorithm", styles["SubHeading"]))
    story.append(
        Paragraph(
            "For each detected face, the system computes L2 (Euclidean) distance between the test "
            "encoding and all known encodings. The closest match below the threshold (default 0.6, "
            "configurable via CameraConfiguration) is accepted. Otherwise, the face is labeled "
            "'Not Recognized'.",
            styles["BodyJustified"],
        )
    )
    story.append(
        Paragraph(
            "<b>Key Functions (views.py):</b><br/>"
            "• detect_and_encode(image) — detects faces and returns encodings + bounding boxes<br/>"
            "• encode_uploaded_images() — loads authorized student photos and generates known encodings<br/>"
            "• recognize_faces(known_encodings, known_names, test_encodings, threshold) — performs matching",
            styles["BodyJustified"],
        )
    )

    # ---- 8. Application Modules & URL Routes ----
    story.append(PageBreak())
    story.append(Paragraph("8. Application Modules &amp; URL Routes", styles["SectionHeading"]))
    routes = [
        ("/", "home", "Dashboard with statistics", "Public"),
        ("/capture_student/", "capture_student", "Student self-registration with webcam", "Public"),
        ("/selfie-success/", "selfie_success", "Registration confirmation page", "Public"),
        ("/capture-and-recognize/", "capture_and_recognize", "Mark attendance via webcam", "Public"),
        ("/api/recognize-face/", "recognize_face_api", "JSON API for face recognition", "Public (CSRF exempt)"),
        ("/students/attendance/", "student_attendance_list", "Attendance reports with search/filter", "Public"),
        ("/students/", "student_list", "List all students", "Admin only"),
        ("/students/<pk>/", "student_detail", "View student details", "Admin only"),
        ("/students/<pk>/authorize/", "student_authorize", "Authorize/deauthorize student", "Admin only"),
        ("/students/<pk>/delete/", "student_delete", "Delete student record", "Admin only"),
        ("/login/", "user_login", "Admin login page", "Public"),
        ("/logout/", "user_logout", "Logout and redirect to login", "Authenticated"),
        ("/camera-config/", "camera_config_create", "Create camera configuration", "Admin only"),
        ("/camera-config/list/", "camera_config_list", "List camera configurations", "Admin only"),
        ("/camera-config/update/<pk>/", "camera_config_update", "Edit camera configuration", "Admin only"),
        ("/camera-config/delete/<pk>/", "camera_config_delete", "Delete camera configuration", "Admin only"),
        ("/admin/", "Django Admin", "Built-in admin panel", "Superuser"),
    ]
    add_table(story, ["URL", "View Name", "Description", "Access"], routes, [4 * cm, 3.5 * cm, 5.5 * cm, 2.5 * cm])

    # ---- 9. User Workflows ----
    story.append(Paragraph("9. User Workflows", styles["SectionHeading"]))

    story.append(Paragraph("9.1 Student Registration Workflow", styles["SubHeading"]))
    reg_steps = [
        "Navigate to Student Registration (/capture_student/).",
        "Fill in name, email, phone number, and class.",
        "Capture a clear face photo using the browser webcam.",
        "Submit the form — student is saved with authorized=False.",
        "Admin reviews and authorizes the student from the Manage Students section.",
    ]
    for i, step in enumerate(reg_steps, 1):
        story.append(Paragraph(f"{i}. {step}", styles["BulletItem"]))

    story.append(Paragraph("9.2 Attendance Marking Workflow", styles["SubHeading"]))
    att_steps = [
        "Ensure at least one student is authorized with a clear profile photo.",
        "Navigate to Mark Attendance (/capture-and-recognize/).",
        "Click Start Camera and allow browser camera permissions.",
        "Stand in front of the camera — the system auto-detects and recognizes faces.",
        "First recognition: Check-in recorded with timestamp.",
        "Second recognition (after 60 seconds): Check-out recorded.",
        "View results in Attendance Details with date and duration.",
    ]
    for i, step in enumerate(att_steps, 1):
        story.append(Paragraph(f"{i}. {step}", styles["BulletItem"]))

    story.append(Paragraph("9.3 Admin Workflow", styles["SubHeading"]))
    admin_steps = [
        "Create superuser: python manage.py createsuperuser",
        "Login at /login/ with admin credentials.",
        "Review registered students and authorize eligible ones.",
        "Configure camera settings (threshold, source) if needed.",
        "Monitor attendance reports and manage records via admin panel.",
    ]
    for i, step in enumerate(admin_steps, 1):
        story.append(Paragraph(f"{i}. {step}", styles["BulletItem"]))

    # ---- 10. Installation & Setup ----
    story.append(PageBreak())
    story.append(Paragraph("10. Installation &amp; Setup", styles["SectionHeading"]))
    story.append(Paragraph("Prerequisites", styles["SubHeading"]))
    prereqs = [
        "Python 3.8 or higher",
        "pip (Python package manager)",
        "Webcam or camera device (for browser-based capture)",
        "Optional: CMake and Visual Studio C++ Build Tools (if using dlib/face_recognition)",
    ]
    for p in prereqs:
        story.append(Paragraph(f"• {p}", styles["BulletItem"]))

    story.append(Paragraph("Installation Steps", styles["SubHeading"]))
    install_cmds = [
        "git clone https://github.com/LokeshwarMenati/AI-Powered-Face-Recognition-Attendance-System.git",
        "cd AI-Powered-Face-Recognition-Attendance-System/Project-Face-attandence-system-version-1.0",
        "python -m venv venv",
        "venv\\Scripts\\activate          (Windows)",
        "source venv/bin/activate          (macOS/Linux)",
        "pip install -r requirements.txt",
        "python manage.py migrate",
        "python manage.py createsuperuser   (optional)",
        "python manage.py runserver",
    ]
    for cmd in install_cmds:
        story.append(Paragraph(cmd, styles["CodeBlock"]))

    story.append(Paragraph("Dependencies (requirements.txt)", styles["SubHeading"]))
    deps = [
        ("Django", ">=5.0.0", "Web framework"),
        ("numpy", "latest", "Numerical computing for face vectors"),
        ("opencv-python-headless", "latest", "Computer vision without GUI dependencies"),
        ("Pillow", "latest", "Image processing and ImageField support"),
    ]
    add_table(story, ["Package", "Version", "Purpose"], deps, [4 * cm, 3 * cm, 9.5 * cm])

    story.append(Paragraph("ONNX Model Files", styles["SubHeading"]))
    story.append(
        Paragraph(
            "Place the following models in the models/ directory:<br/>"
            "• face_detection_yunet_2023mar.onnx — YuNet face detector<br/>"
            "• face_recognition_sface_2021dec.onnx — SFace recognizer<br/><br/>"
            "These can be downloaded from the OpenCV Zoo repository.",
            styles["BodyJustified"],
        )
    )

    # ---- 11. Usage Guide ----
    story.append(Paragraph("11. Usage Guide", styles["SectionHeading"]))
    story.append(
        Paragraph(
            "After starting the server, open <b>http://127.0.0.1:8000/</b> in a modern web browser "
            "(Chrome or Firefox recommended for webcam access).",
            styles["BodyJustified"],
        )
    )
    usage = [
        ("Dashboard", "View total students, attendance records, check-ins, check-outs, and configured cameras."),
        ("Student Registration", "Public page for new students to register with webcam photo capture."),
        ("Manage Students", "Admin-only: view, authorize, and delete student records."),
        ("Mark Attendance", "Open webcam interface; faces are recognized and attendance is auto-recorded."),
        ("Attendance Details", "Search by student name, filter by date, view check-in/out times and duration."),
        ("Manage Cameras", "Admin-only: create/edit/delete camera configurations and recognition thresholds."),
    ]
    add_table(story, ["Page", "How to Use"], usage, [4 * cm, 12.5 * cm])

    # ---- 12. Admin & Security ----
    story.append(Paragraph("12. Admin &amp; Security", styles["SectionHeading"]))
    story.append(Paragraph("Authentication", styles["SubHeading"]))
    story.append(
        Paragraph(
            "Django session-based authentication protects admin-only views. The @login_required and "
            "@user_passes_test(is_admin) decorators restrict student management and camera configuration "
            "to superusers. Public pages (registration, attendance marking, reports) are accessible without login.",
            styles["BodyJustified"],
        )
    )
    story.append(Paragraph("Django Admin Panel", styles["SubHeading"]))
    story.append(
        Paragraph(
            "Available at /admin/. Registered models: Student (with filters by class and authorization), "
            "Attendance (with date filters; check-in/out times are read-only on edit), and "
            "CameraConfiguration.",
            styles["BodyJustified"],
        )
    )
    story.append(Paragraph("Security Notes for Production", styles["SubHeading"]))
    security_notes = [
        "Change SECRET_KEY in settings.py before deployment.",
        "Set DEBUG = False in production.",
        "Configure ALLOWED_HOSTS appropriately (currently set to '*').",
        "Use HTTPS for webcam data transmission.",
        "Consider adding CSRF protection to the recognize_face_api endpoint.",
        "Migrate from SQLite to PostgreSQL for production workloads.",
        "Implement rate limiting on the recognition API.",
    ]
    for note in security_notes:
        story.append(Paragraph(f"• {note}", styles["BulletItem"]))

    # ---- 13. Project Directory Structure ----
    story.append(PageBreak())
    story.append(Paragraph("13. Project Directory Structure", styles["SectionHeading"]))
    structure = """Project-Face-attandence-system-version-1.0/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── db.sqlite3                # SQLite database (after migrate)
├── Project101/               # Django project settings
│   ├── settings.py           # Configuration (DB, media, timezone)
│   ├── urls.py               # Root URL routing
│   ├── wsgi.py / asgi.py     # Server entry points
├── app1/                     # Main application
│   ├── models.py             # Student, Attendance, CameraConfiguration
│   ├── views.py              # All view logic + face recognition
│   ├── urls.py               # App URL patterns
│   ├── forms.py              # Django forms
│   ├── admin.py              # Admin panel configuration
│   └── migrations/           # Database migration files
├── templates/                # HTML templates
│   ├── home.html             # Dashboard
│   ├── capture_student.html  # Registration form
│   ├── capture_and_recognize.html  # Attendance webcam UI
│   ├── student_list.html     # Student management
│   ├── student_attendance_list.html  # Reports
│   └── ...                   # Other templates
├── models/                   # ONNX model files
│   └── face_recognition_sface_2021dec.onnx
├── media/students/           # Uploaded student photos
└── staticfiles/              # Collected static files"""
    for line in structure.split("\n"):
        story.append(Paragraph(line.replace(" ", "&nbsp;"), styles["CodeBlock"]))

    # ---- 14. API Reference ----
    story.append(Paragraph("14. API Reference", styles["SectionHeading"]))
    story.append(Paragraph("POST /api/recognize-face/", styles["SubHeading"]))
    story.append(
        Paragraph(
            "<b>Description:</b> Accepts a Base64-encoded JPEG image from the browser webcam and returns "
            "face recognition results with attendance actions.<br/><br/>"
            "<b>Request:</b> POST with form data<br/>"
            "• image_data: Base64 string (data:image/jpeg;base64,...)<br/><br/>"
            "<b>Response (JSON):</b><br/>"
            "• recognized: boolean — whether any face was matched<br/>"
            "• faces: array of {name, box, recognized}<br/>"
            "• messages: array of attendance status strings<br/>"
            "• error: string (on failure)",
            styles["BodyJustified"],
        )
    )
    story.append(
        Paragraph(
            "<b>Attendance Rules:</b><br/>"
            "• New record for today → mark_checked_in()<br/>"
            "• Existing record, no check-out, ≥60 seconds since check-in → mark_checked_out()<br/>"
            "• Already checked in (<60s) → 'already checked in' message<br/>"
            "• Already checked out → 'already checked out' message",
            styles["BodyJustified"],
        )
    )

    # ---- 15. Limitations & Future Enhancements ----
    story.append(Paragraph("15. Limitations &amp; Future Enhancements", styles["SectionHeading"]))
    story.append(Paragraph("Current Limitations", styles["SubHeading"]))
    limitations = [
        "Recognition accuracy depends on lighting, angle, and photo quality.",
        "Only authorized students with stored photos can be recognized.",
        "Single-day attendance model (one check-in/out pair per day).",
        "SQLite may not scale for large institutions.",
        "No email/SMS notifications for attendance events.",
        "YuNet detection model file may need separate download.",
    ]
    for lim in limitations:
        story.append(Paragraph(f"• {lim}", styles["BulletItem"]))

    story.append(Paragraph("Suggested Future Enhancements", styles["SubHeading"]))
    enhancements = [
        "Multi-face attendance in a single frame with batch processing.",
        "Export attendance reports to CSV/PDF/Excel.",
        "Role-based access (teachers vs. administrators).",
        "Integration with IP cameras via RTSP streams.",
        "Liveness detection to prevent photo spoofing.",
        "Mobile app or PWA for remote attendance.",
        "PostgreSQL/MySQL support and cloud deployment.",
        "Real-time dashboard with charts and analytics.",
    ]
    for enh in enhancements:
        story.append(Paragraph(f"• {enh}", styles["BulletItem"]))

    # ---- Footer ----
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1565c0")))
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "<b>AI-Powered Face Recognition Attendance System v1.0</b><br/>"
            "Developed by Lokeshwar Menati<br/>"
            "Documentation generated automatically from project source code.",
            ParagraphStyle(name="Footer", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER),
        )
    )

    return story


def main():
    import os

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    styles = build_styles()
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="AI Face Attendance System Documentation",
        author="Lokeshwar Menati",
    )

    def add_page_number(canvas, doc_obj):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        page_num = canvas.getPageNumber()
        if page_num > 1:
            canvas.drawCentredString(A4[0] / 2, 1 * cm, f"Page {page_num}")
        canvas.restoreState()

    doc.build(build_story(styles), onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"PDF created successfully: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
