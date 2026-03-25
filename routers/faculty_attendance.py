from fastapi import APIRouter, Request, Depends, Form, responses
from sqlmodel import Session, select
from database import get_session
from models import Faculty, Student, Attendance
from fastapi.templating import Jinja2Templates
from routers.faculty_auth import get_current_faculty
from datetime import datetime
from typing import List

router = APIRouter(prefix="/faculty/attendance", tags=["faculty_attendance"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def attendance_page(
    request: Request, 
    year: str = "1st Year",
    db: Session = Depends(get_session), 
    faculty: Faculty = Depends(get_current_faculty)
):
    students = db.exec(select(Student).where(Student.year == year)).all()
    return templates.TemplateResponse("faculty/attendance.html", {
        "request": request,
        "faculty": faculty,
        "students": students,
        "selected_year": year,
        "active_page": "attendance",
        "now": datetime.now
    })

@router.post("/mark")
def mark_attendance(
    request: Request,
    subject: str = Form(...),
    year: str = Form(...),
    date: str = Form(...),
    student_ids: List[int] = Form(...),
    status: List[str] = Form(...),
    db: Session = Depends(get_session),
    faculty: Faculty = Depends(get_current_faculty)
):
    # Iterate through students and save attendance
    for i in range(len(student_ids)):
        attendance = Attendance(
            student_id=student_ids[i],
            faculty_id=faculty.id,
            date=date,
            status=status[i],
            subject=subject,
            year=year
        )
        db.add(attendance)
        
        # Auto-calculate and update student's overall attendance percentage
        # (This is a simplified version, in a real app you'd aggregate all records)
        student = db.get(Student, student_ids[i])
        if student:
            total_records = db.exec(select(func.count(Attendance.id)).where(Attendance.student_id == student.id)).one() + 1
            present_records = db.exec(select(func.count(Attendance.id)).where(Attendance.student_id == student.id).where(Attendance.status == "Present")).one()
            if status[i] == "Present":
                present_records += 1
            
            student.attendance_percentage = round((present_records / total_records) * 100, 2)
            db.add(student)

    db.commit()
    return responses.RedirectResponse(f"/faculty/attendance?year={year}", status_code=302)

# Import func for count logic
from sqlmodel import func
