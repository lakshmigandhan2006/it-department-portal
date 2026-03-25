from fastapi import APIRouter, Request, Depends, Form, responses, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Achievement
from fastapi.templating import Jinja2Templates
from routers.admin_pages import check_admin

router = APIRouter(prefix="/admin/achievements", tags=["admin_achievements"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_achievements(request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    achievements = db.exec(select(Achievement)).all()
    return templates.TemplateResponse("admin/achievements_list.html", {"request": request, "achievements": achievements})

@router.post("/add")
def add_achievement(
    title: str = Form(...), student_name: str = Form(...),
    description: str = Form(...), date: str = Form(...),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    achievement = Achievement(title=title, student_name=student_name, description=description, date=date)
    db.add(achievement)
    db.commit()
    return responses.RedirectResponse("/admin/achievements", status_code=302)

@router.get("/edit/{achievement_id}")
def edit_achievement_page(achievement_id: int, request: Request, db: Session = Depends(get_session), admin=Depends(check_admin)):
    achievement = db.get(Achievement, achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return templates.TemplateResponse("admin/achievements_edit.html", {"request": request, "achievement": achievement})

@router.post("/edit/{achievement_id}")
def edit_achievement(
    achievement_id: int, request: Request,
    title: str = Form(...), student_name: str = Form(...),
    description: str = Form(...), date: str = Form(...),
    db: Session = Depends(get_session), admin=Depends(check_admin)
):
    achievement = db.get(Achievement, achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    achievement.title = title
    achievement.student_name = student_name
    achievement.description = description
    achievement.date = date
    
    db.add(achievement)
    db.commit()
    return responses.RedirectResponse("/admin/achievements", status_code=302)

@router.get("/delete/{achievement_id}")
def delete_achievement(achievement_id: int, db: Session = Depends(get_session), admin=Depends(check_admin)):
    achievement = db.get(Achievement, achievement_id)
    if achievement:
        db.delete(achievement)
        db.commit()
    return responses.RedirectResponse("/admin/achievements", status_code=302)
