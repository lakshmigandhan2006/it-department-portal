from fastapi import APIRouter, Request, Depends
from sqlmodel import Session
from database import get_session
from fastapi.templating import Jinja2Templates
from routers.student_dashboard import get_current_student

router = APIRouter(prefix="/student/profile", tags=["student"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def student_profile_page(request: Request, db: Session = Depends(get_session)):
    student = get_current_student(request, db)
    if not student:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/student-auth/login")
    
    # Render profile which decrypts adhaar and phones inherently via model properties
    return templates.TemplateResponse("student/profile.html", {"request": request, "student": student})

@router.get("/id_card")
def generate_id_card(request: Request, db: Session = Depends(get_session)):
    student = get_current_student(request, db)
    if not student:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/student-auth/login")
    
    return templates.TemplateResponse("student/id_card.html", {"request": request, "student": student})
