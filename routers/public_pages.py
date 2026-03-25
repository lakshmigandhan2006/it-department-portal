from fastapi import APIRouter, Request, Depends, HTTPException
from database import get_session
from sqlmodel import Session, select
from fastapi.templating import Jinja2Templates
from security import decode_access_token

router = APIRouter(tags=["public"])
templates = Jinja2Templates(directory="templates")

def get_current_admin(request: Request):
    token = request.cookies.get("admin_access_token")
    if not token:
        return None
    payload = decode_access_token(token)
    if payload and payload.get("role") == "admin":
        return payload.get("sub")
    return None

@router.get("/")
def home_page(request: Request, db: Session = Depends(get_session)):
    faculties = db.exec(select(Faculty).limit(4)).all()
    return templates.TemplateResponse("public/home.html", {"request": request, "faculties": faculties})

@router.get("/about")
def about_page(request: Request):
    return templates.TemplateResponse("public/about.html", {"request": request})

@router.get("/contact")
def contact_page(request: Request):
    return templates.TemplateResponse("public/contact.html", {"request": request})

# The following endpoints will fetch DB items:
from models import Faculty, Notice, Achievement
from database import get_session

@router.get("/faculty")
def public_faculty(request: Request, db: Session = Depends(get_session)):
    faculties = db.exec(select(Faculty)).all()
    return templates.TemplateResponse("public/faculty.html", {"request": request, "faculties": faculties})

@router.get("/notices")
def public_notices(request: Request, db: Session = Depends(get_session)):
    notices = db.exec(select(Notice).order_by(Notice.date_posted.desc())).all()
    return templates.TemplateResponse("public/notices.html", {"request": request, "notices": notices})

@router.get("/achievements")
def public_achievements(request: Request, db: Session = Depends(get_session)):
    achievements = db.exec(select(Achievement).order_by(Achievement.id.desc())).all()
    return templates.TemplateResponse("public/achievements.html", {"request": request, "achievements": achievements})
