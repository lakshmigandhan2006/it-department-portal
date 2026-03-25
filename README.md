# IT Department Portal - ULTRA VERSION

A professional Department Management System built with FastAPI, SQLModel, Jinja2, and Bootstrap. Features a Hybrid UI Design (Apple + Next-Gen UI), AES-256 encryption for sensitive data, and comprehensive Admin & Student portals.

## Features
- **Public Website**: Home, About, Faculty, Notices, Achievements, Contact.
- **Admin Portal**: Full CRUD management for Students, Faculty, Syllabus, Exams, Materials, Notices, Achievements, and Timetable.
- **Student Portal**: Authenticated dashboard to view profile (with decrypted sensitive info), syllabus, exams, timetable, and download materials.
- **Security**: Password hashing via Bcrypt, AES encryption for student sensitive data (Aadhaar, Phone, Address), secure JWT cookies for authentication.

## How to Run

1. **Create Virtual Environment & Install Dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

3. **Access the Portal**:
   - Public Site: `http://localhost:8000/`
   - Admin Login: `http://localhost:8000/admin-auth/login`
   - Student Login: `http://localhost:8000/student-auth/login`

## Default Admin Credentials
An admin account is created automatically upon the first startup.
- **Username**: `dept_superadmin`
- **Password**: `itdept2026`

## Notes
- Storage paths for file uploads are automatically created in `static/uploads/`.
- AES Secret Key is handled in `security.py`. In production, supply it via `AES_SECRET_KEY` environment variable.
