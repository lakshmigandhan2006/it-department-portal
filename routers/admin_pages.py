from fastapi import APIRouter, Request, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from fastapi.templating import Jinja2Templates
from routers.public_pages import get_current_admin
from models import Student, Faculty, Exam, StudyMaterial, Notice, Achievement, TimeTable

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")

def check_admin(request: Request):
    username = get_current_admin(request)
    if not username:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return username

@router.get("/")
def admin_dashboard(request: Request, db: Session = Depends(get_session)):
    admin_user = get_current_admin(request)
    if not admin_user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/admin-auth/login")
    
    # Stats
    stats = {
        "students": len(db.exec(select(Student)).all()),
        "faculty": len(db.exec(select(Faculty)).all()),
        "exams": len(db.exec(select(Exam)).all()),
        "materials": len(db.exec(select(StudyMaterial)).all()),
        "notices": len(db.exec(select(Notice)).all()),
        "achievements": len(db.exec(select(Achievement)).all()),
        "timetable": len(db.exec(select(TimeTable)).all()),
    }
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "admin": admin_user,
        "stats": stats
    })
