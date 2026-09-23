-- ==============================================================================
-- AI-Powered Face Recognition Attendance System - Database Schema (SQL)
-- Target RDBMS: SQLite 3 / PostgreSQL / MySQL
-- ==============================================================================

-- 1. Students Table
-- Stores student biometrics, credentials, and facial/fingerprint metadata
CREATE TABLE IF NOT EXISTS app1_student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    student_class VARCHAR(100) NOT NULL,
    image VARCHAR(100) NOT NULL,
    fingerprint_id VARCHAR(255) UNIQUE NULL,
    finger_type VARCHAR(50) DEFAULT 'Right Index',
    fingerprint_data TEXT NULL,
    authorized BOOLEAN DEFAULT 0 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for rapid biometric credential matching during hardware authentication
CREATE INDEX IF NOT EXISTS idx_student_fingerprint_id ON app1_student (fingerprint_id);
CREATE INDEX IF NOT EXISTS idx_student_name ON app1_student (name);
CREATE INDEX IF NOT EXISTS idx_student_authorized ON app1_student (authorized);

-- 2. Attendance Records Table
-- Daily attendance telemetry logs tracking check-in, check-out, and active sessions
CREATE TABLE IF NOT EXISTS app1_attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date DATE NOT NULL,
    check_in_time TIMESTAMP NULL,
    check_out_time TIMESTAMP NULL,
    FOREIGN KEY (student_id) REFERENCES app1_student (id) ON DELETE CASCADE
);

-- Composite index for fast student daily check-in verification
CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON app1_attendance (student_id, date);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON app1_attendance (date);

-- 3. Camera Configurations Table
-- Neural recognition thresholds, camera index mappings, and IP stream feeds
CREATE TABLE IF NOT EXISTS app1_cameraconfiguration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    camera_source VARCHAR(255) NOT NULL,
    threshold REAL DEFAULT 0.6 NOT NULL
);

-- ==============================================================================
-- Analytics Views & Reporting Queries
-- ==============================================================================

CREATE VIEW IF NOT EXISTS v_student_attendance_summary AS
SELECT 
    s.id AS student_id,
    s.name AS student_name,
    s.student_class,
    s.authorized,
    COUNT(a.id) AS total_sessions_logged,
    SUM(CASE WHEN a.check_in_time IS NOT NULL AND a.check_out_time IS NOT NULL THEN 1 ELSE 0 END) AS completed_sessions,
    MAX(a.date) AS last_attended_date
FROM app1_student s
LEFT JOIN app1_attendance a ON s.id = a.student_id
GROUP BY s.id, s.name, s.student_class, s.authorized;

-- 4. Daily Attendance Rate Telemetry
CREATE VIEW IF NOT EXISTS v_daily_attendance_metrics AS
SELECT 
    a.date,
    COUNT(DISTINCT a.student_id) AS present_count,
    ROUND(COUNT(DISTINCT a.student_id) * 100.0 / (SELECT MAX(1, COUNT(*)) FROM app1_student WHERE authorized = 1), 2) AS attendance_rate_pct
FROM app1_attendance a
GROUP BY a.date
ORDER BY a.date DESC;

-- Sample query: Retrieve today's active verified students
-- SELECT * FROM v_student_attendance_summary WHERE last_attended_date = CURRENT_DATE;

