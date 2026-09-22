# AI-Powered-Face-Recognition-Attendance-System
A robust attendance management system leveraging facial recognition technology to automate student attendance tracking. Built with Django and OpenCV.

## Features

*   **Student Management**: 
    *   Register new students with personal details and profile photos.
    *   Authorize students for attendance tracking.
    *   View, update, and delete student records.
*   **Automated Attendance**:
    *   Real-time face detection and recognition using OpenCV.
    *   Automatic Check-In and Check-Out recording.
    *   Prevents duplicate check-ins for the same day.
*   **Attendance Monitoring**:
    *   View detailed attendance logs including date, check-in time, and check-out time.
    *   Automatic calculation of total duration spent.
*   **Camera Configuration**:
    *   Manage and configure camera sources for the recognition system.

## Tech Stack

*   **Backend**: Django (Python)
*   **Computer Vision**: OpenCV (`opencv-contrib-python`), `imutils`, `Pillow`
*   **Database**: SQLite (Default)
*   **Frontend**: HTML/CSS (Django Templates)

## Prerequisites

*   Python 3.8+
*   Pip
*   A webcam or camera device

## Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/LokeshwarMenati/AI-Powered-Face-Recognition-Attendance-System.git
    cd AI-Powered-Face-Recognition-Attendance-System
    ```

2.  **Navigate to the project directory**
    ```bash
    cd Project-Face-attandence-system-version-1.0
    ```

3.  **Create and activate a virtual environment (Recommended)**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

4.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If you plan to use `dlib` or `face_recognition`, ensure you have CMake and Visual Studio C++ Build Tools installed.*

5.  **Apply database migrations**
    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser (Optional, for admin access)**
    ```bash
    python manage.py createsuperuser
    ```

## Usage

1.  **Run the development server**
    ```bash
    python manage.py runserver
    ```

2.  **Access the application**
    Open your browser and navigate to `http://127.0.0.1:8000/`.

3.  **Workflow**
    *   Go to the "Students" section to add new students and upload their photos.
    *   Ensure the student is "Authorized".
    *   Go to the "Capture/Recognize" page to start the camera and mark attendance.
