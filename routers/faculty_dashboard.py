from fastapi import APIRouter, Request, Depends
from sqlmodel import Session, select, func
from database import get_session
from models import Faculty, Student, Attendance, StudyMaterial, Notice
from fastapi.templating import Jinja2Templates
from routers.faculty_auth import get_current_faculty
from datetime import datetime

router = APIRouter(prefix="/faculty", tags=["faculty_dashboard"])
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard")
def faculty_dashboard(
    request: Request, 
    db: Session = Depends(get_session), 
    faculty: Faculty = Depends(get_current_faculty)
):
    # Stats
    total_students = db.exec(select(func.count(Student.id))).one()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_attendance = db.exec(
        select(func.count(Attendance.id))
        .where(Attendance.date == today_str)
        .where(Attendance.faculty_id == faculty.id)
    ).one()
    
    total_materials = db.exec(
        select(func.count(StudyMaterial.id))
        .where(StudyMaterial.uploaded_by == faculty.id)
    ).one()
    
    total_notices = db.exec(
        select(func.count(Notice.id))
        .where(Notice.posted_by == str(faculty.id))
    ).one()

    # Smart Assistant Messages
    smart_messages = []
    
    # 1. Classes today (Dummy logic for now, could be from timetable)
    smart_messages.append({
        "icon": "fa-calendar-check",
        "text": f"You have classes scheduled for your subject: {faculty.subject}.",
        "color": "primary"
    })
    
    # 2. Low attendance alert
    low_attendance_count = db.exec(
        select(func.count(Student.id)).where(Student.attendance_percentage < 75)
    ).one()
    if low_attendance_count > 0:
        smart_messages.append({
            "icon": "fa-triangle-exclamation",
            "text": f"{low_attendance_count} students have below 75% attendance.",
            "color": "danger"
        })
    
    # 3. Quick reminder
    smart_messages.append({
        "icon": "fa-lightbulb",
        "text": "Don't forget to upload today's lecture notes in Materials.",
        "color": "warning"
    })

    return templates.TemplateResponse("faculty/dashboard.html", {
        "request": request,
        "faculty": faculty,
        "active_page": "dashboard",
        "stats": {
            "students": total_students,
            "attendance": today_attendance,
            "materials": total_materials,
            "notices": total_notices
        },
        "smart_messages": smart_messages
    })
