
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
import os

from database import engine, create_db_and_tables, get_session
from models import User
from security import get_password_hash

# Routers
from routers import (
    public_pages, auth_router, admin_pages, students_router, 
    faculty_router, syllabus_router, exams_router, 
    study_materials_router, notices_router, achievements_router, 
    timetable_router, student_auth, student_dashboard, student_profile,
    faculty_auth, faculty_dashboard, faculty_attendance,
    faculty_materials, faculty_notices, faculty_students, faculty_timetable
)

app = FastAPI(title="IT Department Portal - ULTRA VERSION")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/uploads/students", exist_ok=True)
os.makedirs("static/uploads/faculty", exist_ok=True)
os.makedirs("static/uploads/materials", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Include Routers
app.include_router(public_pages.router)
app.include_router(auth_router.router)
app.include_router(admin_pages.router)
app.include_router(students_router.router)
app.include_router(faculty_router.router)
app.include_router(syllabus_router.router)
app.include_router(exams_router.router)
app.include_router(study_materials_router.router)
app.include_router(notices_router.router)
app.include_router(achievements_router.router)
app.include_router(timetable_router.router)
app.include_router(student_auth.router)
app.include_router(student_dashboard.router)
app.include_router(student_profile.router)
app.include_router(faculty_auth.router)
app.include_router(faculty_dashboard.router)
app.include_router(faculty_attendance.router)
app.include_router(faculty_materials.router)
app.include_router(faculty_notices.router)
app.include_router(faculty_students.router)
app.include_router(faculty_timetable.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    with Session(engine) as session:
        admin_user = session.exec(select(User).where(User.username == "dept_superadmin")).first()
        if not admin_user:
            admin_user = User(
                username="dept_superadmin",
                password_hash=get_password_hash("itdept2026"),
                role="admin"
            )
            session.add(admin_user)
            session.commit()
            print("Default admin 'dept_superadmin' created successfully.")

@app.get("/ping")
def ping():
    return {"status": "ok"}
@app.get("/")
def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/home")
