from fastapi import APIRouter, Request, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from fastapi.templating import Jinja2Templates
from security import decode_access_token
from models import Student, Notice, Achievement, TimeTable, Syllabus, Exam, StudyMaterial

router = APIRouter(prefix="/student", tags=["student"])
templates = Jinja2Templates(directory="templates")

def get_current_student(request: Request, db: Session = Depends(get_session)):
    token = request.cookies.get("student_access_token")
    if not token:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/student-auth/login")
    payload = decode_access_token(token)
    if not payload or payload.get("role") != "student":
        return None
    
    student_id = payload.get("sub")
    student = db.get(Student, int(student_id))
    return student

@router.get("/dashboard")
def student_dashboard_page(request: Request, db: Session = Depends(get_session)):
    student = get_current_student(request, db)
    if not student:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/student-auth/login")
    
    notices = db.exec(select(Notice).order_by(Notice.date_posted.desc()).limit(5)).all()
    materials = db.exec(select(StudyMaterial).order_by(StudyMaterial.uploaded_at.desc()).limit(5)).all()
    
    return templates.TemplateResponse("student/dashboard.html", {
        "request": request, 
        "student": student,
        "notices": notices,
        "materials": materials
    })

@router.get("/syllabus")
def student_syllabus(request: Request, db: Session = Depends(get_session)):
    student = get_current_student(request, db)
    if not student:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/student-auth/login")
    syllabi = db.exec(select(Syllabus)).all()
    return templates.TemplateResponse("student/syllabus.html", {"request": request, "student": student, "syllabi": syllabi})

@router.get("/exams")
def student_exams(request: Request, db: Session = Depends(get_session)):
    student = get_current_student(request, db)
    if not student:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/student-auth/login")
    exams = db.exec(select(Exam)).all()
    return templates.TemplateResponse("student/exams.html", {"request": request, "student": student, "exams": exams})

@router.get("/timetable")
def student_timetable(request: Request, db: Session = Depends(get_session)):
    student = get_current_student(request, db)
    if not student:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/student-auth/login")
    timetable = db.exec(select(TimeTable)).all()
    return templates.TemplateResponse("student/timetable.html", {"request": request, "student": student, "timetable": timetable})

@router.get("/materials")
def student_materials(request: Request, db: Session = Depends(get_session)):
    student = get_current_student(request, db)
    if not student:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/student-auth/login")
    materials = db.exec(select(StudyMaterial)).all()
    return templates.TemplateResponse("student/materials.html", {"request": request, "student": student, "materials": materials})
