# AI-Powered-Face-Recognition-Attendance-System

[![Vercel Deployment](https://img.shields.io/badge/Vercel-Live%20Deployment-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://ai-face-attendance-system-omega.vercel.app/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%20Django%205.0-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://ai-face-attendance-system-omega.vercel.app/)

A high-speed, dual-biometric attendance management platform combining deep learning facial recognition with physical hardware fingerprint verification (WebAuthn / Windows Hello), backed by Django 5.0 and OpenCV neural models.

🌐 **Live Production URL**: [https://ai-face-attendance-system-omega.vercel.app/](https://ai-face-attendance-system-omega.vercel.app/)

---

## Language, Skills & Tech Stack Distribution

| Technology / Language | Percentage | Primary Role in System | Frameworks / Libraries / Tools |
| :--- | :---: | :--- | :--- |
| **Python** | **50%** | Backend Core, Neural Inference & Telemetry Pipeline | Django 5.0, OpenCV (`cv2`), NumPy, Pillow, Pygame |
| **HTML5** | **28%** | Responsive UI Viewports, Camera Scanners & Modals | Django Template Language (DTL), Semantic HTML5 |
| **CSS3** | **12%** | Cyberpunk Glassmorphic Theme, Micro-animations | Vanilla CSS, Flexbox/Grid, Neon Glow, Backdrop Blur |
| **JavaScript** | **8%** | WebAuthn Sensor APIs, Webcam Streaming & Telemetry | WebAuthn API, MediaDevices API, Async Fetch |
| **SQL** | **2%** | Relational Schemas, Constraints, Indexes & Views | SQLite 3, PostgreSQL Compatible DDL (`database_schema.sql`) |

```text
Language & Framework Proportion:
██████████████████████████ Python (50%)
██████████████ HTML5 (28%)
██████ CSS3 (12%)
████ JavaScript (8%)
█ SQL (2%)
```

---

## AI/ML Models & Biometric Architecture

| Component | Model / Engine | Architecture / Mechanism | Description |
| :--- | :--- | :--- | :--- |
| **Face Detection** | `YuNet` (ONNX) | Ultra-lightweight CNN (`face_detection_yunet_2023mar.onnx`) | Real-time 5-point facial landmark and bounding box detection with scale invariance. |
| **Face Recognition** | `SFace` (ONNX) | Deep Face Representation (`face_recognition_sface_2021dec.onnx`) | Extracts 128-dimensional embedding vectors matched via Cosine Distance metric. |
| **Hardware Fingerprint** | `WebAuthn / FIDO2` | Hardware Security Key / Windows Hello Fingerprint Reader | Cryptographic challenge-response verifying physical laptop fingerprint sensor. |
| **Audio Feedback** | `Pygame Sound Engine` | Real-time Audio Synthesizer | Chime and buzz feedback on successful recognition or authentication failures. |

---

## Features & Role Architecture

### 1. Student Portal (`/student/dashboard/`)
* **Personalized Dashboard**: Real-time biometric attendance metrics, presence streaks, and daily status.
* **Attendance Scanning**: Real-time facial recognition and hardware fingerprint check-in / check-out.
* **Biometric Enrollment**: Student self-enrollment with automatic facial landmark detection and physical laptop fingerprint binding.
* **Attendance Logs**: Personal telemetry records tracking check-in, check-out, and active duration.

### 2. Administrator Command Center (`/`)
* **System Oversight**: Real-time overview of total registered students, verified attendance logs, and active camera feeds.
* **Student Roster & Verification**: Authorize facial biometric weights, enroll physical laptop fingerprints, or remove records.
* **Inspect Any Student Portal**: One-click access from the roster to switch into and monitor any student's individual portal.
* **Camera Configurations**: Dynamic threshold tuning, camera source switching (webcam, RTSP IP camera streams).

---

## Tech Stack Overview

* **Backend Framework**: Django 5.0.7 (Python 3.11)
* **Computer Vision**: OpenCV (`opencv-python`), ONNX Runtime, NumPy, Pillow
* **Hardware Biometrics**: WebAuthn / FIDO2 / Windows Hello (Zero-Proxy physical sensor matching)
* **Database**: SQLite (Default) / Relational SQL Schema (`database_schema.sql`)
* **Frontend**: HTML5, Modern Glassmorphism CSS, Vanilla ES6+ JavaScript

---

## Prerequisites

* Python 3.8 to 3.11
* Pip
* Webcam or external USB/IP camera
* Optional: Laptop with integrated fingerprint reader (Windows Hello / Touch ID)

---

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/LokeshwarMenati/AI-Powered-Face-Recognition-Attendance-System.git
   cd AI-Powered-Face-Recognition-Attendance-System
   ```

2. **Navigate to the project directory**
   ```bash
   cd Project-Face-attandence-system-version-1.0
   ```

3. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS / Linux:
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create an Administrator Account**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   Open your browser and navigate to `http://localhost:8000/`.
