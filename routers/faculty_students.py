from fastapi import APIRouter, Request, Depends
from sqlmodel import Session, select
from database import get_session
from models import Faculty, Student
from fastapi.templating import Jinja2Templates
from routers.faculty_auth import get_current_faculty

router = APIRouter(prefix="/faculty/students", tags=["faculty_students"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_students(
    request: Request, 
    year: str = "1st Year",
    db: Session = Depends(get_session), 
    faculty: Faculty = Depends(get_current_faculty)
):
    students = db.exec(select(Student).where(Student.year == year)).all()
    return templates.TemplateResponse("faculty/students.html", {
        "request": request,
        "faculty": faculty,
        "students": students,
        "selected_year": year,
        "active_page": "students"
    })
