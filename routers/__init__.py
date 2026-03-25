from fastapi import APIRouter

from . import (
    public_pages, auth_router, admin_pages, students_router, 
    faculty_router, syllabus_router, exams_router, 
    study_materials_router, notices_router, achievements_router, 
    timetable_router, student_auth, student_dashboard, student_profile
)
